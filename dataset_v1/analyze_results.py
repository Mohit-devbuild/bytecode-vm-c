import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# clox Benchmark Analysis - Dataset v1
# ============================================================

RESULTS_DIR = Path("results")

DATASET_FILE = RESULTS_DIR / "dataset_v1.csv"
OPCODE_FILE = RESULTS_DIR / "instruction_frequency_v1.csv"

SUMMARY_FILE = RESULTS_DIR / "summary_v1.csv"
OPCODE_SUMMARY_FILE = RESULTS_DIR / "opcode_summary_v1.csv"
SCALING_FILE = RESULTS_DIR / "scaling_v1.csv"


# ============================================================
# Validation
# ============================================================

if not DATASET_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_FILE}"
    )

if not OPCODE_FILE.exists():
    raise FileNotFoundError(
        f"Instruction frequency dataset not found: {OPCODE_FILE}"
    )


# ============================================================
# Load datasets
# ============================================================

df = pd.read_csv(DATASET_FILE)
opcode_df = pd.read_csv(OPCODE_FILE)


print("============================================")
print("CLOX BENCHMARK ANALYSIS")
print("============================================")
print()
print(f"Raw observations: {len(df)}")
print(f"Opcode observations: {len(opcode_df)}")
print()


# ============================================================
# Basic validation
# ============================================================

expected_rows = 160

if len(df) != expected_rows:
    raise ValueError(
        f"Expected {expected_rows} observations, "
        f"found {len(df)}."
    )

group_counts = (
    df
    .groupby(["benchmark", "input_size"])
    .size()
)

if not (group_counts == 5).all():
    raise ValueError(
        "Not every benchmark/input-size combination "
        "contains exactly 5 runs."
    )

print("Run structure: PASSED")
print("5 repetitions per configuration: PASSED")
print()


# ============================================================
# Descriptive statistics
# ============================================================

group_columns = [
    "benchmark",
    "input_size",
]


# Metrics for mean and standard deviation

metrics = [
    "compilation_time_ms",
    "execution_time_ms",
    "opcode_executions",
    "gc_count",
    "gc_time_ms",
    "peak_heap_usage_bytes",
    "total_bytes_allocated",
    "total_bytes_freed",
]


summary = (
    df
    .groupby(group_columns)[metrics]
    .agg(["mean", "std", "min", "max"])
    .reset_index()
)


# ============================================================
# Flatten column names
# ============================================================

new_columns = []

for column in summary.columns:

    if isinstance(column, tuple):

        if column[1] == "":
            new_columns.append(column[0])
        else:
            new_columns.append(
                f"{column[0]}_{column[1]}"
            )

    else:
        new_columns.append(column)


summary.columns = new_columns


# ============================================================
# Coefficient of variation
# ============================================================

summary["execution_time_cv_percent"] = (
    summary["execution_time_ms_std"]
    / summary["execution_time_ms_mean"]
    * 100
)

summary["compilation_time_cv_percent"] = (
    summary["compilation_time_ms_std"]
    / summary["compilation_time_ms_mean"]
    * 100
)

summary["opcode_executions_cv_percent"] = (
    summary["opcode_executions_std"]
    / summary["opcode_executions_mean"]
    * 100
)


# ============================================================
# Save descriptive summary
# ============================================================

summary.to_csv(
    SUMMARY_FILE,
    index=False
)


# ============================================================
# Opcode summary
# ============================================================

opcode_summary = (
    opcode_df
    .groupby(
        [
            "benchmark",
            "input_size",
            "opcode",
        ]
    )["count"]
    .agg(
        [
            "mean",
            "std",
            "min",
            "max",
        ]
    )
    .reset_index()
)


opcode_summary.columns = [
    "benchmark",
    "input_size",
    "opcode",
    "mean_count",
    "std_count",
    "min_count",
    "max_count",
]


# ============================================================
# Opcode percentage of total execution
# ============================================================

opcode_summary["percentage_of_opcodes"] = 0.0


for index, row in opcode_summary.iterrows():

    benchmark = row["benchmark"]
    input_size = row["input_size"]

    total = summary[
        (summary["benchmark"] == benchmark)
        &
        (summary["input_size"] == input_size)
    ]["opcode_executions_mean"]

    if len(total) == 1 and total.iloc[0] > 0:

        opcode_summary.loc[
            index,
            "percentage_of_opcodes"
        ] = (
            row["mean_count"]
            / total.iloc[0]
            * 100
        )


opcode_summary.to_csv(
    OPCODE_SUMMARY_FILE,
    index=False
)


