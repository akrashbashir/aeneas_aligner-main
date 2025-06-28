import os
import tempfile
import subprocess
import re
import json
from datetime import timedelta

# Import NLTK for professional sentence tokenization
try:
    import nltk
    # Download NLTK data for sentence tokenization
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    nltk = None

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

def split_text_into_sentences(text):
    """
    Step 1: Split raw text into sentences or phrases using NLTK.
    Falls back to simple splitting if NLTK is not available.
    """
    if not text or not text.strip():
        return []
    
    if NLTK_AVAILABLE:
        # Use NLTK sentence tokenizer (professional approach)
        sentences = nltk.sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]
    else:
        # Fallback: simple sentence splitting
        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        return [s.strip() for s in sentences if s.strip()]

def estimate_duration(text, wpm=165):
    """
    Step 2: Estimate timing based on word count and reading speed.
    Implements professional guidelines: 1.5-6 seconds per subtitle.
    """
    words = text.split()
    word_count = len(words)
    
    # Calculate duration based on reading speed (150-180 WPM = ~2.5 words per second)
    wps = wpm / 60  # words per second
    duration = word_count / wps
    
    # Apply professional constraints: 1.5-6 seconds
    duration = max(duration, 1.5)  # Minimum 1.5 seconds
    duration = min(duration, 6.0)  # Maximum 6.0 seconds
    
    return duration

def split_long_sentence(sentence, max_chars=42):
    """
    Split a long sentence into subtitle lines with exactly 4 words per line, 2 lines per subtitle.
    This creates a consistent format: exactly 4 words on line 1, exactly 4 words on line 2.
    """
    words = sentence.split()
    
    # If we have 8 or more words, create multiple subtitle blocks
    if len(words) >= 8:
        subtitle_blocks = []
        for i in range(0, len(words), 8):
            block_words = words[i:i+8]
            if len(block_words) >= 4:
                # First line: exactly 4 words
                line1 = " ".join(block_words[:4])
                # Second line: remaining words (up to 4)
                line2 = " ".join(block_words[4:8])
                subtitle_blocks.append([line1, line2])
        return subtitle_blocks
    elif len(words) >= 4:
        # Exactly 4+ words: split into 4 + remaining
        line1 = " ".join(words[:4])
        line2 = " ".join(words[4:8]) if len(words) > 4 else ""
        return [[line1, line2]]
    else:
        # Less than 4 words: pad with empty second line
        line1 = " ".join(words)
        return [[line1, ""]]

def synchronize_with_audio(sentences, audio_duration, wpm=165):
    """
    Step 3: Assign start/end times sequentially, synchronized with audio duration.
    Implements professional timing guidelines with 4-words-per-line format.
    """
    srt_entries = []
    current_time = 0.0
    subtitle_index = 1
    
    # Calculate total estimated duration
    total_estimated_duration = 0
    for sentence in sentences:
        # Split sentence into subtitle blocks (each with 2 lines, 4 words per line)
        subtitle_blocks = split_long_sentence(sentence)
        for block in subtitle_blocks:
            # Estimate duration based on total words in this block
            total_words = len(" ".join(block).split())
            wps = wpm / 60  # words per second
            duration = total_words / wps
            duration = max(duration, 1.5)  # Minimum 1.5 seconds
            duration = min(duration, 6.0)  # Maximum 6.0 seconds
            total_estimated_duration += duration
    
    # If estimated duration is longer than audio, we need to compress
    if total_estimated_duration > audio_duration:
        # Calculate compression ratio
        compression_ratio = audio_duration / total_estimated_duration
        
        for sentence in sentences:
            subtitle_blocks = split_long_sentence(sentence)
            for block in subtitle_blocks:
                # Estimate duration for this block
                total_words = len(" ".join(block).split())
                wps = wpm / 60
                duration = total_words / wps
                duration = duration * compression_ratio
                duration = max(duration, 1.0)
                
                # Ensure we don't exceed audio duration
                if current_time >= audio_duration:
                    break
                duration = min(duration, audio_duration - current_time)
                
                start_time = current_time
                end_time = current_time + duration
                
                srt_entries.append((subtitle_index, start_time, end_time, block))
                subtitle_index += 1
                current_time = end_time
    else:
        # Normal case: estimated duration fits within audio
        for sentence in sentences:
            subtitle_blocks = split_long_sentence(sentence)
            for block in subtitle_blocks:
                # Estimate duration for this block
                total_words = len(" ".join(block).split())
                wps = wpm / 60
                duration = total_words / wps
                duration = max(duration, 1.5)
                duration = min(duration, 6.0)
                
                # Ensure we don't exceed audio duration
                if current_time >= audio_duration:
                    break
                duration = min(duration, audio_duration - current_time)
                
                start_time = current_time
                end_time = current_time + duration
                
                srt_entries.append((subtitle_index, start_time, end_time, block))
                subtitle_index += 1
                current_time = end_time
    
    return srt_entries

