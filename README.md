# OR-Recorder-Transcriber

This project is designed to transcribe audio recordings from an operating room and classify the events mentioned in the transcriptions. It uses Automatic Speech Recognition (ASR) models to convert speech to text and a supervised clustering model to classify the events.

Also, this project is combined with an other projet called [NOL-Event-Classifier](https://github.com/Gabrieleirbag1/NOL-Event-Data-Classifier), which is used to classify the events mentioned in the transcriptions specifically for the anesthesia domain.

![Recorder](https://github.com/Gabrieleirbag1/OR-Recorder-Transcriber/blob/main/screenshots/ORRT-Recorder.png)
![Graphic](https://github.com/Gabrieleirbag1/OR-Recorder-Transcriber/blob/main/screenshots/ORRT-Graphic.png)


## Installation

> [!WARNING]
> Requires Python 3.12 or higher (tested on 3.12.13 which is highly recommanded)

### Binary package
Download the orrt-setup-1.0.exe for windows in Releases.

### Build locally from source

Get the project

```bash
git clone https://github.com/Gabrieleirbag1/OR-Recorder-Transcriber.git

cd OR-Recorder-Transcriber
```

Install dependancies and build package

```bash
#windows 
./orrt_install.ps1

#linux
./orrt_install.sh
```

Then run the executable file.


### Run Python directly

Run the installation script

```bash
chmod +x setup_workspace.sh
./setup_workspace.sh
```

... or install only OR-Recorder-Transcriber

```bash
pip install -r requirements.txt
```

Run Python File

```bash
python3 src/or-recorder-transcriber/main.py
```

## Author
@Missclick (Developer)
E-mail : gabrielgarronedev@gmail.com
Discord : missclick.net