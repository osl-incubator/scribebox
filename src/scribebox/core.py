"""Core orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import scribebox.backends as backends
from scribebox.backends import ProgressCallback, TranscribeOptions
from scribebox.pdf import write_pdf


@dataclass(frozen=True, slots=True)
class RunResult:
    """Result of a run."""

    text_path: Path
    pdf_path: Path | None
    detected_language: str | None


def run_transcription(
    *,
    audio_path: Path,
    outdir: Path,
    pdf: bool,
    backend: str,
    options: TranscribeOptions,
    title: str | None = None,
    progress_cb: ProgressCallback | None = None,
) -> RunResult:
    """Transcribe an audio file and write TXT/PDF outputs."""
    outdir.mkdir(parents=True, exist_ok=True)

    transcript = backends.transcribe_file(
        audio_path=audio_path,
        backend=backend,
        options=options,
        progress_cb=progress_cb,
    )

    txt_path = outdir / f"{audio_path.stem}.txt"
    txt_path.write_text(transcript.text + "\n", encoding="utf-8")

    pdf_path: Path | None = None
    if pdf:
        pdf_path = outdir / f"{audio_path.stem}.pdf"
        write_pdf(text=transcript.text, output_path=pdf_path, title=title)

    return RunResult(
        text_path=txt_path,
        pdf_path=pdf_path,
        detected_language=transcript.language,
    )
