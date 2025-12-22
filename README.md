Here’s an **updated, more professional README.md** that matches your current `pyproject.toml` (**v0.2.1**) and documents **every CLI parameter** that exists in the app today, with practical examples and troubleshooting.

````markdown
# scribebox

Local-first transcription for **YouTube URLs** and **audio/video files**
(mp3/mp4/m4a/wav) with optional **PDF export**.

**Default (best free local model):** Whisper **large-v3**

---

## Features

- **YouTube URL** → download audio (MP3) → transcribe to **TXT** (+ optional
  **PDF**)
- **Local media** (mp3/mp4/wav/m4a) → transcribe to **TXT** (+ optional **PDF**)
- Two backends:
  - **faster-whisper** (recommended; fast, accurate; supports CPU int8)
  - **openai-whisper** (fallback; slower)
- **Progress bar with percentage** in the CLI (best-effort, duration-based via
  `ffprobe`)
- Optional **glossary prompt** to improve recognition of names and jargon

---

## Requirements

### System dependency

You need **ffmpeg** (and `ffprobe`) installed and available in `PATH`.

Ubuntu/Pop!_OS:

```bash
sudo apt update
sudo apt install -y ffmpeg
````

Verify:

```bash
ffmpeg -version
ffprobe -version
```

### Python

Recommended: **Python 3.12**.

---

## Install

Create and activate a virtualenv:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
```

Install with YouTube + recommended backend:

```bash
pip install -e ".[youtube,faster-whisper]"
```

Fallback backend (no faster-whisper):

```bash
pip install -e ".[youtube,whisper]"
```

Developer tools:

```bash
pip install -e ".[dev,youtube,faster-whisper]"
```

---

## Quick start

### Transcribe a YouTube URL

```bash
scribebox url "https://www.youtube.com/watch?v=VIDEO_ID" --outdir out --pdf
```

### Transcribe a local file

```bash
scribebox file path/to/audio.mp3 --outdir out --pdf
```

### Force language (English)

```bash
scribebox file audio.mp3 --language en
```

### Reduce CPU RAM usage (int8)

```bash
scribebox file audio.mp3 --compute-type int8
```

---

## CLI usage

General form:

```bash
scribebox [GLOBAL OPTIONS] {url,file} ...
```

Global options can be placed **before or after** the subcommand.

### Subcommands

* `scribebox url <youtube_url>`

  * Downloads audio with `yt-dlp` and produces an MP3 inside `--outdir`.
  * Then transcribes that MP3 and writes outputs to `--outdir`.
* `scribebox file <path>`

  * Transcribes a local media file and writes outputs to `--outdir`.

### Output files

scribebox writes:

* `--outdir/<input_stem>.txt`
* `--outdir/<input_stem>.pdf` (only if `--pdf` is provided)

For `url`, `<input_stem>` is the downloaded MP3 name (usually the video id).

---

## Parameters (all available options)

### Output

* `--outdir PATH`

  * Output directory. Default: `out`
* `--pdf`

  * Also export a PDF in addition to TXT.

### Language and translation

* `--language CODE`

  * Force a language code (example: `en`, `pt`).
  * If omitted, the backend may auto-detect.
* `--translate`

  * Translate speech to English when supported.

### Model and decoding

* `--model NAME_OR_PATH`

  * Model name or local path. Default: `large-v3`.
* `--beam-size N`

  * Beam search size. Default: `5`.
  * Higher values can improve accuracy but increase runtime.

### Backend selection

* `--backend {faster-whisper,whisper}`

  * Default: `faster-whisper`.

### Performance / device

* `--device DEVICE`

  * Default: `cpu`.
  * Example: `cuda` (if you have a supported setup).
* `--compute-type TYPE`

  * `faster-whisper` only. Default: `int8`.
  * Common values: `int8`, `float16`, `float32`.

### VAD

* `--no-vad`

  * Disable VAD filtering (voice activity detection).
  * Useful if VAD cuts audio or if you hit dependency errors related to VAD.

### Prompting

* `--prompt-file PATH`

  * Optional “initial prompt” / glossary file to bias transcription toward
    correct names and domain terms.
  * Best practice: short list of nouns/proper nouns, no storytelling.

Example `prompt.txt`:

```text
The Adjustment Bureau
David Norris
Elise Sellas
Harry Mitchell
Chairman
```

### Progress bar

* `--no-progress`

  * Disable the progress bar.

Progress notes:

* When `ffprobe` is available, scribebox reads total duration and displays
  percentage.
* If duration cannot be read, progress falls back to “seconds processed” without
  a reliable percent.

---

## Examples

### Higher-accuracy English decode (slower)

```bash
scribebox file transc/movie_player_david_norris.mp3 \
  --model large-v3 \
  --language en \
  --beam-size 8 \
  --no-vad \
  --prompt-file prompt.txt
```

### YouTube transcription to a dedicated folder

```bash
mkdir -p transc
scribebox url "https://www.youtube.com/watch?v=VIDEO_ID" --outdir transc --pdf
```

### Disable progress

```bash
scribebox file audio.mp3 --no-progress
```

### Use fallback backend

```bash
scribebox file audio.mp3 --backend whisper --model large-v3 --language en
```

---

## Web app

Run:

```bash
uvicorn scribebox.webapp:app --reload
```

Open: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

The web app provides:

* A minimal page to submit a YouTube URL
* A minimal page to upload a file

Note: the web app does not currently provide live progress. If you want progress
in the browser, typical approaches include background jobs + polling, SSE, or
WebSockets.

---

## Troubleshooting

### No percentage / progress looks wrong

Ensure `ffprobe` is available:

```bash
ffprobe -version
```

### `onnxruntime` / VAD-related issues

Try disabling VAD:

```bash
scribebox file audio.mp3 --no-vad
```

Or use the fallback backend:

```bash
pip install -e ".[youtube,whisper]"
scribebox file audio.mp3 --backend whisper
```

---

## License

MIT

````

---
