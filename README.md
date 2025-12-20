# Scribebox

Scribebox is a small Python app that can:

- Download audio from a **YouTube URL** (via `yt-dlp`)
- Accept a **local MP3/MP4/WAV/M4A** file
- Convert to a transcription (**.txt**) and optionally a **PDF**
- Run as a **CLI** or as a tiny **FastAPI web app**

## Requirements

- Python 3.10+
- `ffmpeg` available in your PATH (needed to normalize audio)
- Optional:
  - `yt-dlp` for YouTube downloads
  - `openai-whisper` or `faster-whisper` for transcription

## Install

```bash
pip install -e ".[dev,youtube,faster-whisper]"
```

If you prefer the original Whisper:

```bash
pip install -e ".[dev,youtube,whisper]"
```

## CLI usage

Transcribe a YouTube URL:

```bash
scribebox url "https://www.youtube.com/watch?v=VIDEO_ID" --outdir out --pdf
```

Transcribe a local file:

```bash
scribebox file /path/to/audio.mp3 --outdir out --pdf
```

## Web app

```bash
uvicorn scribebox.webapp:app --reload
```

Open `http://127.0.0.1:8000/`.

## Notes

- The test suite uses a dummy transcriber, so it does not download models.
- For production, install either `faster-whisper` or `openai-whisper`.
