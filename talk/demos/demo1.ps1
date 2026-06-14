#!/usr/bin/env pwsh
# Demo 1 - Copilot scaffolds a tool + guardrail + tests.
Set-Location $PSScriptRoot/../..
Write-Host "`n=== Demo 1 . Tests for find_stalls ===" -ForegroundColor Cyan
& .venv\Scripts\python -m pytest tests/test_find_stalls.py -v