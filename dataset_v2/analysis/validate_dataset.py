import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


CSV_PATH = Path(__file__).resolve().parent.parent / "results" / "dataset_v2.csv"

EXPECTED_BENCHMARKS = {
    "arithmetic": [
        40000, 49100, 60400, 74200, 91100, 112000, 138000, 169000,
        208000, 255000, 314000, 385000, 473000, 581000, 714000,
        878000, 1080000, 1320000, 1630000, 2000000
    ],
    "classes": [
        12000, 14700, 18100, 22300, 27300, 33600, 41300, 50700,
        62300, 76600, 94100, 116000, 142000, 174000, 214000,
        263000, 324000, 397000, 488000, 600000
    ],
    "closures": [
        14000, 17200, 21100, 26000, 31900, 39200, 48200, 59200,
        72700, 89300, 110000, 135000, 166000, 204000, 250000,
        307000, 377000, 464000, 570000, 700000
    ],
    "control_flow": [
        20000, 24600, 30200, 37100, 45600, 56000, 68800, 84500,
        104000, 128000, 157000, 193000, 237000, 291000, 357000,
        439000, 539000, 662000, 814000, 1000000
    ],
    "gc_stress": [
        6000, 7370, 9060, 11100, 13700, 16800, 20600, 25400,
        31200, 38300, 47000, 57800, 71000, 87200, 107000,
        132000, 162000, 199000, 244000, 300000
    ],
    "globals": [
        14000, 17200, 21100, 26000, 31900, 39200, 48200, 59200,
        72700, 89300, 110000, 135000, 166000, 204000, 250000,
        307000, 377000, 464000, 570000, 700000
    ],
    "integrated": [
        8000, 9830, 12100, 14800, 18200, 22400, 27500, 33800,
        41500, 51000, 62700, 77000, 94700, 116000, 143000,
        176000, 216000, 265000, 326000, 400000
    ],
    "locals": [
        28000, 34400, 42300, 51900, 63800, 78400, 96300, 118000,
        145000, 179000, 219000, 270000, 331000, 407000, 500000,
        614000, 755000, 927000, 1140000, 1400000
    ],
    "methods": [
        16000, 19700, 24200, 29700, 36500, 44800, 55000, 67600,
        83100, 102000, 125000, 154000, 189000, 233000, 286000,
        351000, 431000, 530000, 651000, 800000
    ],
    "properties": [
        16000, 19700, 24200, 29700, 36500, 44800, 55000, 67600,
        83100, 102000, 125000, 154000, 189000, 233000, 286000,
        351000, 431000, 530000, 651000, 800000
    ],
    "recursion": list(range(12, 32)),
    "string_concat": [
        2500, 2820, 3190, 3600, 4060, 4580, 5170, 5840, 6590,
        7440, 8400, 9480, 10700, 12100, 13600, 15400, 17400,
        19600, 22100, 25000
    ],
}

EXPECTED_COLUMNS = {
    "run_order",
    "timestamp",
    "benchmark",
    "n",
    "rep",
    "wall_ms",
    "compile_ms",
    "exec_ms",
    "opcodes",
    "gc_count",
    "gc_ms",
    "peak_heap_bytes",
    "bytes_allocated",
    "bytes_freed",
    "output",
    "opcode_counts",
}

NUMERIC_COLUMNS = {
    "run_order",
    "n",
    "rep",
    "wall_ms",
    "compile_ms",
    "exec_ms",
    "opcodes",
    "gc_count",
    "gc_ms",
    "peak_heap_bytes",
    "bytes_allocated",
    "bytes_freed",
}


def fail(message):
    print(f"[FAIL] {message}")


