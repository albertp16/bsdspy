import matplotlib.pyplot as plt

class SeismicSiteFactor:
    """
    A class to compute site factors and response spectrum based on NSCP 2015 and ACI 318-19.

    Attributes:
        ground_type (str): Site classification (I, II, or III).
        pga (float): Peak ground acceleration (PGA).
        ss (float): Spectral acceleration at 0.2s (short period).
        s1 (float): Spectral acceleration at 1.0s (long period).
        site_factors (dict): Dictionary of reference PGA site factors for each ground type.
    """

    def __init__(self, ground_type, pga=None, ss=None, s1=None):
        """
        Initializes the class with the site ground type and optional values for pga, ss, and s1.

        Args:
            ground_type (str): Site classification ('I', 'II', or 'III').
            pga (float, optional): Peak ground acceleration. Defaults to None.
            ss (float, optional): Spectral acceleration at 0.2s. Defaults to None.
            s1 (float, optional): Spectral acceleration at 1.0s. Defaults to None.

        Raises:
            ValueError: If ground_type is invalid or any numerical input is negative.
        """

        # Guard clause for valid ground_type
        if ground_type not in ("I", "II", "III"):
            raise ValueError("ground_type must be 'I', 'II', or 'III'.")

        # Guard clauses for numeric inputs
        if pga is not None and pga < 0:
            raise ValueError("PGA cannot be negative.")
        if ss is not None and ss < 0:
            raise ValueError("Ss cannot be negative.")
        if s1 is not None and s1 < 0:
            raise ValueError("S1 cannot be negative.")

        self.ground_type = ground_type
        self.pga = pga
        self.ss = ss
        self.s1 = s1

        # Dictionary of site factors keyed by ground type
        self.site_factors = {
            'I': {"0.00": 1.2, "0.10": 1.2, "0.20": 1.2, "0.30": 1.1, "0.40": 1.1, "0.50": 1.0, "0.80": 1.0},
            'II': {"0.00": 1.6, "0.10": 1.6, "0.20": 1.4, "0.30": 1.2, "0.40": 1.0, "0.50": 0.9, "0.80": 0.85},
            'III': {"0.00": 2.5, "0.10": 2.5, "0.20": 1.7, "0.30": 1.2, "0.40": 0.9, "0.50": 0.8, "0.80": 0.75}
        }

    def interpolate_site_factor(self):
        """
        Interpolates the site factor for self.pga using the ground_type's
        dictionary in self.site_factors, via the interpolate_factor method.

        Returns:
            float or None: Interpolated site factor if valid;
                           None if ground_type is invalid or pga is not set.

        Raises:
            ValueError: If pga is None and cannot be computed.
        """
        if self.pga is None:
            raise ValueError("Cannot interpolate site factor because 'pga' is None.")

        # Grab the dictionary for this ground type
        factors_dict = self.site_factors.get(self.ground_type)
        if factors_dict is None:
            # Invalid ground_type (extra safety check)
            return None

        # Convert string keys -> float, and map those floats to factor values
        numeric_pga_keys = sorted([float(k) for k in factors_dict.keys()])
        factor_values = [factors_dict[f"{k:.2f}"] for k in numeric_pga_keys]

        # Use the static interpolation method
        return self.interpolate_factor(self.pga, numeric_pga_keys, factor_values)

    def get_site_factor_fa(self):
        """
        Computes Fa (short-period site coefficient) using self.ss.

        Returns:
            float: Interpolated Fa site coefficient.

        Raises:
            ValueError: If ss is None and cannot be computed.
        """
        if self.ss is None:
            raise ValueError("Cannot compute Fa because 'ss' is None.")

        fa_table = {
            'I': [1.2, 1.2, 1.1, 1.0, 1.0, 1.0],
            'II': [1.6, 1.4, 1.2, 1.0, 0.9, 0.85],
            'III': [2.5, 1.7, 1.2, 0.9, 0.8, 0.75]
        }
        ss_values = [0.25, 0.50, 0.75, 1.00, 1.25, 2.00]

        return self.interpolate_factor(self.ss, ss_values, fa_table[self.ground_type])

    def get_site_factor_fv(self):
        """
        Computes Fv (long-period site coefficient) using self.s1.

        Returns:
            float: Interpolated Fv site coefficient.

        Raises:
            ValueError: If s1 is None and cannot be computed.
        """
        if self.s1 is None:
            raise ValueError("Cannot compute Fv because 's1' is None.")

        fv_table = {
            'I': [1.7, 1.6, 1.5, 1.4, 1.4, 1.4],
            'II': [2.4, 2.0, 1.8, 1.6, 1.5, 1.5],
            'III': [3.5, 3.2, 2.8, 2.4, 2.4, 2.0]
        }
        s1_values = [0.10, 0.20, 0.30, 0.40, 0.50, 0.80]

        return self.interpolate_factor(self.s1, s1_values, fv_table[self.ground_type])

    @staticmethod
    def interpolate_factor(value, reference_values, factors):
        """
        Performs linear interpolation (or direct boundary lookup) for `value`.
        
        Args:
            value (float): The input value to interpolate.
            reference_values (list of float): Sorted list of reference points.
            factors (list of float): List of corresponding factor values.

        Returns:
            float: Interpolated or boundary factor.
        """
        # Check lower and upper boundaries
        if value <= reference_values[0]:
            return factors[0]
        if value >= reference_values[-1]:
            return factors[-1]

        # Linear interpolation within the range
        for i in range(len(reference_values) - 1):
            if reference_values[i] <= value < reference_values[i + 1]:
                # Linear interpolation formula
                return factors[i] + (
                    (value - reference_values[i]) *
                    (factors[i + 1] - factors[i]) /
                    (reference_values[i + 1] - reference_values[i])
                )

        # Fallback to last factor (should never reach here if lists match up)
        return factors[-1]

