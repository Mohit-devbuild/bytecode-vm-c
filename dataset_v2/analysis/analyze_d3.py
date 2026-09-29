import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


BASE = os.path.join("dataset_v2", "results")
RAW_FILE = os.path.join(BASE, "dataset_v2.csv")
AGG_FILE = os.path.join(BASE, "aggregated.csv")
FIG_DIR = os.path.join(BASE, "figures")

os.makedirs(FIG_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(RAW_FILE)
agg = pd.read_csv(AGG_FILE)

numeric_cols = [
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

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

print("=" * 70)
print("REMAINING DATASET ANALYSIS")
print("=" * 70)
print(f"Rows loaded: {len(df)}")
print(f"Workloads: {df['benchmark'].nunique()}")
print()


# ============================================================
# 5. OPCODE EXECUTION EFFICIENCY
# ============================================================

print("[1/5] Calculating opcode execution efficiency...")

df["ms_per_million_opcodes"] = (
    df["exec_ms"] * 1_000_000 / df["opcodes"]
)

efficiency = (
    df.groupby(["benchmark", "n"])["ms_per_million_opcodes"]
    .agg(
        mean="mean",
        median="median",
        std="std",
        min="min",
        max="max",
    )
    .reset_index()
)

efficiency["cv"] = efficiency["std"] / efficiency["mean"]

efficiency.to_csv(
    os.path.join(BASE, "opcode_efficiency.csv"),
    index=False
)

eff_summary = []

for benchmark, group in efficiency.groupby("benchmark"):
    group = group.sort_values("n")

    first = group.iloc[0]
    last = group.iloc[-1]

    eff_summary.append({
        "benchmark": benchmark,
        "initial_n": first["n"],
        "final_n": last["n"],
        "initial_ms_per_million": first["mean"],
        "final_ms_per_million": last["mean"],
        "growth_factor": (
            last["mean"] / first["mean"]
            if first["mean"] != 0 else np.nan
        ),
        "percent_change": (
            (last["mean"] - first["mean"])
            / first["mean"] * 100
            if first["mean"] != 0 else np.nan
        ),
    })

pd.DataFrame(eff_summary).to_csv(
    os.path.join(BASE, "opcode_efficiency_summary.csv"),
    index=False
)

print(f"  Saved: {BASE}/opcode_efficiency.csv")
print(f"  Saved: {BASE}/opcode_efficiency_summary.csv")


# ============================================================
# 6. GC BEHAVIOR
# ============================================================

print("[2/5] Analyzing garbage collection behavior...")

gc = (
    df.groupby(["benchmark", "n"])
    .agg(
        mean_gc_count=("gc_count", "mean"),
        median_gc_count=("gc_count", "median"),
        std_gc_count=("gc_count", "std"),

        mean_gc_ms=("gc_ms", "mean"),
        median_gc_ms=("gc_ms", "median"),
        std_gc_ms=("gc_ms", "std"),

        mean_peak_heap=("peak_heap_bytes", "mean"),
        median_peak_heap=("peak_heap_bytes", "median"),

        mean_allocated=("bytes_allocated", "mean"),
        mean_freed=("bytes_freed", "mean"),
    )
    .reset_index()
)

mean_exec = (
    df.groupby(["benchmark", "n"])["exec_ms"]
    .mean()
    .reset_index(name="mean_exec_ms")
)

gc = gc.merge(
    mean_exec,
    on=["benchmark", "n"]
)

gc["gc_time_fraction"] = (
    gc["mean_gc_ms"] / gc["mean_exec_ms"]
)

gc.to_csv(
    os.path.join(BASE, "gc_analysis.csv"),
    index=False
)

print(f"  Saved: {BASE}/gc_analysis.csv")


# ============================================================
# 7. VARIABILITY / STABILITY
# ============================================================

print("[3/5] Analyzing run-to-run variability...")

metrics = [
    "wall_ms",
    "exec_ms",
    "opcodes",
    "gc_count",
    "gc_ms",
    "peak_heap_bytes",
    "bytes_allocated",
    "bytes_freed",
]

variability_parts = []

for metric in metrics:

    temp = (
        df.groupby(["benchmark", "n"])[metric]
        .agg(
            mean="mean",
            median="median",
            std="std",
            min="min",
            max="max",
        )
        .reset_index()
    )

    temp["cv"] = temp["std"] / temp["mean"]
    temp["metric"] = metric

    variability_parts.append(temp)

variability = pd.concat(
    variability_parts,
    ignore_index=True
)

variability.to_csv(
    os.path.join(BASE, "variability_analysis.csv"),
    index=False
)

print(f"  Saved: {BASE}/variability_analysis.csv")


# ============================================================
# 8. CORRELATION ANALYSIS
# ============================================================

print("[4/5] Calculating metric correlations...")

correlation_cols = [
    "n",
    "exec_ms",
    "opcodes",
    "gc_count",
    "gc_ms",
    "peak_heap_bytes",
    "bytes_allocated",
    "bytes_freed",
]

overall_corr = df[correlation_cols].corr(method="pearson")

overall_corr.to_csv(
    os.path.join(BASE, "correlation_overall.csv")
)

rows = []

for benchmark, group in df.groupby("benchmark"):

    corr = group[correlation_cols].corr()

    for metric_a in correlation_cols:
        for metric_b in correlation_cols:

            if metric_a == metric_b:
                continue

            rows.append({
                "benchmark": benchmark,
                "metric_a": metric_a,
                "metric_b": metric_b,
                "pearson_r": corr.loc[
                    metric_a, metric_b
                ],
            })

pd.DataFrame(rows).to_csv(
    os.path.join(BASE, "correlation_by_workload.csv"),
    index=False
)

print(f"  Saved: {BASE}/correlation_overall.csv")
print(f"  Saved: {BASE}/correlation_by_workload.csv")


# ============================================================
# 9. PREPARE AGGREGATED DATA FOR FIGURES
# ============================================================

print("[5/5] Generating figures...")

# Detect the actual mean execution-time column.
if "exec_ms_mean" in agg.columns:
    agg_exec_col = "exec_ms_mean"
elif "exec_ms" in agg.columns:
    agg_exec_col = "exec_ms"
else:
    raise ValueError(
        "Could not find execution-time column in aggregated.csv. "
        f"Columns found: {list(agg.columns)}"
    )

# Detect opcode mean column.
if "opcodes_mean" in agg.columns:
    agg_opcode_col = "opcodes_mean"
elif "opcodes" in agg.columns:
    agg_opcode_col = "opcodes"
else:
    raise ValueError(
        "Could not find opcode column in aggregated.csv."
    )


# ------------------------------------------------------------
# Figure 1: Execution time scaling
# ------------------------------------------------------------

for benchmark, group in agg.groupby("benchmark"):

    group = group.sort_values("n")

    plt.figure(figsize=(8, 5))

    plt.plot(
        group["n"],
        group[agg_exec_col],
        marker="o"
    )

    plt.xlabel("N")
    plt.ylabel("Execution Time (ms)")
    plt.title(f"Execution Time Scaling — {benchmark}")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIG_DIR,
            f"{benchmark}_execution_scaling.png"
        ),
        dpi=200
    )

    plt.close()


