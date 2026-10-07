
# ============================================================
# clox Dataset v3 Benchmark Runner
# ============================================================

$ErrorActionPreference = "Stop"

$RootDir      = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Clox         = Join-Path $RootDir "build\\clox.exe"
$BenchmarkDir = Join-Path $RootDir "dataset_v2\\programs"
$v3Dir        = Join-Path $RootDir "dataset_v3"
$ResultsDir   = Join-Path $v3Dir "results"
$CsvPath      = Join-Path $ResultsDir "dataset_v3.csv"
$TempFile     = Join-Path $ResultsDir "_current_run.lox"

$Repetitions = 40

$Benchmarks = [ordered]@{
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

$TotalRuns = 0
foreach ($BenchmarkName in $Benchmarks.Keys) {
    $TotalRuns += $Benchmarks[$BenchmarkName].Count * $Repetitions
}

Write-Host "============================================================"
Write-Host " clox Dataset v3 Benchmark Runner"
Write-Host "============================================================"

if (-not (Test-Path -LiteralPath $Clox)) {
    throw "clox executable not found: $Clox"
}

New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null

function ConvertTo-CsvField {
    param([AllowNull()][object]$Value)
    if ($null -eq $Value) { return '""' }
    $Text = [string]$Value
    $Text = $Text.Replace('"', '""')
    return '"' + $Text + '"'
}

function Append-CsvLineWithRetry {
    param([string]$Path, [string]$Line)
    $Encoding = New-Object System.Text.UTF8Encoding($false)
    for ($Attempt = 1; $Attempt -le 10; $Attempt++) {
        try {
            [System.IO.File]::AppendAllText($Path, $Line + "`r`n", $Encoding)
            return
        } catch {
            if ($Attempt -eq 10) { throw "Failed: $($_.Exception.Message)" }
            Start-Sleep -Milliseconds 500
        }
    }
}

$Header = "run_order,timestamp,benchmark,n,rep,wall_ms,compile_ms,exec_ms,opcodes,gc_count,gc_ms,peak_heap_bytes,bytes_allocated,bytes_freed,output,opcode_counts"

if (-not (Test-Path -LiteralPath $CsvPath)) {
    [System.IO.File]::WriteAllText($CsvPath, $Header + "`r`n", (New-Object System.Text.UTF8Encoding($false)))
}

$Completed = @{}
if (Test-Path -LiteralPath $CsvPath) {
    $ExistingRows = @(Import-Csv -LiteralPath $CsvPath)
    foreach ($Row in $ExistingRows) {
        if ($null -ne $Row.benchmark -and $null -ne $Row.n -and $null -ne $Row.rep) {
            $Key = "$($Row.benchmark)|$($Row.n)|$($Row.rep)"
            $Completed[$Key] = $true
        }
    }
}

$Plan = New-Object System.Collections.Generic.List[object]
$RunOrder = 0

foreach ($BenchmarkName in $Benchmarks.Keys) {
    foreach ($N in $Benchmarks[$BenchmarkName]) {
        for ($Rep = 1; $Rep -le $Repetitions; $Rep++) {
            $RunOrder++
            $Plan.Add([PSCustomObject]@{RunOrder=$RunOrder; Benchmark=$BenchmarkName; N=$N; Rep=$Rep})
        }
    }
}

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

try {
    foreach ($Run in $Plan) {
        $CompletedKey = "$($Run.Benchmark)|$($Run.N)|$($Run.Rep)"
        if ($Completed.ContainsKey($CompletedKey)) { continue }

        $SourcePath = Join-Path $BenchmarkDir "$($Run.Benchmark).lox"
        $Source = [System.IO.File]::ReadAllText($SourcePath, $Utf8NoBom)
        $InjectedSource = "var n = $($Run.N);`r`n" + $Source

        [System.IO.File]::WriteAllText($TempFile, $InjectedSource, $Utf8NoBom)

        Write-Host ("Run {0}/{1} | {2} | N={3} | rep={4} ... " -f $Run.RunOrder, $TotalRuns, $Run.Benchmark, $Run.N, $Run.Rep) -NoNewline

        $Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            $OutputLines = @(& $Clox $TempFile 2>&1)
            $ExitCode = $LASTEXITCODE
        } catch {
            throw "Execution failed"
        }
        $Stopwatch.Stop()

        if ($ExitCode -ne 0) { throw "Benchmark failed" }

        $RawOutput = ($OutputLines -join "`r`n")
        $CompileMs = 0.0; $ExecMs = 0.0; $Opcodes = 0; $GcCount = 0; $GcMs = 0.0
        $PeakHeapBytes = 0; $BytesAllocated = 0; $BytesFreed = 0

        if ($RawOutput -match '(?im)Compilation time:\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|s)') { $CompileMs = [double]$Matches[1]; if ($Matches[2] -like "s*") { $CompileMs *= 1000.0 } }
        if ($RawOutput -match '(?im)Execution time:\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|s)') { $ExecMs = [double]$Matches[1]; if ($Matches[2] -like "s*") { $ExecMs *= 1000.0 } }
        if ($RawOutput -match '(?im)Opcode executions:\s*([0-9]+)') { $Opcodes = [long]$Matches[1] }
        if ($RawOutput -match '(?im)GC count:\s*([0-9]+)') { $GcCount = [long]$Matches[1] }
        if ($RawOutput -match '(?im)GC time:\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|s)') { $GcMs = [double]$Matches[1]; if ($Matches[2] -like "s*") { $GcMs *= 1000.0 } }
        if ($RawOutput -match '(?im)Peak heap usage:\s*([0-9]+)\s*bytes') { $PeakHeapBytes = [long]$Matches[1] }
        if ($RawOutput -match '(?im)Total bytes allocated:\s*([0-9]+)') { $BytesAllocated = [long]$Matches[1] }
        if ($RawOutput -match '(?im)Total bytes freed:\s*([0-9]+)') { $BytesFreed = [long]$Matches[1] }

        $ProgramLines = New-Object System.Collections.Generic.List[string]
        $OpcodeEntries = New-Object System.Collections.Generic.List[string]

        foreach ($Line in $OutputLines) {
            $Text = [string]$Line
            if ($Text -match '^\s*(O|[A-Z_]+)[\s:=]+([0-9]+)\s*$') { $OpcodeEntries.Add("$($Matches[1])=$($Matches[2])"); continue }
            if ($Text -match '^\s*$' -or $Text -match '^(=+|-+)$' -or $Text -match '^\s*Profiler' -or $Text -match ':\s*([0-9]+)') { continue }
            $ProgramLines.Add($Text)
        }

        $CsvFields = @(
            $Run.RunOrder, (Get-Date).ToString("o"), $Run.Benchmark, $Run.N, $Run.Rep,
            [math]::Round($Stopwatch.Elapsed.TotalMilliseconds, 3), [math]::Round($CompileMs, 3), [math]::Round($ExecMs, 3),
            $Opcodes, $GcCount, [math]::Round($GcMs, 3), $PeakHeapBytes, $BytesAllocated, $BytesFreed,
            ($ProgramLines -join " ").Trim(), ($OpcodeEntries -join ";")
        )

        $CsvLine = ($CsvFields | ForEach-Object { ConvertTo-CsvField $_ }) -join ","
        Append-CsvLineWithRetry -Path $CsvPath -Line $CsvLine
        $Completed[$CompletedKey] = $true

        Write-Host ("OK | exec={0:F3} ms | GC={1}" -f $ExecMs, $GcCount) -ForegroundColor Green
        Start-Sleep -Milliseconds 100
    }
} finally {
    if (Test-Path -LiteralPath $TempFile) { Remove-Item -LiteralPath $TempFile -Force -ErrorAction SilentlyContinue }
}
