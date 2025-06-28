import os
import tempfile
import subprocess
import re
import json
from datetime import timedelta

# Import with error handling for optional dependencies
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

def format_srt_time(seconds):
    """Format seconds as SRT time: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

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

def get_audio_duration(audio_path):
    """Get audio duration using ffprobe (if available)"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
               '-of', 'csv=p=0', audio_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return float(result.stdout.strip()), None
        else:
            return 60.0, None  # Default 1 minute if ffprobe fails
    except:
        return 60.0, None  # Default 1 minute if ffprobe not available

def split_into_fixed_chunks(text, chunk_size=4):
    """Split text into chunks of exactly chunk_size words."""
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def group_chunks(chunks, lines_per_block=2):
    """Group chunks into blocks, each with lines_per_block lines."""
    return [chunks[i:i+lines_per_block] for i in range(0, len(chunks), lines_per_block)]

def convert_audio_to_wav(audio_file):
    import tempfile
    import os

    # DEBUGGING
    print("DEBUG audio_file type:", type(audio_file))
    print("DEBUG audio_file dir:", dir(audio_file))
    print("DEBUG audio_file repr:", repr(audio_file))

    temp_input = None

    # Handle file-like object
    if hasattr(audio_file, "read"):
        ext = os.path.splitext(getattr(audio_file, "name", "audio"))[-1]
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        temp_input.close()
        with open(temp_input.name, "wb") as f_out:
            f_out.write(audio_file.read())
    # Handle Gradio NamedString (has .name and .value)
    elif hasattr(audio_file, "value") and hasattr(audio_file, "name"):
        ext = os.path.splitext(audio_file.name)[-1]
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        temp_input.close()
        with open(temp_input.name, "wb") as f_out:
            f_out.write(audio_file.value)
    # Handle dict (Gradio sometimes passes a dict with 'name' and 'data')
    elif isinstance(audio_file, dict) and "name" in audio_file and "data" in audio_file:
        ext = os.path.splitext(audio_file["name"])[-1]
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        temp_input.close()
        with open(temp_input.name, "wb") as f_out:
            f_out.write(audio_file["data"])
    # Handle string file path
    elif isinstance(audio_file, str) and os.path.exists(audio_file):
        temp_input = audio_file
    else:
        return None, f"Unsupported audio file object type: {type(audio_file)}"

    # Now convert to wav as before
    try:
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_wav.close()
        cmd = [
            'ffmpeg', '-i', temp_input if isinstance(temp_input, str) else temp_input.name,
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
        if temp_input and not isinstance(temp_input, str) and os.path.exists(temp_input.name):
            os.unlink(temp_input.name)
        if os.path.exists(temp_wav.name):
            os.unlink(temp_wav.name)
        return None, str(e)

def smart_align_text_with_audio(audio_file, text_file):
    temp_srt_path = None
    temp_wav_path = None
    try:
        if not audio_file or not hasattr(audio_file, 'name'):
            return "❌ No valid audio file was uploaded. Please upload a valid audio file.", None
        text, _ = extract_text_from_file(text_file)
        if not text or (isinstance(text, str) and text.startswith("Error")):
            return f"❌ Could not extract text: {text}", None
        # Always convert audio to WAV for processing
        temp_wav_path, error = convert_audio_to_wav(audio_file)
        if error:
            return f"❌ Audio conversion error: {error}", None
        audio_path = temp_wav_path
        audio_duration, _ = get_audio_duration(audio_path)
        chunks = split_into_fixed_chunks(text, 4)
        if not chunks:
            return "❌ No text chunks found in the text file.", None
        blocks = group_chunks(chunks, 2)
        block_count = len(blocks)
        min_block_duration = 2.0  # seconds
        total_min_duration = min_block_duration * block_count
        if audio_duration < total_min_duration:
            duration_per_block = min_block_duration
            total_duration = duration_per_block * block_count
        else:
            duration_per_block = audio_duration / block_count
            total_duration = audio_duration
        srt = ""
        for i, block in enumerate(blocks):
            start = i * duration_per_block
            end = (i + 1) * duration_per_block
            if i == block_count - 1:
                end = total_duration
            srt += f"{i+1}\n"
            srt += f"{format_srt_time(start)} --> {format_srt_time(end)}\n"
            srt += '\n'.join(block) + "\n\n"
        temp_srt_fd, temp_srt_path = tempfile.mkstemp(suffix=".srt", text=True)
        with os.fdopen(temp_srt_fd, "w", encoding="utf-8") as f:
            f.write(srt)
        return f"✅ Smart Alignment Complete!\n\n{srt}", temp_srt_path
    except Exception as e:
        return f"❌ ERROR: {str(e)}", None
    finally:
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except:
                pass

def dummy_align_text_with_audio(audio_file, text_file):
    temp_srt_path = None
    temp_wav_path = None
    try:
        if not audio_file or not hasattr(audio_file, 'name'):
            return "❌ No valid audio file was uploaded. Please upload a valid audio file.", None
        text, _ = extract_text_from_file(text_file)
        if not text or (isinstance(text, str) and text.startswith("Error")):
            return f"❌ Could not extract text: {text}", None
        # Always convert audio to WAV for processing
        temp_wav_path, error = convert_audio_to_wav(audio_file)
        if error:
            return f"❌ Audio conversion error: {error}", None
        audio_path = temp_wav_path
        chunks = split_into_fixed_chunks(text, 4)
        if not chunks:
            return "❌ No text chunks found in the text file.", None
        blocks = group_chunks(chunks, 2)
        block_count = len(blocks)
        min_block_duration = 2.0  # seconds
        total_min_duration = min_block_duration * block_count
        total_time = 60.0
        if total_time < total_min_duration:
            duration_per_block = min_block_duration
            total_duration = duration_per_block * block_count
        else:
            duration_per_block = total_time / block_count
            total_duration = total_time
        srt = ""
        for i, block in enumerate(blocks):
            start = i * duration_per_block
            end = (i + 1) * duration_per_block
            if i == block_count - 1:
                end = total_duration
            srt += f"{i+1}\n"
            srt += f"{format_srt_time(start)} --> {format_srt_time(end)}\n"
            srt += '\n'.join(block) + "\n\n"
        temp_srt_fd, temp_srt_path = tempfile.mkstemp(suffix=".srt", text=True)
        with os.fdopen(temp_srt_fd, "w", encoding="utf-8") as f:
            f.write(srt)
        return f"✅ Dummy Alignment Complete!\n\n{srt}", temp_srt_path
    except Exception as e:
        return f"❌ ERROR: {str(e)}", None
    finally:
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except:
                pass

# Check if gradio is available before creating interface
if not GRADIO_AVAILABLE:
    print("❌ Gradio not installed. Please install it first: pip install gradio")
    print("You can still use the alignment functions directly in Python.")
else:
    # Gradio Interface
    with gr.Blocks(title="🎧 Windows Audio-Text Aligner") as interface:
        gr.Markdown("# 🎧 Windows Audio-Text Aligner")
        gr.Markdown("Upload audio + matching text to generate aligned subtitles (.srt).")
        gr.Markdown("**Note:** This is a Windows-compatible version with smart timing estimation.")
        with gr.Row():
            with gr.Column():
                audio_input = gr.File(
                    label="🎙️ Upload Audio (any format, including .mp4)",
                    file_types=None  # Accept any file type
                )
                text_input = gr.File(
                    label="📝 Text File (.txt, .pdf, .docx)",
                    file_types=[".txt", ".pdf", ".docx"]
                )
                with gr.Row():
                    smart_btn = gr.Button("🚀 Smart Alignment", variant="primary")
                    dummy_btn = gr.Button("🎭 Dummy Alignment", variant="secondary")
            with gr.Column():
                output = gr.Textbox(label="📄 Alignment Results", lines=20, max_lines=30)
                download = gr.File(label="⬇️ Download SRT", interactive=False)
        # Event handlers
        smart_btn.click(
            fn=smart_align_text_with_audio,
            inputs=[audio_input, text_input],
            outputs=[output, download]
        )
        dummy_btn.click(
            fn=dummy_align_text_with_audio,
            inputs=[audio_input, text_input],
            outputs=[output, download]
        )
        gr.Markdown("""
        ### How it works:
        - **Smart Alignment**: Estimates timing based on text length and audio duration
        - **Dummy Alignment**: Simple demonstration with evenly spaced timings
        - **Supported Formats**: MP3, WAV, M4A, FLAC, MP4, OGG, AAC, and more (via FFmpeg)
        - **Text**: TXT, PDF, DOCX
        
        ### For real forced alignment:
        Consider using online services like AssemblyAI, Rev AI, or similar APIs.
        """)
    if __name__ == "__main__":
        interface.launch(share=True) 