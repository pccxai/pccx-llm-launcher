#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Three-turn golden smoke test for pccx-launcher Gemma mock chat."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "pccx-launcher"
GOLDEN_PATH = ROOT / "scripts" / "tests" / "golden" / "chat-smoke-3turn.stdout"
TEST_PATH = Path(__file__).resolve()
TURN_PROMPTS = (
    "hello from lane b",
    "summarize fixture status",
    "close the smoke run",
)


def run_turn(prompt: str) -> str:
    result = subprocess.run(
        [sys.executable, str(CLI), "gemma", "chat", "--prompt", prompt],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert re.fullmatch(r"mock-gemma:[0-9a-f]{16}\n", result.stdout)
    return result.stdout


def capture_three_turn_stdout() -> str:
    return "".join(run_turn(prompt) for prompt in TURN_PROMPTS)


def test_three_turn_chat_smoke_matches_checked_golden_stdout() -> None:
    observed = capture_three_turn_stdout()
    expected = GOLDEN_PATH.read_text(encoding="utf-8")

    assert observed == expected


def test_three_turn_chat_smoke_capture_matches_rerun() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        capture_path = Path(tmpdir) / "chat-smoke-3turn.stdout"
        capture_path.write_text(capture_three_turn_stdout(), encoding="utf-8")

        assert capture_path.read_text(encoding="utf-8") == capture_three_turn_stdout()


def test_source_headers_for_chat_smoke_fixture_files() -> None:
    for path in [TEST_PATH, CLI]:
        assert path.read_text(encoding="utf-8").splitlines()[:3] == [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ]


test_three_turn_chat_smoke_matches_checked_golden_stdout()
test_three_turn_chat_smoke_capture_matches_rerun()
test_source_headers_for_chat_smoke_fixture_files()

print("3-turn chat smoke fixture tests ok")
