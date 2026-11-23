# Windows PowerShell：打包迁移包
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
python deploy/migrate.py export @args