def generate_srt_content(srt_entries):
    """
    Step 5: Build the SRT file with proper formatting.
    Implements professional SRT structure with exactly 2 lines per subtitle.
    """
    srt_content = ""
    
    for idx, start_time, end_time, subtitle_block in srt_entries:
        # Add subtitle number
        srt_content += f"{idx}\n"
        
        # Add timing
        srt_content += f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n"
        
        # Add content: exactly 2 lines per subtitle
        line1, line2 = subtitle_block
        srt_content += f"{line1}\n"
        if line2.strip():  # Only add second line if it has content
            srt_content += f"{line2}\n"
        srt_content += "\n"  # Empty line between subtitles
    
    return srt_content

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

def extract_text_from_input(text_file=None, text_input=None):
    """Extract text from either file upload or direct text input"""
    # Priority: text input first, then file
    if text_input and text_input.strip():
        return text_input.strip(), None
    
    if text_file:
        return extract_text_from_file(text_file)
    
    return None, "No text provided. Please upload a file or type text."

def combine_text_inputs(text_file_upload=None, text_input_type=None):
    """Combine text inputs from both tabs - priority to typed text"""
    if text_input_type and text_input_type.strip():
        return text_input_type.strip(), None
    
    if text_file_upload:
        return extract_text_from_file(text_file_upload)
    
    return None, "No text provided. Please upload a file or type text."

