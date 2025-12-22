from __future__ import annotations

from pathlib import Path

import scribebox.backends as backends
from scribebox.backends import TranscribeOptions
from scribebox.core import run_transcription
from scribebox.types import Transcript, TranscriptSegment


def test_run_transcription_writes_txt(tmp_path: Path, monkeypatch) -> None:
    def fake_transcribe_file(
        *,
        audio_path: Path,
        backend: str,
        options: TranscribeOptions,
    ) -> Transcript:
        return Transcript(
            text="a\nb",
            segments=[TranscriptSegment(0.0, 1.0, "a")],
            language="en",
        )

    monkeypatch.setattr(backends, "transcribe_file", fake_transcribe_file)

    audio = tmp_path / "x.mp3"
    audio.write_bytes(b"bin")

    res = run_transcription(
        audio_path=audio,
        outdir=tmp_path / "o",
        pdf=False,
        backend="faster-whisper",
        options=TranscribeOptions(),
        title="t",
    )
    assert res.text_path.exists()
    assert res.text_path.read_text(encoding="utf-8").strip() == "a\nb"
    assert res.pdf_path is None
    assert res.detected_language == "en"
