# clox — A Bytecode Virtual Machine for the Lox Programming Language

A complete implementation of **clox**, a bytecode virtual machine for the Lox programming language written in **C**.

This project explores the implementation of a dynamically typed programming language from source code through compilation, bytecode execution, object management, closures, garbage collection, and runtime profiling.

Beyond the core interpreter, this repository contains an experimental runtime profiling and benchmarking framework used to study execution time, bytecode behaviour, memory allocation, garbage collection, opcode frequency, scaling characteristics, and runtime variability.

---

## Features

* Lexical Scanner

* Pratt Parser

* Single-pass Bytecode Compiler

* Stack-based Virtual Machine

* Dynamic Typing

* Variables and Lexical Scope

* Control Flow

  * `if`

  * `while`

  * `for`

* Functions

* Closures and Upvalues

* Native Functions

* Classes

* Instances

* Methods

* Constructors (`init`)

* Inheritance

* `this`

* `super`

* Dynamic Method Dispatch

* String Interning

* Hash Tables

* Mark-and-Sweep Garbage Collector

* Automatic Memory Management

* Runtime Profiling

* Opcode Instrumentation

* Benchmarking

* Scaling Analysis

* Variability Analysis

* Performance Visualization

* REPL

* Script Execution

---

# Architecture

```text

                 Lox Source Code

                        │

                        ▼

               ┌─────────────────┐

               │     Scanner     │

               └─────────────────┘

                        │

                     Tokens

                        │

                        ▼

               ┌─────────────────┐

               │  Pratt Parser   │

               └─────────────────┘

                        │

                        ▼

          Single-pass Bytecode Compiler

                        │

                        ▼

               ┌─────────────────┐

               │ Bytecode Chunk  │

               └─────────────────┘

                        │

                        ▼

               ┌─────────────────┐

               │ Virtual Machine │

               └─────────────────┘

                        │

                        ▼

                 Program Output

```

The compiler performs parsing and code generation simultaneously, producing bytecode instructions stored in chunks.

The VM then executes these instructions using a stack-based execution model with call frames for function invocation.

The implementation can therefore be viewed as three major stages:

```text

Source Program

      │

      ▼

  Compilation

      │

      ▼

   Bytecode

      │

      ▼

  Interpretation

      │

      ▼

   Runtime

```

---

# Virtual Machine

The VM uses a value stack as its primary operand storage mechanism.

```text

          Top of Stack

                ▲

                │

        ┌──────────────┐

        │    Value     │

        ├──────────────┤

        │    Value     │

        ├──────────────┤

        │    Value     │

        ├──────────────┤

        │    Value     │

        └──────────────┘

                │

          Bottom of Stack

```

Function calls are represented using `CallFrame` structures containing the function closure, instruction pointer, and stack slot associated with the call.

The VM therefore maintains two closely related execution mechanisms:

* A global value stack for operands and local variables

* A call-frame stack representing nested function invocations

Closures extend this model by allowing functions to retain access to variables belonging to enclosing lexical scopes.

---

# Compiler Architecture

`clox` uses a **single-pass compiler** based on Pratt parsing.

Rather than constructing a complete AST and subsequently traversing it, parsing decisions directly emit bytecode into the current chunk.

Conceptually:

```text

Tokens

  │

  ▼

Pratt Parser

  │

  ├── expression parsing

  ├── precedence handling

  ├── variable resolution

  └── statement compilation

          │

          ▼

       Bytecode

```

This design keeps the compiler compact while demonstrating an important trade-off between implementation simplicity and intermediate-representation flexibility.

The compiler also tracks lexical scope, local variables, upvalues, function contexts, and jump patching during bytecode generation.

---

# Runtime Object System

Objects are represented using a common object header, allowing different runtime object types to participate in the same allocation and garbage-collection system.

The runtime includes:

* Strings

* Functions

* Closures

* Upvalues

* Classes

* Instances

* Bound Methods

* Native Functions

Classes and instances use hash tables for property storage and method lookup.

