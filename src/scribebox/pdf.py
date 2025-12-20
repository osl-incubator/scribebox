"""PDF output."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen.canvas import Canvas


def write_pdf(path: Path, title: str, text: str) -> Path:
    """Write a simple, readable PDF transcript.

    Parameters
    ----------
    path:
        Output PDF path.
    title:
        Document title.
    text:
        Transcript text.

    Returns
    -------
    pathlib.Path
        The written PDF path.
    """

    path.parent.mkdir(parents=True, exist_ok=True)

    canvas = Canvas(str(path), pagesize=LETTER)
    width, height = LETTER

    margin = 0.75 * inch
    x = margin
    y = height - margin

    canvas.setTitle(title)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(x, y, title)

    y -= 0.35 * inch
    canvas.setFont("Helvetica", 11)

    line_height = 14
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            y -= line_height
            continue

        while line:
            max_chars = 95
            chunk = line[:max_chars]
            line = line[max_chars:]

            if y < margin:
                canvas.showPage()
                canvas.setFont("Helvetica", 11)
                y = height - margin

            canvas.drawString(x, y, chunk)
            y -= line_height

    canvas.showPage()
    canvas.save()
    return path