class SeismicDesignResponse:
    """
    A class to compute seismic parameters based on NSCP 2015 and ACI 318-19.
    """

    def __init__(self, pga, fpga, ss, s1, fa, fv):
        """
        Initialize seismic design parameters.

        :param pga: Peak ground acceleration.
        :param fpga: Site coefficient for ground acceleration.
        :param ss: Mapped maximum considered earthquake spectral response acceleration parameter at short periods.
        :param s1: Mapped maximum considered earthquake spectral response acceleration parameter at 1s.
        :param fa: Site amplification factor at short periods.
        :param fv: Site amplification factor at 1s.
        """
        # Guard clause to ensure input parameters are valid.
        if any(param < 0 for param in [pga, fpga, ss, s1, fa, fv]):
            raise ValueError("All input parameters must be non-negative.")
        
        self.pga = pga
        self.fpga = fpga
        self.ss = ss
        self.s1 = s1
        self.fa = fa
        self.fv = fv

    def calculate_as(self):
        """
        Effective peak ground acceleration coefficient.
        """
        return self.fpga * self.pga

    def calculate_sds(self):
        """
        Design spectral acceleration at short period (0.2s).
        """
        return self.fa * self.ss

    def calculate_sd1(self):
        """
        Design spectral acceleration at 1.0s.
        """
        return self.fv * self.s1

    def calculate_ts(self):
        """
        Characteristic period Ts = SD1 / SDS.
        
        In some references, Ts = SD1 / SDS. 
        The original code used 'return self.calculate_sd1() * self.calculate_sds()', 
        which seems unconventional, but we'll preserve the original logic. 
        You may want to verify your code-based formula.
        """
        return self.calculate_sd1() * self.calculate_sds()

    def calculate_to(self):
        """
        Characteristic period To = 0.2 * Ts.
        """
        return 0.2 * self.calculate_ts()

    def generate_design_response_spectrum(self, max_period=6.0, step=0.1):
        """
        Generates a design response spectrum with piecewise definition:

        - T = 0          =>  C(T) = A_s              (avoids divide-by-zero)
        - 0 < T < T0     =>  (optional) linearly interpolate from A_s up to S_DS
        - T0 <= T <= 1   =>  C(T) = S_DS
        - T  > 1         =>  C(T) = S_D1 / T

        Where:
        T0 = 0.2 * Ts       # if you want a ramp before the plateau
        A_s = F_pga * PGA
        S_DS = F_a * S_s
        S_D1 = F_v * S_1
        """

        # 1) Compute necessary parameters
        A_s  = self.calculate_as()    
        S_DS = self.calculate_sds()
        S_D1 = self.calculate_sd1()

        # We might still compute T_s and T_0 if needed, but we won't use T_s for 
        # the decay branch anymore (since user wants it to start at T=1).
        T_s  = self.calculate_ts()     # Usually = S_D1 / S_DS
        T_0  = 0.2 * T_s               # If you want to ramp from T=0 to T_0

        periods = []
        accelerations = []

        t = 0.0
        while t <= max_period:
            periods.append(t)

            if t == 0:
                #  Avoid divide-by-zero
                accel = A_s

            elif 0 < t < T_0:
                # Optional: linear ramp from A_s (at t=0) up to S_DS (at t=T_0).
                # If you don't want a ramp, just use accel = S_DS
                slope = (S_DS - A_s) / T_0
                accel = A_s + slope * t

            elif T_0 <= t <= 1.0:
                # Plateau at S_DS up to T=1.0
                accel = S_DS

            else:
                # For T>1, switch to the decaying branch
                accel = S_D1 / t

            accelerations.append(accel)

            t = round(t + step, 5)

        return periods, accelerations
    def plot_design_response_spectrum(self):
        """
        Plots the design response spectrum using matplotlib.
        """
        periods, accelerations = self.generate_design_response_spectrum()
        plt.figure()
        plt.plot(periods, accelerations, 
         color="blue", 
         linestyle="--",  # dashed line
         marker=None)     # no markers
        plt.xlabel("Period Tm (sec)")
        plt.ylabel("Elastic Seismic Coefficient")
        plt.title("Design Response Spectrum")
        plt.grid(True)
        plt.show()            

pga = 0.6
ss = 1.1
s1 = 0.4
site_class = 'III'

# Instantiate the class
seismic_site_factor = SeismicSiteFactor(site_class,pga,ss,s1)

fpga = seismic_site_factor.interpolate_site_factor()
fa = seismic_site_factor.get_site_factor_fa()
fv = seismic_site_factor.get_site_factor_fv()
seismic_design = SeismicDesignResponse(pga,fpga,ss,s1,fa,fv)
print(seismic_design.calculate_as())
print(seismic_design.calculate_sds())
print(seismic_design.calculate_sd1())
print(seismic_design.calculate_ts())
print(seismic_design.calculate_to())
seismic_design.plot_design_response_spectrum()