Inheritance introduces superclass relationships and method lookup through the class hierarchy.

The runtime path can therefore be represented as:

```text

Class Definition

      │

      ▼

   Class Object

      │

      ├── Methods

      │

      └── Superclass

             │

             ▼

        Method Lookup

             │

             ▼

       Bound Invocation

```

---

# Closures and Upvalues

Closures require variables from an enclosing function to remain alive after the enclosing call frame has returned.

`clox` handles this through **upvalues**.

Local variables normally reside in stack slots:

```text

Function Call

     │

     ▼

 Stack Slot

```

When a local variable becomes captured:

```text

Stack Slot

    │

    ▼

Open Upvalue

    │

    │ function returns

    ▼

Closed Heap Value

```

This allows closures to preserve lexical state without requiring every local variable to be heap allocated.

---

# Memory Management

Memory is managed using a **mark-and-sweep garbage collector**.

```text

              Root Set

                  │

                  ▼

          Mark Reachable Objects

                  │

                  ▼

          Trace Object Graph

                  │

                  ▼

      Sweep Unreachable Objects

                  │

                  ▼

          Reclaim Memory

```

The collector operates over the runtime object graph and uses VM roots such as:

* Value stack

* Call frames

* Open upvalues

* Global variables

* Compiler roots

* Interned strings

The runtime also tracks allocation and collection behaviour for experimental analysis.

Measured memory characteristics include:

* Total bytes allocated

* Total bytes freed

* Peak heap usage

* Number of GC cycles

* Time spent performing GC

---

# Runtime Profiling & Experimental Methodology

A dedicated profiling layer was added to the VM to empirically study runtime behaviour rather than relying only on wall-clock execution time.

The profiler measures nine primary runtime metrics:

1. Execution time

2. Compilation time

3. Opcode execution count

4. Instruction frequency

5. Garbage collection count

6. Garbage collection time

7. Peak heap usage

8. Total bytes allocated

9. Total bytes freed

Opcode instrumentation records the number of times each bytecode instruction executes during a benchmark.

This makes it possible to distinguish between:

```text

Program Workload

       │

       ▼

Executed Instructions

       │

       ▼

Instruction Mix

       │

       ▼

Runtime Cost

```

rather than treating execution time as a single unexplained measurement.

---

# Benchmark Suite

The experimental workload contains eight benchmark categories designed to exercise different parts of the runtime:

| Benchmark     | Primary Runtime Behaviour                 |

| ------------- | ----------------------------------------- |

| `allocation`  | Heap allocation and garbage collection    |

| `arithmetic`  | Arithmetic operations and global access   |

| `closures`    | Closure creation and upvalue access       |

| `functions`   | Function calls and local/global access    |

| `inheritance` | Classes, inheritance, and method dispatch |

| `loops`       | Repeated control-flow execution           |

| `objects`     | Instance and property operations          |

| `recursion`   | Deep function-call recursion              |

The iterative benchmarks are evaluated at multiple input sizes, while the recursive benchmark uses smaller input sizes because of its rapidly increasing execution cost.

Each benchmark configuration is executed **five times**.

The resulting experimental dataset contains:

* **160 runtime observations**

* **32 benchmark configurations**

* **5 repetitions per configuration**

* **544 aggregated opcode-analysis rows**

* **31 unique opcode types**

The raw benchmark outputs, processed CSV datasets, opcode analysis, and generated visualisations are retained under `results/` for reproducibility and further analysis.

---

# Performance Findings

The benchmark results provide several clear observations about the runtime.

## 1. Opcode execution is approximately linear for iterative workloads

For the `allocation`, `arithmetic`, `closures`, `functions`, `inheritance`, `loops`, and `objects` workloads, opcode counts scale approximately linearly with input size.

The measured scaling exponents are approximately:

```text

allocation     k ≈ 1.00

arithmetic     k ≈ 1.00

closures       k ≈ 1.00

functions      k ≈ 1.00

inheritance    k ≈ 1.00

loops          k ≈ 1.00

objects        k ≈ 1.00

```

