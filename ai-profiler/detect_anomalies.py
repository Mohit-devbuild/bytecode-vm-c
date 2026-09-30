import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


INPUT_PATH = "results/dataset_v1.csv"
OUTPUT_PATH = "results/dataset_anomalies_v1.csv"

FEATURES = [
    "compilation_time_ms",
    "execution_time_ms",
    "opcode_executions",
    "gc_count",
    "gc_time_ms",
    "peak_heap_usage_bytes",
    "total_bytes_allocated",
    "total_bytes_freed",
]


df = pd.read_csv(INPUT_PATH)
scaled_features = StandardScaler().fit_transform(df[FEATURES])

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42,
)
df["anomaly_label"] = model.fit_predict(scaled_features)
df["anomaly_score"] = model.decision_function(scaled_features)

df.to_csv(OUTPUT_PATH, index=False)
