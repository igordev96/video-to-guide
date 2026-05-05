"""
Fetches YouTube video transcripts using the youtube-transcript-api library.
Usage: python fetch_transcript.py "<YouTube_URL or video_id>"

Features:
- In-process API call (no subprocess — works with uv, venv, or system Python)
- Automatic language fallback (en -> pt -> es -> auto-generated)
- Fetches video title via oEmbed API
- UTF-8 output on Windows
"""

import sys
import json
import re
import urllib.request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

def extract_video_id(url_or_id):
    """Extract video ID from a YouTube URL or use the string directly as ID."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id.strip()

def get_video_title(video_id):
    """Fetch video title via oEmbed API."""
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("title", f"Video {video_id}")
    except Exception:
        return f"Video {video_id}"

def normalize_encoding(text):
    """Fix common double-encoding artifacts in YouTube auto-transcripts.

    These are UTF-8 bytes that got decoded as Windows-1252 then re-encoded as UTF-8.
    Written as hex escapes to avoid any encoding issues in the source file.
    """
    replacements = [
        ("\xc3\xa2\xc2\x80\xc2\x94", "\xe2\x80\x94"),  # em-dash
        ("\xc3\xa2\xc2\x80\xc2\x9c", "\xe2\x80\x9c"),  # left double quote
        ("\xc3\xa2\xc2\x80\xc2\x9d", "\xe2\x80\x9d"),  # right double quote
        ("\xc3\xa2\xc2\x80\xc2\x98", "\xe2\x80\x98"),  # left single quote
        ("\xc3\xa2\xc2\x80\xc2\x99", "\xe2\x80\x99"),  # right single quote / apostrophe
        ("\xc3\x83\xc2\xa9", "\xc3\xa9"),               # e with acute (UTF-8 char left as two chars)
        ("\xc3\x83\xc2\xa7", "\xc3\xa7"),               # c cedilla
        ("\xc3\x83\xc2\xa3", "\xc3\xa3"),               # a with tilde
        ("\xc3\x83\xc2\xa0", "\xc3\xa0"),               # a with grave
        ("\xc3\x83\xc2\xad", "\xc3\xad"),               # i with acute
        ("\xc3\x83\xc2\xb3", "\xc3\xb3"),               # o with acute
        ("\xc3\x83\xc2\xba", "\xc3\xba"),               # u with acute
        ("\xc3\x83\xc2\xaa", "\xc3\xaa"),               # i with circumflex (sometimes left as two chars)
    ]
    for garbled, correct in replacements:
        text = text.replace(garbled, correct)
    return text

def fetch_transcript(video_id, preferred_languages=None):
    """
    Fetch transcript with automatic language fallback.

    Args:
        video_id: YouTube video ID
        preferred_languages: list of language codes to try (in order)
        Returns: (title, list of transcript entries)
    """
    if preferred_languages is None:
        preferred_languages = ["en", "pt", "es"]

    title = get_video_title(video_id)

    # Create API instance and try to fetch directly with preferred languages
    api = YouTubeTranscriptApi()

    for lang in preferred_languages:
        try:
            fetched = api.fetch(video_id, languages=[lang])
            entries = []
            for entry in fetched:
                entries.append({
                    "text": entry.text,
                    "start": entry.start,
                    "duration": entry.duration
                })
            return title, entries
        except Exception:
            continue

    # Last resort: try to get any transcript that's available
    try:
        # List available transcripts to find any usable one
        transcript_list = api.list(video_id)
        all_transcripts = list(transcript_list)

        if all_transcripts:
            # Prefer manually created over auto-generated
            manual = [t for t in all_transcripts if not t.is_generated]
            auto = [t for t in all_transcripts if t.is_generated]
            chosen = manual[0] if manual else auto[0]

            fetched = chosen.fetch()
            entries = []
            for entry in fetched:
                entries.append({
                    "text": entry.text,
                    "start": entry.start,
                    "duration": entry.duration
                })
            return title, entries
    except Exception:
        pass

    print("Error: No transcripts available for this video.")
    sys.exit(1)

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) < 2:
        print("Usage: python fetch_transcript.py <YouTube_URL or video_id> [--language CODE]")
        sys.exit(1)

    preferred_languages = ["en", "pt", "es"]
    video_arg = sys.argv[1]

    if len(sys.argv) > 2 and sys.argv[2] == "--language":
        if len(sys.argv) > 3:
            preferred_languages = [sys.argv[3]]

    video_id = extract_video_id(video_arg)
    title, entries = fetch_transcript(video_id, preferred_languages)

    print(f"TITLE: {title}")
    print("-" * 40)

    for entry in entries:
        text = normalize_encoding(entry["text"])
        print(text)

if __name__ == "__main__":
    main()