The corresponding power-law fits have R² values effectively equal to 1 for these workloads.

This confirms that the dominant bytecode execution work grows proportionally with the benchmark workload for these programs.

---

## 2. Recursion exhibits fundamentally different scaling

The recursive benchmark behaves very differently.

Power-law fitting produced approximately:

```text

Time exponent     k ≈ 12.08

Opcode exponent   k ≈ 12.84

```

However, an exponential model provides a slightly better fit for the measured recursive workload:

```text

Exponential R² ≈ 0.996

Power-law R²    ≈ 0.992

```

The rapidly increasing number of recursive calls therefore dominates execution cost.

The VM executes approximately:

```text

N = 20  →       284,588 opcodes

N = 25  →     3,156,210 opcodes

N = 30  →    35,002,986 opcodes

N = 35  →   388,189,144 opcodes

```

This provides a concrete demonstration of how algorithmic behaviour at the language level directly manifests as instruction-level workload inside the VM.

---

## 3. Global access is a major component of the instruction mix

Across the complete benchmark corpus, the most frequently executed instructions were:

| Rank | Opcode             |  Share |

| ---: | ------------------ | -----: |

|    1 | `OP_GET_GLOBAL`    | 17.65% |

|    2 | `OP_CONSTANT`      | 14.24% |

|    3 | `OP_POP`           | 14.19% |

|    4 | `OP_GET_LOCAL`     |  7.87% |

|    5 | `OP_SET_GLOBAL`    |  7.40% |

|    6 | `OP_ADD`           |  6.23% |

|    7 | `OP_JUMP_IF_FALSE` |  6.21% |

This demonstrates that the VM spends a substantial portion of its execution budget on operand movement and variable access rather than only arithmetic operations.

In particular, global-variable access is significantly more frequent than specialised object-oriented instructions across the complete benchmark corpus.

---

## 4. Benchmark behaviour is dominated by workload structure

The opcode profiles reveal distinct execution signatures.

For example:

* `loops` is dominated by conditional branches, comparisons, global accesses, and repeated loop control.

* `recursion` is dominated by local-variable access, constants, calls, and returns.

* `closures` produces substantial upvalue activity.

* `inheritance` exercises class, method-dispatch, and return-related execution.

* `allocation` produces substantial allocation and garbage-collection activity.

This demonstrates why a single aggregate benchmark score would provide an incomplete view of VM performance.

Different language features produce fundamentally different instruction mixes and runtime costs.

---

## 5. Garbage collection is workload dependent

Most benchmarks allocate relatively little memory compared with the dedicated allocation workload.

The allocation benchmark behaves differently:

```text

Input        GC Cycles

1,000             0

10,000          300

100,000       8,481

1,000,000    90,300

```

Peak heap usage stabilises around:

```text

≈ 1.05 MB

```

while cumulative allocation continues increasing substantially with workload size.

This indicates that the collector is reclaiming short-lived objects rather than allowing live heap usage to grow proportionally with total allocation.

At the largest allocation workload:

```text

Total allocated ≈ 156 MB

Total freed     ≈ 156 MB

Peak heap       ≈ 1.05 MB

```

The distinction between **cumulative allocation** and **live heap size** is particularly important when evaluating garbage-collected runtimes.

---

## 6. Runtime variability decreases for larger workloads

Small workloads show substantial timing variability because fixed system and measurement overhead becomes large relative to actual execution time.

Several small-input configurations exhibit high coefficients of variation, with some 1,000-operation configurations exceeding 100%.

As workloads become larger, the measurements become considerably more stable.

Representative larger workloads include:

```text

arithmetic 10,000,000    CV ≈ 4.68%

loops      10,000,000    CV ≈ 3.73%

inheritance 1,000,000    CV ≈ 2.87%

```

This supports using sufficiently large workloads when comparing VM performance, since the execution signal becomes much larger than measurement noise.

---

# Performance Visualisation

The experimental analysis produces visualisations covering:

* Execution-time scaling

* Opcode scaling

* Benchmark comparison

