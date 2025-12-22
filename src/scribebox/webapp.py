"""Minimal FastAPI web app."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

from .backends import TranscribeOptions
from .core import run_transcription
from .youtube import download_youtube_audio

app = FastAPI(title="scribebox")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Render a small HTML form."""
    return """<!doctype html>
<html>
  <head><meta charset="utf-8"><title>scribebox</title></head>
  <body>
    <h2>scribebox</h2>

    <h3>YouTube URL</h3>
    <form action="/transcribe-url" method="post">
      <input type="text" name="url" size="80" placeholder="YouTube URL" />
      <label><input type="checkbox" name="pdf" /> PDF</label>
      <input type="text" name="language" placeholder="language (e.g. en)" />
      <button type="submit">Transcribe</button>
    </form>

    <h3>Upload audio (mp3/mp4/wav/m4a)</h3>
    <form action="/transcribe-file" method="post"
          enctype="multipart/form-data">
      <input type="file" name="file" />
      <label><input type="checkbox" name="pdf" /> PDF</label>
      <input type="text" name="language" placeholder="language (e.g. en)" />
      <button type="submit">Transcribe</button>
    </form>
  </body>
</html>
"""


@app.post("/transcribe-url")
def transcribe_url(
    url: str = Form(...),
    pdf: bool = Form(False),
    language: str | None = Form(None),
) -> FileResponse:
    """Download and transcribe a YouTube URL."""
    outdir = Path(tempfile.mkdtemp(prefix="scribebox_"))
    audio = download_youtube_audio(url=url, outdir=outdir)

    options = TranscribeOptions(model="large-v3", language=language)
    result = run_transcription(
        audio_path=audio,
        outdir=outdir,
        pdf=pdf,
        backend="faster-whisper",
        options=options,
        title=url,
    )
    chosen = result.pdf_path if pdf else result.text_path
    return FileResponse(path=str(chosen), filename=chosen.name)


@app.post("/transcribe-file")
async def transcribe_file_endpoint(
    file: UploadFile = File(...),
    pdf: bool = Form(False),
    language: str | None = Form(None),
) -> FileResponse:
    """Transcribe an uploaded file."""
    outdir = Path(tempfile.mkdtemp(prefix="scribebox_"))
    path = outdir / (file.filename or "audio.bin")
    path.write_bytes(await file.read())

    options = TranscribeOptions(model="large-v3", language=language)
    result = run_transcription(
        audio_path=path,
        outdir=outdir,
        pdf=pdf,
        backend="faster-whisper",
        options=options,
        title=file.filename,
    )
    chosen = result.pdf_path if pdf else result.text_path
    return FileResponse(path=str(chosen), filename=chosen.name)
