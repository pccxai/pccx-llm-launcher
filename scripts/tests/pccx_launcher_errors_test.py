#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Tests for the launcher typed error hierarchy."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pccx_launcher.errors import (  # noqa: E402
    AxiError,
    GemmaError,
    KV260Error,
    PCCXLauncherError,
    TraceError,
    format_error,
)


def test_error_hierarchy_and_domains() -> None:
    expected = [
        (KV260Error, "kv260"),
        (AxiError, "axi"),
        (GemmaError, "gemma"),
        (TraceError, "trace"),
    ]
    for error_cls, domain in expected:
        error = error_cls("fixture failure")
        assert isinstance(error, PCCXLauncherError)
        assert error.domain == domain
        assert error.as_dict()["type"] == error_cls.__name__


def test_format_error_includes_type_code_and_message() -> None:
    error = GemmaError(
        "Gemma assets are not configured",
        code="gemma_assets_missing",
    )
    assert (
        format_error(error)
        == "[ERROR] GemmaError(gemma_assets_missing): Gemma assets are not configured"
    )


def test_error_cli_formats_shell_stub_output() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "pccx_launcher" / "errors.py"),
            "KV260Error",
            "--target must be kv260",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout == ""
    assert result.stderr == "[ERROR] KV260Error(kv260_error): --target must be kv260\n"


test_error_hierarchy_and_domains()
test_format_error_includes_type_code_and_message()
test_error_cli_formats_shell_stub_output()
