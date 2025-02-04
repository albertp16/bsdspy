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


class SeismicDesign:
    """
    A class to compute seismic parameters based on NSCP 2015 and ACI 318-19.
    """

    def __init__(self, ground_type):
        self.ground_type = ground_type

    def get_site_factor_fa(self, ss):
        """
        Computes Fa (short-period site coefficient).

        :param ss: Spectral acceleration at 0.2s (Ss).
        :return: Site factor Fa.
        """
        fa_table = {
            'I': [1.2, 1.2, 1.1, 1.0, 1.0, 1.0],
            'II': [1.6, 1.4, 1.2, 1.0, 0.9, 0.85],
            'III': [2.5, 1.7, 1.2, 0.9, 0.8, 0.75]
        }
        ss_values = [0.25, 0.50, 0.75, 1.00, 1.25, 2.00]
        return self.interpolate_factor(ss, ss_values, fa_table[self.ground_type])

    def get_site_factor_fv(self, s1):
        """
        Computes Fv (long-period site coefficient).

        :param s1: Spectral acceleration at 1.0s (S1).
        :return: Site factor Fv.
        """
        fv_table = {
            'I': [1.7, 1.6, 1.5, 1.4, 1.4, 1.4],
            'II': [2.4, 2.0, 1.8, 1.6, 1.5, 1.5],
            'III': [3.5, 3.2, 2.8, 2.4, 2.4, 2.0]
        }
        s1_values = [0.10, 0.20, 0.30, 0.40, 0.50, 0.80]
        return self.interpolate_factor(s1, s1_values, fv_table[self.ground_type])

    @staticmethod
    def interpolate_factor(value, reference_values, factors):
        """
        Performs linear interpolation between given reference values.

        :param value: The input value to interpolate.
        :param reference_values: List of reference values.
        :param factors: List of corresponding factor values.
        :return: Interpolated factor.
        """
        for i in range(len(reference_values) - 1):
            if value <= reference_values[i]:
                return factors[i]
            elif reference_values[i] < value < reference_values[i + 1]:
                return factors[i] + (factors[i + 1] - factors[i]) * \
                       (value - reference_values[i]) / (reference_values[i + 1] - reference_values[i])
        return factors[-1]

    @staticmethod
    def generate_design_response_spectrum(to, ts, As, sds, sd1):
        """
        Generates a design response spectrum.

        :param to: Characteristic period To.
        :param ts: Characteristic period Ts.
        :param As: Peak ground acceleration.
        :param sds: Design spectral acceleration at short period.
        :param sd1: Design spectral acceleration at 1.0s.
        :return: Tuple (periods, accelerations).
        """
        periods = [0, to, ts] + [ts + 0.5 * i for i in range(1, 13)]
        accelerations = [As, sds, sds] + [sd1 / periods[i] for i in range(3, len(periods))]
        return periods, accelerations

    @staticmethod
    def plot_design_response_spectrum(periods, accelerations):
        """
        Plots the design response spectrum.

        :param periods: List of periods.
        :param accelerations: List of spectral accelerations.
        """
        plt.plot(periods, accelerations, marker='o')
        plt.xlabel('Period (s)')
        plt.ylabel('Spectral Acceleration (g)')
        plt.title('Design Response Spectrum')
        plt.grid()
        plt.show()
