# ============================================================
# clox Dataset v2 Runner
# 12 workloads x 20 N values x 40 repetitions = 9600 runs
# ============================================================

$ErrorActionPreference = "Stop"

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------

$RootDir      = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Clox         = Join-Path $RootDir "build\clox.exe"
$BenchmarkDir = Join-Path $RootDir "dataset_v2\programs"
$ResultsDir   = Join-Path $RootDir "dataset_v2\results"
$RawDir       = Join-Path $ResultsDir "raw"
$TempDir      = Join-Path $ResultsDir "temp"
$CsvPath      = Join-Path $ResultsDir "dataset_v2.csv"

$Repetitions = 40

# ------------------------------------------------------------
# Benchmark N values
# ------------------------------------------------------------

$Benchmarks = [ordered]@{

    "arithmetic" = @(
        40000, 49100, 60400, 74200, 91100,
        112000, 138000, 169000, 208000, 255000,
        314000, 385000, 473000, 581000, 714000,
        878000, 1080000, 1320000, 1630000, 2000000
    )

    "classes" = @(
        12000, 14700, 18100, 22300, 27300,
        33600, 41300, 50700, 62300, 76600,
        94100, 116000, 142000, 174000, 214000,
        263000, 324000, 397000, 488000, 600000
    )

    "closures" = @(
        14000, 17200, 21100, 26000, 31900,
        39200, 48200, 59200, 72700, 89300,
        110000, 135000, 166000, 204000, 250000,
        307000, 377000, 464000, 570000, 700000
    )

    "control_flow" = @(
        20000, 24600, 30200, 37100, 45600,
        56000, 68800, 84500, 104000, 128000,
        157000, 193000, 237000, 291000, 357000,
        439000, 539000, 662000, 814000, 1000000
    )

    "gc_stress" = @(
        6000, 7370, 9060, 11100, 13700,
        16800, 20600, 25400, 31200, 38300,
        47000, 57800, 71000, 87200, 107000,
        132000, 162000, 199000, 244000, 300000
    )

    "globals" = @(
        14000, 17200, 21100, 26000, 31900,
        39200, 48200, 59200, 72700, 89300,
        110000, 135000, 166000, 204000, 250000,
        307000, 377000, 464000, 570000, 700000
    )

    "integrated" = @(
        8000, 9830, 12100, 14800, 18200,
        22400, 27500, 33800, 41500, 51000,
        62700, 77000, 94700, 116000, 143000,
        176000, 216000, 265000, 326000, 400000
    )

    "locals" = @(
        28000, 34400, 42300, 51900, 63800,
        78400, 96300, 118000, 145000, 179000,
        219000, 270000, 331000, 407000, 500000,
        614000, 755000, 927000, 1140000, 1400000
    )

    "methods" = @(
        16000, 19700, 24200, 29700, 36500,
        44800, 55000, 67600, 83100, 102000,
        125000, 154000, 189000, 233000, 286000,
        351000, 431000, 530000, 651000, 800000
    )

    "properties" = @(
        16000, 19700, 24200, 29700, 36500,
        44800, 55000, 67600, 83100, 102000,
        125000, 154000, 189000, 233000, 286000,
        351000, 431000, 530000, 651000, 800000
    )

    "recursion" = @(
        12, 13, 14, 15, 16,
        17, 18, 19, 20, 21,
        22, 23, 24, 25, 26,
        27, 28, 29, 30, 31
    )

    "string_concat" = @(
        2500, 2820, 3190, 3600, 4060,
        4580, 5170, 5840, 6590, 7440,
        8400, 9480, 10700, 12100, 13600,
        15400, 17400, 19600, 22100, 25000
    )
}

# ------------------------------------------------------------
# Expected total
# ------------------------------------------------------------

$TotalRuns = 0

foreach ($BenchmarkName in $Benchmarks.Keys) {
    $TotalRuns += $Benchmarks[$BenchmarkName].Count * $Repetitions
}

Write-Host ""
Write-Host "============================================================"
Write-Host " clox Dataset v2 Benchmark Runner"
Write-Host "============================================================"
Write-Host "Benchmarks : $($Benchmarks.Count)"
Write-Host "N values   : 20"
Write-Host "Repetitions: $Repetitions"
Write-Host "Total runs : $TotalRuns"
Write-Host "============================================================"
Write-Host ""

