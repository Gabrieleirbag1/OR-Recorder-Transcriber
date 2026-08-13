# OR-Recorder-Transcriber

This project is designed to transcribe audio recordings from an operating room and classify the events mentioned in the transcriptions. It uses Automatic Speech Recognition (ASR) models to convert speech to text and a supervised clustering model to classify the events.

Also, this project is combined with an other projet called [NOL-Event-Classifier](https://github.com/Gabrieleirbag1/NOL-Event-Data-Classifier), which is used to classify the events mentioned in the transcriptions specifically for the anesthesia domain.

![Recorder](https://github.com/Gabrieleirbag1/OR-Recorder-Transcriber/blob/main/screenshots/ORRT-Recorder.png)
![Graphic](https://github.com/Gabrieleirbag1/OR-Recorder-Transcriber/blob/main/screenshots/ORRT-Graphic.png)


## Installation

> [!WARNING]
> Requires Python 3.12 or higher (tested on 3.12.13 which is highly recommanded)

> [!IMPORTANT]
> **Windows Dependency Setup**<br>
> FFmpeg is required for audio processing. Follow these steps to set it up:
> 1. Download [ffmpeg-git-essentials](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z) and extract the archive.
> 2. Copy `ffmpeg.exe` from the extracted `bin/` folder.
> 3. Paste `ffmpeg.exe` directly into the root folder of this project.
> 
> OR-Recorder-Transcriber/<br>
> ├── src/<br>
> ├── screenshots/<br>
> ├── ffmpeg.exe         <-- Place ffmpeg.exe here<br>
> ├── ORRT.exe<br>
> ├── requirements.txt<br>
> └── README.md

``` bash
### Binary package
Download the binary packages in Releases.
```

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

## Documentation

**User Guide:** See the [guide.pdf](https://github.com/Gabrieleirbag1/OR-Recorder-Transcriber/blob/main/guide.pdf) for end-user instructions and workflows.

**Developer Docs:** Check the Sphinx developer docs for code structure and technical guidelines.
```bash
chmod +x sphinx_docs_setup.sh
./sphinx_docs_setup.sh
```

## Author
@Missclick (Developer)
E-mail : gabrielgarronedev@gmail.com
Discord : missclick.net
