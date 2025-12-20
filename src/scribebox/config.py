"""Configuration models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class TranscribeOptions:
    """Options for the transcription pipeline.

    Parameters
    ----------
    language:
        Source language code (e.g., ``"en"``). Use ``None`` for auto-detect.
    translate_to_english:
        If ``True``, attempt to translate to English instead of transcribing in
        the source language (supported by Whisper-family models).
    model:
        Model identifier to pass to the transcriber implementation.
    device:
        Device hint for the transcriber (e.g., ``"cpu"``, ``"cuda"``).
    """

    language: str | None = None
    translate_to_english: bool = False
    model: str = "base"
    device: str = "cpu"


@dataclass(frozen=True, slots=True)
class OutputOptions:
    """Options for writing outputs.

    Parameters
    ----------
    outdir:
        Directory where outputs will be written.
    write_pdf:
        If ``True``, also write a PDF.
    """

    outdir: Path
    write_pdf: bool = False
