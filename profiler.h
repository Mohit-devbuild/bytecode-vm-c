#ifndef clox_profiler_h
#define clox_profiler_h

#include <time.h>

typedef struct {
  double executionTime;
  clock_t executionStart;
} Profiler;

void initProfiler(Profiler* profiler);
void startExecutionTimer(Profiler* profiler);
void stopExecutionTimer(Profiler* profiler);
void printProfilerReport(const Profiler* profiler);

#endif