#!/usr/bin/env pwsh
param(
    [Alias("d")]
    [switch]$desktop
)

$currentDir = (Get-Location).Path

# $desktop est déjà vrai si la commande est appelée avec -desktop ou -d
$createDesktop = $desktop.IsPresent

# Check Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH. Please install Python 3.12+ and ensure it's on PATH."
    exit 1
}

# Create the virtual environment
$venvPath = Join-Path $currentDir "venv"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

# Activate the virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
. $activateScript

pip install pyinstaller

# Install dependencies
$requirementsPath = Join-Path $currentDir "requirements.txt"
pip install -r $requirementsPath

# Create Build directory only if it does not exist
$buildDir = Join-Path $currentDir "Build"
if (-not (Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir | Out-Null
}
Set-Location $buildDir

# Create the executable
$assetsData = "$currentDir\src\or_recorder_transcriber\assets;assets/"
$configData = "$currentDir\src\or_recorder_transcriber\config;config/"
$mainScript = "$currentDir\src\or_recorder_transcriber\main.py"

# Resolve whisper's and faster_whisper's own bundled data-asset directories
# from the venv (mel_filters.npz / silero_vad_*.onnx), since PyInstaller does
# not pick these up automatically.
$whisperAssetsPath = python -c "import whisper, os; print(os.path.join(os.path.dirname(whisper.__file__), 'assets'))"
$fasterWhisperAssetsPath = python -c "import faster_whisper, os; print(os.path.join(os.path.dirname(faster_whisper.__file__), 'assets'))"

$whisperData = "$whisperAssetsPath;whisper/assets"
$fasterWhisperData = "$fasterWhisperAssetsPath;faster_whisper/assets"

pyinstaller --noconfirm --onefile --windowed `
    --add-data "$assetsData" `
    --add-data "$configData" `
    --add-data "$whisperData" `
    --add-data "$fasterWhisperData" `
    --add-binary "$currentDir\ffmpeg.exe;ffmpeg/" `
    --distpath "$currentDir" `
    --name "ORRT" `
    "$mainScript"

# Return to the original directory
Set-Location $currentDir

# Deactivate before removing the venv directory
deactivate

# Remove the virtual environment
Remove-Item -Recurse -Force $venvPath

Write-Host "ORRT installation script completed successfully."