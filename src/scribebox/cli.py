"""Command line interface."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .config import OutputOptions, TranscribeOptions
from .exceptions import ScribeboxError
from .service import transcribe_local_file, transcribe_youtube_url
from .transcribe.factory import build_transcriber


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scribebox")
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("out"),
        help="Output directory.",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also write a PDF transcript.",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Language code (e.g. en, pt, es). Default: auto.",
    )
    parser.add_argument(
        "--translate",
        action="store_true",
        help="Translate to English (if supported by backend).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        help="Model name (backend-specific). Default: base.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        help='Device hint. Examples: "cpu", "cuda".',
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="faster-whisper",
        choices=["faster-whisper", "whisper"],
        help="Transcriber backend preference.",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_url = sub.add_parser("url", help="Transcribe a YouTube URL.")
    p_url.add_argument("url", type=str)

    p_file = sub.add_parser("file", help="Transcribe a local file.")
    p_file.add_argument("path", type=Path)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI entrypoint."""

    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    transcriber = build_transcriber(args.backend)
    t_opts = TranscribeOptions(
        language=args.language,
        translate_to_english=args.translate,
        model=args.model,
        device=args.device,
    )
    o_opts = OutputOptions(outdir=args.outdir, write_pdf=args.pdf)

    try:
        if args.cmd == "url":
            out = transcribe_youtube_url(
                args.url,
                transcriber=transcriber,
                options=t_opts,
                outputs=o_opts,
            )
        else:
            out = transcribe_local_file(
                args.path,
                transcriber=transcriber,
                options=t_opts,
                outputs=o_opts,
            )
    except ScribeboxError as exc:
        parser.exit(2, f"Error: {exc}\n")

    print(f"Text: {out.text_path}")
    if out.pdf_path is not None:
        print(f"PDF:  {out.pdf_path}")
    if out.language is not None:
        print(f"Lang: {out.language}")
    return 0
