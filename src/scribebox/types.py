"""Shared types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Segment:
    """A single transcription segment.

    Parameters
    ----------
    start_s:
        Segment start time in seconds.
    end_s:
        Segment end time in seconds.
    text:
        Segment text.
    """

    start_s: float
    end_s: float
    text: str
