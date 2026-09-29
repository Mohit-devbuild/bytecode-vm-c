import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, stdev


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_CSV = BASE_DIR / "results" / "dataset_v2.csv"
OUTPUT_CSV = BASE_DIR / "results" / "aggregated.csv"


METRICS = [
    "wall_ms",
    "compile_ms",
    "exec_ms",
    "opcodes",
    "gc_count",
    "gc_ms",
    "peak_heap_bytes",
    "bytes_allocated",
    "bytes_freed",
]


def coefficient_of_variation(values):
    """
    CV = standard deviation / mean.

    Returns NaN when the mean is zero because CV is undefined.
    """
    avg = mean(values)

    if avg == 0:
        return float("nan")

    if len(values) < 2:
        return float("nan")

    return stdev(values) / avg


def format_number(value):
    """
    Keep CSV output readable while preserving useful precision.
    """
    if isinstance(value, int):
        return str(value)

    if math.isnan(value):
        return ""

    return f"{value:.6f}"


def main():
    print("=" * 60)
    print("clox v2 DATASET AGGREGATION")
    print("=" * 60)
    print(f"Input : {INPUT_CSV}")
    print(f"Output: {OUTPUT_CSV}")
    print()

    if not INPUT_CSV.exists():
        print(f"[FAIL] Input CSV not found: {INPUT_CSV}")
        raise SystemExit(1)

    # ---------------------------------------------------------
    # Read raw dataset
    # ---------------------------------------------------------
    with INPUT_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded rows: {len(rows)}")

    # ---------------------------------------------------------
    # Group by benchmark + N
    # ---------------------------------------------------------
    groups = defaultdict(list)

    for row in rows:
        benchmark = row["benchmark"]
        n = int(row["n"])

        groups[(benchmark, n)].append(row)

    print(f"Unique benchmark × N groups: {len(groups)}")

    # ---------------------------------------------------------
    # Aggregate
    # ---------------------------------------------------------
    output_rows = []

    for (benchmark, n), group in sorted(
        groups.items(),
        key=lambda item: (item[0][0], item[0][1])
    ):
        output = {
            "benchmark": benchmark,
            "n": n,
            "repetitions": len(group),
        }

        for metric in METRICS:
            values = [float(row[metric]) for row in group]

            output[f"{metric}_mean"] = mean(values)
            output[f"{metric}_median"] = median(values)

            if len(values) >= 2:
                output[f"{metric}_std"] = stdev(values)
            else:
                output[f"{metric}_std"] = float("nan")

            output[f"{metric}_min"] = min(values)
            output[f"{metric}_max"] = max(values)
            output[f"{metric}_cv"] = coefficient_of_variation(values)

        output_rows.append(output)

    # ---------------------------------------------------------
    # Write aggregated CSV
    # ---------------------------------------------------------
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "benchmark",
        "n",
        "repetitions",
    ]

    for metric in METRICS:
        fieldnames.extend([
            f"{metric}_mean",
            f"{metric}_median",
            f"{metric}_std",
            f"{metric}_min",
            f"{metric}_max",
            f"{metric}_cv",
        ])

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in output_rows:
            formatted = {}

            for field in fieldnames:
                value = row[field]

                if field in {"benchmark"}:
                    formatted[field] = value
                elif field in {"n", "repetitions"}:
                    formatted[field] = str(value)
                else:
                    formatted[field] = format_number(value)

            writer.writerow(formatted)

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------
    print()
    print(f"Aggregated rows written: {len(output_rows)}")
    print(f"Output file: {OUTPUT_CSV}")
    print()

    expected_groups = 12 * 20

    if len(output_rows) == expected_groups:
        print(f"[PASS] Exactly {expected_groups} benchmark × N groups")
    else:
        print(
            f"[FAIL] Expected {expected_groups} groups, "
            f"got {len(output_rows)}"
        )
        raise SystemExit(1)

    bad_repetitions = [
        row
        for row in output_rows
        if row["repetitions"] != 40
    ]

    if not bad_repetitions:
        print("[PASS] Every group contains exactly 40 repetitions")
    else:
        print(
            f"[FAIL] {len(bad_repetitions)} groups "
            f"do not contain 40 repetitions"
        )
        raise SystemExit(1)

    print()
    print("=" * 60)
    print("AGGREGATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()