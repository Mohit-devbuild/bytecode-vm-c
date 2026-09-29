import csv
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_CSV = BASE_DIR / "results" / "dataset_v2.csv"
OUTPUT_CSV = BASE_DIR / "results" / "opcode_long.csv"
SUMMARY_CSV = BASE_DIR / "results" / "opcode_summary.csv"


def parse_opcode_counts(text):
    """
    Parse:
        OP_CONSTANT=10;OP_ADD=5;OP_RETURN=1

    Also tolerate whitespace and empty entries.
    """
    counts = {}

    if not text:
        return counts

    text = text.strip()

    for item in text.split(";"):
        item = item.strip()

        if not item or "=" not in item:
            continue

        opcode, value = item.rsplit("=", 1)

        opcode = opcode.strip()

        try:
            count = int(value.strip())
        except ValueError:
            continue

        counts[opcode] = count

    return counts


def main():
    print("=" * 60)
    print("clox v2 OPCODE ANALYSIS")
    print("=" * 60)

    if not INPUT_CSV.exists():
        raise FileNotFoundError(INPUT_CSV)

    with INPUT_CSV.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header.")

        required = {
            "benchmark",
            "n",
            "rep",
            "opcode_counts",
        }

        missing = required - set(reader.fieldnames)

        if missing:
            raise ValueError(
                f"Missing columns: {sorted(missing)}"
            )

        rows = list(reader)

    print(f"Loaded raw rows: {len(rows)}")

    if len(rows) != 9600:
        raise ValueError(
            f"Expected 9600 rows, found {len(rows)}"
        )

    # ---------------------------------------------------------
    # Parse opcode data
    # ---------------------------------------------------------

    long_rows = []

    workload_rows = defaultdict(int)
    workload_opcode_rows = defaultdict(int)

    for row in rows:
        benchmark = row["benchmark"].strip()
        n = int(row["n"])
        rep = int(row["rep"])

        workload_rows[benchmark] += 1

        opcode_counts = parse_opcode_counts(
            row["opcode_counts"]
        )

        workload_opcode_rows[benchmark] += len(opcode_counts)

        for opcode, count in opcode_counts.items():
            long_rows.append({
                "benchmark": benchmark,
                "n": n,
                "rep": rep,
                "opcode": opcode,
                "count": count,
            })

    # ---------------------------------------------------------
    # Verify all 12 workloads have opcode data
    # ---------------------------------------------------------

    print()
    print("Opcode records by workload:")

    for benchmark in sorted(workload_rows):
        print(
            f"  {benchmark:20s}"
            f" rows={workload_rows[benchmark]:4d}"
            f" opcode_records={workload_opcode_rows[benchmark]:6d}"
        )

    empty_workloads = [
        benchmark
        for benchmark in workload_rows
        if workload_opcode_rows[benchmark] == 0
    ]

    if empty_workloads:
        raise ValueError(
            "No opcode records found for: "
            + ", ".join(empty_workloads)
        )

    # ---------------------------------------------------------
    # Write normalized long-form dataset
    # ---------------------------------------------------------

    with OUTPUT_CSV.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        fieldnames = [
            "benchmark",
            "n",
            "rep",
            "opcode",
            "count",
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(long_rows)

    # ---------------------------------------------------------
    # Aggregate opcode totals
    # ---------------------------------------------------------

    totals = defaultdict(int)

    for row in long_rows:
        key = (
            row["benchmark"],
            row["opcode"],
        )

        totals[key] += row["count"]

    workload_totals = defaultdict(int)

    for (benchmark, opcode), count in totals.items():
        workload_totals[benchmark] += count

    summary_rows = []

    for (benchmark, opcode), count in totals.items():

        total = workload_totals[benchmark]

        percentage = (
            100.0 * count / total
            if total > 0
            else 0.0
        )

        summary_rows.append({
            "benchmark": benchmark,
            "opcode": opcode,
            "total_count": count,
            "percentage": percentage,
        })

    # ---------------------------------------------------------
    # Write summary
    # ---------------------------------------------------------

    with SUMMARY_CSV.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as f:

        fieldnames = [
            "benchmark",
            "opcode",
            "total_count",
            "percentage",
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in sorted(
            summary_rows,
            key=lambda x: (
                x["benchmark"],
                -x["total_count"]
            )
        ):
            writer.writerow({
                "benchmark": row["benchmark"],
                "opcode": row["opcode"],
                "total_count": row["total_count"],
                "percentage": (
                    f"{row['percentage']:.6f}"
                ),
            })

    # ---------------------------------------------------------
    # Dominant opcodes
    # ---------------------------------------------------------

    print()
    print("-" * 60)
    print("DOMINANT OPCODES BY WORKLOAD")
    print("-" * 60)

    for benchmark in sorted(workload_totals):

        entries = [
            row
            for row in summary_rows
            if row["benchmark"] == benchmark
        ]

        entries.sort(
            key=lambda x: x["total_count"],
            reverse=True
        )

        print()
        print(benchmark)

        for row in entries[:10]:
            print(
                f"  {row['opcode']:22s}"
                f" {row['total_count']:12,d}"
                f" ({row['percentage']:7.2f}%)"
            )

    # ---------------------------------------------------------
    # Final validation
    # ---------------------------------------------------------

    unique_opcodes = {
        row["opcode"]
        for row in long_rows
    }

    print()
    print("-" * 60)
    print(f"[PASS] Raw rows: {len(rows)}")
    print(f"[PASS] Opcode records: {len(long_rows)}")
    print(f"[PASS] Unique opcodes: {len(unique_opcodes)}")
    print(f"[PASS] Workloads: {len(workload_totals)}")

    if len(workload_totals) != 12:
        raise ValueError(
            f"Expected 12 workloads, found "
            f"{len(workload_totals)}"
        )

    print()
    print(f"Long-form : {OUTPUT_CSV}")
    print(f"Summary   : {SUMMARY_CSV}")

    print()
    print("=" * 60)
    print("OPCODE ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()