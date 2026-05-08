# Video to Guide 📺📝

An AI skill that creates **massive, detailed study guides** from YouTube videos — every detail preserved, no summarizing.

Unlike simple summarizers that strip out the nuance, this skill extracts every example, explanation, and point to produce a document you can actually study from without watching the video.

## Install

```bash
npx skills add igordev96/video-to-guide
```

## Usage

Paste a YouTube URL with a phrase like:

- "turn this video into a guide"
- "convert this video into a study guide"
- "create a guide from this video"
- "make a written guide from this YouTube video"

The skill will:
1. Fetch the transcript automatically (handles language fallback)
2. Clean up encoding artifacts
3. Build a structured guide with headers, bullet points, and a Key Takeaways section

## Setup for Work Environments

The script uses [uv](https://github.com/astral-sh/uv) and automatically installs its dependency. If `uv` is not available, install manually:

```bash
# uv (recommended — auto-installs dependencies)
uv run scripts/fetch_transcript.py "<YouTube_URL>"

# Manual dependency
pip install youtube-transcript-api
python scripts/fetch_transcript.py "<YouTube_URL>"
```

On Windows, always write output to a `.md` file directly rather than relying on terminal display to avoid garbled characters.

## Features

- **Automatic language fallback**: tries English → Portuguese → Spanish → any available transcript
- **Non-English videos**: fetches native-language transcripts and translates them into English for the guide
- **Encoding normalization**: fixes garbled characters that often appear in YouTube auto-transcripts
- **No summarizing**: every example, nuance, and explanation is preserved
- **Video title auto-fetch**: extracts the title via oEmbed API so the guide header is accurate

## Example

**Input:**
> turn this video into a guide: https://www.youtube.com/watch?v=WL6VSc5XQ-8

**Output:**
A full structured markdown guide with:
- Video title as H1
- Overview section
- Detailed Breakdown by topic
- Context section (if applicable)
- Key Takeaways extracted from the full content
- Bolded technical terms, bullet-pointed steps, callouts for emphasized points