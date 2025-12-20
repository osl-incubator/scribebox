"""Factory for selecting a transcriber implementation."""

from __future__ import annotations

from .base import Transcriber
from ..exceptions import DependencyMissingError


def build_transcriber(prefer: str = "faster-whisper") -> Transcriber:
    """Build a transcriber.

    Parameters
    ----------
    prefer:
        Either ``"faster-whisper"`` or ``"whisper"``.

    Returns
    -------
    Transcriber
        A transcriber implementation.

    Raises
    ------
    DependencyMissingError
        If no supported transcriber is available.
    """

    prefer_norm = prefer.strip().lower()
    if prefer_norm == "faster-whisper":
        try:
            from .faster_whisper_impl import FasterWhisperTranscriber
        except Exception:
            prefer_norm = "whisper"
        else:
            return FasterWhisperTranscriber()

    if prefer_norm == "whisper":
        try:
            from .whisper_impl import WhisperTranscriber
        except Exception as exc:
            raise DependencyMissingError(
                "No transcriber backend is installed. Install either "
                "`scribebox[faster-whisper]` or `scribebox[whisper]`."
            ) from exc
        return WhisperTranscriber()

    raise DependencyMissingError(
        'Unknown transcriber preference. Use "faster-whisper" or "whisper".'
    )
