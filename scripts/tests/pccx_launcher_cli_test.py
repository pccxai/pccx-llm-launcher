#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""CLI tests for pccx-launcher Gemma mock chat."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "pccx-launcher"
TEST_PATH = Path(__file__).resolve()


def run_cli(prompt: str, seed: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CLI),
            "gemma",
            "chat",
            "--prompt",
            prompt,
            "--seed",
            str(seed),
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_interactive_cli(
    prompts: list[str],
    seed: int = 0,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CLI),
            "gemma",
            "chat",
            "--interactive",
            "--seed",
            str(seed),
        ],
        cwd=ROOT,
        check=False,
        input="\n".join(prompts) + "\n",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_gemma_chat_cli_prints_mock_output_text_only() -> None:
    result = run_cli("hello cli")

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.startswith("mock-gemma:")
    assert len(result.stdout.strip()) == len("mock-gemma:") + 16


def test_gemma_chat_cli_is_deterministic_for_same_prompt() -> None:
    first = run_cli("same cli prompt")
    second = run_cli("same cli prompt")
    third = run_cli("different cli prompt")

    assert first.returncode == 0
    assert second.returncode == 0
    assert third.returncode == 0
    assert first.stdout == second.stdout
    assert first.stdout != third.stdout


def test_gemma_chat_cli_seed_controls_deterministic_output() -> None:
    first = run_cli("seeded cli prompt", seed=123)
    second = run_cli("seeded cli prompt", seed=123)
    third = run_cli("seeded cli prompt", seed=124)

    assert first.returncode == 0
    assert second.returncode == 0
    assert third.returncode == 0
    assert first.stdout == second.stdout
    assert first.stdout != third.stdout


def test_gemma_chat_interactive_repl_keeps_multi_turn_state() -> None:
    first = run_interactive_cli(["first repl turn", "second repl turn", ":quit"], seed=3)
    second = run_interactive_cli(["first repl turn", "second repl turn", ":quit"], seed=3)
    third = run_interactive_cli(["first repl turn", "second repl turn", ":quit"], seed=4)

    assert first.returncode == 0
    assert first.stderr == ""
    assert first.stdout == second.stdout
    assert first.stdout != third.stdout
    assert first.stdout.count("user> ") == 3
    assert first.stdout.count("assistant> mock-gemma:") == 2


def test_serial_transport_is_stubbed() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "gemma",
            "chat",
            "--transport",
            "serial",
            "--prompt",
            "hello",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert "stubbed pending board evidence" in result.stderr


def test_source_headers_for_cli_files() -> None:
    for path in [CLI, TEST_PATH]:
        assert path.read_text(encoding="utf-8").splitlines()[:3] == [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ]


test_gemma_chat_cli_prints_mock_output_text_only()
test_gemma_chat_cli_is_deterministic_for_same_prompt()
test_gemma_chat_cli_seed_controls_deterministic_output()
test_gemma_chat_interactive_repl_keeps_multi_turn_state()
test_serial_transport_is_stubbed()
test_source_headers_for_cli_files()

print("pccx-launcher CLI tests ok")
