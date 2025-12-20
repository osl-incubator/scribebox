from __future__ import annotations

from pathlib import Path

from scribebox.pdf import write_pdf
from scribebox.transcript import format_transcript
from scribebox.types import Segment


def test_format_transcript_joins_segments() -> None:
    segments = [
        Segment(0.0, 1.0, "Hello"),
        Segment(1.0, 2.0, "world!"),
    ]
    txt = format_transcript(segments)
    assert "Hello" in txt
    assert "world!" in txt
    assert txt.endswith("\n")


def test_write_pdf_creates_pdf(tmp_path: Path) -> None:
    out = tmp_path / "t.pdf"
    write_pdf(out, title="T", text="hello\nworld\n")
    data = out.read_bytes()
    assert data.startswith(b"%PDF")
