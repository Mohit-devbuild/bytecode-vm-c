import os
import sys
import numpy as np
import pandas as pd

def find_file(filename):
    candidates = [
        filename,
        os.path.join("results", filename),
        os.path.join("dataset_v3", "results", filename),
        os.path.join("..", "dataset_v3", "results", filename),
        os.path.join("..", "dataset_v2", "results", filename),
        os.path.join("dataset_v2", "results", filename),
    ]
    for c in candidates:
        if os.path.exists(c) and filename in c:
            return c
    return None

v3_path = find_file("dataset_v3.csv")
v2_path = find_file("dataset_v2.csv")

output_dir = "analysis_results"
os.makedirs(output_dir, exist_ok=True)

print("=" * 60)
print(" STAGE 2: STATISTICAL AGGREGATION & V2 VS V3 COMPARISON")
print(f" Dataset v3 Source: {v3_path}")
print(f" Dataset v2 Source: {v2_path if v2_path else 'Not Found (Skipping Comparison)'}")
print("=" * 60)

if not v3_path:
    print("[ERROR] Could not locate dataset_v3.csv.")
    sys.exit(1)

df_v3 = pd.read_csv(v3_path)
metrics = ['exec_ms', 'opcodes', 'gc_count', 'gc_ms', 'peak_heap_bytes', 'bytes_allocated', 'bytes_freed']

# 1. Aggregation (Mean, Median, Standard Deviation, Min, Max)
grouped = df_v3.groupby(['benchmark', 'n'])[metrics].agg(['mean', 'median', 'std', 'min', 'max'])
grouped.columns = ['_'.join(col) for col in grouped.columns]
grouped = grouped.reset_index()

# 2. Coefficient of Variation (CV %) & Derived Metrics
for m in metrics:
    grouped[f'{m}_cv'] = (grouped[f'{m}_std'] / np.maximum(grouped[f'{m}_mean'], 1e-9)) * 100

grouped['ms_per_million_opcodes'] = grouped['exec_ms_mean'] / (grouped['opcodes_mean'] / 1e6)
grouped['gc_overhead_pct'] = (grouped['gc_ms_mean'] / np.maximum(grouped['exec_ms_mean'], 1e-9)) * 100

agg_out = os.path.join(output_dir, "dataset_v3_aggregated.csv")
grouped.to_csv(agg_out, index=False)
print(f"1. Aggregated Metrics Saved -> {agg_out}")

# 3. Direct Speedup and GC Comparison against Dataset v2
if v2_path:
    df_v2 = pd.read_csv(v2_path)
    v2_agg = df_v2.groupby(['benchmark', 'n'])[['exec_ms', 'gc_count', 'gc_ms', 'peak_heap_bytes']].mean().reset_index()
    v3_agg = df_v3.groupby(['benchmark', 'n'])[['exec_ms', 'gc_count', 'gc_ms', 'peak_heap_bytes']].mean().reset_index()

    comp = pd.merge(v2_agg, v3_agg, on=['benchmark', 'n'], suffixes=('_v2', '_v3'))

    comp['speedup_ratio'] = comp['exec_ms_v2'] / np.maximum(comp['exec_ms_v3'], 1e-9)
    comp['gc_count_reduction'] = comp['gc_count_v2'] - comp['gc_count_v3']
    comp['gc_ms_saved'] = comp['gc_ms_v2'] - comp['gc_ms_v3']

    comp_out = os.path.join(output_dir, "v2_vs_v3_comparison.csv")
    comp.to_csv(comp_out, index=False)
    print(f"2. Baseline Comparison Saved -> {comp_out}")

    sc_comp = comp[comp['benchmark'] == 'string_concat'].tail(5)
    print("\n--- string_concat Optimization Impact (Sample High N Values) ---")
    print(sc_comp[['n', 'exec_ms_v2', 'exec_ms_v3', 'speedup_ratio', 'gc_count_v2', 'gc_count_v3']].to_string(index=False))

print("\n[SUCCESS] Aggregation and Comparison Complete!")