Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$proj = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $proj

$py = "D:\\python\\python.exe"
if (-not (Test-Path $py)) {
  Write-Host "找不到 $py"
  Write-Host "请把 run_conda.ps1 里的 `$py 改成你实际的 conda python 路径。"
  exit 1
}

Write-Host "Using python: $py"
& $py -c 'import sys; print("sys.executable =", sys.executable)'

# 进程级禁用 oneDNN/MKLDNN/PIR/new_executor（避免 onednn_instruction.cc 未实现错误）
$env:FLAGS_use_mkldnn = "0"
$env:FLAGS_use_mkldnn_int8 = "0"
$env:FLAGS_use_onednn = "0"
$env:FLAGS_enable_new_executor = "0"
$env:FLAGS_enable_pir_in_executor = "0"
$env:FLAGS_enable_pir_api = "0"

& $py app.py

