# clox — A Bytecode Virtual Machine for the Lox Programming Language

A complete implementation of **clox**, a high-performance bytecode virtual machine for the Lox programming language written in **C**.

This project demonstrates the complete implementation of a dynamically typed programming language, including lexical analysis, parsing, bytecode compilation, virtual machine execution, object-oriented programming, closures, garbage collection, and memory management.

Unlike a tree-walk interpreter, `clox` compiles source code into bytecode which is then executed by a stack-based virtual machine, providing significantly better runtime performance while maintaining a compact implementation.

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
* REPL
* Script Execution

---

# Architecture

```
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

The compiler performs parsing and code generation simultaneously, producing compact bytecode instructions executed directly by the virtual machine.

---

# Virtual Machine Overview

The VM executes bytecode using a value stack.

```
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

The virtual machine manages:

* Operand stack
* Call frames
* Closures
* Upvalues
* Global variables
* Object allocation
* Automatic garbage collection

---

# Memory Management

Memory is managed automatically using a **mark-and-sweep garbage collector**.

```
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

Objects are allocated dynamically and reclaimed automatically once they become unreachable.

The implementation also includes:

* Object graph traversal
* String interning
* Object tables
* Automatic heap growth
* Debug garbage collection support
* Stress GC mode

---

# Repository Structure

```
clox/
│
├── chunk.c
├── chunk.h
├── common.h
├── compiler.c
├── compiler.h
├── debug.c
├── debug.h
├── main.c
├── Makefile
├── memory.c
├── memory.h
├── object.c
├── object.h
├── scanner.c
├── scanner.h
├── table.c
├── table.h
├── value.c
├── value.h
├── vm.c
├── vm.h
│
├── build/
└── README.md
```

---

# Building

Requirements

* GCC
* GNU Make (or MinGW Make on Windows)

Compile:

```bash
mingw32-make
```

The executable will be generated inside:

```
build/clox.exe
```

---

# Running

Interactive REPL

```bash
./build/clox.exe
```

Run a script

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

Output

```
120
generic
woof
```

---

# Implemented Components

## Front End

* Scanner
* Tokeniser
* Pratt Parser
* Bytecode Compiler

## Runtime

* Bytecode Interpreter
* Virtual Machine
* Value Stack
* Call Frames
* Closures
* Upvalues

## Object System

* Strings
* Functions
* Closures
* Classes
* Instances
* Bound Methods
* Native Functions

## Memory System

* Heap Allocation
* String Interning
* Hash Tables
* Mark-and-Sweep Garbage Collector

---

# Future Work / TODO

This project serves as a strong foundation for further exploration into virtual machine implementation, compiler construction, and programming language design.

## Performance & VM Research

* Profile interpreter performance and identify execution hotspots
* Benchmark against other bytecode interpreters (e.g. Lua, Python)
* Investigate peephole bytecode optimisations
* Explore constant folding and constant propagation
* Experiment with inline caching for method dispatch
* Evaluate register-based VM designs
* Investigate generational and incremental garbage collection
* Explore alternative string interning strategies
* Study instruction dispatch optimisations
* Build a comprehensive benchmarking suite

## Language Extensions

* Module/import system
* Lists, maps, and sets
* Exception handling
* Anonymous functions
* Pattern matching
* Optional static typing experiments
* Additional native library functions

## Tooling

* Bytecode disassembler improvements
* Interactive debugger
* Execution profiler
* Memory visualiser
* GC statistics and diagnostics

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
* Software Architecture

---

# Acknowledgements

The Lox programming language, virtual machine architecture, and implementation strategy were originally designed by **Bob Nystrom** in his outstanding book **Crafting Interpreters**.

This repository is my own implementation developed by carefully studying, implementing, testing, and understanding the concepts presented throughout the book. I am deeply grateful to Bob Nystrom for creating one of the most approachable, insightful, and influential resources on programming language implementation, which has inspired countless developers to explore compiler and virtual machine design.
