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
               │     Scanner     │
               └─────────────────┘
                        │
                     Tokens
                        │
                        ▼
               ┌─────────────────┐
               │  Pratt Parser   │
               └─────────────────┘
                        │
                        ▼
          Single-pass Bytecode Compiler
                        │
                        ▼
               ┌─────────────────┐
               │ Bytecode Chunk  │
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
        │    Value     │
        ├──────────────┤
        │    Value     │
        ├──────────────┤
        │    Value     │
        ├──────────────┤
        │    Value     │
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

| Benchmark     | Primary Runtime Behaviour                 |
| ------------- | ----------------------------------------- |
| `allocation`  | Heap allocation and garbage collection    |
| `arithmetic`  | Arithmetic operations and global access   |
| `closures`    | Closure creation and upvalue access       |
| `functions`   | Function calls and local/global access    |
| `inheritance` | Classes, inheritance, and method dispatch |
| `loops`       | Repeated control-flow execution           |
| `objects`     | Instance and property operations          |
| `recursion`   | Deep function-call recursion              |

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
allocation     k ≈ 1.00
arithmetic     k ≈ 1.00
closures       k ≈ 1.00
functions      k ≈ 1.00
inheritance    k ≈ 1.00
loops          k ≈ 1.00
objects        k ≈ 1.00
```

The corresponding power-law fits have R² values effectively equal to 1 for these workloads.

This confirms that the dominant bytecode execution work grows proportionally with the benchmark workload for these programs.

---

## 2. Recursion exhibits fundamentally different scaling

The recursive benchmark behaves very differently.

Power-law fitting produced approximately:

```text
Time exponent     k ≈ 12.08
Opcode exponent   k ≈ 12.84
```

However, an exponential model provides a slightly better fit for the measured recursive workload:

```text
Exponential R² ≈ 0.996
Power-law R²    ≈ 0.992
```

The rapidly increasing number of recursive calls therefore dominates execution cost.

The VM executes approximately:

```text
N = 20  →       284,588 opcodes
N = 25  →     3,156,210 opcodes
N = 30  →    35,002,986 opcodes
N = 35  →   388,189,144 opcodes
```

This provides a concrete demonstration of how algorithmic behaviour at the language level directly manifests as instruction-level workload inside the VM.

---

## 3. Global access is a major component of the instruction mix

Across the complete benchmark corpus, the most frequently executed instructions were:

| Rank | Opcode             |  Share |
| ---: | ------------------ | -----: |
|    1 | `OP_GET_GLOBAL`    | 17.65% |
|    2 | `OP_CONSTANT`      | 14.24% |
|    3 | `OP_POP`           | 14.19% |
|    4 | `OP_GET_LOCAL`     |  7.87% |
|    5 | `OP_SET_GLOBAL`    |  7.40% |
|    6 | `OP_ADD`           |  6.23% |
|    7 | `OP_JUMP_IF_FALSE` |  6.21% |

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
Input        GC Cycles
1,000             0
10,000          300
100,000       8,481
1,000,000    90,300
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
Total freed     ≈ 156 MB
Peak heap       ≈ 1.05 MB
```

The distinction between **cumulative allocation** and **live heap size** is particularly important when evaluating garbage-collected runtimes.

---

## 6. Runtime variability decreases for larger workloads

Small workloads show substantial timing variability because fixed system and measurement overhead becomes large relative to actual execution time.

Several small-input configurations exhibit high coefficients of variation, with some 1,000-operation configurations exceeding 100%.

As workloads become larger, the measurements become considerably more stable.

Representative larger workloads include:

```text
arithmetic 10,000,000    CV ≈ 4.68%
loops      10,000,000    CV ≈ 3.73%
inheritance 1,000,000    CV ≈ 2.87%
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
│   ├── analyze_opcodes.py
│   ├── analyze_variability.py
│   └── make_graphs.py
│
├── benchmarks/
│   ├── allocation.lox
│   ├── arithmetic.lox
│   ├── closures.lox
│   ├── functions.lox
│   ├── inheritance.lox
│   ├── loops.lox
│   ├── objects.lox
│   └── recursion.lox
│
├── build/
│   └── clox.exe
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
    │   ├── benchmark_comparison.png
    │   ├── execution_time_scaling.png
    │   ├── gc_behavior.png
    │   ├── memory_behavior.png
    │   ├── opcode_composition.png
    │   ├── opcode_scaling.png
    │   ├── recursion_scaling.png
    │   └── variability.png
    │
    ├── opcode_analysis/
    │   ├── benchmark_opcode_profile_v1.csv
    │   ├── opcode_ranking_v1.csv
    │   ├── opcode_totals_v1.csv
    │   └── top_opcodes_v1.csv
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

# Acknowledgements

The Lox programming language, virtual machine architecture, and implementation strategy were originally designed by **Bob Nystrom** in his outstanding book **Crafting Interpreters**.

This repository is my own implementation developed by carefully studying, implementing, testing, profiling, and analysing the concepts presented throughout the book. I am deeply grateful to Bob Nystrom for creating one of the most approachable and insightful resources on programming language implementation, which inspired this exploration of compiler and virtual machine design.
