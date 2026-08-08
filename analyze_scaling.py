import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# clox Scaling Analysis - Dataset v1
#
# Model:
#
#     y = a * N^k
#
# Taking logarithms:
#
#     log(y) = log(a) + k * log(N)
#
# Therefore:
#
#     k = scaling exponent
#
# k ≈ 1  -> linear
# k ≈ 2  -> quadratic
# k < 1  -> sublinear
# k > 1  -> superlinear
#
# For recursion, this power-law model is expected to fit poorly.
# We therefore also calculate exponential scaling:
#
#     y = a * b^N
#
# Taking logarithms:
#
#     log(y) = log(a) + N * log(b)
# ============================================================


RESULTS_DIR = Path("results")

DATASET_FILE = RESULTS_DIR / "dataset_v1.csv"

SCALING_FILE = RESULTS_DIR / "scaling_exponents_v1.csv"


# ============================================================
# Load dataset
# ============================================================

if not DATASET_FILE.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_FILE}"
    )

df = pd.read_csv(DATASET_FILE)


# ============================================================
# Validate dataset
# ============================================================

if len(df) != 160:
    raise ValueError(
        f"Expected 160 observations, found {len(df)}."
    )


group_counts = (
    df
    .groupby(["benchmark", "input_size"])
    .size()
)

if not (group_counts == 5).all():
    raise ValueError(
        "Every benchmark/input-size combination "
        "must contain exactly 5 runs."
    )


# ============================================================
# Aggregate repetitions
# ============================================================

summary = (
    df
    .groupby(
        ["benchmark", "input_size"]
    )
    .agg(
        execution_time_ms=(
            "execution_time_ms",
            "mean"
        ),

        opcode_executions=(
            "opcode_executions",
            "mean"
        ),

        peak_heap_usage_bytes=(
            "peak_heap_usage_bytes",
            "mean"
        ),

        total_bytes_allocated=(
            "total_bytes_allocated",
            "mean"
        ),

        gc_count=(
            "gc_count",
            "mean"
        ),

        gc_time_ms=(
            "gc_time_ms",
            "mean"
        ),
    )
    .reset_index()
)


# ============================================================
# Regression helper
# ============================================================

def calculate_r_squared(actual, predicted):

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


# ============================================================
# Power-law scaling
#
# y = a * N^k
#
# log(y) = log(a) + k*log(N)
# ============================================================

def power_law_fit(x, y):

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    valid = (
        (x > 0)
        &
        (y > 0)
        &
        np.isfinite(x)
        &
        np.isfinite(y)
    )

    x = x[valid]
    y = y[valid]

    if len(x) < 2:
        return np.nan, np.nan, np.nan

    log_x = np.log(x)
    log_y = np.log(y)

    slope, intercept = np.polyfit(
        log_x,
        log_y,
        1
    )

    predicted_log_y = (
        slope * log_x
        + intercept
    )

    r_squared = calculate_r_squared(
        log_y,
        predicted_log_y
    )

    exponent = slope

    coefficient = np.exp(
        intercept
    )

    return (
        exponent,
        coefficient,
        r_squared
    )


# ============================================================
# Exponential scaling
#
# y = a * b^N
#
# log(y) = log(a) + N*log(b)
# ============================================================

def exponential_fit(x, y):

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    valid = (
        (x > 0)
        &
        (y > 0)
        &
        np.isfinite(x)
        &
        np.isfinite(y)
    )

    x = x[valid]
    y = y[valid]

    if len(x) < 2:
        return np.nan, np.nan, np.nan

    log_y = np.log(y)

    slope, intercept = np.polyfit(
        x,
        log_y,
        1
    )

    predicted_log_y = (
        slope * x
        + intercept
    )

    r_squared = calculate_r_squared(
        log_y,
        predicted_log_y
    )

    coefficient = np.exp(
        intercept
    )

    base = np.exp(
        slope
    )

    return (
        coefficient,
        base,
        r_squared
    )


# ============================================================
# Calculate scaling for each workload
# ============================================================

results = []


