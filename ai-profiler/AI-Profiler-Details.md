Here's some research papers we referenced for this project:

GC Vulnerabilities Papers
[iLeakage Paper](https://dl.acm.org/doi/epdf/10.1145/3576915.3616611)
[Top GC Vulnerabilities paper](https://www.usenix.org/conference/usenixsecurity21/presentation/han-hyungseok)
[Securing the heap paper](https://www.usenix.org/legacy/event/woot/tech/final_files/Novark.pdf)
[Rage against the machine Paper](https://www.usenix.org/conference/usenixsecurity21/presentation/ragab) 

AI Profiler papers
[Isolation Forest for Anomaly Detection](https://onlinelibrary.wiley.com/doi/10.1002/cpe.5306)
[Isolation Forest](https://ieeexplore.ieee.org/document/4781136)


Here are the important links for this project:

[GC Github](https://github.com/moonboyknm/bytecode-vm-c-ai-profiler)
[Colab Notebook]([https://colab.research.google.com/drive/1mFd5XLfHybbzp38zd28GAXYzfHnP1Z3T#scrollTo=i4tLtpIqh92M](https://colab.research.google.com/drive/1mFd5XLfHybbzp38zd28GAXYzfHnP1Z3T?usp=sharing))
### Research Gaps and Our Contribution

Existing research has explored machine-learning-based performance anomaly detection, particularly in cloud and application environments, but there is comparatively less focus on **bytecode virtual machines and language-runtime behavior**. Additionally, performance anomalies are often studied using general system metrics rather than VM-specific execution characteristics.

Our project addresses these gaps by applying **Isolation Forest** to runtime data collected directly from a bytecode VM. We use multiple VM-specific metrics—including opcode executions, execution time, garbage collection, heap usage, and memory allocation—to detect unusual runtime behavior. The project therefore connects **program workloads, VM execution, runtime profiling, and automated anomaly detection** into a single pipeline. The detected anomalies are further evaluated using precision, recall, F1-score, and a confusion matrix.
### Case Studies

**1. Allocation and Garbage Collection:**  
The allocation benchmark examines memory-management behavior under increasing workloads. As allocations increase, garbage-collection activity and memory allocation rise significantly. This case study demonstrates how VM memory behavior can be captured through runtime profiling metrics.

**2. Recursive Execution:**  
The recursion benchmark studies the performance impact of increasingly deep recursive computation. Opcode executions and execution time grow rapidly with input size, demonstrating the relationship between algorithmic complexity and VM-level performance.

**3. Runtime Anomaly Detection:**  
The complete dataset of 160 runtime observations is processed using StandardScaler and Isolation Forest. The model analyzes execution, opcode, garbage-collection, and memory metrics to identify unusual executions. Its results are evaluated using a confusion matrix, precision, recall, and F1-score, demonstrating the practical application of machine-learning-based anomaly detection to VM performance profiling.
### Flow Diagram
                 ┌──────────────────────┐
                 │   Lox VM Benchmarks  │
                 │ allocation/arithmetic│
                 │ closures/functions   │
                 │ inheritance/loops    │
                 │ objects/recursion    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Runtime Profiling   │
                 │ Execution Time      │
                 │ Opcode Count        │
                 │ GC Metrics          │
                 │ Memory Metrics      │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Dataset Creation  │
                 │ 160 Runtime Records │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Feature Selection    │
                 │ 8 Runtime Features   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Standard Scaling     │
                 │    StandardScaler    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Isolation Forest   │
                 │ 100 Trees / 5%       │
                 │ Contamination        │
                 └──────────┬───────────┘
                            │
                    ┌───────┴────────┐
                    ▼                ▼
             ┌────────────┐   ┌─────────────┐
             │ Normal Run │   │   Anomaly   │
             │   (+1)     │   │    (-1)     │
             └────────────┘   └──────┬──────┘
                                     │
                                     ▼
                           ┌──────────────────┐
                           │ Anomaly Scores   │
                           │ + Visualization  │
                           └────────┬─────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │ Model Evaluation │
                           │ Precision/Recall │
                           │ F1 + Confusion   │
                           │ Matrix           │
                           └──────────────────┘
### Algorithms Used

The AI profiler uses a preprocessing and anomaly-detection pipeline based on **StandardScaler** and **Isolation Forest**. First, **StandardScaler** standardizes the eight runtime features by transforming them to have a mean of approximately zero and a standard deviation of one. This prevents metrics with larger numerical ranges, such as memory allocation or opcode counts, from dominating the analysis.

The scaled data is then processed using the **Isolation Forest** algorithm. Isolation Forest is an unsupervised anomaly-detection algorithm that identifies observations that are easier to isolate from the rest of the dataset. It constructs multiple random decision trees and calculates an anomaly score based on how quickly each observation becomes isolated. The implementation uses **100 trees** with a **5% contamination rate** and a fixed random seed for reproducibility. Each observation is classified as either normal or anomalous.
## Dataset

The AI profiler uses a dataset containing **160 runtime observations** collected from the bytecode virtual machine. These observations are generated from **32 benchmark configurations, each executed five times**, covering allocation, arithmetic, closures, functions, inheritance, loops, objects, and recursion. Each observation records eight performance and memory metrics: compilation time, execution time, opcode executions, garbage-collection count, garbage-collection time, peak heap usage, total bytes allocated, and total bytes freed. The dataset is used as input to the Isolation Forest model after feature scaling. The model identifies unusual runtime executions and assigns each observation an anomaly label and anomaly score.
### Short Note on the AI Profiler

The `ai-profiler` component extends the bytecode virtual machine with a machine-learning-based approach for detecting unusual runtime behavior. It analyzes performance and memory-related metrics collected while executing VM programs and uses them to identify anomalous executions.

The profiler works with several runtime metrics, including **compilation time, execution time, opcode execution count, garbage-collection count, garbage-collection time, peak heap usage, total bytes allocated, and total bytes freed**. These measurements provide a numerical representation of the VM’s behavior during each benchmark execution.

The collected data is stored in a CSV dataset and processed using Python. Before applying the machine-learning algorithm, the profiler uses **StandardScaler** to normalize the different metrics so that features with larger numerical ranges do not disproportionately influence the model.

For anomaly detection, the project uses an **Isolation Forest** algorithm. Isolation Forest is an unsupervised machine-learning technique designed to identify observations that are significantly different from the majority of the dataset. The model uses multiple decision trees to isolate unusual data points and produces both an **anomaly prediction** and an **anomaly score** for each execution. The implementation uses 100 trees, a contamination value of 5%, and a fixed random seed to make results reproducible.

The profiler also includes an evaluation stage. The detected anomalies are compared against labelled anomalies in the dataset using a confusion matrix. The reported results give approximately **75% precision, 60% recall, and 66.7% F1-score**, providing a quantitative measure of how effectively the model identifies abnormal VM executions.

Finally, the project provides visualization through an **anomaly scatter plot** and stores the processed results in a CSV file. This makes it possible to inspect which executions were classified as anomalous and examine their associated performance characteristics.

Overall, the AI profiler combines **runtime telemetry, data preprocessing, machine-learning-based anomaly detection, evaluation, and visualization** to automatically identify unusual performance behavior in the bytecode VM.