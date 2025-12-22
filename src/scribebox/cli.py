"""CLI entrypoint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tqdm import tqdm

from .backends import ProgressCallback, TranscribeOptions
from .core import run_transcription
from .errors import ScribeboxError
from .media import get_audio_duration_s
from .youtube import download_youtube_audio


def _add_common_args(
    parser: argparse.ArgumentParser,
    *,
    with_defaults: bool,
) -> None:
    default = None if with_defaults else argparse.SUPPRESS

    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("out") if with_defaults else argparse.SUPPRESS,
        help="Output directory (default: out).",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        default=False if with_defaults else argparse.SUPPRESS,
        help="Also export a PDF.",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None if with_defaults else argparse.SUPPRESS,
        help="Language code (e.g. en). Default: auto-detect.",
    )
    parser.add_argument(
        "--translate",
        action="store_true",
        default=False if with_defaults else argparse.SUPPRESS,
        help="Translate to English when supported.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="large-v3" if with_defaults else argparse.SUPPRESS,
        help="Model name or path (default: large-v3).",
    )
    parser.add_argument(
        "--backend",
        choices=["faster-whisper", "whisper"],
        default="faster-whisper" if with_defaults else argparse.SUPPRESS,
        help="Backend (default: faster-whisper).",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cpu" if with_defaults else argparse.SUPPRESS,
        help="Device (default: cpu).",
    )
    parser.add_argument(
        "--compute-type",
        type=str,
        default="int8" if with_defaults else argparse.SUPPRESS,
        help="faster-whisper compute type (default: int8).",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5 if with_defaults else argparse.SUPPRESS,
        help="Beam size (default: 5).",
    )
    parser.add_argument(
        "--no-vad",
        action="store_true",
        default=False if with_defaults else argparse.SUPPRESS,
        help="Disable VAD filtering.",
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        default=None if with_defaults else argparse.SUPPRESS,
        help="Optional prompt/glossary file.",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        default=False if with_defaults else argparse.SUPPRESS,
        help="Disable the progress bar.",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    common_main = argparse.ArgumentParser(add_help=False)
    _add_common_args(common_main, with_defaults=True)

    common_sub = argparse.ArgumentParser(add_help=False)
    _add_common_args(common_sub, with_defaults=False)

    parser = argparse.ArgumentParser(
        prog="scribebox",
        description=(
            "Local transcription (free): YouTube URL or audio file -> TXT/PDF."
        ),
        parents=[common_main],
    )

    subs = parser.add_subparsers(dest="command", required=True)

    p_url = subs.add_parser("url", help="Transcribe a YouTube URL.",
                            parents=[common_sub])
    p_url.add_argument("youtube_url", type=str)

    p_file = subs.add_parser("file", help="Transcribe a local audio file.",
                             parents=[common_sub])
    p_file.add_argument("path", type=Path)

    return parser


def _make_progress_cb(
    *,
    total_s: float | None,
    enabled: bool,
) -> tuple[ProgressCallback | None, callable | None]:
    if not enabled or not sys.stderr.isatty():
        return None, None
    if total_s is None:
        bar = tqdm(total=None, unit="s", dynamic_ncols=True)
        last = 0.0

        def cb(cur_s: float) -> None:
            nonlocal last
            delta = max(0.0, cur_s - last)
            last = cur_s
            bar.update(delta)

        return cb, bar.close

    bar = tqdm(total=total_s, unit="s", dynamic_ncols=True)
    last = 0.0

    def cb(cur_s: float) -> None:
        nonlocal last
        delta = max(0.0, min(total_s, cur_s) - last)
        last = min(total_s, cur_s)
        bar.update(delta)

    return cb, bar.close


def main(argv: list[str] | None = None) -> None:
    """Run CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    prompt: str | None = None
    if getattr(args, "prompt_file", None) is not None:
        prompt_file: Path = args.prompt_file
        prompt = prompt_file.read_text(encoding="utf-8").strip() or None

    options = TranscribeOptions(
        model=getattr(args, "model", "large-v3"),
        language=getattr(args, "language", None),
        translate=bool(getattr(args, "translate", False)),
        device=getattr(args, "device", "cpu"),
        compute_type=getattr(args, "compute_type", "int8"),
        vad_filter=not bool(getattr(args, "no_vad", False)),
        beam_size=int(getattr(args, "beam_size", 5)),
        initial_prompt=prompt,
    )

    outdir = Path(getattr(args, "outdir", Path("out")))
    pdf = bool(getattr(args, "pdf", False))
    backend = str(getattr(args, "backend", "faster-whisper"))
    progress_enabled = not bool(getattr(args, "no_progress", False))

    try:
        if args.command == "url":
            audio_path = download_youtube_audio(
                url=args.youtube_url,
                outdir=outdir,
            )
            title = args.youtube_url
        else:
            audio_path = args.path
            title = audio_path.name

        total_s = get_audio_duration_s(audio_path)
        progress_cb, progress_close = _make_progress_cb(
            total_s=total_s,
            enabled=progress_enabled,
        )

        try:
            result = run_transcription(
                audio_path=audio_path,
                outdir=outdir,
                pdf=pdf,
                backend=backend,
                options=options,
                title=title,
                progress_cb=progress_cb,
            )
        finally:
            if progress_close is not None:
                progress_close()

    except ScribeboxError as exc:
        raise SystemExit(str(exc)) from exc

    print(f"TXT: {result.text_path}")
    if result.pdf_path is not None:
        print(f"PDF: {result.pdf_path}")
    if result.detected_language is not None:
        print(f"Detected language: {result.detected_language}")
