#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Typed launcher error hierarchy and formatting helpers."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping
from typing import ClassVar


class PCCXLauncherError(Exception):
    """Base class for typed launcher failures."""

    domain: ClassVar[str] = "launcher"
    default_code: ClassVar[str] = "pccx_launcher_error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        hint: str | None = None,
        details: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.default_code
        self.hint = hint
        self.details = dict(details or {})

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "type": type(self).__name__,
            "domain": self.domain,
            "code": self.code,
            "message": self.message,
        }
        if self.hint:
            payload["hint"] = self.hint
        if self.details:
            payload["details"] = self.details
        return payload


class KV260Error(PCCXLauncherError):
    """KV260 target detection, access, or support failure."""

    domain = "kv260"
    default_code = "kv260_error"


class AxiError(PCCXLauncherError):
    """AXI bridge, register, or FPGA fabric access failure."""

    domain = "axi"
    default_code = "axi_error"


class GemmaError(PCCXLauncherError):
    """Gemma model descriptor, asset, or runtime handoff failure."""

    domain = "gemma"
    default_code = "gemma_error"


class TraceError(PCCXLauncherError):
    """Launcher trace, diagnostics, fixture, or argument failure."""

    domain = "trace"
    default_code = "trace_error"


ERROR_TYPES: dict[str, type[PCCXLauncherError]] = {
    cls.__name__: cls
    for cls in (
        PCCXLauncherError,
        KV260Error,
        AxiError,
        GemmaError,
        TraceError,
    )
}


def format_error(error: PCCXLauncherError) -> str:
    text = f"[ERROR] {type(error).__name__}({error.code}): {error.message}"
    if error.hint:
        text = f"{text}\n        hint: {error.hint}"
    return text


def create_error(
    error_type: str,
    message: str,
    *,
    code: str | None = None,
    hint: str | None = None,
) -> PCCXLauncherError:
    try:
        error_cls = ERROR_TYPES[error_type]
    except KeyError as exc:
        supported = ", ".join(sorted(ERROR_TYPES))
        raise TraceError(
            f"unknown launcher error type: {error_type}",
            code="unknown_error_type",
            hint=f"supported types: {supported}",
        ) from exc
    return error_cls(message, code=code, hint=hint)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Format a typed PCCX launcher error for shell stubs.",
    )
    parser.add_argument("error_type", choices=tuple(sorted(ERROR_TYPES)))
    parser.add_argument("message")
    parser.add_argument("--code", default=None)
    parser.add_argument("--hint", default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    error = create_error(
        args.error_type,
        args.message,
        code=args.code,
        hint=args.hint,
    )
    sys.stderr.write(format_error(error) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
