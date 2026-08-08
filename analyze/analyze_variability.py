import pandas as pd
from pathlib import Path


# ============================================================
# clox Benchmark Variability Analysis
# Dataset v1
# ============================================================

DATASET_FILE = Path("results/dataset_v1.csv")
OUTPUT_FILE = Path("results/variability_v1.csv")


# ============================================================
# Load dataset
# ============================================================

if not DATASET_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_FILE}"
    )

df = pd.read_csv(DATASET_FILE)


# ============================================================
# Validate
# ============================================================

if len(df) != 160:
    raise ValueError(
        f"Expected 160 observations, found {len(df)}."
    )


grouped = df.groupby(
    ["benchmark", "input_size"]
)


counts = grouped.size()

if not (counts == 5).all():
    raise ValueError(
        "Every benchmark/input-size configuration "
        "must contain exactly 5 repetitions."
    )


# ============================================================
# Calculate variability statistics
# ============================================================

result = (
    grouped["execution_time_ms"]
    .agg(
        mean_ms="mean",
        std_ms="std",
        min_ms="min",
        max_ms="max",
        median_ms="median"
    )
    .reset_index()
)


# ============================================================
# Derived metrics
# ============================================================

result["cv_percent"] = (
    result["std_ms"]
    / result["mean_ms"]
    * 100
)


result["range_ms"] = (
    result["max_ms"]
    - result["min_ms"]
)


result["range_percent"] = (
    result["range_ms"]
    / result["mean_ms"]
    * 100
)


# ============================================================
# Stability classification
#
# These are descriptive thresholds, not scientific laws.
# ============================================================

def classify_cv(cv):

    if cv < 5:
        return "Very stable"

    if cv < 10:
        return "Stable"

    if cv < 20:
        return "Moderate variability"

    if cv < 50:
        return "High variability"

    return "Very high variability"


result["stability"] = (
    result["cv_percent"]
    .apply(classify_cv)
)


# ============================================================
# Save
# ============================================================

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# Print complete configuration-level results
# ============================================================

print()
print("============================================")
print("CLOX BENCHMARK VARIABILITY ANALYSIS")
print("============================================")
print()

print(
    result[
        [
            "benchmark",
            "input_size",
            "mean_ms",
            "std_ms",
            "cv_percent",
            "min_ms",
            "max_ms",
            "range_percent",
            "stability"
        ]
    ].to_string(index=False)
)


# ============================================================
# Overall benchmark-level variability
# ============================================================

benchmark_summary = (
    result
    .groupby("benchmark")
    .agg(
        configurations=("input_size", "count"),
        mean_cv_percent=("cv_percent", "mean"),
        median_cv_percent=("cv_percent", "median"),
        max_cv_percent=("cv_percent", "max")
    )
    .reset_index()
)


print()
print("============================================")
print("BENCHMARK-LEVEL VARIABILITY")
print("============================================")
print()

print(
    benchmark_summary.to_string(
        index=False
    )
)


# ============================================================
# Identify noisy configurations
# ============================================================

noisy = result[
    result["cv_percent"] >= 20
].sort_values(
    "cv_percent",
    ascending=False
)


print()
print("============================================")
print("CONFIGURATIONS WITH CV >= 20%")
print("============================================")
print()

if len(noisy) == 0:

    print("None.")

else:

    print(
        noisy[
            [
                "benchmark",
                "input_size",
                "mean_ms",
                "std_ms",
                "cv_percent",
                "stability"
            ]
        ].to_string(index=False)
    )


# ============================================================
# Identify stable configurations
# ============================================================

stable = result[
    result["cv_percent"] < 10
]


print()
print("============================================")
print("CONFIGURATIONS WITH CV < 10%")
print("============================================")
print()

print(
    f"Stable configurations: "
    f"{len(stable)} / {len(result)}"
)


print()
print("============================================")
print("SUMMARY")
print("============================================")
print()

print(
    f"Configurations analysed: {len(result)}"
)

print(
    f"Stable (<10% CV): {len(stable)}"
)

print(
    f"CV >= 20%: {len(noisy)}"
)

print()
print(f"Created: {OUTPUT_FILE}")
print("============================================")