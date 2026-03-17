param(
    [string]$OutputDir = "dist"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$staging = Join-Path $OutputDir "interview-tracker-$timestamp"
$zipPath = "$staging.zip"

if (Test-Path $staging) {
    Remove-Item -Path $staging -Recurse -Force
}

New-Item -ItemType Directory -Path $staging | Out-Null

$itemsToCopy = @(
    "app",
    "templates",
    "static",
    "docs",
    "main.py",
    "requirements.txt",
    "README.md",
    "start_tracker.cmd",
    "seed_demo_data.py"
)

foreach ($item in $itemsToCopy) {
    Copy-Item -Path (Join-Path $root $item) -Destination $staging -Recurse -Force
}

if (Test-Path $zipPath) {
    Remove-Item -Path $zipPath -Force
}

Compress-Archive -Path "$staging\*" -DestinationPath $zipPath
Remove-Item -Path $staging -Recurse -Force

Write-Host "Created release ZIP: $zipPath"
