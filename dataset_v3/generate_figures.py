import os
import matplotlib.pyplot as plt
import pandas as pd

# Path configuration
comp_path = "analysis_results/v2_vs_v3_comparison.csv"
output_dir = "analysis_results/figures"

os.makedirs(output_dir, exist_ok=True)

if not os.path.exists(comp_path):
    print(f"[ERROR] Could not locate {comp_path}. Run Stage 2 aggregation first.")
    exit(1)

df_comp = pd.read_csv(comp_path)

# Set clean scientific plotting style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# ---------------------------------------------------------
# Figure 1: string_concat Execution Time Scaling (v2 vs v3)
# ---------------------------------------------------------
sc = df_comp[df_comp['benchmark'] == 'string_concat']

plt.figure(figsize=(8, 5))
plt.plot(sc['n'], sc['exec_ms_v2'], 'r-o', label='v2 Baseline (20KB Dynamic GC)', linewidth=2)
plt.plot(sc['n'], sc['exec_ms_v3'], 'b-s', label='v3 Fixed (1MB Heap Floor)', linewidth=2)
plt.title('string_concat: Execution Time vs. Input Size (N)', fontsize=12, fontweight='bold')
plt.xlabel('Input Size (N)', fontsize=11)
plt.ylabel('Execution Time (ms)', fontsize=11)
plt.legend()
plt.tight_layout()
fig1_path = os.path.join(output_dir, 'fig1_string_concat_exec_time.png')
plt.savefig(fig1_path, dpi=300)
plt.close()
print(f"Saved Figure 1 -> {fig1_path}")

# ---------------------------------------------------------
# Figure 2: string_concat GC Invocations (v2 vs v3)
# ---------------------------------------------------------
plt.figure(figsize=(8, 5))
plt.plot(sc['n'], sc['gc_count_v2'], 'r-o', label='v2 Baseline (GC Thrashing)', linewidth=2)
plt.plot(sc['n'], sc['gc_count_v3'], 'g-^', label='v3 Fixed (1MB Heap Floor)', linewidth=2)
plt.title('string_concat: GC Collection Cycles vs. Input Size (N)', fontsize=12, fontweight='bold')
plt.xlabel('Input Size (N)', fontsize=11)
plt.ylabel('GC Invocation Count', fontsize=11)
plt.legend()
plt.tight_layout()
fig2_path = os.path.join(output_dir, 'fig2_string_concat_gc_count.png')
plt.savefig(fig2_path, dpi=300)
plt.close()
print(f"Saved Figure 2 -> {fig2_path}")

# ---------------------------------------------------------
# Figure 3: Cross-Workload Regression Check at Max N
# ---------------------------------------------------------
max_n_per_workload = df_comp.groupby('benchmark')['n'].max().reset_index()
max_comp = pd.merge(max_n_per_workload, df_comp, on=['benchmark', 'n'])

plt.figure(figsize=(10, 5))
bars = plt.bar(max_comp['benchmark'], max_comp['speedup_ratio'], color='skyblue', edgecolor='black')
plt.axhline(1.0, color='red', linestyle='--', label='Parity (1.0x)')
plt.title('Speedup Ratio (v2_exec_ms / v3_exec_ms) Across All 12 Workloads at Max N', fontsize=12, fontweight='bold')
plt.xlabel('Workload', fontsize=11)
plt.ylabel('Speedup Ratio', fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.legend()
plt.tight_layout()
fig3_path = os.path.join(output_dir, 'fig3_cross_workload_speedup.png')
plt.savefig(fig3_path, dpi=300)
plt.close()
print(f"Saved Figure 3 -> {fig3_path}")

print("\n[SUCCESS] All paper figures generated successfully!")