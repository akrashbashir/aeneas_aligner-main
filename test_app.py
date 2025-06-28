#!/usr/bin/env python3
"""
Test script for the SRT Subtitle Generator

This script tests the core functionality without requiring audio files.
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from srt_generator import (
    split_text_into_sentences,
    split_long_sentence,
    estimate_duration,
    format_srt_time,
    generate_srt_content,
    synchronize_with_audio
)


def test_text_processing():
    """Test text processing functions"""
    print("🧪 Testing text processing functions...")
    
    # Test sample text
    sample_text = "Hello world! This is a test of the professional SRT generator. It should create subtitles with exactly four words per line and two lines per subtitle."
    
    # Test sentence splitting
    sentences = split_text_into_sentences(sample_text)
    print(f"✅ Sentence splitting: {len(sentences)} sentences found")
    for i, sentence in enumerate(sentences, 1):
        print(f"   {i}. {sentence}")
    
    # Test subtitle splitting
    print("\n📝 Testing subtitle splitting (4 words per line):")
    for sentence in sentences:
        blocks = split_long_sentence(sentence)
        print(f"   Sentence: {sentence}")
        for j, block in enumerate(blocks, 1):
            print(f"   Block {j}: {block}")
    
    return True


def test_timing_functions():
    """Test timing and duration functions"""
    print("\n⏱️ Testing timing functions...")
    
    # Test duration estimation
    test_text = "Hello world! This is a test."
    duration = estimate_duration(test_text, wpm=165)
    print(f"✅ Duration estimation: '{test_text}' -> {duration:.2f}s")
    
    # Test SRT time formatting
    test_times = [0.0, 1.5, 65.123, 3661.999]
    for time in test_times:
        formatted = format_srt_time(time)
        print(f"✅ Time formatting: {time}s -> {formatted}")
    
    return True


def test_srt_generation():
    """Test SRT content generation"""
    print("\n📄 Testing SRT generation...")
    
    # Test with sample sentences
    sentences = [
        "Hello world! This is a test.",
        "The SRT generator should work properly.",
        "Each subtitle should have exactly four words per line."
    ]
    
    # Generate SRT entries
    srt_entries = synchronize_with_audio(sentences, audio_duration=30.0, wpm=165)
    print(f"✅ Generated {len(srt_entries)} SRT entries")
    
    # Generate SRT content
    srt_content = generate_srt_content(srt_entries)
    print("✅ SRT content generated successfully")
    print("\n📝 Sample SRT output:")
    print("=" * 50)
    print(srt_content[:500] + "..." if len(srt_content) > 500 else srt_content)
    print("=" * 50)
    
    return True


def test_dependencies():
    """Test if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    dependencies = {
        'nltk': 'NLTK for sentence tokenization',
        'gradio': 'Gradio for web interface',
        'pdfminer.six': 'PDF text extraction',
        'python-docx': 'DOCX file support'
    }
    
    missing = []
    for dep, description in dependencies.items():
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}: {description}")
        except ImportError:
            print(f"❌ {dep}: {description} (not installed)")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Run all tests"""
    print("🎧 SRT Subtitle Generator - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Text Processing", test_text_processing),
        ("Timing Functions", test_timing_functions),
        ("SRT Generation", test_srt_generation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        print("\n🚀 To run the web application:")
        print("   python app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 