"""Transcription backends."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .types import Transcript, TranscriptSegment

ProgressCallback = Callable[[float], None]


@dataclass(frozen=True, slots=True)
class TranscribeOptions:
    """Transcription options.

    Parameters
    ----------
    model:
        Model name or path. Default is ``large-v3``.
    language:
        Two-letter language code (e.g. ``en``). If None, auto-detect.
    translate:
        If True, translate into English when supported.
    device:
        Inference device (e.g. ``cpu``, ``cuda``).
    compute_type:
        Quantization/compute type for faster-whisper (e.g. ``int8``).
    vad_filter:
        If True, apply VAD filtering when supported.
    beam_size:
        Beam size for decoding when supported.
    initial_prompt:
        Optional prompt/glossary to bias decoding.
    """

    model: str = "large-v3"
    language: str | None = None
    translate: bool = False
    device: str = "cpu"
    compute_type: str = "int8"
    vad_filter: bool = True
    beam_size: int = 5
    initial_prompt: str | None = None


def transcribe_file(
    *,
    audio_path: Path,
    backend: str,
    options: TranscribeOptions,
    progress_cb: ProgressCallback | None = None,
) -> Transcript:
    """Transcribe a local audio file.

    Parameters
    ----------
    audio_path:
        Path to a local audio file.
    backend:
        ``faster-whisper`` or ``whisper``.
    options:
        Transcription options.
    progress_cb:
        Optional callback receiving the current processed time (seconds).

    Returns
    -------
    Transcript
        Transcription result.
    """
    if backend == "faster-whisper":
        return _transcribe_faster_whisper(
            audio_path=audio_path,
            options=options,
            progress_cb=progress_cb,
        )
    if backend == "whisper":
        return _transcribe_whisper(
            audio_path=audio_path,
            options=options,
            progress_cb=progress_cb,
        )
    raise ValueError(f"Unsupported backend: {backend}")


def _transcribe_faster_whisper(
    *,
    audio_path: Path,
    options: TranscribeOptions,
    progress_cb: ProgressCallback | None,
) -> Transcript:
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:  # pragma: no cover
        raise ImportError(
            "faster-whisper is not installed. "
            "Install with: pip install -e '.[faster-whisper]'"
        ) from exc

    model = WhisperModel(
        options.model,
        device=options.device,
        compute_type=options.compute_type,
    )

    task = "translate" if options.translate else "transcribe"

    try:
        segments_iter, info = model.transcribe(
            str(audio_path),
            language=options.language,
            task=task,
            vad_filter=options.vad_filter,
            beam_size=options.beam_size,
            initial_prompt=options.initial_prompt,
        )
    except RuntimeError as exc:
        msg = str(exc)
        if "onnxruntime" in msg.lower() and options.vad_filter:
            raise RuntimeError(
                "VAD filtering requires 'onnxruntime'. Either install it, "
                "or re-run with --no-vad."
            ) from exc
        raise

    segments: list[TranscriptSegment] = []
    texts: list[str] = []

    last_end = 0.0
    for seg in segments_iter:
        seg_text = str(seg.text).strip()
        end_s = float(seg.end)
        segments.append(
            TranscriptSegment(
                start_s=float(seg.start),
                end_s=end_s,
                text=seg_text,
            )
        )
        if seg_text:
            texts.append(seg_text)

        if progress_cb is not None and end_s >= last_end:
            last_end = end_s
            progress_cb(end_s)

    detected = getattr(info, "language", None)
    return Transcript(
        text="\n".join(texts).strip(),
        segments=segments,
        language=detected,
    )


def _transcribe_whisper(
    *,
    audio_path: Path,
    options: TranscribeOptions,
    progress_cb: ProgressCallback | None,
) -> Transcript:
    try:
        import whisper
    except Exception as exc:  # pragma: no cover
        raise ImportError(
            "openai-whisper is not installed. "
            "Install with: pip install -e '.[whisper]'"
        ) from exc

    model = whisper.load_model(options.model)
    task = "translate" if options.translate else "transcribe"

    result = model.transcribe(
        str(audio_path),
        language=options.language,
        task=task,
        initial_prompt=options.initial_prompt,
        verbose=False,
    )

    segs: list[TranscriptSegment] = []
    texts: list[str] = []

    last_end = 0.0
    for seg in result.get("segments", []) or []:
        seg_text = str(seg.get("text", "")).strip()
        end_s = float(seg.get("end", 0.0))
        segs.append(
            TranscriptSegment(
                start_s=float(seg.get("start", 0.0)),
                end_s=end_s,
                text=seg_text,
            )
        )
        if seg_text:
            texts.append(seg_text)
        if progress_cb is not None and end_s >= last_end:
            last_end = end_s
            progress_cb(end_s)

    return Transcript(
        text="\n".join(texts).strip(),
        segments=segs,
        language=result.get("language"),
    )
