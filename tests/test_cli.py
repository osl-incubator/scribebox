from __future__ import annotations

from scribebox.cli import build_parser


def test_common_args_work_before_or_after_subcommand() -> None:
    parser = build_parser()

    ns1 = parser.parse_args(
        ["url", "https://example.com", "--outdir", "x", "--pdf"]
    )
    assert str(ns1.outdir) == "x"
    assert ns1.pdf is True

    ns2 = parser.parse_args(
        ["--outdir", "x", "--pdf", "url", "https://example.com"]
    )
    assert str(ns2.outdir) == "x"
    assert ns2.pdf is True
