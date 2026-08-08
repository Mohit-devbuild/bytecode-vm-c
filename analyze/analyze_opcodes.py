from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT / "results" / "opcode_summary_v1.csv"
OUTPUT_DIR = ROOT / "results" / "opcode_analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print()
    print("============================================")
    print("CLOX OPCODE ANALYSIS")
    print("============================================")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Could not find: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    required = [
        "benchmark",
        "input_size",
        "opcode",
        "mean_count",
        "std_count",
        "min_count",
        "max_count",
        "percentage_of_opcodes",
    ]

    missing = sorted(set(required) - set(df.columns))

    if missing:
        raise ValueError(
            f"Missing columns: {missing}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    print(f"Input rows: {len(df)}")
    print(f"Benchmarks: {df['benchmark'].nunique()}")
    print(f"Configurations: {df[['benchmark', 'input_size']].drop_duplicates().shape[0]}")
    print(f"Unique opcodes: {df['opcode'].nunique()}")

    # --------------------------------------------------------
    # TOP OPCODES PER CONFIGURATION
    # --------------------------------------------------------

    top_rows = []

    for (benchmark, input_size), group in df.groupby(
        ["benchmark", "input_size"]
    ):
        group = group.sort_values(
            "mean_count",
            ascending=False
        ).copy()

        total = group["mean_count"].sum()

        if total > 0:
            group["percentage_of_total"] = (
                group["mean_count"] / total * 100
            )
        else:
            group["percentage_of_total"] = 0.0

        group["rank"] = range(1, len(group) + 1)

        for _, row in group.head(10).iterrows():
            top_rows.append({
                "benchmark": benchmark,
                "input_size": input_size,
                "rank": int(row["rank"]),
                "opcode": row["opcode"],
                "mean_count": row["mean_count"],
                "percentage_of_total": row["percentage_of_total"],
            })

    top_df = pd.DataFrame(top_rows)

    top_file = OUTPUT_DIR / "top_opcodes_v1.csv"
    top_df.to_csv(top_file, index=False)

    print(f"Created: {top_file.relative_to(ROOT)}")

    # --------------------------------------------------------
    # BENCHMARK OPCODE PROFILE
    # --------------------------------------------------------

    profile = (
        df.groupby(
            ["benchmark", "opcode"],
            as_index=False
        )["mean_count"]
        .mean()
    )

    profile["percentage_of_benchmark"] = (
        profile.groupby("benchmark")["mean_count"]
        .transform(
            lambda x: x / x.sum() * 100
            if x.sum() > 0
            else 0.0
        )
    )

    profile = profile.sort_values(
        ["benchmark", "mean_count"],
        ascending=[True, False]
    )

    profile_file = OUTPUT_DIR / "benchmark_opcode_profile_v1.csv"
    profile.to_csv(profile_file, index=False)

    print(
        f"Created: {profile_file.relative_to(ROOT)}"
    )

    # --------------------------------------------------------
    # GLOBAL OPCODE TOTALS
    # --------------------------------------------------------

    totals = (
        df.groupby(
            "opcode",
            as_index=False
        )["mean_count"]
        .sum()
    )

    grand_total = totals["mean_count"].sum()

    if grand_total > 0:
        totals["percentage_of_all_opcodes"] = (
            totals["mean_count"] / grand_total * 100
        )
    else:
        totals["percentage_of_all_opcodes"] = 0.0

    totals = totals.sort_values(
        "mean_count",
        ascending=False
    )

    totals_file = OUTPUT_DIR / "opcode_totals_v1.csv"
    totals.to_csv(totals_file, index=False)

    print(
        f"Created: {totals_file.relative_to(ROOT)}"
    )

    # --------------------------------------------------------
    # OPCODE RANKING
    # --------------------------------------------------------

    ranking = totals.copy()

    ranking.insert(
        0,
        "rank",
        range(1, len(ranking) + 1)
    )

    ranking_file = OUTPUT_DIR / "opcode_ranking_v1.csv"
    ranking.to_csv(ranking_file, index=False)

    print(
        f"Created: {ranking_file.relative_to(ROOT)}"
    )

    # --------------------------------------------------------
    # TOP 20 OPCODES
    # --------------------------------------------------------

    print()
    print("============================================")
    print("TOP 20 OPCODES")
    print("============================================")

    print(
        ranking.head(20).to_string(index=False)
    )

    # --------------------------------------------------------
    # DOMINANT OPCODES BY BENCHMARK
    # --------------------------------------------------------

    print()
    print("============================================")
    print("DOMINANT OPCODES BY BENCHMARK")
    print("============================================")

    for benchmark in sorted(df["benchmark"].unique()):
        print()
        print(benchmark)

        benchmark_profile = profile[
            profile["benchmark"] == benchmark
        ].head(5)

        print(
            benchmark_profile[
                [
                    "opcode",
                    "mean_count",
                    "percentage_of_benchmark",
                ]
            ].to_string(index=False)
        )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    print()
    print("============================================")
    print("VALIDATION")
    print("============================================")

    if df["benchmark"].nunique() == 8:
        print("Benchmark count: PASSED")
    else:
        print(
            "Benchmark count: FAILED "
            f"(found {df['benchmark'].nunique()})"
        )

    if df["mean_count"].ge(0).all():
        print("Opcode counts: PASSED")
    else:
        print("Opcode counts: FAILED")

    if df["percentage_of_opcodes"].ge(0).all():
        print("Opcode percentages: PASSED")
    else:
        print("Opcode percentages: FAILED")

    print()
    print("============================================")
    print("OPCODE ANALYSIS COMPLETE")
    print("============================================")


if __name__ == "__main__":
    main()