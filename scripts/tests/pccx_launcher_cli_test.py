#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""CLI tests for pccx-launcher Gemma mock chat."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "pccx-launcher"
TEST_PATH = Path(__file__).resolve()


def run_cli(
    prompt: str,
    seed: int = 0,
    history_file: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(CLI),
        "gemma",
        "chat",
        "--prompt",
        prompt,
        "--seed",
        str(seed),
    ]
    if history_file is not None:
        command.extend(["--history-file", str(history_file)])
    return subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_interactive_cli(
    prompts: list[str],
    seed: int = 0,
    history_file: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(CLI),
        "gemma",
        "chat",
        "--interactive",
        "--seed",
        str(seed),
    ]
    if history_file is not None:
        command.extend(["--history-file", str(history_file)])
    return subprocess.run(
        command,
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


def test_gemma_chat_history_file_loads_and_appends_jsonl() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        history_path = Path(temp_dir) / "history.jsonl"
        first = run_cli("persist one", seed=9, history_file=history_path)
        second = run_cli("persist two", seed=9, history_file=history_path)

        replay_path = Path(temp_dir) / "replay.jsonl"
        replay_first = run_cli("persist one", seed=9, history_file=replay_path)
        replay_second = run_cli("persist two", seed=9, history_file=replay_path)

        assert first.returncode == 0
        assert second.returncode == 0
        assert replay_first.returncode == 0
        assert replay_second.returncode == 0
        assert first.stderr == ""
        assert second.stderr == ""
        assert replay_first.stderr == ""
        assert replay_second.stderr == ""
        assert first.stdout == replay_first.stdout
        assert second.stdout == replay_second.stdout
        assert [
            json.loads(line)
            for line in history_path.read_text(encoding="utf-8").splitlines()
        ] == [
            ["user", "persist one"],
            ["assistant", first.stdout.strip()],
            ["user", "persist two"],
            ["assistant", second.stdout.strip()],
        ]


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
test_gemma_chat_history_file_loads_and_appends_jsonl()
test_serial_transport_is_stubbed()
test_source_headers_for_cli_files()

print("pccx-launcher CLI tests ok")
