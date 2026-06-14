#!/usr/bin/env pwsh
# Demo 3 - Observability + governance + eval loop.
Set-Location $PSScriptRoot/../..
$env:PYTHONIOENCODING = "utf-8"

Write-Host "`n=== Demo 3 . Step 1: a normal request (clean trace) ===" -ForegroundColor Cyan
& .venv\Scripts\merlions ask "dinner near marina bay"

Write-Host "`n=== Demo 3 . Step 2: a malicious arg triggers a policy.deny ===" -ForegroundColor Cyan
& .venv\Scripts\merlions call-tool find_stalls --arg "location=marina bay" --arg "cuisine=api_key=AKIA-fake-please-deny"
if ($LASTEXITCODE -ne 0) { Write-Host "(expected refusal - exit code $LASTEXITCODE)" -ForegroundColor Yellow }

Write-Host "`n=== Demo 3 . Step 3: audit log ===" -ForegroundColor Cyan
& .venv\Scripts\merlions audit --last 8

Write-Host "`n=== Demo 3 . Step 4: eval suite (real traces -> eval cases -> next build) ===" -ForegroundColor Cyan
& .venv\Scripts\merlions evals --suite hawker --since yesterday