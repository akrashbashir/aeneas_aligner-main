"""
Professional SRT Subtitle Generator - Web Application

A user-friendly web interface for generating professional SRT subtitle files
from text transcripts and audio/video files.
"""

import os
import sys

# Import the core SRT generation functionality
from srt_generator import (
    professional_align_text_with_audio,
    smart_align_text_with_audio,
    dummy_align_text_with_audio
)

# Import Gradio for the web interface
try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False
    gr = None
    print("❌ Gradio not installed. Please install it first: pip install gradio")
    print("You can still use the alignment functions directly in Python.")
    sys.exit(1)


def create_interface():
    """Create the Gradio web interface"""
    
    with gr.Blocks(title="🎧 Professional SRT Subtitle Generator") as interface:
        gr.Markdown("# 🎧 Professional SRT Subtitle Generator")
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
                    
                    with gr.TabItem("✏️ Type Text"):
                        text_input_type_tab = gr.Textbox(
                            label="📝 Enter Your Text",
                            lines=12,
                            placeholder="Type or paste your transcript, script, or any text here...\n\nExample:\nHello world! This is a test of the professional SRT generator. It should create subtitles with exactly 4 words per line and 2 lines per subtitle.",
                            max_lines=20
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
    
    return interface


def main():
    """Main function to run the application"""
    print("🎧 Starting Professional SRT Subtitle Generator...")
    print("📝 Loading web interface...")
    
    interface = create_interface()
    
    print("🚀 Launching web interface...")
    print("🌐 The application will open in your browser shortly.")
    print("📖 For help, see the README.md file.")
    
    # Launch the interface
    interface.launch(
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,       # Default Gradio port
        share=True,             # Create public link
        show_error=True,        # Show detailed errors
        quiet=False             # Show launch information
    )


if __name__ == "__main__":
    main() 