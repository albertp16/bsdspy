def interpolate_site_factor(pga, ground_type):
    site_factors = {
        'I': {"0.00":1.2, "0.10": 1.2, "0.20": 1.2, "0.30": 1.1, "0.40": 1.1, "0.50": 1.0, "0.80": 1.0},
        'II': {"0.00":1.6, "0.10": 1.6, "0.20": 1.4, "0.30": 1.2, "0.40": 1.0, "0.50": 0.9, "0.80": 0.85},
        'III': {"0.00":2.5, "0.10": 2.5, "0.20": 1.7, "0.30": 1.2, "0.40": 0.9, "0.50": 0.8, "0.80": 0.75}
    }
    factors = site_factors.get(ground_type)
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


def get_site_factor_fa(ss, ground_type):
    fa_table = {
        'I': [
            {'maxSs': 0.25, 'Fa': 1.2},
            {'maxSs': 0.50, 'Fa': 1.2},
            {'maxSs': 0.75, 'Fa': 1.1},
            {'maxSs': 1.00, 'Fa': 1.0},
            {'maxSs': 1.25, 'Fa': 1.0},
            {'maxSs': 2.00, 'Fa': 1.0}
        ],
        'II': [
            {'maxSs': 0.25, 'Fa': 1.6},
            {'maxSs': 0.50, 'Fa': 1.4},
            {'maxSs': 0.75, 'Fa': 1.2},
            {'maxSs': 1.00, 'Fa': 1.0},
            {'maxSs': 1.25, 'Fa': 0.9},
            {'maxSs': 2.00, 'Fa': 0.85}
        ],
        'III': [
            {'maxSs': 0.25, 'Fa': 2.5},
            {'maxSs': 0.50, 'Fa': 1.7},
            {'maxSs': 0.75, 'Fa': 1.2},
            {'maxSs': 1.00, 'Fa': 0.9},
            {'maxSs': 1.25, 'Fa': 0.8},
            {'maxSs': 2.00, 'Fa': 0.75}
        ]
    }

    table = fa_table.get(ground_type)
    if not table:
        return None

    for i in range(len(table) - 1):
        current = table[i]
        nxt = table[i + 1]
        if ss <= current['maxSs']:
            return current['Fa']
        if current['maxSs'] < ss <= nxt['maxSs']:
            slope = (nxt['Fa'] - current['Fa']) / (nxt['maxSs'] - current['maxSs'])
            return current['Fa'] + slope * (ss - current['maxSs'])

    return table[-1]['Fa']


def get_site_factor_fv(s1, ground_type):
    table = {
        'I':   [1.7, 1.6, 1.5, 1.4, 1.4, 1.4],
        'II':  [2.4, 2.0, 1.8, 1.6, 1.5, 1.5],
        'III': [3.5, 3.2, 2.8, 2.4, 2.4, 2.0]
    }
    s1_values = [0.10, 0.20, 0.30, 0.40, 0.50, 0.80]

    row = table.get(ground_type)
    if not row:
        return None

    for i in range(len(s1_values) - 1):
        if s1 <= s1_values[i]:
            return row[i]
        elif s1_values[i] < s1 < s1_values[i + 1]:
            factor1 = row[i]
            factor2 = row[i + 1]
            lower = s1_values[i]
            upper = s1_values[i + 1]
            return factor1 + ((factor2 - factor1) * (s1 - lower) / (upper - lower))
        else:
            # s1 >= 0.80
            pass
    return row[-1]


pga = 0.6
ss = 1.1 
s1 = 0.4

print(interpolate_site_factor(pga, 'III'))  # 1.0
print(get_site_factor_fa(ss, 'III'))  # 1.0
print(get_site_factor_fv(s1, 'III'))  # 1.4