# ------------------------------------------------------------
# Validate executable
# ------------------------------------------------------------

if (-not (Test-Path -LiteralPath $Clox)) {
    throw "clox executable not found: $Clox"
}

# ------------------------------------------------------------
# Create directories
# ------------------------------------------------------------

New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
New-Item -ItemType Directory -Force -Path $RawDir | Out-Null
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

# ------------------------------------------------------------
# CSV escaping
# ------------------------------------------------------------

function ConvertTo-CsvField {
    param(
        [AllowNull()]
        [object]$Value
    )

    if ($null -eq $Value) {
        return '""'
    }

    $Text = [string]$Value
    $Text = $Text.Replace('"', '""')

    return '"' + $Text + '"'
}

# ------------------------------------------------------------
# CSV append with retry
# ------------------------------------------------------------

function Append-CsvLineWithRetry {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Line
    )

    $Encoding = New-Object System.Text.UTF8Encoding($false)

    for ($Attempt = 1; $Attempt -le 10; $Attempt++) {
        try {
            [System.IO.File]::AppendAllText(
                $Path,
                $Line + [Environment]::NewLine,
                $Encoding
            )

            return
        }
        catch {
            if ($Attempt -eq 10) {
                throw "Failed to append CSV after 10 attempts: $($_.Exception.Message)"
            }

            Write-Host ""
            Write-Host "CSV temporarily locked. Retry $Attempt/10..." -ForegroundColor Yellow
            Start-Sleep -Milliseconds 500
        }
    }
}

# ------------------------------------------------------------
# Create CSV if necessary
# ------------------------------------------------------------

$Header = "run_order,timestamp,benchmark,n,rep,wall_ms,compile_ms,exec_ms,opcodes,gc_count,gc_ms,peak_heap_bytes,bytes_allocated,bytes_freed,output,opcode_counts"

if (-not (Test-Path -LiteralPath $CsvPath)) {
    [System.IO.File]::WriteAllText(
        $CsvPath,
        $Header + [Environment]::NewLine,
        (New-Object System.Text.UTF8Encoding($false))
    )
}

# ------------------------------------------------------------
# Read already completed runs
# ------------------------------------------------------------

$Completed = @{}

if (Test-Path -LiteralPath $CsvPath) {

    try {
        $ExistingRows = @(Import-Csv -LiteralPath $CsvPath)

        foreach ($Row in $ExistingRows) {

            if (
                $null -ne $Row.benchmark -and
                $null -ne $Row.n -and
                $null -ne $Row.rep
            ) {
                $Key = "$($Row.benchmark)|$($Row.n)|$($Row.rep)"
                $Completed[$Key] = $true
            }
        }
    }
    catch {
        throw "Could not read existing CSV: $($_.Exception.Message)"
    }
}

Write-Host "Already completed: $($Completed.Count) / $TotalRuns"
Write-Host ""

# ------------------------------------------------------------
# Build deterministic plan
# ------------------------------------------------------------

$Plan = New-Object System.Collections.Generic.List[object]

$RunOrder = 0

foreach ($BenchmarkName in $Benchmarks.Keys) {

    foreach ($N in $Benchmarks[$BenchmarkName]) {

        for ($Rep = 1; $Rep -le $Repetitions; $Rep++) {

            $RunOrder++

            $Plan.Add([PSCustomObject]@{
                RunOrder  = $RunOrder
                Benchmark = $BenchmarkName
                N         = $N
                Rep       = $Rep
            })
        }
    }
}

# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------

