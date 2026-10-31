param(
    [string]$ArtifactName = 'PvzMiniGame-v0.7.0',
    [switch]$Diagnostic
)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$buildRoot = Join-Path $projectRoot 'build\windows'
$distRoot = Join-Path $projectRoot 'dist\windows'
$workPath = Join-Path $buildRoot $ArtifactName
$bundlePath = Join-Path $distRoot $ArtifactName

if ($ArtifactName -notmatch '^PvzMiniGame-[A-Za-z0-9._-]+$') {
    throw 'ArtifactName must begin with PvzMiniGame- and contain only letters, digits, dot, underscore or hyphen'
}
if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) { throw "Missing project Python: $pythonPath" }
if (Test-Path -LiteralPath $bundlePath) { throw "Refusing to overwrite existing Windows release: $bundlePath" }
New-Item -ItemType Directory -Force -Path $buildRoot,$distRoot,(Join-Path $projectRoot '.tools\windows\pyinstaller') | Out-Null
Push-Location $projectRoot
try {
    & $pythonPath -c "import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize('P') == 8"
    if ($LASTEXITCODE -ne 0) { throw 'Requires project Python 3.12 x64' }
    & $pythonPath tools\validate_assets.py
    if ($LASTEXITCODE -ne 0) { throw 'Asset validation failed; Windows build stopped' }

    $env:PVZ_DIAGNOSTIC = if ($Diagnostic) { '1' } else { '0' }
    $env:PVZ_OUTPUT_NAME = $ArtifactName
    $env:PYINSTALLER_CONFIG_DIR = Join-Path $projectRoot '.tools\windows\pyinstaller'
    & $pythonPath -m PyInstaller --noconfirm --clean --distpath $distRoot --workpath $workPath packaging\windows\pvz_game.spec
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
    & $pythonPath packaging\windows\copy_release_files.py --artifact-name $ArtifactName
    if ($LASTEXITCODE -ne 0) { throw 'Release guide copy failed' }
    Write-Host "Windows directory release created: $bundlePath"
} finally {
    Remove-Item Env:PVZ_DIAGNOSTIC -ErrorAction SilentlyContinue
    Remove-Item Env:PVZ_OUTPUT_NAME -ErrorAction SilentlyContinue
    Remove-Item Env:PYINSTALLER_CONFIG_DIR -ErrorAction SilentlyContinue
    Pop-Location
}
