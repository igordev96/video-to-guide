# /// script
# dependencies = [
#   "youtube-transcript-api",
# ]
# ///

import sys
import json
import re
import urllib.request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

def extract_video_id(url_or_id):
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id.strip()

def get_video_title(video_id):
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("title", f"Video {video_id}")
    except Exception:
        return f"Video {video_id}"

def normalize_encoding(text):
    replacements = [
        ("\xc3\xa2\xc2\x80\xc2\x94", "\xe2\x80\x94"),
        ("\xc3\xa2\xc2\x80\xc2\x9c", "\xe2\x80\x9c"),
        ("\xc3\xa2\xc2\x80\xc2\x9d", "\xe2\x80\x9d"),
        ("\xc3\xa2\xc2\x80\xc2\x98", "\xe2\x80\x98"),
        ("\xc3\xa2\xc2\x80\xc2\x99", "\xe2\x80\x99"),
        ("\xc3\x83\xc2\xa9", "\xc3\xa9"),
        ("\xc3\x83\xc2\xa7", "\xc3\xa7"),
        ("\xc3\x83\xc2\xa3", "\xc3\xa3"),
        ("\xc3\x83\xc2\xa0", "\xc3\xa0"),
        ("\xc3\x83\xc2\xad", "\xc3\xad"),
        ("\xc3\x83\xc2\xb3", "\xc3\xb3"),
        ("\xc3\x83\xc2\xba", "\xc3\xba"),
        ("\xc3\x83\xc2\xaa", "\xc3\xaa"),
    ]
    for garbled, correct in replacements:
        text = text.replace(garbled, correct)
    return text

def fetch_transcript(video_id, preferred_languages=None):
    if preferred_languages is None:
        preferred_languages = ["en", "pt", "es"]

    title = get_video_title(video_id)
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

    try:
        transcript_list = api.list(video_id)
        all_transcripts = list(transcript_list)

        if all_transcripts:
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
        print("Usage: uv run scripts/fetch_transcript.py <YouTube_URL>")
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