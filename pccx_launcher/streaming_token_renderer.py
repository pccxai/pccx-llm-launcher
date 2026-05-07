#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Streaming token rendering helpers for launcher chat output."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import sys
from typing import Iterable, Iterator, Protocol, TextIO, runtime_checkable


class FlushBehavior(str, Enum):
    """Supported stdout flush policies for token rendering."""

    NEVER = "never"
    TOKEN = "token"
    END = "end"


ANSI_COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
}
ANSI_RESET = "\033[0m"


@dataclass(frozen=True)
class ResultStreamToken:
    """A token event emitted by a result stream."""

    token: str


@runtime_checkable
class ResultStream(Protocol):
    """Synchronous stream of token-like result events."""

    def __iter__(self) -> Iterator[object]:
        """Yield token events as they arrive."""


@dataclass(frozen=True)
class StreamingTokenRenderer:
    """Write result-stream tokens directly to stdout-like output."""

    color: str | None = None
    flush: FlushBehavior | str | bool = FlushBehavior.TOKEN
    output: TextIO | None = None

    def render(self, result_stream: ResultStream | Iterable[object]) -> str:
        """Render token events and return the assembled response text."""

        output = self.output if self.output is not None else sys.stdout
        flush_behavior = normalize_flush_behavior(self.flush)
        color_prefix = ansi_color_prefix(self.color)
        rendered: list[str] = []
        wrote_color = False

        try:
            for event in result_stream:
                token = token_text(event)
                if token is None:
                    continue
                if color_prefix and not wrote_color:
                    output.write(color_prefix)
                    wrote_color = True
                output.write(token)
                rendered.append(token)
                if flush_behavior is FlushBehavior.TOKEN:
                    output.flush()
        finally:
            if wrote_color:
                output.write(ANSI_RESET)

        if flush_behavior is FlushBehavior.END:
            output.flush()
        return "".join(rendered)


def normalize_flush_behavior(value: FlushBehavior | str | bool) -> FlushBehavior:
    """Normalize public flush configuration into an enum value."""

    if isinstance(value, FlushBehavior):
        return value
    if value is True:
        return FlushBehavior.TOKEN
    if value is False:
        return FlushBehavior.NEVER
    try:
        return FlushBehavior(str(value))
    except ValueError as exc:
        choices = ", ".join(behavior.value for behavior in FlushBehavior)
        raise ValueError(f"unknown flush behavior {value!r}; expected {choices}") from exc


def ansi_color_prefix(color: str | None) -> str | None:
    """Return the ANSI prefix for a named color or raw escape sequence."""

    if color is None:
        return None
    if color.startswith("\033["):
        return color
    try:
        return ANSI_COLORS[color]
    except KeyError as exc:
        choices = ", ".join(sorted(ANSI_COLORS))
        raise ValueError(f"unknown ANSI color {color!r}; expected one of {choices}") from exc


def token_text(event: object) -> str | None:
    """Extract token text from common ResultStream event shapes."""

    if isinstance(event, str):
        return event
    if isinstance(event, bytes):
        return event.decode("utf-8")
    if isinstance(event, ResultStreamToken):
        return event.token
    if isinstance(event, dict):
        token = event.get("token", event.get("text"))
        return token if isinstance(token, str) else None

    token = getattr(event, "token", None)
    if isinstance(token, str):
        return token
    text = getattr(event, "text", None)
    if isinstance(text, str):
        return text
    return None
