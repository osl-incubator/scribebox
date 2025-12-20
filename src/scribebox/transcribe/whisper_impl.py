"""OpenAI-Whisper transcriber implementation."""

from __future__ import annotations

from pathlib import Path

from ..types import Segment
from .base import TranscriptionResult, Transcriber


class WhisperTranscriber(Transcriber):
    """Transcriber based on `openai-whisper`."""

    def __init__(self) -> None:
        import whisper  # type: ignore

        self._whisper = whisper

    def transcribe(
        self,
        audio_path: Path,
        *,
        language: str | None,
        translate_to_english: bool,
        model: str,
        device: str,
    ) -> TranscriptionResult:
        """Transcribe audio using `openai-whisper`.

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
        w_model = self._whisper.load_model(model, device=device)

        kwargs: dict[str, object] = {"task": task}
        if language is not None:
            kwargs["language"] = language

        result = w_model.transcribe(str(audio_path), **kwargs)
        segments_raw = result.get("segments") or []
        detected_lang = result.get("language")

        segments: list[Segment] = []
        if isinstance(segments_raw, list):
            for item in segments_raw:
                if not isinstance(item, dict):
                    continue
                text = str(item.get("text", "")).strip()
                start = float(item.get("start", 0.0))
                end = float(item.get("end", 0.0))
                if text:
                    segments.append(Segment(start_s=start, end_s=end, text=text))

        lang: str | None
        lang = detected_lang if isinstance(detected_lang, str) else None
        return TranscriptionResult(segments=segments, language=lang)
