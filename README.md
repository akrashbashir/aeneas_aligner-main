<<<<<<< HEAD
# 🎧 Professional SRT Subtitle Generator

A professional-grade tool for generating synchronized SRT subtitle files from text transcripts and audio/video files. This tool implements industry-standard captioning guidelines and provides a user-friendly web interface.

## ✨ Features

- **🎯 Professional Formatting**: Exactly 4 words per line, 2 lines per subtitle
- **⏱️ Smart Timing**: 1.5-6 seconds per subtitle with adjustable reading speed
- **🎵 Audio Synchronization**: Proper alignment with audio duration
- **📝 Multiple Input Formats**: Support for TXT, PDF, DOCX files and direct text input
- **🎬 Audio Support**: MP3, WAV, M4A, FLAC, MP4, OGG, AAC and more
- **🌐 Web Interface**: User-friendly Gradio-based web application
- **🧠 NLTK Integration**: Professional sentence tokenization

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- FFmpeg (for audio processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd srt-subtitle-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg** (if not already installed)
   - **Windows**: Download from [FFmpeg.org](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

4. **Run the application**
   
   **Option 1: Complete Application (Recommended)**
   ```bash
   python app_windows.py
   ```
   
   **Option 2: Modular Application**
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to the provided URL (usually `http://localhost:7860`)

## 📋 Usage

### Web Interface

1. **Upload Audio**: Select your audio/video file (any format supported by FFmpeg)
2. **Add Text**: Either upload a text file or type your transcript directly
3. **Adjust Settings**: Set your preferred words per minute (150-180 WPM)
4. **Generate**: Click "Professional Alignment" for industry-standard results
5. **Download**: Get your SRT file ready for use

### Programmatic Usage

```python
from srt_generator import professional_align_text_with_audio

# Example usage
result, srt_file_path = professional_align_text_with_audio(
    audio_file="path/to/audio.mp3",
    text_input="Your transcript text here",
    wpm=165
)
```

## 🎯 Professional Guidelines

This tool implements industry-standard captioning guidelines:

- **📝 Format**: Exactly 4 words per line, 2 lines per subtitle
- **⏱️ Duration**: 1.5 to 6 seconds per subtitle
- **📖 Reading Speed**: 150-180 words per minute (adjustable)
- **🎵 Audio Sync**: Proper synchronization with audio duration
- **🧠 Smart Splitting**: NLTK-based sentence tokenization

### Example Output

```
1
00:00:00,000 --> 00:00:02,500
Hello world! This is
a test of the professional

2
00:00:02,500 --> 00:00:05,000
SRT generator. It should
create subtitles following

3
00:00:05,000 --> 00:00:07,500
all the guidelines. Each
subtitle should be between
```

## 📁 Project Structure

```
srt-subtitle-generator/
├── app_windows.py          # Complete application (recommended)
├── app.py                  # Modular web application
├── srt_generator.py        # Core SRT generation logic
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore            # Git ignore rules
├── LICENSE               # MIT License
├── test_app.py           # Test suite
└── examples/             # Example files and usage
    ├── sample_audio.mp3
    └── sample_transcript.txt
```

## 🔧 Configuration

### Words Per Minute (WPM)

Adjust the reading speed to match your content:
- **150 WPM**: Slower, more readable for complex content
- **165 WPM**: Standard reading speed (default)
- **180 WPM**: Faster, for quick-paced content

### Supported File Formats

**Audio/Video**: MP3, WAV, M4A, FLAC, MP4, OGG, AAC, and more
**Text**: TXT, PDF, DOCX, or direct text input

## 🛠️ Development

### Running Tests

```bash
python test_app.py
```

### Code Style

This project follows PEP 8 style guidelines. Use a linter like `flake8` or `black` for code formatting.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NLTK**: For professional sentence tokenization
- **Gradio**: For the web interface
- **FFmpeg**: For audio processing capabilities
- **pdfminer.six**: For PDF text extraction
- **python-docx**: For DOCX file support

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-username/srt-subtitle-generator/issues) page
2. Create a new issue with detailed information
3. Include your operating system, Python version, and error messages

## 🔄 Version History

- **v1.0.0**: Initial release with professional SRT generation
- **v1.1.0**: Added web interface and multiple input formats
- **v1.2.0**: Enhanced audio synchronization and timing algorithms

---

**Made with ❤️ for content creators and accessibility advocates**
=======
# aeneas_aligner-main
>>>>>>> origin/main