* Opcode composition

* Garbage-collection behaviour

* Memory behaviour

* Measurement variability

* Recursive scaling

These visualisations are stored under:

```text

results/graphs/

```

The numerical results remain available as CSV datasets, while the raw benchmark outputs are retained under:

```text

results/raw/

```

The opcode-specific analysis is stored under:

```text

results/opcode_analysis/

```

This allows the experimental results to be inspected, analysed, or extended without immediately rerunning the entire benchmark suite.

---

# Repository Structure

```text

clox/

│

├── .gitignore

├── README.md

├── Makefile

│

├── chunk.c

├── chunk.h

├── common.h

├── compiler.c

├── compiler.h

├── debug.c

├── debug.h

├── main.c

├── memory.c

├── memory.h

├── object.c

├── object.h

├── profiler.c

├── profiler.h

├── scanner.c

├── scanner.h

├── table.c

├── table.h

├── value.c

├── value.h

├── vm.c

├── vm.h

│

├── analyze_results.py

├── analyze_scaling.py

├── parse_results.py

├── run_benchmarks.ps1

│

├── analyze/

│   ├── analyze_opcodes.py

│   ├── analyze_variability.py

│   └── make_graphs.py

│

├── benchmarks/

│   ├── allocation.lox

│   ├── arithmetic.lox

│   ├── closures.lox

│   ├── functions.lox

│   ├── inheritance.lox

│   ├── loops.lox

│   ├── objects.lox

│   └── recursion.lox

│

├── build/

│   └── clox.exe

│

└── results/

    ├── dataset_v1.csv

    ├── instruction_frequency_v1.csv

    ├── opcode_summary_v1.csv

    ├── scaling_exponents_v1.csv

    ├── scaling_v1.csv

    ├── summary_v1.csv

    ├── variability_v1.csv

    │

    ├── graphs/

    │   ├── benchmark_comparison.png

    │   ├── execution_time_scaling.png

    │   ├── gc_behavior.png

    │   ├── memory_behavior.png

    │   ├── opcode_composition.png

    │   ├── opcode_scaling.png

    │   ├── recursion_scaling.png

    │   └── variability.png

    │

    ├── opcode_analysis/

    │   ├── benchmark_opcode_profile_v1.csv

    │   ├── opcode_ranking_v1.csv

    │   ├── opcode_totals_v1.csv

    │   └── top_opcodes_v1.csv

    │

    └── raw/

        └── benchmark run outputs

```

---

# Building

### Requirements

* GCC

* GNU Make / MinGW Make

* Python 3

* pandas

* matplotlib

Compile the VM:

```bash

mingw32-make

```

The executable is generated at:

```text

build/clox.exe

```

---

# Running

Start the interactive REPL:

```bash

./build/clox.exe

```

Run a Lox script:

```bash

./build/clox.exe program.lox

```

---

# Example Program

```lox

class Animal {

  speak() {

    print "generic";

  }

}

class Dog < Animal {

  speak() {

    super.speak();

    print "woof";

  }

}

fun factorial(n) {

  if (n <= 1) return 1;

  return n * factorial(n - 1);

}

print factorial(5);

Dog().speak();

```

Output:

```text

120

generic

woof

```

---

# Future Work

## Performance & VM Research

* Benchmark against other bytecode interpreters

* Investigate peephole bytecode optimisations

* Explore constant folding and propagation

* Experiment with inline caching for method dispatch

* Evaluate register-based VM architectures

* Investigate generational and incremental garbage collection

* Study instruction dispatch optimisations

* Investigate additional VM-level optimisations

## Language Extensions

* Module/import system

* Lists, maps, and sets

* Exception handling

* Anonymous functions

* Pattern matching

* Optional static typing experiments

* Additional native library functions

## Tooling

* Interactive debugger

* Memory visualiser

* Extended GC diagnostics

* Interactive profiling dashboard

---

# Skills Demonstrated

* Systems Programming in C

* Compiler Construction

* Bytecode Generation

* Virtual Machine Design

* Runtime Systems

