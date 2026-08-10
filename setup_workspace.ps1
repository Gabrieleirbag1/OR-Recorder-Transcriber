#!/usr/bin/env pwsh

## CHECK IF GIT IS INSTALLED
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "git could not be found, please install git first (e.g. via https://git-scm.com/download/win or winget install --id Git.Git)."
    exit 1
}

## CHECK IF PYTHON 3.10 OR HIGHER IS INSTALLED
$pythonOk = $false
if (Get-Command python -ErrorAction SilentlyContinue) {
    $versionInfo = python -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')"
    $major, $minor = $versionInfo -split '\.'
    if ([int]$major -gt 3 -or ([int]$major -eq 3 -and [int]$minor -ge 10)) {
        $pythonOk = $true
    }
}

if (-not $pythonOk) {
    Write-Host "Python 3.10 or higher is required."
    exit 1
}

## Clone the NOL-Event-Data-Classifier repository
Set-Location ..
git clone https://github.com/Gabrieleirbag1/NOL-Event-Data-Classifier.git

## Create a virtual environment and activate it
python -m venv venv
. .\venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r OR-Recorder-Transcriber\requirements.txt
pip install -r NOL-Event-Data-Classifier\requirements.txt

# Create workspace file
$workspaceContent = @"
{
        "folders": [
                {
                        "path": "OR-Recorder-Transcriber"
                },
                {
                        "path": "NOL-Event-Data-Classifier"
                }
        ],
        "settings": {}
}
"@

Set-Content -Path ".code-workspace" -Value $workspaceContent