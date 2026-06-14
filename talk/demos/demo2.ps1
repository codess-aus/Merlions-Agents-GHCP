#!/usr/bin/env pwsh
# Demo 2 - Multi-agent composite question.
Set-Location $PSScriptRoot/../..
$env:PYTHONIOENCODING = "utf-8"
Write-Host "`n=== Demo 2 . Composite question ===" -ForegroundColor Cyan
& .venv\Scripts\merlions demo
Write-Host "`n=== Traces for this run ===" -ForegroundColor Cyan
& .venv\Scripts\merlions traces --last 12