* Stack Machine Architecture

* Parsing Algorithms

* Dynamic Typing

* Object-Oriented Runtime Design

* Closures and Lexical Scoping

* Garbage Collection

* Memory Management

* Hash Tables

* Performance Profiling

* Benchmark Design

* Statistical Analysis

* Data Visualisation

* Experimental Evaluation

* Software Architecture

---

V2 Expanded Experimental Dataset

The original V1 benchmark suite established the initial profiling framework and provided a controlled baseline for studying clox runtime behaviour. The experiment was subsequently expanded into a substantially larger V2 dataset to increase workload diversity, input-size coverage, and statistical robustness.

The V2 dataset contains:

12 benchmark workloads

20 workload-specific input sizes

40 repetitions per benchmark configuration

240 benchmark × input-size configurations

9,600 total program executions

The same runtime profiling framework is used for every execution, recording execution time, compilation time, opcode execution count, opcode frequency, garbage-collection activity, peak heap usage, total allocation, and total deallocation.

The V2 experiment therefore expands the original 160-run dataset into a much broader experimental population while preserving the same core measurement methodology.

V2 Experimental Methodology

The V2 experiment evaluates the VM across multiple workload structures and multiple scales rather than relying on a single benchmark or input size.

Input sizes were selected using approximately logarithmic/geometric spacing where practical. This provides coverage across multiple orders of magnitude while keeping the total number of experimental configurations manageable.

The rationale is:

Small inputs expose fixed startup and measurement overhead.

Intermediate inputs show the transition into sustained execution.

Large inputs make the runtime signal substantially larger than fixed measurement overhead.

Logarithmic/geometric spacing provides broad scale coverage without requiring every integer input size to be tested.

Computationally explosive workloads, particularly recursion, use smaller ranges because their execution cost grows extremely rapidly.

The input-size sequence is therefore workload-specific rather than forcing every benchmark to use exactly the same values.

Each benchmark × input-size configuration is executed 40 times, allowing both average behaviour and run-to-run variability to be studied.

The overall experimental structure is:

Benchmark Workload
       │
       ▼
Multiple Input Sizes
       │
       ▼
40 Repeated Executions
       │
       ▼
Runtime Profiling
       │
       ├── Execution Time
       ├── Compilation Time
       ├── Opcode Count
       ├── Opcode Frequency
       ├── GC Count
       ├── GC Time
       ├── Peak Heap Usage
       ├── Bytes Allocated
       └── Bytes Freed
       │
       ▼
Aggregated Experimental Dataset
       │
       ▼
Scaling + Variability + Runtime Analysis

Relationship Between V1 and V2

V1 and V2 serve complementary purposes.

The original V1 experiment contains:

8 workloads
32 configurations
5 repetitions per configuration
160 total executions

V1 established the profiling infrastructure, benchmark methodology, scaling analysis, opcode analysis, garbage-collection measurements, and variability analysis.

V2 expands the experiment to:

12 workloads
240 configurations
40 repetitions per configuration
9,600 total executions

The original 160-run suite therefore serves as the initial controlled reference/baseline, while V2 provides a substantially broader dataset for testing whether the observed runtime behaviour remains visible across more diverse workloads and repeated measurements.

The V2 dataset is an expansion of the original experiment rather than a replacement for it.

V2 Findings

The expanded dataset reinforces a central observation from the original experiment:

Execution time and opcode count alone are not sufficient to explain VM performance.

Different workloads can produce very different relationships between:

Input Size
     │
     ├── Opcode Count
     │
     ├── Execution Time
     │
     ├── Allocation
     │
     ├── Garbage Collection
     │
     └── Memory Reclamation

The V2 measurements therefore support analysing instruction activity together with memory-management behaviour and workload structure.

A workload that executes more bytecode is not necessarily slower by the same proportion as another workload with a similar increase in instruction count. The cost of individual runtime paths, allocation behaviour, garbage collection, and the particular instruction mix all contribute to observed execution time.

V2 String Concatenation Observation

