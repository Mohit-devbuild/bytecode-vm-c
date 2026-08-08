#include <stdio.h>
#include "profiler.h"
#include "debug.h"

void initProfiler(Profiler* profiler) {
  profiler->executionTime = 0.0;
  profiler->executionStart = 0;

  profiler->compilationTime = 0.0;
  profiler->compilationStart = 0;

  profiler->opcodeCount = 0;

  for (int i = 0; i < OP_COUNT; i++) {
    profiler->opcodeFrequency[i] = 0;
  }

  profiler->gcCount = 0;

  profiler->gcStart = 0;
  profiler->gcTime = 0.0;

  profiler->peakHeapUsage = 0;
  profiler->totalBytesAllocated = 0;
  profiler->totalBytesFreed = 0;
}

void startExecutionTimer(Profiler* profiler) {
  profiler->executionStart = clock();
}

void stopExecutionTimer(Profiler* profiler) {
  clock_t executionEnd = clock();

  profiler->executionTime =
      (double)(executionEnd - profiler->executionStart) /
      CLOCKS_PER_SEC;
}

void startCompilationTimer(Profiler* profiler) {
  profiler->compilationStart = clock();
}

void stopCompilationTimer(Profiler* profiler) {
  clock_t compilationEnd = clock();

  profiler->compilationTime =
      (double)(compilationEnd - profiler->compilationStart) /
      CLOCKS_PER_SEC;
}

void printProfilerReport(const Profiler* profiler) {
  printf("\n========== CLOX PROFILER ==========\n");
  printf("Compilation time: %.3f ms\n",profiler->compilationTime * 1000.0);
  printf("Execution time: %.3f ms\n",profiler->executionTime * 1000.0);
  printf("Opcode executions: %llu\n",(unsigned long long)profiler->opcodeCount);
  printf("GC count: %llu\n",(unsigned long long)profiler->gcCount);
  printf("GC time: %.3f ms\n",profiler->gcTime * 1000.0);
  printf("Peak heap usage: %zu bytes\n",profiler->peakHeapUsage);
  printf("Total bytes allocated: %zu bytes\n",profiler->totalBytesAllocated);
  printf("Total bytes freed: %zu bytes\n",profiler->totalBytesFreed);
  printf("\n----- Instruction Frequency -----\n");

  for (int i = 0; i < OP_COUNT; i++) {
    if (profiler->opcodeFrequency[i] > 0) {
      printf("%-20s %llu\n",
             opcodeName((OpCode)i),
             (unsigned long long)profiler->opcodeFrequency[i]);
    }
  }
  printf("===================================\n");
}