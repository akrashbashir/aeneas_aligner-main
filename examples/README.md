# Examples

This directory contains example files for testing the SRT Subtitle Generator.

## Files

- `sample_transcript.txt` - A sample transcript for testing the subtitle generation
- `sample_audio.mp3` - (Add your own audio file for testing)

## Usage

1. Use the sample transcript to test text input functionality
2. Add your own audio file to test the complete alignment process
3. The sample transcript is designed to demonstrate the 4-words-per-line format

## Testing

You can test the application with these files:

```bash
# Run the web application
python app.py

# Then upload the sample files through the web interface
```

## Expected Output

The sample transcript should generate subtitles like:

```
1
00:00:00,000 --> 00:00:02,500
Hello world! This is
a test of the professional

2
00:00:02,500 --> 00:00:05,000
SRT subtitle generator. It
should create subtitles with
```

## Note

- Add your own audio files for complete testing
- The sample transcript is designed to work with any audio duration
- Adjust the WPM setting to match your audio content 