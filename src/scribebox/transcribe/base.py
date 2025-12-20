"""Transcription abstraction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..types import Segment


@dataclass(frozen=True, slots=True)
class TranscriptionResult:
    """Result returned by a transcriber.

    Parameters
    ----------
    segments:
        Ordered list of transcript segments.
    language:
        Detected or used language code.
    """

    segments: list[Segment]
    language: str | None = None


class Transcriber(Protocol):
    """Transcriber protocol."""

    def transcribe(
        self,
        audio_path: Path,
        *,
        language: str | None,
        translate_to_english: bool,
        model: str,
        device: str,
    ) -> TranscriptionResult:
        """Transcribe a WAV file."""
