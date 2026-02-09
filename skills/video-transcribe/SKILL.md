---
name: video-transcribe
description: Download and transcribe videos from any platform URL (TikTok, X/Twitter, Instagram, Reddit, YouTube, etc.) to text. Use when a user pastes a video URL and wants it downloaded, transcribed, or summarized. Also use for "transcribe this video", "what does this video say", or "download this video".
---

# Video Transcribe

Download videos from any URL via `yt-dlp` and transcribe to text.

## Decision tree

1. **YouTube URL?** → Use `summarize` CLI (fastest, no download needed)
2. **Other platform?** → Use `yt-dlp` to download, then `summarize` on the local file
3. **Need raw video file?** → Use `yt-dlp` without `--extract-audio`

## YouTube (preferred path)

```bash
# Transcript only
summarize "<youtube-url>" --youtube auto --extract-only

# Summary
summarize "<youtube-url>" --youtube auto --length long
```

## Non-YouTube platforms (TikTok, X, Instagram, Reddit, etc.)

```bash
# Download video
yt-dlp -o "/tmp/%(id)s.%(ext)s" "<URL>" 2>&1

# Transcribe via summarize (uses cloud model, fast)
summarize "/tmp/<id>.mp4" --length long

# Or extract audio first for smaller file
yt-dlp -x --audio-format mp3 -o "/tmp/%(id)s.%(ext)s" "<URL>" 2>&1
summarize "/tmp/<id>.mp3" --length long
```

## Download only (keep video)

```bash
yt-dlp -o "/tmp/%(id)s.%(ext)s" "<URL>" 2>&1
# Best quality: yt-dlp -f "bestvideo+bestaudio" -o "/tmp/%(id)s.%(ext)s" "<URL>"
```

## Local Whisper (when offline or for privacy)

Only use on machines with 8GB+ free RAM. The turbo model needs ~6GB.

```bash
yt-dlp -x --audio-format wav -o "/tmp/%(id)s.%(ext)s" "<URL>" 2>&1
whisper /tmp/<id>.wav --model base --language en --output_format txt --output_dir /tmp
```

## Key yt-dlp flags

- `--cookies-from-browser chrome` — auth-gated content
- `--geo-bypass` — geo-blocked content
- `--sleep-interval 2` — rate limiting
- `-x --audio-format mp3` — extract audio only (smaller)
- `--max-filesize 100M` — limit download size

## Supported platforms

1000+ sites: YouTube, TikTok, X/Twitter, Instagram, Reddit, Facebook, Twitch, Vimeo, and many more.

## Cleanup

```bash
rm -f /tmp/<id>.*
```
