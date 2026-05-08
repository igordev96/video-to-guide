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

# Exit codes
EXIT_SUCCESS = 0
EXIT_GENERIC = 1
EXIT_NO_TRANSCRIPTS = 2
EXIT_INVALID_URL = 3
EXIT_NETWORK = 4

def extract_video_id(url_or_id):
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    video_id = url_or_id.strip()
    if len(video_id) == 11 and re.match(r'^[0-9A-Za-z_-]+$', video_id):
        return video_id
    print("Error: Invalid URL or video ID", file=sys.stderr)
    sys.exit(EXIT_INVALID_URL)

def get_video_title(video_id):
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("title", f"Video {video_id}")
    except urllib.error.HTTPError:
        raise
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
    detected_language = None

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
            detected_language = lang
            return title, entries, detected_language
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
            detected_language = chosen.language_code
            return title, entries, detected_language
    except Exception:
        pass

    print("Error: No transcripts available for this video.", file=sys.stderr)
    sys.exit(EXIT_NO_TRANSCRIPTS)

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) < 2:
        print("Usage: uv run scripts/fetch_transcript.py <YouTube_URL> [--json] [--language <code>]", file=sys.stderr)
        sys.exit(EXIT_GENERIC)

    use_json = "--json" in sys.argv
    preferred_languages = ["en", "pt", "es"]

    lang_idx = None
    if "--language" in sys.argv:
        lang_idx = sys.argv.index("--language")
        if lang_idx + 1 < len(sys.argv):
            preferred_languages = [sys.argv[lang_idx + 1]]

    video_arg = sys.argv[1]
    video_id = extract_video_id(video_arg)

    try:
        title, entries, language = fetch_transcript(video_id, preferred_languages)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("Error: Video not found (404)", file=sys.stderr)
            sys.exit(EXIT_INVALID_URL)
        print("Error: Network error while fetching video", file=sys.stderr)
        sys.exit(EXIT_NETWORK)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_GENERIC)

    if use_json:
        output = {
            "title": title,
            "video_id": video_id,
            "language": language,
            "entries": entries
        }
        print(json.dumps(output, ensure_ascii=False))
    else:
        print(f"TITLE: {title}")
        print("-" * 40)
        for entry in entries:
            text = normalize_encoding(entry["text"])
            print(text)

if __name__ == "__main__":
    main()