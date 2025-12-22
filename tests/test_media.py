from __future__ import annotations

from pathlib import Path

import scribebox.media as media


class _P:
    def __init__(self, returncode: int, stdout: str) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = ""


def test_get_audio_duration_s_parses_float(monkeypatch, tmp_path: Path) -> None:
    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"bin")

    def fake_run(*args, **kwargs):
        return _P(returncode=0, stdout="12.34\n")

    monkeypatch.setattr(media.subprocess, "run", fake_run)
    assert media.get_audio_duration_s(audio) == 12.34


def test_get_audio_duration_s_returns_none_on_failure(
    monkeypatch,
    tmp_path: Path,
) -> None:
    audio = tmp_path / "a.mp3"
    audio.write_bytes(b"bin")

    def fake_run(*args, **kwargs):
        return _P(returncode=1, stdout="")

    monkeypatch.setattr(media.subprocess, "run", fake_run)
    assert media.get_audio_duration_s(audio) is None
