import csv
import math
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_CSV = BASE_DIR / "results" / "aggregated.csv"
OUTPUT_CSV = BASE_DIR / "results" / "scaling_analysis.csv"


METRICS = [
    "exec_ms",
    "opcodes",
    "bytes_allocated",
    "bytes_freed",
    "peak_heap_bytes",
    "gc_count",
    "gc_ms",
]


def safe_float(value):
    if value is None or value == "":
        return float("nan")
    return float(value)


def percent_change(first, last):
    if first == 0:
        return float("nan")
    return ((last - first) / first) * 100.0


def growth_factor(first, last):
    if first == 0:
        return float("nan")
    return last / first


def slope_per_n(first_n, last_n, first_value, last_value):
    if last_n == first_n:
        return float("nan")
    return (last_value - first_value) / (last_n - first_n)


def format_value(value):
    if isinstance(value, str):
        return value

    if math.isnan(value):
        return ""

    return f"{value:.6f}"


def main():
    print("=" * 65)
    print("clox v2 SCALING ANALYSIS")
    print("=" * 65)
    print(f"Input : {INPUT_CSV}")
    print(f"Output: {OUTPUT_CSV}")
    print()

    if not INPUT_CSV.exists():
        print(f"[FAIL] Missing input file: {INPUT_CSV}")
        raise SystemExit(1)

    with INPUT_CSV.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        rows = list(csv.DictReader(f))

    print(f"Loaded aggregated rows: {len(rows)}")

    # ---------------------------------------------------------
    # Group by benchmark
    # ---------------------------------------------------------
    benchmarks = {}

    for row in rows:
        benchmark = row["benchmark"]
        benchmarks.setdefault(benchmark, []).append(row)

    # Sort every workload by N.
    for benchmark in benchmarks:
        benchmarks[benchmark].sort(
            key=lambda row: int(row["n"])
        )

    # ---------------------------------------------------------
    # Generate workload-level scaling summary
    # ---------------------------------------------------------
    results = []

    for benchmark, workload_rows in sorted(benchmarks.items()):

        first = workload_rows[0]
        last = workload_rows[-1]

        first_n = int(first["n"])
        last_n = int(last["n"])

        result = {
            "benchmark": benchmark,
            "n_min": first_n,
            "n_max": last_n,
        }

        for metric in METRICS:

            first_value = safe_float(first[f"{metric}_mean"])
            last_value = safe_float(last[f"{metric}_mean"])

            result[f"{metric}_initial"] = first_value
            result[f"{metric}_final"] = last_value

            result[f"{metric}_growth_factor"] = growth_factor(
                first_value,
                last_value
            )

            result[f"{metric}_percent_change"] = percent_change(
                first_value,
                last_value
            )

            result[f"{metric}_slope_per_n"] = slope_per_n(
                first_n,
                last_n,
                first_value,
                last_value
            )

        results.append(result)

    # ---------------------------------------------------------
    # Write scaling summary
    # ---------------------------------------------------------
    fieldnames = [
        "benchmark",
        "n_min",
        "n_max",
    ]

    for metric in METRICS:
        fieldnames.extend([
            f"{metric}_initial",
            f"{metric}_final",
            f"{metric}_growth_factor",
            f"{metric}_percent_change",
            f"{metric}_slope_per_n",
        ])

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            row = {}

            for field in fieldnames:
                value = result[field]

                if field == "benchmark":
                    row[field] = value
                elif field in {"n_min", "n_max"}:
                    row[field] = str(value)
                else:
                    row[field] = format_value(value)

            writer.writerow(row)

    # ---------------------------------------------------------
    # Print compact human-readable summary
    # ---------------------------------------------------------
    print()
    print("-" * 65)
    print("WORKLOAD SCALING SUMMARY")
    print("-" * 65)

    for result in results:
        print()
        print(
            f"{result['benchmark']:15s} "
            f"N={result['n_min']} → {result['n_max']}"
        )

        for metric in METRICS:
            growth = result[f"{metric}_growth_factor"]
            change = result[f"{metric}_percent_change"]

            if math.isnan(growth):
                print(f"  {metric:20s}: undefined")
            else:
                print(
                    f"  {metric:20s}: "
                    f"{growth:10.3f}x "
                    f"({change:10.2f}%)"
                )

    # ---------------------------------------------------------
    # Sanity checks
    # ---------------------------------------------------------
    print()
    print("-" * 65)

    if len(results) == 12:
        print("[PASS] Scaling summary contains all 12 workloads")
    else:
        print(
            f"[FAIL] Expected 12 workloads, got {len(results)}"
        )
        raise SystemExit(1)

    if len(rows) == 240:
        print("[PASS] Input contains all 240 aggregated observations")
    else:
        print(
            f"[FAIL] Expected 240 aggregated rows, got {len(rows)}"
        )
        raise SystemExit(1)

    print()
    print(f"Scaling analysis written to:")
    print(OUTPUT_CSV)

    print()
    print("=" * 65)
    print("SCALING ANALYSIS COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    main()