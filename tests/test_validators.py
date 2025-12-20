from __future__ import annotations

import pytest

from scribebox.exceptions import InvalidInputError
from scribebox.validators import validate_youtube_url


def test_validate_youtube_url_accepts_youtube_com() -> None:
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert validate_youtube_url(url) == url


def test_validate_youtube_url_accepts_youtu_be() -> None:
    url = "https://youtu.be/dQw4w9WgXcQ"
    assert validate_youtube_url(url) == url


def test_validate_youtube_url_rejects_other_host() -> None:
    with pytest.raises(InvalidInputError):
        validate_youtube_url("https://example.com/video")
