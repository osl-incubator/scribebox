from __future__ import annotations

from pathlib import Path

import scribebox.backends as backends
from scribebox.backends import TranscribeOptions
from scribebox.core import run_transcription
from scribebox.types import Transcript, TranscriptSegment


def test_run_transcription_passes_progress_cb(
    tmp_path: Path,
    monkeypatch,
) -> None:
    seen: list[float] = []

    def fake_transcribe_file(
        *,
        audio_path: Path,
        backend: str,
        options: TranscribeOptions,
        progress_cb,
    ) -> Transcript:
        if progress_cb is not None:
            progress_cb(1.0)
            progress_cb(2.0)
        return Transcript(
            text="ok",
            segments=[TranscriptSegment(0.0, 2.0, "ok")],
            language="en",
        )

    monkeypatch.setattr(backends, "transcribe_file", fake_transcribe_file)

    def cb(cur: float) -> None:
        seen.append(cur)

    audio = tmp_path / "x.mp3"
    audio.write_bytes(b"bin")

    res = run_transcription(
        audio_path=audio,
        outdir=tmp_path / "o",
        pdf=False,
        backend="faster-whisper",
        options=TranscribeOptions(),
        title="t",
        progress_cb=cb,
    )
    assert res.text_path.exists()
    assert seen == [1.0, 2.0]
