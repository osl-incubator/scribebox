"""PDF export utilities."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas


def write_pdf(
    *,
    text: str,
    output_path: Path,
    title: str | None = None,
    font_name: str = "Helvetica",
    font_size: int = 11,
    margin_in: float = 0.75,
) -> None:
    """Write a plain-text PDF.

    Parameters
    ----------
    text:
        Text to write.
    output_path:
        Destination PDF path.
    title:
        Optional title shown at the top.
    font_name:
        ReportLab font name.
    font_size:
        Base font size for body text.
    margin_in:
        Page margins in inches.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    canvas = Canvas(str(output_path), pagesize=LETTER)
    width, height = LETTER

    margin = margin_in * inch
    usable_width = width - 2 * margin
    y = height - margin
    line_height = font_size * 1.35

    def ensure_page(ypos: float) -> float:
        if ypos >= margin:
            return ypos
        canvas.showPage()
        canvas.setFont(font_name, font_size)
        _, h = LETTER
        return h - margin

    def draw_wrapped(ypos: float, line: str, size: int) -> float:
        for wrapped in _wrap_line(
            line=line,
            usable_width=usable_width,
            font_name=font_name,
            font_size=size,
        ):
            ypos = ensure_page(ypos)
            canvas.drawString(margin, ypos, wrapped)
            ypos -= line_height
        return ypos

    canvas.setFont(font_name, font_size)

    if title:
        canvas.setFont(font_name, font_size + 3)
        y = draw_wrapped(y, title, font_size + 3)
        y -= line_height * 0.25
        canvas.setFont(font_name, font_size)

    for raw in text.splitlines():
        if not raw.strip():
            y -= line_height
            y = ensure_page(y)
            continue
        y = draw_wrapped(y, raw, font_size)

    canvas.save()


def _wrap_line(
    *,
    line: str,
    usable_width: float,
    font_name: str,
    font_size: int,
) -> list[str]:
    words = line.split()
    if not words:
        return [""]

    out: list[str] = []
    cur: list[str] = []

    for word in words:
        trial = " ".join([*cur, word])
        if stringWidth(trial, font_name, font_size) <= usable_width:
            cur.append(word)
            continue

        if cur:
            out.append(" ".join(cur))
            cur = [word]
            continue

        out.append(word)

    if cur:
        out.append(" ".join(cur))
    return out
