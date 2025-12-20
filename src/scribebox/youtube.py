"""YouTube download functionality."""

from __future__ import annotations

from pathlib import Path

from .exceptions import DependencyMissingError
from .validators import validate_youtube_url


def download_youtube_audio(
    url: str,
    outdir: Path,
) -> Path:
    """Download best-quality audio from a YouTube URL.

    This function requires the optional dependency `yt-dlp`.

    Parameters
    ----------
    url:
        YouTube URL.
    outdir:
        Directory where the audio will be written.

    Returns
    -------
    pathlib.Path
        Path to the downloaded audio file.

    Raises
    ------
    DependencyMissingError
        If `yt-dlp` is not installed.
    """

    validate_youtube_url(url)

    try:
        from yt_dlp import YoutubeDL  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise DependencyMissingError(
            "Missing dependency: yt-dlp. Install with "
            "`pip install scribebox[youtube]`."
        ) from exc

    outdir.mkdir(parents=True, exist_ok=True)
    template = str(outdir / "%(id)s.%(ext)s")

    ydl_opts: dict[str, object] = {
        "format": "bestaudio/best",
        "outtmpl": template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "0",
            }
        ],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info.get("id")
        if not isinstance(video_id, str) or not video_id:
            raise DependencyMissingError(
                "yt-dlp did not return a video id."
            )

    candidate = outdir / f"{video_id}.wav"
    if candidate.exists():
        return candidate

    for p in outdir.glob(f"{video_id}.*"):
        return p

    raise DependencyMissingError(
        "Audio download finished, but output file was not found."
    )
