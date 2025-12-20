"""Transcript formatting and output."""

from __future__ import annotations

from pathlib import Path

from .types import Segment


def format_transcript(segments: list[Segment]) -> str:
    """Combine segments into a readable transcript.

    Parameters
    ----------
    segments:
        Ordered segments.

    Returns
    -------
    str
        Combined text.
    """

    parts: list[str] = []
    for seg in segments:
        txt = seg.text.strip()
        if txt:
            parts.append(txt)
    return "\n".join(parts).strip() + "\n"


def write_text(path: Path, text: str) -> Path:
    """Write plain text to disk.

    Parameters
    ----------
    path:
        Output file path.
    text:
        Content.

    Returns
    -------
    pathlib.Path
        The same path.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
