#ifndef clox_profiler_h
#define clox_profiler_h
#include <stdint.h>
#include <time.h>
#include "chunk.h"

typedef struct {
  double executionTime;
  clock_t executionStart;

  double compilationTime;
  clock_t compilationStart;

  uint64_t opcodeCount;
  uint64_t opcodeFrequency[OP_COUNT];

  uint64_t gcCount;
} Profiler;

void initProfiler(Profiler* profiler);

void startExecutionTimer(Profiler* profiler);
void stopExecutionTimer(Profiler* profiler);

void startCompilationTimer(Profiler* profiler);
void stopCompilationTimer(Profiler* profiler);

void printProfilerReport(const Profiler* profiler);

#endif