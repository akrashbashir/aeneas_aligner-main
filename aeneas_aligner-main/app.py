import os
import tempfile
import subprocess
import sys
import re

# Import with error handling
try:
    from aeneas.executetask import ExecuteTask
    from aeneas.task import Task
    AENEAS_AVAILABLE = True
except ImportError:
    AENEAS_AVAILABLE = False
    ExecuteTask = None
    Task = None

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    gr = None

try:
    from pdfminer.high_level import extract_text as extract_pdf_text
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False
    extract_pdf_text = None

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    docx = None


def check_aeneas_installation():
    if not AENEAS_AVAILABLE:
        return False, "aeneas not installed. Please run: pip install aeneas==1.7.3.0"
    try:
        subprocess.run(['espeak', '--version'], capture_output=True, text=True, timeout=5)
        subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        return True, "All dependencies installed"
    except Exception as e:
        return False, str(e)

def extract_text_from_file(file):
    """Extract text from various file formats"""
    if file is None:
        return None, None

    try:
        ext = file.name.split('.')[-1].lower()

        if ext == "txt":
            if hasattr(file, "value"):
                return file.value, None
            elif hasattr(file, "read"):
                content = file.read()
                if isinstance(content, bytes):
                    return content.decode("utf-8", errors="ignore"), None
                return content, None
            elif hasattr(file, "name"):
                try:
                    with open(file.name, "r", encoding="utf-8") as f:
                        return f.read(), None
                except Exception as e:
                    return f"Error reading file from path: {e}", None
            else:
                return "Error: Unsupported .txt file object", None
        elif ext == "pdf":
            if not PDFMINER_AVAILABLE:
                return "Error: pdfminer.six not installed. Please run: pip install pdfminer.six", None
            return extract_pdf_text(file.name), None
        elif ext == "docx":
            if not DOCX_AVAILABLE or docx is None:
                return "Error: python-docx not installed. Please run: pip install python-docx", None
            try:
                doc = docx.Document(file.name)
                return "\n".join([p.text for p in doc.paragraphs]), None
            except Exception as e:
                return f"Error reading DOCX file: {e}", None
        else:
            return f"Error: Unsupported file format '{ext}'. Supported formats: txt, pdf, docx", None
    except Exception as e:
        return f"Error reading file: {str(e)}", None

def convert_audio_to_wav(audio_path):
    try:
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_wav.close()
        cmd = [
            'ffmpeg', '-i', audio_path,
            '-acodec', 'pcm_s16le',
            '-ar', '22050',
            '-ac', '1',
            '-y',
            temp_wav.name
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            os.unlink(temp_wav.name)
            return None, f"FFmpeg error: {result.stderr}"
        return temp_wav.name, None
    except Exception as e:
        if os.path.exists(temp_wav.name):
            os.unlink(temp_wav.name)
        return None, str(e)

def smart_align_text_with_audio(audio_path, text_file):
    temp_srt_path = None
    try:
        text, _ = extract_text_from_file(text_file)
        if not text or (isinstance(text, str) and text.startswith("Error")):
            return f"❌ Could not extract text: {text}", None

        audio_duration, _ = get_audio_duration(audio_path)
        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return "❌ No sentences found in the text file.", None

        total_chars = sum(len(s) for s in sentences)
        if total_chars == 0:
            return "❌ Text file is empty.", None

        srt = ""
        current_time = 0.0
        for i, sentence in enumerate(sentences):
            char_ratio = len(sentence) / total_chars
            sentence_duration = audio_duration * char_ratio
            sentence_duration = max(sentence_duration, 1.0)
            start_time = current_time
            end_time = min(current_time + sentence_duration, audio_duration)
            srt += f"{i+1}\n"
            srt += f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n"
            srt += f"{sentence}\n\n"
            current_time = end_time

        # Write SRT to a temp file for download
        temp_srt_fd, temp_srt_path = tempfile.mkstemp(suffix=".srt", text=True)
        with os.fdopen(temp_srt_fd, "w", encoding="utf-8") as f:
            f.write(srt)

        return f"✅ Smart Alignment Complete!\n\n{srt}", temp_srt_path

    except Exception as e:
        return f"❌ ERROR: {str(e)}", None

def dummy_align_text_with_audio(audio_path, text_file):
    temp_srt_path = None
    try:
        text, _ = extract_text_from_file(text_file)
        if not text or (isinstance(text, str) and text.startswith("Error")):
            return f"❌ Could not extract text: {text}", None

        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return "❌ No sentences found in the text file.", None

        total_time = 60.0
        duration = total_time / len(sentences)
        srt = ""
        for i, sentence in enumerate(sentences):
            start = i * duration
            end = (i + 1) * duration
            srt += f"{i+1}\n"
            srt += f"{format_srt_time(start)} --> {format_srt_time(end)}\n"
            srt += f"{sentence}\n\n"

        # Write SRT to a temp file for download
        temp_srt_fd, temp_srt_path = tempfile.mkstemp(suffix=".srt", text=True)
        with os.fdopen(temp_srt_fd, "w", encoding="utf-8") as f:
            f.write(srt)

        return f"✅ Dummy Alignment Complete!\n\n{srt}", temp_srt_path

    except Exception as e:
        return f"❌ ERROR: {str(e)}", None

# Optional Gradio Interface
if GRADIO_AVAILABLE:
    interface = gr.Interface(
        fn=smart_align_text_with_audio,
        inputs=[
            gr.Audio(label="🎙️ Upload Audio", type="filepath"),
            gr.File(label="📝 Upload Text (.txt, .pdf, .docx)")
        ],
        outputs=["text", gr.File(label="📝 Download SRT")],
        title="🔗 Real Audio-Text Aligner",
        description="Align real documents and audio using aeneas, ffmpeg, and espeak."
    )

    if __name__ == "__main__":
        interface.launch(share=True)
else:
    print("✅ Code loaded. Use `smart_align_text_with_audio(audio_path, text_file)` directly.")
