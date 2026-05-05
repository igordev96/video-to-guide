---
name: video-to-guide
description: Transforms YouTube videos into exhaustive written guides. Use when the user says "turn this video into a guide", "convert this video into a study guide", "create a guide from this video", "make a written guide from this YouTube video", or any variation asking to transform a video into a written, structured format. Handles transcript extraction, language fallback, and cleaning. Automatically fetches the video title and tries English first, then Portuguese and Spanish, then any available transcript.
---

# Video-to-Guide Skill

This skill transforms a YouTube video into a complete, structured written guide. It extracts every instruction, example, and explanation — no details omitted, no summarizing.

## Environment Pre-flight

Before running the transcript script:

1. **Prefer `uv run`** if available — `uv run python scripts/fetch_transcript.py "<URL>"`
2. **Fallback**: `python scripts/fetch_transcript.py "<URL>"`
3. **If dependency missing**: install with `pip install -r requirements.txt` (recommended) or `pip install youtube-transcript-api`
4. **On Windows**: always write output to a `.md` file directly rather than relying on terminal display to avoid garbled characters

## Workflow

1. **Receive a YouTube URL** from the user
2. **Fetch the transcript** by running the bundled script:
   ```bash
   # Prefer uv if available
   uv run python scripts/fetch_transcript.py "<YouTube_URL>"
   # Or just python
   python scripts/fetch_transcript.py "<YouTube_URL>"
   ```
3. **Process and clean** the transcript (remove fillers, fix encoding artifacts, preserve depth and tone)
4. **Structure into a guide** using the format below
5. **Write the guide to a `.md` file** in the user's project directory — do NOT just print it to the terminal. Save it as `[video-title].md` or `guide.md` in the current working directory. Tell the user the file was saved.
6. **Return the guide** (you can also show it inline, but the file is required)

## Transcript Fetching Details

The script automatically:
- Extracts the video ID from URLs or accepts video IDs directly
- Fetches the video title via oEmbed API
- Tries languages in order: English → Portuguese → Spanish → any available auto-generated
- Normalizes encoding artifacts (`â€"` → `—`, etc.)
- Outputs UTF-8 safe text

**Non-English transcripts:** If the video has no English transcript but has a native-language transcript (e.g., Portuguese auto-generated), fetch that transcript and **translate the content into English** while creating the guide. Do not refuse the video. The guide language should match what the user would expect — if they asked in English, deliver in English.

**No transcript available:** If the script fails with "No transcripts available" or "Transcripts disabled", offer the user a choice:

> The script couldn't fetch the transcript automatically (YouTube may have restricted this video). You have two options:
>
> **1. Agentic fetch** — I use my web browsing tools to try to get the transcript directly from the YouTube page (uses more tokens, but handles restricted videos).
>
> **2. Manual paste** — You copy the transcript from YouTube (click the three dots below the video → "Show transcript") and paste it here. Saves tokens and works for any video.
>
> Which do you prefer?

**Option 1 — Agentic Web Fetch:** Use WebFetch to request the YouTube video page and extract the transcript data from the page's JSON data. If the video has a transcript available via the web interface, it can usually be found in the page source. Extract and process it, then proceed to guide creation.

**Option 2 — Manual Paste:** If the user provides transcript text directly, use that instead. Process it the same way — remove fillers, fix encoding, structure into the guide format.

## Guide Structure

Follow this exact format:

```markdown
# [Video Title]

## Overview
[Brief description of what the video covers — 1-2 sentences. Not a summary, just orientation.]

## Detailed Breakdown

### [Topic 1]
[All content related to this topic — every point, example, and nuance captured. Write generously. A video covering a topic in depth should produce a guide that reflects that depth.]

### [Topic 2]
[Continue through the video's logical flow. Do not cut corners on length — if the speaker spent 5 minutes on a topic, your section should be substantial, not a 2-sentence summary.]

## Context (if needed)
[Only if the speaker's wandering was meaningful to a point. Brief 1-2 sentence resume of non-essential but relevant background.]

## Key Takeaways
- [Point 1 — extracted from the full content, not a substitute for it]
- [Point 2]
- [Point 3]
```

## Expected Guide Length

Guides should be **substantial** — not short summaries. If a video is 20-45 minutes and covers a topic thoroughly, the guide should reflect that same depth. A good rule of thumb:
- A 5-minute quick tip video → guide is roughly 400-800 words
- A 20-minute tutorial → guide is roughly 1500-2500 words
- A 45+ minute masterclass → guide is roughly 3000+ words

If your guide feels "short" for the video's length, you are likely condensing. Go deeper — capture the speaker's examples, nuances, tangents that clarified understanding, and every distinct point made. The goal is that someone reading the guide could follow along without watching the video.

## Formatting Rules

1. **Remove fillers**: Strip "um," "uh," "you know," "like," repeated stutters. Do not remove words that carry meaning or emphasis.
2. **Preserve emphasis**: If the speaker repeats something for emphasis, do NOT include all repetitions verbatim. Instead, mark truly important repeated points with a callout:
   ```
   > ⚠️ Key Point (emphasized by speaker): [the point]
   ```
3. **Describe visual references**: When the speaker says "look at this," "click this button," "see this here" — briefly describe the visual element so the text is self-contained.
4. **Use bolding** for: technical terms, key commands, tool names, fundamental concepts.
5. **Use bullet points** for: lists of materials, steps, features, actionable items.
6. **Maintain depth**: If the speaker explains a concept in multiple ways, capture all of them. Do not condense.
7. **No condensation**: Never synthesize or shorten. What was said is what gets written — just organized better.

## Handling the "Meander" Case

- If the speaker goes off-track but lands on something important → capture the landing, briefly note the context in the "Context" section
- If the speaker goes off-track and doesn't land → skip it entirely, no "Context" needed
- If something is important for the learning process → include it fully

## Quality Check

Before returning the guide, verify:
- [ ] Every major topic from the video appears in the guide
- [ ] No section is a thin summary — each has full depth
- [ ] Filler words are removed but meaning is preserved
- [ ] Key Takeaways are genuinely extracted, not synthesized
- [ ] Visual references are described in-context
- [ ] The guide length feels proportional to the video's depth and length
- [ ] Non-English transcripts have been translated to match the user's expected language