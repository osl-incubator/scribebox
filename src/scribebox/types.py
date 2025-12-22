"""Public transcript types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TranscriptSegment:
    """A transcript segment.

    Parameters
    ----------
    start_s:
        Segment start timestamp in seconds.
    end_s:
        Segment end timestamp in seconds.
    text:
        Segment text.
    """

    start_s: float
    end_s: float
    text: str


@dataclass(frozen=True, slots=True)
class Transcript:
    """A full transcript.

    Parameters
    ----------
    text:
        Transcript full text.
    segments:
        Segment-level transcript.
    language:
        Detected language (if provided by the backend).
    """

    text: str
    segments: list[TranscriptSegment]
    language: str | None
