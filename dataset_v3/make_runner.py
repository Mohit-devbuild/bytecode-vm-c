raw_ps1 = r"""
# ============================================================
# clox Dataset v3 Benchmark Runner
# ============================================================

D_ErrorActionPreference = "Stop"

D_RootDir      = (Resolve-Path (Join-Path D_PSScriptRoot "..")).Path
D_Clox         = Join-Path D_RootDir "build\\clox.exe"
D_BenchmarkDir = Join-Path D_RootDir "dataset_v2\\programs"
D_v3Dir        = Join-Path D_RootDir "dataset_v3"
D_ResultsDir   = Join-Path D_v3Dir "results"
D_CsvPath      = Join-Path D_ResultsDir "dataset_v3.csv"
D_TempFile     = Join-Path D_ResultsDir "_current_run.lox"

D_Repetitions = 40

D_Benchmarks = [ordered]@{
    "arithmetic" = @(40000, 49100, 60400, 74200, 91100, 112000, 138000, 169000, 208000, 255000, 314000, 385000, 473000, 581000, 714000, 878000, 1080000, 1320000, 1630000, 2000000)
    "classes" = @(12000, 14700, 18100, 22300, 27300, 33600, 41300, 50700, 62300, 76600, 94100, 116000, 142000, 174000, 214000, 263000, 324000, 397000, 488000, 600000)
    "closures" = @(14000, 17200, 21100, 26000, 31900, 39200, 48200, 59200, 72700, 89300, 110000, 135000, 166000, 204000, 250000, 307000, 377000, 464000, 570000, 700000)
    "control_flow" = @(20000, 24600, 30200, 37100, 45600, 56000, 68800, 84500, 104000, 128000, 157000, 193000, 237000, 291000, 357000, 439000, 539000, 662000, 814000, 1000000)
    "gc_stress" = @(6000, 7370, 9060, 11100, 13700, 16800, 20600, 25400, 31200, 38300, 47000, 57800, 71000, 87200, 107000, 132000, 162000, 199000, 244000, 300000)
    "globals" = @(14000, 17200, 21100, 26000, 31900, 39200, 48200, 59200, 72700, 89300, 110000, 135000, 166000, 204000, 250000, 307000, 377000, 464000, 570000, 700000)
    "integrated" = @(8000, 9830, 12100, 14800, 18200, 22400, 27500, 33800, 41500, 51000, 62700, 77000, 94700, 116000, 143000, 176000, 216000, 265000, 326000, 400000)
    "locals" = @(28000, 34400, 42300, 51900, 63800, 78400, 96300, 118000, 145000, 179000, 219000, 270000, 331000, 407000, 500000, 614000, 755000, 927000, 1140000, 1400000)
    "methods" = @(16000, 19700, 24200, 29700, 36500, 44800, 55000, 67600, 83100, 102000, 125000, 154000, 189000, 233000, 286000, 351000, 431000, 530000, 651000, 800000)
    "properties" = @(16000, 19700, 24200, 29700, 36500, 44800, 55000, 67600, 83100, 102000, 125000, 154000, 189000, 233000, 286000, 351000, 431000, 530000, 651000, 800000)
    "recursion" = @(12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31)
    "string_concat" = @(2500, 2820, 3190, 3600, 4060, 4580, 5170, 5840, 6590, 7440, 8400, 9480, 10700, 12100, 13600, 15400, 17400, 19600, 22100, 25000)
}

D_TotalRuns = 0
foreach (D_BenchmarkName in D_Benchmarks.Keys) {
    D_TotalRuns += D_Benchmarks[D_BenchmarkName].Count * D_Repetitions
}

Write-Host "============================================================"
Write-Host " clox Dataset v3 Benchmark Runner"
Write-Host "============================================================"

if (-not (Test-Path -LiteralPath D_Clox)) {
    throw "clox executable not found: D_Clox"
}

New-Item -ItemType Directory -Force -Path D_ResultsDir P_ Out-Null

function ConvertTo-CsvField {
    param([AllowNull()][object]D_Value)
    if (D_null -eq D_Value) { return '""' }
    D_Text = [string]D_Value
    D_Text = D_Text.Replace('"', '""')
    return '"' + D_Text + '"'
}

function Append-CsvLineWithRetry {
    param([string]D_Path, [string]D_Line)
    D_Encoding = New-Object System.Text.UTF8Encoding(D_false)
    for (D_Attempt = 1; D_Attempt -le 10; D_Attempt++) {
        try {
            [System.IO.File]::AppendAllText(D_Path, D_Line + "`r`n", D_Encoding)
            return
        } catch {
            if (D_Attempt -eq 10) { throw "Failed: D_(D__.Exception.Message)" }
            Start-Sleep -Milliseconds 500
        }
    }
}

D_Header = "run_order,timestamp,benchmark,n,rep,wall_ms,compile_ms,exec_ms,opcodes,gc_count,gc_ms,peak_heap_bytes,bytes_allocated,bytes_freed,output,opcode_counts"

if (-not (Test-Path -LiteralPath D_CsvPath)) {
    [System.IO.File]::WriteAllText(D_CsvPath, D_Header + "`r`n", (New-Object System.Text.UTF8Encoding(D_false)))
}

D_Completed = @{}
if (Test-Path -LiteralPath D_CsvPath) {
    D_ExistingRows = @(Import-Csv -LiteralPath D_CsvPath)
    foreach (D_Row in D_ExistingRows) {
        if (D_null -ne D_Row.benchmark -and D_null -ne D_Row.n -and D_null -ne D_Row.rep) {
            D_Key = "D_(D_Row.benchmark)P_D_(D_Row.n)P_D_(D_Row.rep)"
            D_Completed[D_Key] = D_true
        }
    }
}

D_Plan = New-Object System.Collections.Generic.List[object]
D_RunOrder = 0

foreach (D_BenchmarkName in D_Benchmarks.Keys) {
    foreach (D_N in D_Benchmarks[D_BenchmarkName]) {
        for (D_Rep = 1; D_Rep -le D_Repetitions; D_Rep++) {
            D_RunOrder++
            D_Plan.Add([PSCustomObject]@{RunOrder=D_RunOrder; Benchmark=D_BenchmarkName; N=D_N; Rep=D_Rep})
        }
    }
}

D_Utf8NoBom = New-Object System.Text.UTF8Encoding(D_false)

try {
    foreach (D_Run in D_Plan) {
        D_CompletedKey = "D_(D_Run.Benchmark)P_D_(D_Run.N)P_D_(D_Run.Rep)"
        if (D_Completed.ContainsKey(D_CompletedKey)) { continue }

        D_SourcePath = Join-Path D_BenchmarkDir "D_(D_Run.Benchmark).lox"
        D_Source = [System.IO.File]::ReadAllText(D_SourcePath, D_Utf8NoBom)
        D_InjectedSource = "var n = D_(D_Run.N);`r`n" + D_Source

        [System.IO.File]::WriteAllText(D_TempFile, D_InjectedSource, D_Utf8NoBom)

        Write-Host ("Run {0}/{1} P_ {2} P_ N={3} P_ rep={4} ... " -f D_Run.RunOrder, D_TotalRuns, D_Run.Benchmark, D_Run.N, D_Run.Rep) -NoNewline

        D_Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            D_OutputLines = @(& D_Clox D_TempFile 2>&1)
            D_ExitCode = D_LASTEXITCODE
        } catch {
            throw "Execution failed"
        }
        D_Stopwatch.Stop()

        if (D_ExitCode -ne 0) { throw "Benchmark failed" }

        D_RawOutput = (D_OutputLines -join "`r`n")
        D_CompileMs = 0.0; D_ExecMs = 0.0; D_Opcodes = 0; D_GcCount = 0; D_GcMs = 0.0
        D_PeakHeapBytes = 0; D_BytesAllocated = 0; D_BytesFreed = 0

        if (D_RawOutput -match '(?im)Compilation time:\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|s)') { D_CompileMs = [double]D_Matches[1]; if (D_Matches[2] -like "s*") { D_CompileMs *= 1000.0 } }
        if (D_RawOutput -match '(?im)Execution time:\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|s)') { D_ExecMs = [double]D_Matches[1]; if (D_Matches[2] -like "s*") { D_ExecMs *= 1000.0 } }
        if (D_RawOutput -match '(?im)Opcode executions:\s*([0-9]+)') { D_Opcodes = [long]D_Matches[1] }
        if (D_RawOutput -match '(?im)GC count:\s*([0-9]+)') { D_GcCount = [long]D_Matches[1] }
        if (D_RawOutput -match '(?im)GC time:\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|s)') { D_GcMs = [double]D_Matches[1]; if (D_Matches[2] -like "s*") { D_GcMs *= 1000.0 } }
        if (D_RawOutput -match '(?im)Peak heap usage:\s*([0-9]+)\s*bytes') { D_PeakHeapBytes = [long]D_Matches[1] }
        if (D_RawOutput -match '(?im)Total bytes allocated:\s*([0-9]+)') { D_BytesAllocated = [long]D_Matches[1] }
        if (D_RawOutput -match '(?im)Total bytes freed:\s*([0-9]+)') { D_BytesFreed = [long]D_Matches[1] }

        D_ProgramLines = New-Object System.Collections.Generic.List[string]
        D_OpcodeEntries = New-Object System.Collections.Generic.List[string]

        foreach (D_Line in D_OutputLines) {
            D_Text = [string]D_Line
            if (D_Text -match '^\s*(OP_[A-Z_]+)[\s:=]+([0-9]+)\s*D_') { D_OpcodeEntries.Add("D_(D_Matches[1])=D_(D_Matches[2])"); continue }
            if (D_Text -match '^\s*D_' -or D_Text -match '^(=+|-+)D_' -or D_Text -match '^\s*Profiler' -or D_Text -match ':\s*([0-9]+)') { continue }
            D_ProgramLines.Add(D_Text)
        }

        D_CsvFields = @(
            D_Run.RunOrder, (Get-Date).ToString("o"), D_Run.Benchmark, D_Run.N, D_Run.Rep,
            [math]::Round(D_Stopwatch.Elapsed.TotalMilliseconds, 3), [math]::Round(D_CompileMs, 3), [math]::Round(D_ExecMs, 3),
            D_Opcodes, D_GcCount, [math]::Round(D_GcMs, 3), D_PeakHeapBytes, D_BytesAllocated, D_BytesFreed,
            (D_ProgramLines -join " ").Trim(), (D_OpcodeEntries -join ";")
        )

        D_CsvLine = (D_CsvFields P_ ForEach-Object { ConvertTo-CsvField D__ }) -join ","
        Append-CsvLineWithRetry -Path D_CsvPath -Line D_CsvLine
        D_Completed[D_CompletedKey] = D_true

        Write-Host ("OK P_ exec={0:F3} ms P_ GC={1}" -f D_ExecMs, D_GcCount) -ForegroundColor Green
        Start-Sleep -Milliseconds 100
    }
} finally {
    if (Test-Path -LiteralPath D_TempFile) { Remove-Item -LiteralPath D_TempFile -Force -ErrorAction SilentlyContinue }
}
"""

# Re-injects proper characters to bypass chat formatting
script = raw_ps1.replace("D_", chr(36)).replace("P_", chr(124))

with open("run_benchmarks_v3.ps1", "w", encoding="utf-8") as f:
    f.write(script)
print("SUCCESS: run_benchmarks_v3.ps1 has been correctly generated!")