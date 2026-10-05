$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $projectDir ".venv\Scripts\python.exe"
$app = Join-Path $projectDir "app.py"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Không tìm thấy môi trường Python của dự án tại $python. Tạo .venv bằng Python 3.12 rồi cài requirement.txt trước."
}

$pythonVersion = & $python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($pythonVersion -ne "3.12") {
    throw "Dự án yêu cầu Python 3.12; .venv hiện đang dùng Python $pythonVersion."
}

Write-Host "Đang chạy dashboard bằng Python $pythonVersion tại http://localhost:8501"
& $python -m streamlit run $app --server.port 8501
