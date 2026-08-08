$ErrorActionPreference = "Stop"

# ============================================================
# clox Benchmark Experiment Runner
# Dataset v1
# ============================================================

$Clox = ".\build\clox.exe"
$BenchmarkDir = ".\benchmarks"
$ResultsDir = ".\results"
$RawDir = ".\results\raw"
$TempDir = ".\results\temp"

$Repetitions = 5

# ------------------------------------------------------------
# Benchmark configuration
# ------------------------------------------------------------

$Benchmarks = @(
    @{
        Name = "arithmetic"
        File = "arithmetic.lox"
        Sizes = @(10000, 100000, 1000000, 10000000)
    },
    @{
        Name = "loops"
        File = "loops.lox"
        Sizes = @(10000, 100000, 1000000, 10000000)
    },
    @{
        Name = "functions"
        File = "functions.lox"
        Sizes = @(1000, 10000, 100000, 1000000)
    },
    @{
        Name = "recursion"
        File = "recursion.lox"
        Sizes = @(20, 25, 30, 35)
    },
    @{
        Name = "closures"
        File = "closures.lox"
        Sizes = @(1000, 10000, 100000, 1000000)
    },
    @{
        Name = "objects"
        File = "objects.lox"
        Sizes = @(1000, 10000, 100000, 1000000)
    },
    @{
        Name = "inheritance"
        File = "inheritance.lox"
        Sizes = @(1000, 10000, 100000, 1000000)
    },
    @{
        Name = "allocation"
        File = "allocation.lox"
        Sizes = @(1000, 10000, 100000, 1000000)
    }
)

# ------------------------------------------------------------
# Create required directories
# ------------------------------------------------------------

New-Item -ItemType Directory -Force $ResultsDir | Out-Null
New-Item -ItemType Directory -Force $RawDir | Out-Null
New-Item -ItemType Directory -Force $TempDir | Out-Null

# ------------------------------------------------------------
# Verify clox
# ------------------------------------------------------------

if (!(Test-Path $Clox)) {
    throw "clox.exe not found at $Clox"
}

# ------------------------------------------------------------
# Generate benchmark source for a specific N
# ------------------------------------------------------------

function Create-ScaledBenchmark {
    param (
        [string]$OriginalSource,
        [int]$Size,
        [string]$BenchmarkName
    )

    $pattern = 'var\s+n\s*=\s*\d+\s*;'

    if (-not [regex]::IsMatch($OriginalSource, $pattern)) {
        throw "Benchmark '$BenchmarkName' does not contain 'var n = <number>;'."
    }

    return [regex]::Replace(
        $OriginalSource,
        $pattern,
        "var n = $Size;",
        1
    )
}

# ------------------------------------------------------------
# Collection
# ------------------------------------------------------------

$totalRuns = 0

foreach ($benchmark in $Benchmarks) {

    $sourcePath = Join-Path $BenchmarkDir $benchmark.File

    if (!(Test-Path $sourcePath)) {
        throw "Benchmark file not found: $sourcePath"
    }

    # Read the original benchmark ONCE.
    $originalSource = Get-Content $sourcePath -Raw

    Write-Host ""
    Write-Host "============================================"
    Write-Host "Benchmark: $($benchmark.Name)"
    Write-Host "File:      $($benchmark.File)"
    Write-Host "============================================"

    foreach ($size in $benchmark.Sizes) {

        Write-Host ""
        Write-Host "N = $size"

        # Create a temporary benchmark file.
        $scaledSource = Create-ScaledBenchmark `
            -OriginalSource $originalSource `
            -Size $size `
            -BenchmarkName $benchmark.Name

        $tempFile = Join-Path `
            $TempDir `
            "$($benchmark.Name)_N$size.lox"

        Set-Content `
            -Path $tempFile `
            -Value $scaledSource `
            -NoNewline

        try {

            for ($run = 1; $run -le $Repetitions; $run++) {

                $totalRuns++

                Write-Host "Run $run / $Repetitions"

                $timestamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"

                $rawFile = Join-Path `
                    $RawDir `
                    "$($benchmark.Name)_N$size`_run$run`_$timestamp.txt"

                # Run clox against the TEMPORARY benchmark.
                & $Clox $tempFile *> $rawFile

                if ($LASTEXITCODE -ne 0) {
                    throw "Benchmark failed: $($benchmark.Name), N=$size, run=$run. Exit code: $LASTEXITCODE"
                }

                Start-Sleep -Milliseconds 100
            }
        }
        finally {

            # Delete temporary benchmark.
            if (Test-Path $tempFile) {
                Remove-Item $tempFile -Force
            }
        }
    }
}

# ------------------------------------------------------------
# Final cleanup
# ------------------------------------------------------------

if (Test-Path $TempDir) {
    $remaining = Get-ChildItem $TempDir -File

    if ($remaining.Count -eq 0) {
        Remove-Item $TempDir -Force
    }
}

Write-Host ""
Write-Host "============================================"
Write-Host "COLLECTION COMPLETE"
Write-Host "Total runs: $totalRuns"
Write-Host "Raw results: $RawDir"
Write-Host "============================================"