# OR-Recorder-Transcriber

This project is designed to transcribe audio recordings from an operating room and classify the events mentioned in the transcriptions. It uses Automatic Speech Recognition (ASR) models to convert speech to text and a supervised clustering model to classify the events.

Also, this project is combined with an other projet called [NOL-Event-Classifier](https://github.com/Gabrieleirbag1/NOL-Event-Data-Classifier), which is used to classify the events mentioned in the transcriptions specifically for the anesthesia domain.

Requires Python 3.10 or higher (tested on 3.12.13 which is recommanded)

## Setup the workspace

### Run the installation script

```bash
chmod +x setup_workspace.sh
./setup_workspace.sh
```

### Or install only OR-Recorder-Transcriber

```bash
pip install -r requirements.txt
```

## Run Project

```bash
python3 src/or-recorder-transcriber/main.py
```