def main():
    print("=" * 60)
    print("clox v2 DATASET VALIDATION")
    print("=" * 60)
    print(f"CSV: {CSV_PATH}")
    print()

    if not CSV_PATH.exists():
        print(f"[FAIL] CSV not found: {CSV_PATH}")
        sys.exit(1)

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = set(reader.fieldnames or [])

    errors = []

    # ---------------------------------------------------------
    # 1. Row count
    # ---------------------------------------------------------
    expected_rows = 12 * 20 * 40

    if len(rows) == expected_rows:
        print(f"[PASS] Row count: {len(rows)}")
    else:
        fail(f"Row count: expected {expected_rows}, got {len(rows)}")
        errors.append("row count")

    # ---------------------------------------------------------
    # 2. Columns
    # ---------------------------------------------------------
    missing_columns = EXPECTED_COLUMNS - columns
    extra_columns = columns - EXPECTED_COLUMNS

    if not missing_columns:
        print("[PASS] Required columns present")
    else:
        fail(f"Missing columns: {sorted(missing_columns)}")
        errors.append("columns")

    if extra_columns:
        print(f"[INFO] Extra columns: {sorted(extra_columns)}")

    # ---------------------------------------------------------
    # 3. Benchmark set
    # ---------------------------------------------------------
    observed_benchmarks = set(row["benchmark"] for row in rows)

    expected_benchmarks = set(EXPECTED_BENCHMARKS)

    if observed_benchmarks == expected_benchmarks:
        print("[PASS] Exactly 12 expected workloads present")
    else:
        fail(
            f"Workload mismatch\n"
            f"  Missing: {sorted(expected_benchmarks - observed_benchmarks)}\n"
            f"  Unexpected: {sorted(observed_benchmarks - expected_benchmarks)}"
        )
        errors.append("benchmarks")

    # ---------------------------------------------------------
    # 4. Numeric parsing
    # ---------------------------------------------------------
    numeric_errors = []

    for i, row in enumerate(rows, start=2):
        for column in NUMERIC_COLUMNS:
            try:
                value = row[column]

                if column in {"run_order", "n", "rep", "opcodes",
                              "gc_count", "peak_heap_bytes",
                              "bytes_allocated", "bytes_freed"}:
                    int(value)
                else:
                    float(value)

            except (ValueError, TypeError, KeyError):
                numeric_errors.append((i, column, row.get(column)))

    if not numeric_errors:
        print("[PASS] Numeric columns parse correctly")
    else:
        fail(f"{len(numeric_errors)} numeric parsing errors")
        for error in numeric_errors[:5]:
            print(f"       Row {error[0]}: {error[1]} = {error[2]!r}")
        errors.append("numeric parsing")

    # ---------------------------------------------------------
    # 5. Missing critical values
    # ---------------------------------------------------------
    critical_columns = [
        "run_order",
        "benchmark",
        "n",
        "rep",
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

    missing_values = []

    for i, row in enumerate(rows, start=2):
        for column in critical_columns:
            if row.get(column, "").strip() == "":
                missing_values.append((i, column))

    if not missing_values:
        print("[PASS] No missing critical values")
    else:
        fail(f"{len(missing_values)} missing critical values")
        for item in missing_values[:10]:
            print(f"       Row {item[0]}: missing {item[1]}")
        errors.append("missing values")

    # ---------------------------------------------------------
    # 6. Rows per workload
    # ---------------------------------------------------------
    benchmark_counts = Counter(row["benchmark"] for row in rows)

    workload_errors = []

    for benchmark in EXPECTED_BENCHMARKS:
        count = benchmark_counts.get(benchmark, 0)

        if count != 800:
            workload_errors.append((benchmark, count))

    if not workload_errors:
        print("[PASS] Every workload has exactly 800 rows")
    else:
        fail("Incorrect workload row counts:")
        for benchmark, count in workload_errors:
            print(f"       {benchmark}: {count}")
        errors.append("workload counts")

    # ---------------------------------------------------------
    # 7. N values
    # ---------------------------------------------------------
    n_errors = []

    observed_n = defaultdict(set)

    for row in rows:
        benchmark = row["benchmark"]

        try:
            n = int(row["n"])
            observed_n[benchmark].add(n)
        except ValueError:
            continue

    for benchmark, expected_ns in EXPECTED_BENCHMARKS.items():
        expected_set = set(expected_ns)
        actual_set = observed_n.get(benchmark, set())

        missing = expected_set - actual_set
        unexpected = actual_set - expected_set

        if missing or unexpected:
            n_errors.append(
                (benchmark, sorted(missing), sorted(unexpected))
            )

    if not n_errors:
        print("[PASS] Exact N values match experimental design")
    else:
        fail("N-value mismatch detected:")
        for benchmark, missing, unexpected in n_errors:
            print(f"       {benchmark}")
            if missing:
                print(f"         Missing: {missing}")
            if unexpected:
                print(f"         Unexpected: {unexpected}")
        errors.append("N values")

    # ---------------------------------------------------------
    # 8. Exactly 40 repetitions per benchmark × N
    # ---------------------------------------------------------
    combination_counts = Counter(
        (row["benchmark"], int(row["n"]))
        for row in rows
    )

    repetition_errors = []

    for benchmark, expected_ns in EXPECTED_BENCHMARKS.items():
        for n in expected_ns:
            count = combination_counts.get((benchmark, n), 0)

            if count != 40:
                repetition_errors.append((benchmark, n, count))

    if not repetition_errors:
        print("[PASS] Every workload × N combination has 40 repetitions")
    else:
        fail(f"{len(repetition_errors)} combinations have incorrect repetition counts")
        for benchmark, n, count in repetition_errors[:20]:
            print(f"       {benchmark}, N={n}: {count} repetitions")
        errors.append("repetition counts")

    # ---------------------------------------------------------
    # 9. Duplicate (benchmark, N, rep)
    # ---------------------------------------------------------
    keys = [
        (row["benchmark"], int(row["n"]), int(row["rep"]))
        for row in rows
    ]

    key_counts = Counter(keys)
    duplicates = [
        (key, count)
        for key, count in key_counts.items()
        if count > 1
    ]

    if not duplicates:
        print("[PASS] No duplicate (benchmark, N, rep) combinations")
    else:
        fail(f"{len(duplicates)} duplicate combinations found")
        for key, count in duplicates[:10]:
            print(f"       {key}: {count} occurrences")
        errors.append("duplicates")

    # ---------------------------------------------------------
    # 10. Repetition range
    # ---------------------------------------------------------
    rep_errors = []

    reps_by_combination = defaultdict(set)

    for row in rows:
        key = (row["benchmark"], int(row["n"]))
        reps_by_combination[key].add(int(row["rep"]))

    for key, reps in reps_by_combination.items():
        expected_reps = set(range(1, 41))

        if reps != expected_reps:
            rep_errors.append(
                (key, sorted(expected_reps - reps), sorted(reps - expected_reps))
            )

    if not rep_errors:
        print("[PASS] Every combination contains repetitions 1–40")
    else:
        fail(f"{len(rep_errors)} combinations have incorrect repetition numbering")
        for key, missing, unexpected in rep_errors[:10]:
            print(f"       {key}")
            if missing:
                print(f"         Missing reps: {missing}")
            if unexpected:
                print(f"         Unexpected reps: {unexpected}")
        errors.append("rep numbering")

    # ---------------------------------------------------------
    # 11. run_order
    # ---------------------------------------------------------
    run_orders = []

    for row in rows:
        try:
            run_orders.append(int(row["run_order"]))
        except ValueError:
            pass

    expected_orders = set(range(1, expected_rows + 1))
    actual_orders = set(run_orders)

    if actual_orders == expected_orders and len(run_orders) == len(set(run_orders)):
        print("[PASS] run_order covers exactly 1–9600 with no duplicates")
    else:
        fail("run_order is not a unique contiguous 1–9600 sequence")
        errors.append("run_order")

    # ---------------------------------------------------------
    # 12. Obvious failed/invalid executions
    # ---------------------------------------------------------
    invalid_rows = []

    for i, row in enumerate(rows, start=2):
        try:
            wall = float(row["wall_ms"])
            compile_ms = float(row["compile_ms"])
            exec_ms = float(row["exec_ms"])
            opcodes = int(row["opcodes"])
            gc_count = int(row["gc_count"])
            gc_ms = float(row["gc_ms"])
            heap = int(row["peak_heap_bytes"])
            allocated = int(row["bytes_allocated"])
            freed = int(row["bytes_freed"])

            if (
                wall < 0
                or compile_ms < 0
                or exec_ms < 0
                or opcodes < 0
                or gc_count < 0
                or gc_ms < 0
                or heap < 0
                or allocated < 0
                or freed < 0
            ):
                invalid_rows.append(i)

        except (ValueError, TypeError):
            invalid_rows.append(i)

    if not invalid_rows:
        print("[PASS] No negative/obviously invalid profiler metrics")
    else:
        fail(f"{len(invalid_rows)} rows contain invalid metric values")
        print(f"       Rows: {invalid_rows[:20]}")
        errors.append("invalid metrics")

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------
    print()
    print("=" * 60)

    if not errors:
        print("VALIDATION PASSED")
        print("Dataset is structurally consistent with the 9,600-run design.")
        print("=" * 60)
        sys.exit(0)

    print("VALIDATION FAILED")
    print()
    print("Problems detected:")
    for error in errors:
        print(f"  - {error}")

    print("=" * 60)
    sys.exit(1)


if __name__ == "__main__":
    main()