foreach ($Run in $Plan) {

    $RunOrder      = $Run.RunOrder
    $BenchmarkName = $Run.Benchmark
    $N             = $Run.N
    $Repetition    = $Run.Rep

    $CompletedKey = "$BenchmarkName|$N|$Repetition"

    if ($Completed.ContainsKey($CompletedKey)) {
        continue
    }

    $SourcePath = Join-Path $BenchmarkDir "$BenchmarkName.lox"

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        throw "Benchmark source not found: $SourcePath"
    }

    # --------------------------------------------------------
    # Read original source
    # --------------------------------------------------------

    $Source = [System.IO.File]::ReadAllText(
        $SourcePath,
        (New-Object System.Text.UTF8Encoding($false))
    )

    # --------------------------------------------------------
    # Inject n WITHOUT BOM
    # --------------------------------------------------------

    $InjectedSource = "var n = $N;`r`n" + $Source

    $TempFile = Join-Path $TempDir (
        "${BenchmarkName}_N${N}_run${Repetition}.lox"
    )

    $RawFile = Join-Path $RawDir (
        "${BenchmarkName}_N${N}_run${Repetition}.txt"
    )

    # CRITICAL:
    # Windows PowerShell Set-Content -Encoding UTF8 can write a BOM.
    # clox's scanner sees that BOM as an unexpected character.
    #
    # WriteAllText with UTF8Encoding(false) produces UTF-8 WITHOUT BOM.

    [System.IO.File]::WriteAllText(
        $TempFile,
        $InjectedSource,
        (New-Object System.Text.UTF8Encoding($false))
    )

    Write-Host (
        "Run {0}/{1} | {2} | N={3} | rep={4} ... " -f `
        $RunOrder,
        $TotalRuns,
        $BenchmarkName,
        $N,
        $Repetition
    ) -NoNewline

    # --------------------------------------------------------
    # Execute clox
    # --------------------------------------------------------

    $Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    try {

        $OutputLines = @(& $Clox $TempFile 2>&1)

        $ExitCode = $LASTEXITCODE

    }
    catch {

        $Stopwatch.Stop()

        Remove-Item -LiteralPath $TempFile -Force -ErrorAction SilentlyContinue

        throw "clox execution failed for $BenchmarkName N=$N rep=$Repetition : $($_.Exception.Message)"
    }

    $Stopwatch.Stop()

    $WallMs = [math]::Round(
        $Stopwatch.Elapsed.TotalMilliseconds,
        3
    )

    $RawOutput = ($OutputLines -join [Environment]::NewLine)

    # Save raw output without BOM as well.
    [System.IO.File]::WriteAllText(
        $RawFile,
        $RawOutput,
        (New-Object System.Text.UTF8Encoding($false))
    )

    Remove-Item -LiteralPath $TempFile -Force -ErrorAction SilentlyContinue

    # --------------------------------------------------------
    # Check exit code
    # --------------------------------------------------------

    if ($ExitCode -ne 0) {

        Write-Host " FAILED (exit code $ExitCode)" -ForegroundColor Red

        throw @"
Benchmark failed.

Benchmark : $BenchmarkName
N         : $N
Repetition: $Repetition
Exit code : $ExitCode

Raw output:
$RawOutput
"@
    }

    # --------------------------------------------------------
    # Parse profiler output
    # --------------------------------------------------------

    $CompileMs       = 0.0
    $ExecMs          = 0.0
    $Opcodes         = 0
    $GcCount         = 0
    $GcMs            = 0.0
    $PeakHeapBytes   = 0
    $BytesAllocated  = 0
    $BytesFreed      = 0
    $ProgramOutput   = ""
    $OpcodeCounts    = ""

    # Compilation time
    if ($RawOutput -match '(?im)Compilation time:\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|milliseconds|s|seconds)') {

        $Value = [double]$Matches[1]
        $Unit = $Matches[2].ToLower()

        if ($Unit -eq "s" -or $Unit -eq "seconds") {
            $CompileMs = $Value * 1000.0
        }
        else {
            $CompileMs = $Value
        }
    }

    # Execution time
    if ($RawOutput -match '(?im)Execution time:\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|milliseconds|s|seconds)') {

        $Value = [double]$Matches[1]
        $Unit = $Matches[2].ToLower()

        if ($Unit -eq "s" -or $Unit -eq "seconds") {
            $ExecMs = $Value * 1000.0
        }
        else {
            $ExecMs = $Value
        }
    }

    # Opcode execution count
    if ($RawOutput -match '(?im)(?:Opcode executions|Opcode execution count|Total opcode executions):\s*([0-9]+)') {
        $Opcodes = [long]$Matches[1]
    }

    # GC count
    if ($RawOutput -match '(?im)GC count:\s*([0-9]+)') {
        $GcCount = [long]$Matches[1]
    }

    # GC time
    if ($RawOutput -match '(?im)GC time:\s*([0-9]+(?:\.[0-9]+)?)\s*(ms|milliseconds|s|seconds)') {

        $Value = [double]$Matches[1]
        $Unit = $Matches[2].ToLower()

        if ($Unit -eq "s" -or $Unit -eq "seconds") {
            $GcMs = $Value * 1000.0
        }
        else {
            $GcMs = $Value
        }
    }

    # Peak heap
    if ($RawOutput -match '(?im)Peak heap usage:\s*([0-9]+)\s*bytes') {
        $PeakHeapBytes = [long]$Matches[1]
    }
    elseif ($RawOutput -match '(?im)Peak heap:\s*([0-9]+)\s*bytes') {
        $PeakHeapBytes = [long]$Matches[1]
    }

    # Allocated
    if ($RawOutput -match '(?im)Total bytes allocated:\s*([0-9]+)') {
        $BytesAllocated = [long]$Matches[1]
    }

    # Freed
    if ($RawOutput -match '(?im)Total bytes freed:\s*([0-9]+)') {
        $BytesFreed = [long]$Matches[1]
    }

    # --------------------------------------------------------
    # Extract program output
    # --------------------------------------------------------

    $ProgramLines = New-Object System.Collections.Generic.List[string]

    foreach ($Line in $OutputLines) {

        $Text = [string]$Line

        if ($Text -match '^\s*$') {
            continue
        }

        if ($Text -match '^(=+|-+)$') {
            continue
        }

        if ($Text -match '^\s*Profiler') {
            continue
        }

        if ($Text -match '^\s*(Execution time|Compilation time|Opcode executions|Opcode execution count|Total opcode executions):') {
            continue
        }

        if ($Text -match '^\s*(GC count|GC time|Peak heap usage|Peak heap|Total bytes allocated|Total bytes freed):') {
            continue
        }

        if ($Text -match '^\s*Opcode (frequency|counts|execution counts)') {
            continue
        }

        if ($Text -match '^\s*OP_[A-Z_]+') {
            continue
        }

        $ProgramLines.Add($Text)
    }

    $ProgramOutput = ($ProgramLines -join " ").Trim()

    # --------------------------------------------------------
    # Extract opcode frequency report
    # --------------------------------------------------------

    $OpcodeEntries = New-Object System.Collections.Generic.List[string]

    foreach ($Line in $OutputLines) {

        $Text = [string]$Line

        if ($Text -match '^\s*(OP_[A-Z_]+)\s*[:=]\s*([0-9]+)\s*$') {

            $OpcodeName  = $Matches[1]
            $OpcodeValue = $Matches[2]

            $OpcodeEntries.Add(
                "$OpcodeName=$OpcodeValue"
            )
        }
    }

    $OpcodeCounts = ($OpcodeEntries -join ";")

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    $CompileMs = [math]::Round($CompileMs, 3)
    $ExecMs = [math]::Round($ExecMs, 3)
    $GcMs = [math]::Round($GcMs, 3)

    # --------------------------------------------------------
    # Build CSV row
    # --------------------------------------------------------

    $Timestamp = (Get-Date).ToString("o")

    $CsvFields = @(
        $RunOrder
        $Timestamp
        $BenchmarkName
        $N
        $Repetition
        $WallMs
        $CompileMs
        $ExecMs
        $Opcodes
        $GcCount
        $GcMs
        $PeakHeapBytes
        $BytesAllocated
        $BytesFreed
        $ProgramOutput
        $OpcodeCounts
    )

    $CsvLine = (
        $CsvFields |
        ForEach-Object {
            ConvertTo-CsvField $_
        }
    ) -join ","

    # --------------------------------------------------------
    # Persist result
    # --------------------------------------------------------

    Append-CsvLineWithRetry `
        -Path $CsvPath `
        -Line $CsvLine

    # Only mark completed AFTER successful CSV write.
    $Completed[$CompletedKey] = $true

    Write-Host (
        "OK | exec={0:F3} ms | ops={1:N0} | GC={2}" -f `
        $ExecMs,
        $Opcodes,
        $GcCount
    ) -ForegroundColor Green
}

# ------------------------------------------------------------
# Final status
# ------------------------------------------------------------

$FinalRows = 0

if (Test-Path -LiteralPath $CsvPath) {
    try {
        $FinalRows = @(Import-Csv -LiteralPath $CsvPath).Count
    }
    catch {
        Write-Host ""
        Write-Host "WARNING: Could not read final CSV." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host " Dataset complete"
Write-Host "============================================================"
Write-Host "CSV rows: $FinalRows / $TotalRuns"
Write-Host "CSV     : $CsvPath"
Write-Host "Raw     : $RawDir"
Write-Host "============================================================"
Write-Host ""