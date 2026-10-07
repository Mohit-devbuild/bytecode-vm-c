import os
import sys
import pandas as pd

def find_file(filename):
    candidates = [
        filename,
        os.path.join("results", filename),
        os.path.join("dataset_v3", "results", filename),
        os.path.join("..", "dataset_v3", "results", filename),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

csv_path = find_file("dataset_v3.csv")

print("=" * 60)
print(" STAGE 1: DATASET V3 VALIDATION CHECK")
print(f" Target File: {csv_path if csv_path else 'NOT FOUND'}")
print("=" * 60)

if not csv_path:
    print("[ERROR] Could not locate dataset_v3.csv. Check working directory.")
    sys.exit(1)

df = pd.read_csv(csv_path)

# 1. Total Rows
total_rows = len(df)
expected_rows = 9600
row_pass = total_rows == expected_rows
print(f"1. Total Rows        : {total_rows:,} / {expected_rows:,} [{'PASS' if row_pass else 'FAIL'}]")

# 2. Workload Count
workload_count = df['benchmark'].nunique()
expected_workloads = 12
workload_pass = workload_count == expected_workloads
print(f"2. Workload Count    : {workload_count} / {expected_workloads} [{'PASS' if workload_pass else 'FAIL'}]")

# 3. N Values per Workload
n_counts = df.groupby('benchmark')['n'].nunique()
n_pass = (n_counts == 20).all()
print(f"3. N Values / Workload: Min {n_counts.min()}, Max {n_counts.max()} (Expected: 20) [{'PASS' if n_pass else 'FAIL'}]")

# 4. Repetition Counts
reps = df.groupby(['benchmark', 'n'])['rep'].count()
rep_pass = (reps.min() == 40) and (reps.max() == 40)
print(f"4. Reps per Config   : Min {reps.min()}, Max {reps.max()} (Expected: 40) [{'PASS' if rep_pass else 'FAIL'}]")

# 5. Key Uniqueness
duplicates = df.duplicated(subset=['benchmark', 'n', 'rep']).sum()
dup_pass = duplicates == 0
print(f"5. Duplicate Keys    : {duplicates} (Expected: 0) [{'PASS' if dup_pass else 'FAIL'}]")

# 6. Null / NaN Values
required_cols = ['exec_ms', 'opcodes', 'gc_count', 'gc_ms', 'peak_heap_bytes', 'bytes_allocated']
null_count = df[required_cols].isnull().sum().sum()
null_pass = null_count == 0
print(f"6. Missing/NaN Values: {null_count} (Expected: 0) [{'PASS' if null_pass else 'FAIL'}]")

# 7. string_concat GC Fix Check
sc_df = df[df['benchmark'] == 'string_concat']
sc_heap_min = sc_df['peak_heap_bytes'].min() if not sc_df.empty else 0
sc_heap_pass = sc_heap_min >= 1000000
print(f"7. string_concat Heap : Min peak heap = {sc_heap_min:,} bytes (Expected >= 1 MB) [{'PASS' if sc_heap_pass else 'FAIL'}]")

print("-" * 60)
if all([row_pass, workload_pass, n_pass, rep_pass, dup_pass, null_pass, sc_heap_pass]):
    print("[SUCCESS] Dataset v3 passed all structural and metric validation checks!")
else:
    print("[WARNING] Validation failed. Check failures above before proceeding.")