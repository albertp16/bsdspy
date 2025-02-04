import matplotlib.pyplot as plt


class SeismicSiteFactor:
    """
    A class to compute site factors and response spectrum based on NSCP 2015 and ACI 318-19.

    Attributes:
        ground_type (str): Site classification (I, II, or III).
    """

    def __init__(self, ground_type):
        """
        Initializes the class with the site ground type.

        :param ground_type: Site classification (I, II, or III).
        """
        self.ground_type = ground_type
        self.site_factors = {
            'I': {"0.00": 1.2, "0.10": 1.2, "0.20": 1.2, "0.30": 1.1, "0.40": 1.1, "0.50": 1.0, "0.80": 1.0},
            'II': {"0.00": 1.6, "0.10": 1.6, "0.20": 1.4, "0.30": 1.2, "0.40": 1.0, "0.50": 0.9, "0.80": 0.85},
            'III': {"0.00": 2.5, "0.10": 2.5, "0.20": 1.7, "0.30": 1.2, "0.40": 0.9, "0.50": 0.8, "0.80": 0.75}
        }

    def interpolate_site_factor(self, pga):
        """
        Interpolates the site factor for a given PGA.

        :param pga: Peak ground acceleration (PGA).
        :return: Interpolated site factor.
        """
        factors = self.site_factors.get(self.ground_type)
        if not factors:
            return None

        numeric_pga_keys = sorted([float(k) for k in factors.keys()])
        if pga <= numeric_pga_keys[0]:
            return factors["{:.2f}".format(numeric_pga_keys[0])]
        if pga >= numeric_pga_keys[-1]:
            return factors["{:.2f}".format(numeric_pga_keys[-1])]

        for i in range(len(numeric_pga_keys) - 1):
            if numeric_pga_keys[i] <= pga < numeric_pga_keys[i + 1]:
                lower_pga = numeric_pga_keys[i]
                upper_pga = numeric_pga_keys[i + 1]
                lower_factor = factors["{:.2f}".format(lower_pga)]
                upper_factor = factors["{:.2f}".format(upper_pga)]
                return lower_factor + (pga - lower_pga) * \
                    (upper_factor - lower_factor) / (upper_pga - lower_pga)

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
