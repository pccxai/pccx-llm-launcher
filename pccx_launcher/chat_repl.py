#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Dry-run chat REPL helpers for launcher terminal output."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, Iterator, TextIO

from pccx_launcher.streaming_token_renderer import (
    ANSI_COLORS,
    FlushBehavior,
    ResultStream,
    ResultStreamToken,
    StreamingTokenRenderer,
)


PLACEHOLDER_RESPONSE_TOKENS = (
    "[placeholder ",
    "- ",
    "real inference requires pccx-FPGA bring-up evidence]",
)


def render_result_stream(
    result_stream: ResultStream | Iterable[object],
    *,
    stdout: TextIO | None = None,
    color: str | None = None,
    flush: FlushBehavior | str | bool = FlushBehavior.TOKEN,
) -> str:
    """Render a chat result stream to the REPL output surface."""

    renderer = StreamingTokenRenderer(color=color, flush=flush, output=stdout)
    return renderer.render(result_stream)


def dry_run_result_stream() -> Iterator[ResultStreamToken]:
    """Return a deterministic placeholder stream for dry-run chat."""

    for token in PLACEHOLDER_RESPONSE_TOKENS:
        yield ResultStreamToken(token)


def dry_run_response(
    *,
    stdout: TextIO | None = None,
    color: str | None = None,
    flush: FlushBehavior | str | bool = FlushBehavior.TOKEN,
) -> str:
    """Render the guarded dry-run response stream."""

    return render_result_stream(
        dry_run_result_stream(),
        stdout=stdout,
        color=color,
        flush=flush,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render launcher chat output.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="render placeholder output",
    )
    parser.add_argument("--prompt", help="accepted for dry-run parity; not echoed")
    parser.add_argument("--color", choices=sorted(ANSI_COLORS))
    parser.add_argument(
        "--flush",
        choices=[behavior.value for behavior in FlushBehavior],
        default=FlushBehavior.TOKEN.value,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.dry_run:
        print(
            "[ERROR] --dry-run is required. No model is available for execution.",
            file=sys.stderr,
        )
        return 1
    dry_run_response(stdout=sys.stdout, color=args.color, flush=args.flush)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
