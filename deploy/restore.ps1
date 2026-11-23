# Windows PowerShell：从迁移包还原
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if (Test-Path "deploy\migrate.py") {
    python deploy\migrate.py restore @args
} else {
    python migrate.py restore @args
}
