# classify_ground_type.py

"""
MIT License

Copyright (c) 2025 Albert Pamonag Engineering Consultancy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

Ground Type Classification Tool
================================
This script computes the ground characteristic value TG for seismic site classification 
based on cumulative layer properties, and classifies the ground type according to standards.

Reference Formula:
    TG = 4 * Σ(H/Vs)

Ground Type Classification:
    - Type I  : TG < 0.2
    - Type II : 0.2 ≤ TG < 0.6
    - Type III: 0.6 ≤ TG
"""

def classify_ground_type(data=None):
    """
    Classifies ground type per cumulative layer and builds a detailed table.

    Parameters:
    ----------
    data : list of lists, optional
        Input data, each sublist containing [H (m), Vs (m/s)].
        If None, default example data is used.

    Returns:
    -------
    list of lists
        Table where each row contains [H, Vs, H/V, TG, Ground Type].
    """
    if data is None:
        # Default example dataset
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
    cumulative_sum = 0.0

    for H, Vs in data:
        if Vs == 0:
            Hv = None
        else:
            Hv = H / Vs
            cumulative_sum += Hv

        Tg = 4 * cumulative_sum

        # Ground Type Classification
        if Tg < 0.2:
            ground_type = "Type I"
        elif 0.2 <= Tg < 0.6:
            ground_type = "Type II"
        else:
            ground_type = "Type III"

        table.append([H, Vs, Hv, Tg, ground_type])

    return table


if __name__ == "__main__":
    # Example usage: Run as standalone script
    result_table = classify_ground_type()

    # Table headers
    print(f"{'H':>3} {'Vs':>10} {'H/V':>15} {'TG = 4*sum':>15} {'Type':>10}")
    for row in result_table:
        H, Vs, Hv, Tg, ground_type = row
        print(f"{H:>3} {Vs:>10.6f} {Hv:>15.12f} {Tg:>15.6f} {ground_type:>10}")
