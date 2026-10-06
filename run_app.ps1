$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $projectDir ".venv\Scripts\python.exe"
$app = Join-Path $projectDir "app.py"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Project Python environment not found at $python. Create .venv with Python 3.12 and install requirements.txt first."
}

$versionOutput = & $python --version 2>&1
if ($LASTEXITCODE -ne 0 -or $versionOutput -notmatch '^Python 3\.12(?:\.|$)') {
    throw "This project requires Python 3.12. The .venv currently reports: $versionOutput"
}
$pythonVersion = $versionOutput -replace '^Python\s+', ''

Write-Host "Starting dashboard with Python $pythonVersion at http://localhost:8501"
& $python -m streamlit run $app --server.port 8501