# ------------------------------------------------------------
# Figure 2: Opcode count scaling
# ------------------------------------------------------------

for benchmark, group in agg.groupby("benchmark"):

    group = group.sort_values("n")

    plt.figure(figsize=(8, 5))

    plt.plot(
        group["n"],
        group[agg_opcode_col],
        marker="o"
    )

    plt.xlabel("N")
    plt.ylabel("Executed Bytecode Instructions")
    plt.title(f"Opcode Count Scaling — {benchmark}")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIG_DIR,
            f"{benchmark}_opcode_scaling.png"
        ),
        dpi=200
    )

    plt.close()


# ------------------------------------------------------------
# Figure 3: Execution cost per million opcodes
# ------------------------------------------------------------

for benchmark, group in efficiency.groupby("benchmark"):

    group = group.sort_values("n")

    plt.figure(figsize=(8, 5))

    plt.plot(
        group["n"],
        group["mean"],
        marker="o"
    )

    plt.xlabel("N")
    plt.ylabel("Execution Time per Million Opcodes (ms/Mop)")
    plt.title(
        f"Bytecode Execution Efficiency — {benchmark}"
    )
    plt.xscale("log")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIG_DIR,
            f"{benchmark}_opcode_efficiency.png"
        ),
        dpi=200
    )

    plt.close()


# ------------------------------------------------------------
# Figure 4: GC behavior
# ------------------------------------------------------------

for benchmark, group in gc.groupby("benchmark"):

    group = group.sort_values("n")

    plt.figure(figsize=(8, 5))

    plt.plot(
        group["n"],
        group["mean_gc_count"],
        marker="o"
    )

    plt.xlabel("N")
    plt.ylabel("Mean GC Cycles")
    plt.title(f"GC Activity — {benchmark}")
    plt.xscale("log")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIG_DIR,
            f"{benchmark}_gc.png"
        ),
        dpi=200
    )

    plt.close()


# ------------------------------------------------------------
# Figure 5: Peak heap
# ------------------------------------------------------------

for benchmark, group in gc.groupby("benchmark"):

    group = group.sort_values("n")

    plt.figure(figsize=(8, 5))

    plt.plot(
        group["n"],
        group["mean_peak_heap"],
        marker="o"
    )

    plt.xlabel("N")
    plt.ylabel("Peak Heap Usage (bytes)")
    plt.title(f"Peak Heap Usage — {benchmark}")
    plt.xscale("log")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            FIG_DIR,
            f"{benchmark}_heap.png"
        ),
        dpi=200
    )

    plt.close()


# ============================================================
# FINAL REPORT
# ============================================================

print()
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print()
print("Generated:")
print("  opcode_efficiency.csv")
print("  opcode_efficiency_summary.csv")
print("  gc_analysis.csv")
print("  variability_analysis.csv")
print("  correlation_overall.csv")
print("  correlation_by_workload.csv")
print("  figures/*.png")

print()
print(f"Figures generated: {len(os.listdir(FIG_DIR))}")