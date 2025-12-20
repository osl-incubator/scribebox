"""FastAPI web app."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, PlainTextResponse

from .config import OutputOptions, TranscribeOptions
from .exceptions import ScribeboxError
from .service import transcribe_local_file, transcribe_youtube_url
from .transcribe.factory import build_transcriber


app = FastAPI(title="Scribebox")


_INDEX_HTML = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Scribebox</title>
  </head>
  <body style="font-family: sans-serif; max-width: 820px; margin: 2rem auto;">
    <h1>Scribebox</h1>
    <p>Transcribe YouTube URLs or local audio/video files.</p>

    <h2>YouTube URL</h2>
    <form action="/transcribe/url" method="post">
      <input
        type="text"
        name="url"
        placeholder="https://www.youtube.com/watch?v=..."
        style="width: 100%; padding: 0.6rem;"
      />
      <label style="display:block; margin-top:0.6rem;">
        <input type="checkbox" name="pdf" /> Also generate PDF
      </label>
      <button style="margin-top: 0.8rem; padding: 0.6rem 1rem;">
        Transcribe URL
      </button>
    </form>

    <h2 style="margin-top: 2rem;">Upload file</h2>
    <form action="/transcribe/file" method="post" enctype="multipart/form-data">
      <input type="file" name="file" />
      <label style="display:block; margin-top:0.6rem;">
        <input type="checkbox" name="pdf" /> Also generate PDF
      </label>
      <button style="margin-top: 0.8rem; padding: 0.6rem 1rem;">
        Transcribe file
      </button>
    </form>

    <p style="margin-top: 2rem; color: #555;">
      Outputs are written to <code>./out</code> by default.
    </p>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _INDEX_HTML


@app.post("/transcribe/url")
def transcribe_url(
    url: str = Form(...),
    pdf: str | None = Form(default=None),
) -> PlainTextResponse:
    transcriber = build_transcriber("faster-whisper")
    t_opts = TranscribeOptions()
    o_opts = OutputOptions(outdir=Path("out"), write_pdf=pdf is not None)

    try:
        out = transcribe_youtube_url(
            url,
            transcriber=transcriber,
            options=t_opts,
            outputs=o_opts,
        )
    except ScribeboxError as exc:
        return PlainTextResponse(f"Error: {exc}", status_code=400)

    msg = f"Text: {out.text_path}\n"
    if out.pdf_path is not None:
        msg += f"PDF:  {out.pdf_path}\n"
    return PlainTextResponse(msg)


@app.post("/transcribe/file")
async def transcribe_file(
    file: UploadFile = File(...),
    pdf: str | None = Form(default=None),
) -> PlainTextResponse:
    suffix = Path(file.filename or "upload").suffix or ".bin"
    transcriber = build_transcriber("faster-whisper")
    t_opts = TranscribeOptions()
    o_opts = OutputOptions(outdir=Path("out"), write_pdf=pdf is not None)

    with tempfile.TemporaryDirectory(prefix="scribebox_upload_") as tmpdir:
        tmp_path = Path(tmpdir) / f"upload{suffix}"
        content = await file.read()
        tmp_path.write_bytes(content)

        try:
            out = transcribe_local_file(
                tmp_path,
                source_id=file.filename or "upload",
                transcriber=transcriber,
                options=t_opts,
                outputs=o_opts,
            )
        except ScribeboxError as exc:
            return PlainTextResponse(f"Error: {exc}", status_code=400)

    msg = f"Text: {out.text_path}\n"
    if out.pdf_path is not None:
        msg += f"PDF:  {out.pdf_path}\n"
    return PlainTextResponse(msg)
