from __future__ import annotations

from pathlib import Path

import pytest

from scribebox.config import OutputOptions, TranscribeOptions
from scribebox.service import transcribe_local_file
from scribebox.transcribe.base import TranscriptionResult, Transcriber
from scribebox.types import Segment


class DummyTranscriber(Transcriber):
    def transcribe(
        self,
        audio_path: Path,
        *,
        language: str | None,
        translate_to_english: bool,
        model: str,
        device: str,
    ) -> TranscriptionResult:
        segments = [
            Segment(0.0, 1.0, "A"),
            Segment(1.0, 2.0, "B"),
        ]
        return TranscriptionResult(segments=segments, language=language or "en")


def test_transcribe_local_file_writes_outputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "in.mp3"
    input_path.write_bytes(b"not really audio")

    def _fake_convert(inp: Path, out: Path) -> Path:
        out.write_bytes(b"RIFF....WAVEfmt ")
        return out

    monkeypatch.setattr(
        "scribebox.service.convert_to_wav_16k_mono",
        _fake_convert,
    )

    transcriber = DummyTranscriber()
    opts = TranscribeOptions(language="en")
    out_opts = OutputOptions(outdir=tmp_path / "out", write_pdf=True)

    out = transcribe_local_file(
        input_path,
        transcriber=transcriber,
        options=opts,
        outputs=out_opts,
    )

    assert out.text_path.exists()
    assert out.pdf_path is not None and out.pdf_path.exists()

    txt = out.text_path.read_text(encoding="utf-8")
    assert "A" in txt and "B" in txt