One of the most notable observations in the expanded V2 dataset occurs in the string-concatenation workload.

For the compared input sizes, the observed metrics increase at substantially different rates:

Metric                    Approximate Increase

Opcode executions         ≈ 10×
Execution time            ≈ 46.6×
Bytes allocated            ≈ 98×
Bytes freed                ≈ 99×
GC count                   ≈ 48×

The measured runtime cost per million executed bytecodes therefore increases by approximately 4.67× between the compared workloads.

This is significant because it demonstrates that bytecode count is not, by itself, a complete proxy for runtime cost.

The simultaneous increases in allocation, memory reclamation, and garbage-collection activity indicate a strong association between the string workload and memory-management behaviour. These measurements do not, by themselves, establish causality or identify one internal operation as solely responsible for the additional runtime cost.

The observation therefore provides a concrete target for future fine-grained instrumentation of string operations, allocation paths, garbage collection, and instruction dispatch.

What the V2 Dataset Indicates

The expanded dataset provides evidence for several broader conclusions about the measured clox runtime:

Workload structure matters. Different language features generate different instruction mixes and runtime behaviours.

Opcode count is useful but incomplete. It measures the amount of interpreted bytecode work, but not the full cost associated with every runtime operation.

Memory behaviour can strongly affect execution cost. Allocation and garbage collection can grow much faster than instruction count for particular workloads.

Repeated measurements are important. Forty repetitions per configuration provide a stronger basis for examining variability than the original five-run V1 dataset.

Input-size selection matters. Logarithmic/geometric spacing makes it possible to observe behaviour across several scales without requiring an impractically large number of configurations.

Different optimisation opportunities may exist for different workloads. A workload dominated by global access, allocation, closures, dispatch, or strings may require a different optimisation strategy.

The V2 experiment therefore shifts the project from simply measuring whether a program is fast or slow toward analysing which runtime behaviours accompany the observed performance.

V2 Data Quality and Reproducibility

The V2 dataset was generated systematically using the instrumented clox runtime rather than through manually selected individual executions.

Every benchmark configuration follows the same profiling procedure, with repeated runs providing multiple observations for the same workload and input size.

This supports:

Scaling analysis

Repetition-level variability analysis

Workload comparison

Opcode-frequency analysis

Memory-allocation analysis

Garbage-collection analysis

Cross-metric comparison

The raw executions and processed datasets can be retained independently, allowing later analyses to be performed without modifying the VM or rerunning the complete benchmark suite.

V2 Future Research Directions

The V2 results provide several concrete directions for further experimentation.

Fine-Grained Runtime Instrumentation

The current profiler records aggregate opcode and memory behaviour. Future instrumentation can break down individual runtime paths, particularly for string concatenation, object allocation, hash-table operations, method dispatch, closure access, and garbage collection.

String Runtime Optimisation

The string-concatenation observation motivates investigation of temporary string creation, copying costs, allocation frequency, string interning, and interaction with garbage collection.

Garbage Collection Experiments

The expanded allocation measurements provide a basis for experiments involving GC thresholds, allocation policies, generational collection, incremental collection, and reduced temporary-object creation.

Instruction Dispatch

Alternative opcode-dispatch mechanisms, including threaded/computed-goto dispatch, can be evaluated using the same benchmark methodology. This would allow dispatch overhead to be studied independently from the workload-level effects already observed.

Cross-VM Comparison

The same workload-oriented methodology could eventually be applied to other bytecode interpreters or virtual machines, enabling comparison of instruction counts, execution time, memory behaviour, garbage collection, dispatch mechanisms, and workload-specific scaling.

# Acknowledgements

The Lox programming language, virtual machine architecture, and implementation strategy were originally designed by **Bob Nystrom** in his outstanding book **Crafting Interpreters**.

This repository is my own implementation developed by carefully studying, implementing, testing, profiling, and analysing the concepts presented throughout the book. I am deeply grateful to Bob Nystrom for creating one of the most approachable and insightful resources on programming language implementation, which inspired this exploration of compiler and virtual machine design.