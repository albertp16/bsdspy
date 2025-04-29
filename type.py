def classify_ground_type_table(data=None):
    """
    Classifies ground type per cumulative layer and builds a detailed table.
    
    Formula:
        TG = 4 * sum(H/Vs)

    Ground Type Classification:
        - Type I  : TG < 0.2
        - Type II : 0.2 ≤ TG < 0.6
        - Type III: 0.6 ≤ TG

    Parameters:
        data (list of lists, optional): Each sublist contains [H (m), Vs (m/s)].
            Example:
            [
                [4, 281.25],
                [2, 290],
                [15, 301],
                ...
            ]

    Returns:
        list of lists: Table with columns [H, Vs, H/V, TG, Ground Type].
    """
    if data is None:
        # Default sample data if none provided
        data = [
            [4, 281.25],
            [2, 290],
            [15, 301],
            [6, 291.8333333],
            [5, 311.8],
            [19, 330.5263158],
            [4, 456.25],
            [1, 481],
            [1, 740],
            [1, 679],
            [3, 938.6666667],
            [11, 1705.818182]
        ]

    table = []
    cumulative_sum = 0

    for H, Vs in data:
        if Vs == 0:
            Hv = None
        else:
            Hv = H / Vs
            cumulative_sum += Hv

        Tg = 4 * cumulative_sum

        # Determine ground type
        if Tg < 0.2:
            ground_type = "Type I"
        elif 0.2 <= Tg < 0.6:
            ground_type = "Type II"
        else:
            ground_type = "Type III"

        table.append([H, Vs, Hv, Tg, ground_type])

    return table


if __name__ == "__main__":
    # Example usage if run directly
    result_table = classify_ground_type_table()

    print(f"{'H':>3} {'Vs':>10} {'H/V':>15} {'TG = 4*sum':>15} {'Type':>10}")
    for row in result_table:
        H, Vs, Hv, Tg, ground_type = row
        print(f"{H:>3} {Vs:>10.6f} {Hv:>15.12f} {Tg:>15.6f} {ground_type:>10}")
