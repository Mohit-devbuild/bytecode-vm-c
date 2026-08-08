import csv
import re
from pathlib import Path


# ============================================================
# clox Dataset v1 Parser
# ============================================================

RAW_DIR = Path("results/raw")
RESULTS_DIR = Path("results")


# ------------------------------------------------------------
# Raw result filename format
#
# benchmark_N<input_size>_run<run>_<timestamp>.txt
#
# Example:
# arithmetic_N10000_run1_20260809_010203_123.txt
# ------------------------------------------------------------

RUN_OUTPUT_PATTERN = re.compile(
    r"^(?P<benchmark>.+)_N(?P<input_size>\d+)"
    r"_run(?P<run>\d+)_\d{8}_\d{6}_\d+\.txt$"
)


# ------------------------------------------------------------
# Profiler metric patterns
# ------------------------------------------------------------

METRIC_PATTERNS = {
    "compilation_time_ms": re.compile(
        r"Compilation time:\s*([0-9.]+)\s*ms"
    ),

    "execution_time_ms": re.compile(
        r"Execution time:\s*([0-9.]+)\s*ms"
    ),

    "opcode_executions": re.compile(
        r"Opcode executions:\s*(\d+)"
    ),

    "gc_count": re.compile(
        r"GC count:\s*(\d+)"
    ),

    "gc_time_ms": re.compile(
        r"GC time:\s*([0-9.]+)\s*ms"
    ),

    "peak_heap_usage_bytes": re.compile(
        r"Peak heap usage:\s*(\d+)\s*bytes"
    ),

    "total_bytes_allocated": re.compile(
        r"Total bytes allocated:\s*(\d+)\s*bytes"
    ),

    "total_bytes_freed": re.compile(
        r"Total bytes freed:\s*(\d+)\s*bytes"
    ),
}


# ------------------------------------------------------------
# Read PowerShell-generated result files
#
# PowerShell may write redirected output as UTF-16 LE.
# We detect the BOM instead of assuming UTF-8.
# ------------------------------------------------------------

def read_result_file(path):
    raw_bytes = path.read_bytes()

    # UTF-16 Little Endian BOM
    if raw_bytes.startswith(b"\xff\xfe"):
        return raw_bytes.decode("utf-16")

    # UTF-16 Big Endian BOM
    if raw_bytes.startswith(b"\xfe\xff"):
        return raw_bytes.decode("utf-16")

    # UTF-8 with or without BOM
    return raw_bytes.decode("utf-8-sig")


# ------------------------------------------------------------
# Parse filename metadata
# ------------------------------------------------------------

def parse_filename(filename):

    match = RUN_OUTPUT_PATTERN.match(filename)

    if not match:
        raise ValueError(
            f"Unexpected result filename: {filename}"
        )

    return {
        "benchmark": match.group("benchmark"),
        "input_size": int(match.group("input_size")),
        "run": int(match.group("run")),
    }


# ------------------------------------------------------------
# Parse profiler metrics
# ------------------------------------------------------------

def parse_metrics(text):

    metrics = {}

    for name, pattern in METRIC_PATTERNS.items():

        match = pattern.search(text)

        if not match:
            raise ValueError(
                f"Could not find metric '{name}'."
            )

        value = match.group(1)

        if name in {
            "compilation_time_ms",
            "execution_time_ms",
            "gc_time_ms",
        }:
            metrics[name] = float(value)

        else:
            metrics[name] = int(value)

    return metrics


# ------------------------------------------------------------
# Parse instruction frequency
# ------------------------------------------------------------

def parse_instruction_frequency(text):

    frequencies = {}

    marker = "----- Instruction Frequency -----"

    if marker not in text:
        raise ValueError(
            "Instruction Frequency section not found."
        )

    section = text.split(marker, 1)[1]

    section = section.split(
        "===================================",
        1
    )[0]

    for line in section.strip().splitlines():

        parts = line.split()

        if len(parts) != 2:
            continue

        opcode = parts[0]
        count = int(parts[1])

        frequencies[opcode] = count

    return frequencies


# ------------------------------------------------------------
# Main parser
# ------------------------------------------------------------

def main():

    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"Raw results directory not found: {RAW_DIR}"
        )

    result_files = sorted(
        RAW_DIR.glob("*.txt")
    )

    if not result_files:
        raise FileNotFoundError(
            "No raw result files found."
        )

    dataset_rows = []
    frequency_rows = []

    # --------------------------------------------------------
    # Parse every raw profiler output
    # --------------------------------------------------------

    for index, path in enumerate(result_files, start=1):

        print(
            f"Parsing {index}/{len(result_files)}: "
            f"{path.name}"
        )

        metadata = parse_filename(
            path.name
        )

        text = read_result_file(path)

        metrics = parse_metrics(text)

        frequencies = parse_instruction_frequency(
            text
        )

        # ----------------------------------------------------
        # Validate opcode totals
        # ----------------------------------------------------

        frequency_total = sum(
            frequencies.values()
        )

        if frequency_total != metrics["opcode_executions"]:

            raise ValueError(
                f"Opcode mismatch in {path.name}: "
                f"aggregate="
                f"{metrics['opcode_executions']} "
                f"frequency_sum="
                f"{frequency_total}"
            )

        # ----------------------------------------------------
        # Main dataset row
        # ----------------------------------------------------

        row = {
            **metadata,
            **metrics,
        }

        dataset_rows.append(row)

        # ----------------------------------------------------
        # Instruction frequency rows
        # ----------------------------------------------------

        for opcode, count in frequencies.items():

            frequency_rows.append({
                **metadata,
                "opcode": opcode,
                "count": count,
            })

    # --------------------------------------------------------
    # Validate number of runs
    # --------------------------------------------------------

    expected_runs = 160

    if len(dataset_rows) != expected_runs:

        raise ValueError(
            f"Expected {expected_runs} runs, "
            f"but parsed {len(dataset_rows)}."
        )

    # --------------------------------------------------------
    # Write main dataset
    # --------------------------------------------------------

    dataset_path = (
        RESULTS_DIR / "dataset_v1.csv"
    )

    dataset_fields = [
        "benchmark",
        "input_size",
        "run",
        "compilation_time_ms",
        "execution_time_ms",
        "opcode_executions",
        "gc_count",
        "gc_time_ms",
        "peak_heap_usage_bytes",
        "total_bytes_allocated",
        "total_bytes_freed",
    ]

    with dataset_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=dataset_fields,
        )

        writer.writeheader()

        writer.writerows(
            dataset_rows
        )

    # --------------------------------------------------------
    # Write instruction frequency dataset
    # --------------------------------------------------------

    frequency_path = (
        RESULTS_DIR /
        "instruction_frequency_v1.csv"
    )

    frequency_fields = [
        "benchmark",
        "input_size",
        "run",
        "opcode",
        "count",
    ]

    with frequency_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=frequency_fields,
        )

        writer.writeheader()

        writer.writerows(
            frequency_rows
        )

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    print()
    print("============================================")
    print("DATASET VALIDATION")
    print("============================================")

    print(
        f"Parsed runs: {len(dataset_rows)}"
    )

    print(
        f"Instruction frequency rows: "
        f"{len(frequency_rows)}"
    )

    print(
        f"Created: {dataset_path}"
    )

    print(
        f"Created: {frequency_path}"
    )

    print(
        "Opcode validation: PASSED"
    )

    print(
        "Run count validation: PASSED"
    )

    print(
        "Dataset validation: PASSED"
    )

    print("============================================")


if __name__ == "__main__":
    main()