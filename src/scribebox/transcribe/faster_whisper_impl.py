"""Faster-Whisper transcriber implementation."""

from __future__ import annotations

from pathlib import Path

from ..types import Segment
from .base import TranscriptionResult, Transcriber


class FasterWhisperTranscriber(Transcriber):
    """Transcriber based on `faster-whisper`."""

    def __init__(self) -> None:
        from faster_whisper import WhisperModel  # type: ignore

        self._WhisperModel = WhisperModel

    def transcribe(
        self,
        audio_path: Path,
        *,
        language: str | None,
        translate_to_english: bool,
        model: str,
        device: str,
    ) -> TranscriptionResult:
        """Transcribe audio using `faster-whisper`.

        Parameters
        ----------
        audio_path:
            Input WAV file.
        language:
            Optional language code.
        translate_to_english:
            If True, run in translate mode.
        model:
            Model name, e.g. "base", "small", "medium".
        device:
            Device hint, e.g. "cpu" or "cuda".

        Returns
        -------
        TranscriptionResult
            Transcription output.
        """

        task = "translate" if translate_to_english else "transcribe"
        fw_model = self._WhisperModel(model, device=device)
        segments_iter, info = fw_model.transcribe(
            str(audio_path),
            language=language,
            task=task,
        )

        segments: list[Segment] = []
        for seg in segments_iter:
            segments.append(
                Segment(
                    start_s=float(seg.start),
                    end_s=float(seg.end),
                    text=str(seg.text).strip(),
                )
            )

        lang = getattr(info, "language", None)
        if not isinstance(lang, str):
            lang = None

        return TranscriptionResult(segments=segments, language=lang)
