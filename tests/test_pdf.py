from __future__ import annotations

from pathlib import Path

from scribebox.pdf import write_pdf


def test_write_pdf(tmp_path: Path) -> None:
    out = tmp_path / "out.pdf"
    write_pdf(text="hello\nworld", output_path=out, title="Title")
    assert out.exists()
    assert out.stat().st_size > 0
