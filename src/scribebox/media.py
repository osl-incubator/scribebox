"""Media utilities (ffprobe)."""

from __future__ import annotations

import subprocess
from pathlib import Path


def get_audio_duration_s(audio_path: Path) -> float | None:
    """Return media duration in seconds using ffprobe.

    Parameters
    ----------
    audio_path:
        Path to a local media file supported by ffprobe.

    Returns
    -------
    float | None
        Duration in seconds if available; otherwise None.

    Notes
    -----
    This function relies on the `ffprobe` executable being available in PATH.
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None

    if proc.returncode != 0:
        return None

    val = (proc.stdout or "").strip()
    if not val:
        return None

    try:
        dur = float(val)
    except ValueError:
        return None

    if dur <= 0.0:
        return None
    return dur
