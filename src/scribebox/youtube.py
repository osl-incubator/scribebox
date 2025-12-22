"""YouTube helpers."""

from __future__ import annotations

from pathlib import Path

from .errors import ScribeboxError


def download_youtube_audio(*, url: str, outdir: Path) -> Path:
    """Download YouTube audio as MP3 using yt-dlp.

    Parameters
    ----------
    url:
        YouTube video URL.
    outdir:
        Output directory for the produced MP3.

    Returns
    -------
    pathlib.Path
        Path to the produced MP3 file.

    Raises
    ------
    ScribeboxError
        If yt-dlp is missing or the download fails.
    """
    try:
        import yt_dlp
    except Exception as exc:  # pragma: no cover
        raise ScribeboxError(
            "YouTube support requires 'yt-dlp'. "
            "Install with: pip install -e '.[youtube]'"
        ) from exc

    outdir.mkdir(parents=True, exist_ok=True)

    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(outdir / "%(id)s.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as exc:
        raise ScribeboxError(f"Failed to download YouTube audio: {exc}") from exc

    video_id = info.get("id") if isinstance(info, dict) else None
    if not video_id:
        raise ScribeboxError("Could not determine YouTube video id.")

    mp3_path = outdir / f"{video_id}.mp3"
    if not mp3_path.exists():
        raise ScribeboxError("yt-dlp finished but MP3 was not created.")

    return mp3_path