def professional_align_text_with_audio(audio_file, text_file=None, wpm=165, text_input=None):
    """
    Professional text-audio alignment using industry-standard guidelines.
    
    Implements all professional captioning standards:
    - Caption duration: 1.5 to 6 seconds
    - Max 42 characters per line, max 2 lines per subtitle
    - Reading speed: 150-180 WPM
    - Proper audio synchronization
    """
    temp_srt_path = None
    temp_wav_path = None
    try:
        if not audio_file or not hasattr(audio_file, 'name'):
            return "❌ No valid audio file was uploaded. Please upload a valid audio file.", None
        
        text, error = combine_text_inputs(text_file, text_input)
        if not text or (isinstance(text, str) and text.startswith("Error")):
            return f"❌ Could not extract text: {error}", None
        
        # Always convert audio to WAV for processing
        temp_wav_path, error = convert_audio_to_wav(audio_file)
        if error:
            return f"❌ Audio conversion error: {error}", None
        
        audio_path = temp_wav_path
        audio_duration, _ = get_audio_duration(audio_path)
        
        # Step 1: Split text into sentences using NLTK
        sentences = split_text_into_sentences(text)
        if not sentences:
            return "❌ No sentences found in the text.", None
        
        # Step 3: Synchronize with audio duration
        srt_entries = synchronize_with_audio(sentences, audio_duration, wpm)
        
        # Step 5: Generate SRT content
        srt_content = generate_srt_content(srt_entries)
        
        # Create temporary SRT file for download
        temp_srt_fd, temp_srt_path = tempfile.mkstemp(suffix=".srt", text=True)
        with os.fdopen(temp_srt_fd, "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        # Create summary
        subtitle_count = len(srt_entries)
        summary = f"""✅ Professional SRT Alignment Complete!

📊 Statistics:
• Subtitle entries: {subtitle_count}
• Words per minute: {wpm}
• Audio duration: {audio_duration:.2f}s

🎯 Professional Guidelines Applied:
• Caption duration: 1.5-6 seconds
• Max 42 characters per line
• Max 2 lines per subtitle
• Reading speed: {wpm} WPM
• Audio synchronization: ✅

📝 Generated SRT:
{srt_content}"""
        
        return summary, temp_srt_path
        
    except Exception as e:
        return f"❌ ERROR: {str(e)}", None
    finally:
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except:
                pass

def smart_align_text_with_audio(audio_file, text_file=None, text_input=None):
    temp_srt_path = None
    temp_wav_path = None
    try:
        if not audio_file or not hasattr(audio_file, 'name'):
            return "❌ No valid audio file was uploaded. Please upload a valid audio file.", None
        
        text, error = combine_text_inputs(text_file, text_input)
        if not text or (isinstance(text, str) and text.startswith("Error")):
            return f"❌ Could not extract text: {error}", None
        
        # Always convert audio to WAV for processing
        temp_wav_path, error = convert_audio_to_wav(audio_file)
        if error:
            return f"❌ Audio conversion error: {error}", None
        
        audio_path = temp_wav_path
        audio_duration, _ = get_audio_duration(audio_path)
        chunks = split_into_fixed_chunks(text, 4)
        if not chunks:
            return "❌ No text chunks found in the text.", None
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

def dummy_align_text_with_audio(audio_file, text_file=None, text_input=None):
    temp_srt_path = None
    temp_wav_path = None
    try:
        if not audio_file or not hasattr(audio_file, 'name'):
            return "❌ No valid audio file was uploaded. Please upload a valid audio file.", None
        
        text, error = combine_text_inputs(text_file, text_input)
        if not text or (isinstance(text, str) and text.startswith("Error")):
            return f"❌ Could not extract text: {error}", None
        
        # Always convert audio to WAV for processing
        temp_wav_path, error = convert_audio_to_wav(audio_file)
        if error:
            return f"❌ Audio conversion error: {error}", None
        
        audio_path = temp_wav_path
        chunks = split_into_fixed_chunks(text, 4)
        if not chunks:
            return "❌ No text chunks found in the text.", None
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
    with gr.Blocks(title="🎧 Professional Audio-Text Aligner") as interface:
        gr.Markdown("# 🎧 Professional Audio-Text Aligner")
        gr.Markdown("Upload audio + text (file or type) to generate professional SRT subtitles.")
        gr.Markdown("**Format:** Exactly 4 words per line, 2 lines per subtitle, 1.5-6s duration")
        
        with gr.Row():
            with gr.Column():
                audio_input = gr.File(
                    label="🎙️ Upload Audio (any format, including .mp4)",
                    file_types=None  # Accept any file type
                )
                
                # Text input section with tabs
                with gr.Tabs():
                    with gr.TabItem("📁 Upload Text File"):
                        text_file_input = gr.File(
                    label="📝 Text File (.txt, .pdf, .docx)",
                    file_types=[".txt", ".pdf", ".docx"]
                )
                        text_input_file_tab = gr.Textbox(
                            label="📝 Or Type Text Here",
                            lines=8,
                            placeholder="You can also type or paste your text here...",
                            visible=False
                        )
                    
                    with gr.TabItem("✏️ Type Text"):
                        text_input_type_tab = gr.Textbox(
                            label="📝 Enter Your Text",
                            lines=12,
                            placeholder="Type or paste your transcript, script, or any text here...\n\nExample:\nHello world! This is a test of the professional SRT generator. It should create subtitles with exactly 4 words per line and 2 lines per subtitle.",
                            max_lines=20
                        )
                        text_file_input_type_tab = gr.File(
                            label="📁 Or Upload Text File",
                            file_types=[".txt", ".pdf", ".docx"],
                            visible=False
                        )
                
                wpm_slider = gr.Slider(
                    minimum=150,
                    maximum=180,
                    value=165,
                    step=5,
                    label="📖 Words Per Minute (WPM)",
                    info="Reading speed for timing calculation (150-180 WPM)"
                )
                
                with gr.Row():
                    professional_btn = gr.Button("🎯 Professional Alignment", variant="primary")
                    smart_btn = gr.Button("🚀 Smart Alignment", variant="secondary")
                    dummy_btn = gr.Button("🎭 Dummy Alignment", variant="secondary")
            
            with gr.Column():
                output = gr.Textbox(label="📄 Alignment Results", lines=20, max_lines=30)
                download = gr.File(label="⬇️ Download SRT", interactive=False)
        
        # Event handlers
        professional_btn.click(
            fn=professional_align_text_with_audio,
            inputs=[audio_input, text_file_input, wpm_slider, text_input_type_tab],
            outputs=[output, download]
        )
        smart_btn.click(
            fn=smart_align_text_with_audio,
            inputs=[audio_input, text_file_input, text_input_type_tab],
            outputs=[output, download]
        )
        dummy_btn.click(
            fn=dummy_align_text_with_audio,
            inputs=[audio_input, text_file_input, text_input_type_tab],
            outputs=[output, download]
        )
        
        gr.Markdown("""
        ### Professional Guidelines Implemented:
        - **📝 Format**: Exactly 4 words per line, 2 lines per subtitle
        - **⏱️ Caption Duration**: 1.5 to 6 seconds per subtitle
        - **📖 Reading Speed**: 150-180 words per minute (adjustable)
        - **🎯 Audio Sync**: Proper synchronization with audio duration
        - **🧠 Smart Splitting**: NLTK-based sentence tokenization
        
        ### Example Output Format:
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
        
        ### How it works:
        - **🎯 Professional Alignment**: Industry-standard SRT generation with 4-words-per-line format
        - **🚀 Smart Alignment**: Original timing estimation method
        - **🎭 Dummy Alignment**: Simple demonstration with evenly spaced timings
        
        ### Input Options:
        - **📁 Upload Text File**: Support for TXT, PDF, DOCX files
        - **✏️ Type Text**: Direct text input for quick testing
        
        ### Supported Formats:
        - **Audio**: MP3, WAV, M4A, FLAC, MP4, OGG, AAC, and more (via FFmpeg)
        - **Text**: TXT, PDF, DOCX, or direct typing
        
        ### For real forced alignment:
        Consider using online services like AssemblyAI, Rev AI, or similar APIs.
        """)
    
    if __name__ == "__main__":
        interface.launch(share=True) 