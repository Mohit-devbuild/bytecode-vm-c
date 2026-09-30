from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
GRAPHS = RESULTS / "graphs"


def load_data():
    summary = pd.read_csv(RESULTS / "summary_v1.csv")
    opcode = pd.read_csv(RESULTS / "opcode_summary_v1.csv")
    variability = pd.read_csv(RESULTS / "variability_v1.csv")

    return summary, opcode, variability


def save_figure(filename):
    path = GRAPHS / filename
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Created: {path}")


def execution_time_scaling(summary):
    plt.figure(figsize=(10, 6))

    for benchmark, group in summary.groupby("benchmark"):
        group = group.sort_values("input_size")
        plt.plot(
            group["input_size"],
            group["execution_time_ms_mean"],
            marker="o",
            label=benchmark,
        )

    plt.xlabel("Input size")
    plt.ylabel("Mean execution time (ms)")
    plt.title("Clox Execution Time Scaling")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend()
    plt.grid(True, alpha=0.3)

    save_figure("execution_time_scaling.png")


def opcode_scaling(summary):
    plt.figure(figsize=(10, 6))

    for benchmark, group in summary.groupby("benchmark"):
        group = group.sort_values("input_size")
        plt.plot(
            group["input_size"],
            group["opcode_executions_mean"],
            marker="o",
            label=benchmark,
        )

    plt.xlabel("Input size")
    plt.ylabel("Mean opcode executions")
    plt.title("Clox Opcode Execution Scaling")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend()
    plt.grid(True, alpha=0.3)

    save_figure("opcode_scaling.png")


def benchmark_comparison(summary):
    largest = (
        summary.sort_values("input_size")
        .groupby("benchmark", as_index=False)
        .tail(1)
        .sort_values("execution_time_ms_mean", ascending=False)
    )

    plt.figure(figsize=(10, 6))

    plt.bar(
        largest["benchmark"],
        largest["execution_time_ms_mean"],
    )

    plt.xlabel("Benchmark")
    plt.ylabel("Mean execution time (ms)")
    plt.title("Execution Time at Largest Tested Input")
    plt.xticks(rotation=30, ha="right")

    save_figure("benchmark_comparison.png")


def opcode_composition(opcode):
    totals = (
        opcode.groupby("opcode")["mean_count"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    plt.figure(figsize=(10, 6))

    plt.bar(
        totals.index,
        totals.values,
    )

    plt.xlabel("Opcode")
    plt.ylabel("Total mean executions")
    plt.title("Most Frequently Executed Opcodes")
    plt.xticks(rotation=45, ha="right")

    save_figure("opcode_composition.png")


def gc_behavior(summary):
    allocation = summary[
        summary["benchmark"] == "allocation"
    ].sort_values("input_size")

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(
        allocation["input_size"],
        allocation["gc_count_mean"],
        marker="o",
        label="GC count",
    )

    ax1.set_xlabel("Input size")
    ax1.set_ylabel("Mean GC count")
    ax1.set_xscale("log")

    ax2 = ax1.twinx()

    ax2.plot(
        allocation["input_size"],
        allocation["gc_time_ms_mean"],
        marker="s",
        label="GC time",
    )

    ax2.set_ylabel("Mean GC time (ms)")

    plt.title("Garbage Collection Behavior")

    save_figure("gc_behavior.png")


def memory_behavior(summary):
    allocation = summary[
        summary["benchmark"] == "allocation"
    ].sort_values("input_size")

    plt.figure(figsize=(10, 6))

    plt.plot(
        allocation["input_size"],
        allocation["total_bytes_allocated_mean"],
        marker="o",
        label="Bytes allocated",
    )

    plt.plot(
        allocation["input_size"],
        allocation["total_bytes_freed_mean"],
        marker="s",
        label="Bytes freed",
    )

    plt.plot(
        allocation["input_size"],
        allocation["peak_heap_usage_bytes_mean"],
        marker="^",
        label="Peak heap",
    )

    plt.xlabel("Input size")
    plt.ylabel("Bytes")
    plt.title("Memory Allocation and Heap Behavior")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend()
    plt.grid(True, alpha=0.3)

    save_figure("memory_behavior.png")


def variability_plot(variability):
    plt.figure(figsize=(10, 6))

    for benchmark, group in variability.groupby("benchmark"):
        group = group.sort_values("input_size")

        plt.plot(
            group["input_size"],
            group["cv_percent"],
            marker="o",
            label=benchmark,
        )

    plt.axhline(
        10,
        linestyle="--",
        label="10% CV",
    )

    plt.xlabel("Input size")
    plt.ylabel("Coefficient of variation (%)")
    plt.title("Benchmark Measurement Variability")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend()
    plt.grid(True, alpha=0.3)

    save_figure("variability.png")


def recursion_scaling(summary):
    recursion = summary[
        summary["benchmark"] == "recursion"
    ].sort_values("input_size")

    plt.figure(figsize=(10, 6))

    plt.plot(
        recursion["input_size"],
        recursion["execution_time_ms_mean"],
        marker="o",
    )

    plt.xlabel("Recursion input N")
    plt.ylabel("Mean execution time (ms)")
    plt.title("Recursive Workload Scaling")
    plt.yscale("log")
    plt.grid(True, alpha=0.3)

    save_figure("recursion_scaling.png")


def main():
    print("============================================")
    print("CLOX GRAPH GENERATION")
    print("============================================")

    GRAPHS.mkdir(parents=True, exist_ok=True)

    summary, opcode, variability = load_data()

    print(f"Summary rows: {len(summary)}")
    print(f"Opcode rows: {len(opcode)}")
    print(f"Variability rows: {len(variability)}")
    print()

    execution_time_scaling(summary)
    opcode_scaling(summary)
    benchmark_comparison(summary)
    opcode_composition(opcode)
    gc_behavior(summary)
    memory_behavior(summary)
    variability_plot(variability)
    recursion_scaling(summary)

    print()
    print("============================================")
    print("GRAPH GENERATION COMPLETE")
    print("============================================")


if __name__ == "__main__":
    main()