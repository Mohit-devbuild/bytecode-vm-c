#ifndef clox_profiler_h
#define clox_profiler_h
#include <stdint.h>
#include <time.h>

typedef struct {
  double executionTime;
  clock_t executionStart;

  double compilationTime;
  clock_t compilationStart;

  uint64_t opcodeCount;
} Profiler;

void initProfiler(Profiler* profiler);

void startExecutionTimer(Profiler* profiler);
void stopExecutionTimer(Profiler* profiler);

void startCompilationTimer(Profiler* profiler);
void stopCompilationTimer(Profiler* profiler);

void printProfilerReport(const Profiler* profiler);

#endif