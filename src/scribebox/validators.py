"""Validation helpers."""

from __future__ import annotations

from urllib.parse import urlparse

from .exceptions import InvalidInputError


def validate_youtube_url(url: str) -> str:
    """Validate that a URL looks like a YouTube link.

    Parameters
    ----------
    url:
        Input URL.

    Returns
    -------
    str
        The normalized URL (currently unchanged).

    Raises
    ------
    InvalidInputError
        If the URL is empty or not a YouTube URL.
    """

    if not url.strip():
        raise InvalidInputError("YouTube URL cannot be empty.")

    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()

    if host.endswith("youtube.com") or host.endswith("youtu.be"):
        return url

    raise InvalidInputError(
        "URL does not look like a YouTube URL "
        "(expected youtube.com or youtu.be)."
    )
