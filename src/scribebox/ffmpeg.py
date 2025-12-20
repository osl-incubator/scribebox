"""FFmpeg helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .exceptions import ExternalToolError


def convert_to_wav_16k_mono(
    input_path: Path,
    output_path: Path,
) -> Path:
    """Convert an audio/video file to a normalized WAV file.

    The resulting file is 16kHz mono PCM (s16le), which is a good baseline for
    Whisper-family speech models.

    Parameters
    ----------
    input_path:
        Path to the input media file.
    output_path:
        Target path for the WAV output.

    Returns
    -------
    pathlib.Path
        The ``output_path``.

    Raises
    ------
    ExternalToolError
        If `ffmpeg` fails.
    """

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-vn",
        "-f",
        "wav",
        str(output_path),
    ]

    proc = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0:
        raise ExternalToolError(
            "ffmpeg failed. Ensure ffmpeg is installed and "
            f"readable. stderr: {proc.stderr.strip()}"
        )

    return output_path
