#!/bin/bash

## CHECK IF GIT IS INSTALLED
if ! command -v git &> /dev/null
then
    echo "git could not be found, installing git..."
    sudo apt update
    sudo apt install git -y
fi

## CHECK IF PYTHON 3.10 OR HIGHER IS INSTALLED
if ! command -v python3 &> /dev/null || [[ $(python3 -c 'import sys; print(sys.version_info[:2])') < (3, 10) ]]; then
    echo "Python 3.10 or higher is required."
    exit 1
fi

## Clone the NOL-Event-Data-Classifier repository
cd .. && git clone https://github.com/Gabrieleirbag1/NOL-Event-Data-Classifier.git

## Create a virtual environment and activate it
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r OR-Recorder-Transcriber/requirements.txt
pip install -r NOL-Event-Data-Classifier/requirements.txt

#create workspace file
CAT <<EOT >> .code-workspace
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