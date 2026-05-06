#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Tests for the standalone chat surface preview."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "chat-surface-preview.sh"


def run_preview(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT_PATH), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def test_preview_outputs_blocked_chat_surface() -> None:
    result = run_preview("--model", "gemma3n-e4b", "--target", "kv260")
    output = result.stdout

    assert result.stderr == ""
    assert "=== standalone chat surface preview ===" in output
    assert "boundary   : read-only local preview; no prompt/model/provider/hardware/lab/IDE execution" in output
    assert "target     : kv260" in output
    assert "model      : gemma3n-e4b" in output
    assert "surface    : blocked" in output
    assert "chat       : inactive" in output
    assert "input      : ready_for_inputs" in output
    assert "send       : disabled" in output
    assert "model load : not_loaded" in output
    assert "[CHAT]  system     : local chat is blocked until readiness and session evidence exist" in output
    assert "[CHAT]  input      : ready for future explicit input; no content is captured here" in output
    assert "[CHAT]  assistant  : unavailable" in output
    assert "new_session : placeholder (disabled)" in output
    assert "model_status : not_loaded (disabled)" in output
    assert "send_message : disabled (disabled)" in output
    assert "clear_session : inactive (disabled)" in output
    assert "export_summary : blocked (disabled)" in output
    assert "runtime_readiness_blocked -> send_message_enabled" in output
    assert "chat_runtime_not_implemented -> session_start_enabled" in output
    assert "readOnly=true dataOnly=true runtimeExecution=false modelExecution=false kv260Access=false providerCalls=false" in output


def test_preview_is_deterministic_and_does_not_echo_prompts() -> None:
    first = run_preview()
    second = run_preview()

    assert first.stdout == second.stdout
    assert "hello" not in first.stdout.lower()
    assert "prompt   :" not in first.stdout


def test_preview_avoids_runtime_and_readiness_overclaims() -> None:
    output = run_preview().stdout.lower()

    forbidden = [
        "kv260 inference works",
        "gemma 3n e4b runs on kv260",
        "20 tok/s achieved",
        "timing closed",
        "bitstream ready",
        "production-ready",
        "marketplace-ready",
        "stable api",
        "stable abi",
        "model executed",
        "provider call made",
    ]
    for phrase in forbidden:
        assert phrase not in output, phrase


def test_html_preview_uses_pccx_ui_assets_without_runtime_claims() -> None:
    result = run_preview("--html")
    output = result.stdout
    lower_output = output.lower()

    assert result.stderr == ""
    assert '<link rel="icon" href="assets/icon.svg" type="image/svg+xml">' in output
    assert '<link rel="stylesheet" href="assets/pccx-ui/launcher.css">' in output
    assert 'src="assets/pccx-ui/logo-mark.svg"' in output
    assert "pccx-ui theme tokens and logo assets are applied" in lower_output
    assert "visual app-shell preview only" in lower_output
    assert "no model is loaded" in lower_output
    assert "no runtime path is executed" in lower_output
    assert "no provider is called" in lower_output
    assert "no kv260 access is attempted" in lower_output

    forbidden = [
        "kv260 inference works",
        "gemma 3n e4b runs on kv260",
        "20 tok/s achieved",
        "model executed",
        "provider call made",
    ]
    for phrase in forbidden:
        assert phrase not in lower_output, phrase


def test_unknown_model_is_rejected() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), "--model", "unknown", "--target", "kv260"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "chat/session stub failed" in result.stderr


test_preview_outputs_blocked_chat_surface()
test_preview_is_deterministic_and_does_not_echo_prompts()
test_preview_avoids_runtime_and_readiness_overclaims()
test_html_preview_uses_pccx_ui_assets_without_runtime_claims()
test_unknown_model_is_rejected()

print("chat surface preview tests ok")
