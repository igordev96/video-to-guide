"""
Fetches YouTube video transcripts using the youtube-transcript-api library.
Usage: python fetch_transcript.py "<YouTube_URL or video_id>"
"""

import sys
import subprocess
import re

def extract_video_id(url_or_id):
    """Extract video ID from a YouTube URL or use the string directly as ID."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id.strip()

def normalize_encoding(text):
    """Fix common encoding issues in YouTube transcripts."""
    replacements = [
        ("—", "—"),  # em-dash
        ("“", '"'),  # left double quote
        ("”", '"'),  # right double quote
        ("‘", "'"),  # left single quote
        ("’", "'"),  # right single quote / apostrophe
    ]
    for garbled, correct in replacements:
        text = text.replace(garbled, correct)
    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_transcript.py <YouTube_URL or video_id>")
        sys.exit(1)

    input_arg = sys.argv[1]
    video_id = extract_video_id(input_arg)

    try:
        result = subprocess.run(
            ["python", "-m", "youtube_transcript_api", video_id],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60
        )
        if result.returncode == 0:
            normalized = normalize_encoding(result.stdout)
            print(normalized)
        else:
            print(f"Error: {result.stderr}")
            sys.exit(1)
    except FileNotFoundError:
        print("Error: youtube-transcript-api not found. Install with: pip install youtube-transcript-api")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Error: Request timed out. The video may be unavailable or has no transcript.")
        sys.exit(1)

if __name__ == "__main__":
    main()