param([switch]$Diagnostic)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    $pythonPath = Join-Path $projectRoot '.venv/Scripts/python.exe'
    & $pythonPath -c "import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize('P') == 8"
    if ($LASTEXITCODE -ne 0) { throw 'Requires project Python 3.12 x64' }
    & $pythonPath -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed; build stopped' }
    & $pythonPath tools/validate_assets.py
    if ($LASTEXITCODE -ne 0) { throw 'Complete classic and dog assets required; build stopped' }
    $env:PVZ_DIAGNOSTIC = if ($Diagnostic) { '1' } else { '0' }
    & $pythonPath -m PyInstaller --noconfirm --clean packaging/pvz_game.spec
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
    Copy-Item -LiteralPath (Join-Path $projectRoot 'packaging/开始游戏.txt') -Destination (Join-Path $projectRoot 'dist/PvzMiniGame-v0.2.0/开始游戏.txt') -Force
    Copy-Item -LiteralPath (Join-Path $projectRoot 'assets/fonts/OFL.txt') -Destination (Join-Path $projectRoot 'dist/PvzMiniGame-v0.2.0/字体许可.txt') -Force
    if (-not $Diagnostic) {
        $source = Join-Path $projectRoot 'dist/PvzMiniGame-v0.2.0'
        $archive = Join-Path $projectRoot 'dist/PvzMiniGame-windows-x64.zip'
        for ($attempt = 1; $attempt -le 3; $attempt++) {
            try {
                Compress-Archive -Path $source -DestinationPath $archive -Force
                break
            } catch {
                if ($attempt -eq 3) { throw }
                Start-Sleep -Seconds 2
            }
        }
    }
} finally {
    Remove-Item Env:PVZ_DIAGNOSTIC -ErrorAction SilentlyContinue
    Pop-Location
}