for benchmark, group in (
    summary.groupby("benchmark")
):

    group = group.sort_values(
        "input_size"
    )

    x = group[
        "input_size"
    ].to_numpy(
        dtype=float
    )

    execution_time = group[
        "execution_time_ms"
    ].to_numpy(
        dtype=float
    )

    opcode_count = group[
        "opcode_executions"
    ].to_numpy(
        dtype=float
    )

    heap_usage = group[
        "peak_heap_usage_bytes"
    ].to_numpy(
        dtype=float
    )

    allocation = group[
        "total_bytes_allocated"
    ].to_numpy(
        dtype=float
    )

    gc_count = group[
        "gc_count"
    ].to_numpy(
        dtype=float
    )


    # --------------------------------------------------------
    # Execution time power-law fit
    # --------------------------------------------------------

    time_k, time_a, time_r2 = power_law_fit(
        x,
        execution_time
    )


    # --------------------------------------------------------
    # Opcode power-law fit
    # --------------------------------------------------------

    opcode_k, opcode_a, opcode_r2 = power_law_fit(
        x,
        opcode_count
    )


    # --------------------------------------------------------
    # Heap power-law fit
    # --------------------------------------------------------

    heap_k, heap_a, heap_r2 = power_law_fit(
        x,
        heap_usage
    )


    # --------------------------------------------------------
    # Allocation power-law fit
    # --------------------------------------------------------

    allocation_k, allocation_a, allocation_r2 = power_law_fit(
        x,
        allocation
    )


    # --------------------------------------------------------
    # GC count power-law fit
    #
    # Only meaningful if there are non-zero GC observations.
    # --------------------------------------------------------

    if np.any(gc_count > 0):

        gc_k, gc_a, gc_r2 = power_law_fit(
            x,
            gc_count
        )

    else:

        gc_k = np.nan
        gc_a = np.nan
        gc_r2 = np.nan


    # --------------------------------------------------------
    # Execution-time exponential fit
    # --------------------------------------------------------

    exp_a, exp_b, exp_r2 = exponential_fit(
        x,
        execution_time
    )


    # --------------------------------------------------------
    # Store result
    # --------------------------------------------------------

    results.append({

        "benchmark":
            benchmark,

        "num_input_sizes":
            len(x),

        # Execution time
        "time_power_exponent_k":
            time_k,

        "time_power_coefficient_a":
            time_a,

        "time_power_r2":
            time_r2,

        # Opcode count
        "opcode_power_exponent_k":
            opcode_k,

        "opcode_power_coefficient_a":
            opcode_a,

        "opcode_power_r2":
            opcode_r2,

        # Heap
        "heap_power_exponent_k":
            heap_k,

        "heap_power_coefficient_a":
            heap_a,

        "heap_power_r2":
            heap_r2,

        # Allocation
        "allocation_power_exponent_k":
            allocation_k,

        "allocation_power_coefficient_a":
            allocation_a,

        "allocation_power_r2":
            allocation_r2,

        # GC
        "gc_power_exponent_k":
            gc_k,

        "gc_power_coefficient_a":
            gc_a,

        "gc_power_r2":
            gc_r2,

        # Exponential execution-time model
        "time_exponential_coefficient_a":
            exp_a,

        "time_exponential_base_b":
            exp_b,

        "time_exponential_r2":
            exp_r2,
    })


# ============================================================
# Create dataframe
# ============================================================

scaling = pd.DataFrame(
    results
)


# ============================================================
# Save results
# ============================================================

scaling.to_csv(
    SCALING_FILE,
    index=False
)


# ============================================================
# Print results
# ============================================================

print()
print("============================================")
print("CLOX SCALING ANALYSIS")
print("============================================")
print()

print(
    scaling[
        [
            "benchmark",
            "time_power_exponent_k",
            "time_power_r2",
            "opcode_power_exponent_k",
            "opcode_power_r2",
            "time_exponential_base_b",
            "time_exponential_r2",
        ]
    ].to_string(
        index=False
    )
)

print()
print("============================================")
print("INTERPRETATION GUIDE")
print("============================================")
print()
print("Power-law exponent k:")
print("  k ≈ 1  -> linear scaling")
print("  k ≈ 2  -> quadratic scaling")
print("  k < 1  -> sublinear scaling")
print("  k > 1  -> superlinear scaling")
print()
print("R² closer to 1 means a better fit.")
print()
print("For recursion, compare the power-law")
print("fit against the exponential fit.")
print()
print(f"Created: {SCALING_FILE}")
print("============================================")