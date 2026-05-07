#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Tests for streaming token rendering into stdout-like output."""

from __future__ import annotations

from dataclasses import dataclass
import io
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pccx_launcher.chat_repl import render_result_stream
from pccx_launcher.streaming_token_renderer import (
    ANSI_RESET,
    ResultStreamToken,
    StreamingTokenRenderer,
)


@dataclass(frozen=True)
class ObjectToken:
    token: str


class MockResultStream:
    def __iter__(self):
        yield ResultStreamToken("Hel")
        yield {"token": "lo"}
        yield ObjectToken(", ")
        yield {"event": "progress"}
        yield "world"


class RecordingStdout(io.StringIO):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[tuple[str, str]] = []

    def write(self, value: str) -> int:
        self.events.append(("write", value))
        return super().write(value)

    def flush(self) -> None:
        self.events.append(("flush", ""))
        super().flush()


def test_streaming_renderer_writes_and_flushes_tokens_in_arrival_order() -> None:
    stdout = RecordingStdout()
    renderer = StreamingTokenRenderer(output=stdout, flush="token")

    rendered = renderer.render(MockResultStream())

    assert rendered == "Hello, world"
    assert stdout.getvalue() == "Hello, world"
    assert stdout.events == [
        ("write", "Hel"),
        ("flush", ""),
        ("write", "lo"),
        ("flush", ""),
        ("write", ", "),
        ("flush", ""),
        ("write", "world"),
        ("flush", ""),
    ]


def test_streaming_renderer_can_flush_only_at_end() -> None:
    stdout = RecordingStdout()
    renderer = StreamingTokenRenderer(output=stdout, flush="end")

    renderer.render(["one", " ", "two"])

    assert stdout.getvalue() == "one two"
    assert stdout.events == [
        ("write", "one"),
        ("write", " "),
        ("write", "two"),
        ("flush", ""),
    ]


def test_streaming_renderer_can_skip_flushes() -> None:
    stdout = RecordingStdout()
    renderer = StreamingTokenRenderer(output=stdout, flush=False)

    renderer.render(["quiet"])

    assert stdout.getvalue() == "quiet"
    assert stdout.events == [("write", "quiet")]


def test_streaming_renderer_wraps_stream_with_optional_ansi_color() -> None:
    stdout = RecordingStdout()
    renderer = StreamingTokenRenderer(output=stdout, color="cyan", flush="end")

    renderer.render(["blue"])

    assert stdout.getvalue() == f"\033[36mblue{ANSI_RESET}"
    assert stdout.events == [
        ("write", "\033[36m"),
        ("write", "blue"),
        ("write", ANSI_RESET),
        ("flush", ""),
    ]


def test_chat_repl_renders_result_stream_to_stdout() -> None:
    stdout = RecordingStdout()

    rendered = render_result_stream(["A", "B", "C"], stdout=stdout, flush="token")

    assert rendered == "ABC"
    assert stdout.getvalue() == "ABC"
    assert stdout.events == [
        ("write", "A"),
        ("flush", ""),
        ("write", "B"),
        ("flush", ""),
        ("write", "C"),
        ("flush", ""),
    ]


if __name__ == "__main__":
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
    print("streaming token renderer tests ok")