# ============================================================
# Scaling analysis
# ============================================================

scaling_rows = []


for benchmark, group in (
    summary.groupby("benchmark")
):

    group = group.sort_values(
        "input_size"
    )

    x = group["input_size"].to_numpy(
        dtype=float
    )

    y_time = group[
        "execution_time_ms_mean"
    ].to_numpy(
        dtype=float
    )

    y_opcodes = group[
        "opcode_executions_mean"
    ].to_numpy(
        dtype=float
    )

    y_heap = group[
        "peak_heap_usage_bytes_mean"
    ].to_numpy(
        dtype=float
    )

    y_alloc = group[
        "total_bytes_allocated_mean"
    ].to_numpy(
        dtype=float
    )

    # --------------------------------------------------------
    # Linear regression
    # --------------------------------------------------------

    if len(x) >= 2:

        time_slope, time_intercept = np.polyfit(
            x,
            y_time,
            1
        )

        opcode_slope, opcode_intercept = np.polyfit(
            x,
            y_opcodes,
            1
        )

        heap_slope, heap_intercept = np.polyfit(
            x,
            y_heap,
            1
        )

        alloc_slope, alloc_intercept = np.polyfit(
            x,
            y_alloc,
            1
        )

        time_prediction = (
            time_slope * x
            + time_intercept
        )

        opcode_prediction = (
            opcode_slope * x
            + opcode_intercept
        )

        heap_prediction = (
            heap_slope * x
            + heap_intercept
        )

        alloc_prediction = (
            alloc_slope * x
            + alloc_intercept
        )

        def r_squared(actual, predicted):

            ss_res = np.sum(
                (actual - predicted) ** 2
            )

            ss_tot = np.sum(
                (actual - np.mean(actual)) ** 2
            )

            if ss_tot == 0:
                return 1.0

            return 1 - (
                ss_res / ss_tot
            )

        time_r2 = r_squared(
            y_time,
            time_prediction
        )

        opcode_r2 = r_squared(
            y_opcodes,
            opcode_prediction
        )

        heap_r2 = r_squared(
            y_heap,
            heap_prediction
        )

        alloc_r2 = r_squared(
            y_alloc,
            alloc_prediction
        )

    else:

        time_slope = np.nan
        time_intercept = np.nan
        opcode_slope = np.nan
        opcode_intercept = np.nan
        heap_slope = np.nan
        heap_intercept = np.nan
        alloc_slope = np.nan
        alloc_intercept = np.nan

        time_r2 = np.nan
        opcode_r2 = np.nan
        heap_r2 = np.nan
        alloc_r2 = np.nan


    # --------------------------------------------------------
    # Add one row per input size
    # --------------------------------------------------------

    for _, row in group.iterrows():

        scaling_rows.append({

            "benchmark":
                benchmark,

            "input_size":
                row["input_size"],

            "mean_execution_time_ms":
                row["execution_time_ms_mean"],

            "mean_opcode_executions":
                row["opcode_executions_mean"],

            "mean_peak_heap_bytes":
                row["peak_heap_usage_bytes_mean"],

            "mean_bytes_allocated":
                row["total_bytes_allocated_mean"],

            "linear_time_slope":
                time_slope,

            "linear_time_r2":
                time_r2,

            "linear_opcode_slope":
                opcode_slope,

            "linear_opcode_r2":
                opcode_r2,

            "linear_heap_slope":
                heap_slope,

            "linear_heap_r2":
                heap_r2,

            "linear_allocation_slope":
                alloc_slope,

            "linear_allocation_r2":
                alloc_r2,
        })


scaling = pd.DataFrame(
    scaling_rows
)


scaling.to_csv(
    SCALING_FILE,
    index=False
)


# ============================================================
# Print useful overview
# ============================================================

print("============================================")
print("OUTPUT FILES")
print("============================================")

print(
    f"Summary:              {SUMMARY_FILE}"
)

print(
    f"Opcode summary:       {OPCODE_SUMMARY_FILE}"
)

print(
    f"Scaling analysis:     {SCALING_FILE}"
)

print()

print("============================================")
print("EXECUTION TIME SUMMARY")
print("============================================")

display_columns = [
    "benchmark",
    "input_size",
    "execution_time_ms_mean",
    "execution_time_ms_std",
    "execution_time_cv_percent",
]

print(
    summary[
        display_columns
    ].to_string(
        index=False
    )
)

print()

print("============================================")
print("ANALYSIS COMPLETE")
print("============================================")