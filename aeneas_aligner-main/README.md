# Real Audio-Text Aligner (Local System)

This application performs **real forced alignment** of audio and text files using the aeneas library. It supports multiple audio formats and text file types (DOCX, PDF, TXT).

## Features

- ✅ **Real forced alignment** (not dummy)
- ✅ **Multiple audio formats** (MP3, WAV, M4A, FLAC, etc.)
- ✅ **Multiple text formats** (DOCX, PDF, TXT)
- ✅ **Automatic audio conversion** to WAV format
- ✅ **SRT subtitle output**
- ✅ **Web interface** using Gradio

## System Requirements

- **Operating System**: Linux (Ubuntu/Debian recommended), macOS, or Windows
- **Python**: 3.7 or higher
- **System Dependencies**: espeak, ffmpeg

## Installation Guide

### 1. Install System Dependencies

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y espeak ffmpeg
```

#### On macOS (using Homebrew):
```bash
brew install espeak ffmpeg
```

#### On Windows:
- Download and install [eSpeak](http://espeak.sourceforge.net/download.html)
- Download and install [FFmpeg](https://ffmpeg.org/download.html)
- Add both to your system PATH

### 2. Install Python Dependencies

```bash
# Clone or download this project
cd aeneas_aligner-main

# Install Python packages
pip install -r requirements.txt
```

### 3. Verify Installation

```bash
# Test espeak
espeak --version

# Test ffmpeg
ffmpeg -version

# Test aeneas
python -c "from aeneas.executetask import ExecuteTask; print('aeneas installed successfully')"
```

## Usage

### Run the Application

```bash
python app.py
```

The web interface will open at `http://localhost:7860`

### How to Use

1. **Upload Audio File**: Any format (MP3, WAV, M4A, FLAC, etc.)
2. **Upload Text File**: DOCX, PDF, or TXT format
3. **Click Submit**: The app will perform real forced alignment
4. **Download Results**: Get the SRT subtitle file

## How It Works

1. **Audio Processing**: Converts any audio format to WAV using FFmpeg
2. **Text Extraction**: Extracts text from DOCX, PDF, or TXT files
3. **Real Alignment**: Uses aeneas to perform forced alignment
4. **Output**: Generates SRT subtitle file with accurate timings

## Troubleshooting

### Common Issues

#### "espeak not found"
```bash
# Ubuntu/Debian
sudo apt-get install espeak

# macOS
brew install espeak

# Windows: Download from http://espeak.sourceforge.net/download.html
```

#### "ffmpeg not found"
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows: Download from https://ffmpeg.org/download.html
```

#### "aeneas installation failed"
```bash
# Make sure you have build tools
sudo apt-get install build-essential python3-dev

# Try installing aeneas again
pip install aeneas==1.7.3.0
```

### Performance Tips

- **Audio Quality**: Higher quality audio gives better alignment results
- **Text Quality**: Clean, properly formatted text improves accuracy
- **File Size**: Very large files may take longer to process

## Supported Formats

### Audio Formats
- MP3, WAV, M4A, FLAC, OGG, AAC, and more (via FFmpeg)

### Text Formats
- **DOCX**: Microsoft Word documents
- **PDF**: PDF documents
- **TXT**: Plain text files

### Output Format
- **SRT**: Standard subtitle format

## Example Output

```
1
00:00:00,000 --> 00:00:02,500
Hello world.

2
00:00:02,500 --> 00:00:05,200
This is a test of the alignment system.

3
00:00:05,200 --> 00:00:08,100
The timings are now accurate to the actual speech.
```

## Technical Details

- **Alignment Engine**: aeneas (forced alignment library)
- **Audio Processing**: FFmpeg for format conversion
- **Text Processing**: python-docx, pdfminer.six
- **Web Interface**: Gradio
- **Language**: English (configurable in code)

## License

This project uses open-source libraries. Please check individual library licenses.

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all system dependencies are installed
3. Ensure Python packages are correctly installed
4. Check that your audio and text files are valid
