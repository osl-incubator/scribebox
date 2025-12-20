"""Orchestration for the transcription pipeline."""

from __future__ import annotations

import hashlib
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .config import OutputOptions, TranscribeOptions
from .exceptions import InvalidInputError
from .ffmpeg import convert_to_wav_16k_mono
from .pdf import write_pdf
from .transcribe.base import Transcriber, TranscriptionResult
from .transcript import format_transcript, write_text
from .youtube import download_youtube_audio


@dataclass(frozen=True, slots=True)
class PipelineOutputs:
    """Paths produced by a pipeline run.

    Parameters
    ----------
    text_path:
        Path to the generated text transcript.
    pdf_path:
        Path to the generated PDF transcript, if requested.
    language:
        Detected or used language.
    """

    text_path: Path
    pdf_path: Path | None
    language: str | None


def _hash_source_id(source_id: str) -> str:
    digest = hashlib.sha256(source_id.encode("utf-8")).hexdigest()
    return digest[:16]


def transcribe_youtube_url(
    url: str,
    *,
    transcriber: Transcriber,
    options: TranscribeOptions,
    outputs: OutputOptions,
) -> PipelineOutputs:
    """Transcribe audio from a YouTube URL.

    Parameters
    ----------
    url:
        YouTube URL.
    transcriber:
        Transcriber implementation.
    options:
        Transcription options.
    outputs:
        Output options.

    Returns
    -------
    PipelineOutputs
        Output paths and detected language.
    """

    if not url.strip():
        raise InvalidInputError("YouTube URL cannot be empty.")

    with tempfile.TemporaryDirectory(prefix="scribebox_") as tmpdir:
        tmp = Path(tmpdir)
        downloaded = download_youtube_audio(url, tmp)
        return transcribe_local_file(
            downloaded,
            source_id=url,
            transcriber=transcriber,
            options=options,
            outputs=outputs,
        )


def transcribe_local_file(
    input_path: Path,
    *,
    source_id: str | None = None,
    transcriber: Transcriber,
    options: TranscribeOptions,
    outputs: OutputOptions,
) -> PipelineOutputs:
    """Transcribe a local media file.

    Parameters
    ----------
    input_path:
        Input media file.
    source_id:
        Optional stable identifier to name outputs (e.g., the URL).
    transcriber:
        Transcriber implementation.
    options:
        Transcription options.
    outputs:
        Output options.

    Returns
    -------
    PipelineOutputs
        Output paths and detected language.
    """

    if not input_path.exists():
        raise InvalidInputError(f"File does not exist: {input_path}")

    source = source_id or str(input_path.resolve())
    stem = _hash_source_id(source)

    outdir = outputs.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    wav_path = outdir / f"{stem}.wav"
    txt_path = outdir / f"{stem}.txt"
    pdf_path = outdir / f"{stem}.pdf" if outputs.write_pdf else None

    convert_to_wav_16k_mono(input_path, wav_path)

    result = transcriber.transcribe(
        wav_path,
        language=options.language,
        translate_to_english=options.translate_to_english,
        model=options.model,
        device=options.device,
    )

    transcript = format_transcript(result.segments)
    write_text(txt_path, transcript)

    if pdf_path is not None:
        title = f"Scribebox transcript ({stem})"
        write_pdf(pdf_path, title=title, text=transcript)

    return PipelineOutputs(
        text_path=txt_path,
        pdf_path=pdf_path,
        language=result.language,
    )
