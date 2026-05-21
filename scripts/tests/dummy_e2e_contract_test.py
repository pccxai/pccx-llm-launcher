#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Tests for the offline dummy end-to-end launcher run."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contracts.dummy_e2e_contract import (
    SCHEMA_VERSION,
    TOKEN_COUNT,
    ResultStream,
    dummy_e2e,
    format_dummy_e2e_summary,
)


MODULE_PATH = ROOT / "contracts" / "dummy_e2e_contract.py"
CLI_PATH = ROOT / "scripts" / "pccx-launcher"
TEST_PATH = Path(__file__).resolve()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_dummy_e2e_is_deterministic_for_same_seed() -> None:
    first = dummy_e2e(42)
    second = dummy_e2e(42)
    different = dummy_e2e(43)

    assert first == second
    assert format_dummy_e2e_summary(first) == format_dummy_e2e_summary(second)
    assert first != different
    assert first.tokens != different.tokens


def test_dummy_e2e_wires_manifest_axi_mock_and_result_stream() -> None:
    stream = dummy_e2e(7)

    assert isinstance(stream, ResultStream)
    assert stream.schema_version == SCHEMA_VERSION
    assert stream.seed == 7
    assert stream.manifest_id == "gemma_weight_prep_seed_7_dummy"
    assert stream.completed is True
    assert stream.token_count == TOKEN_COUNT
    assert len(stream.command_trace) == 3
    assert tuple(trace.name for trace in stream.command_trace) == (
        "load_dummy_manifest",
        "prime_fake_stream",
        "finish_fake_stream",
    )
    assert tuple(trace.status.completion_count for trace in stream.command_trace) == (
        1,
        2,
        3,
    )
    assert all(trace.mmio_cmd == trace.command.register_value() for trace in stream.command_trace)
    assert all(trace.mmio_stat == trace.status.register_value() for trace in stream.command_trace)
    assert tuple(token.index for token in stream.tokens) == tuple(range(TOKEN_COUNT))
    assert stream.text == " ".join(token.text for token in stream.tokens)

    flags = dict(stream.safety_flags)
    assert flags["offlineOnly"] is True
    assert flags["deterministic"] is True
    assert flags["dummyManifestOnly"] is True
    assert flags["fakeTokensOnly"] is True
    assert flags["boardAccess"] is False
    assert flags["sshExecution"] is False
    assert flags["hfTouched"] is False
    assert flags["networkCalls"] is False
    assert flags["environmentRead"] is False
    assert flags["modelExecution"] is False


def test_cli_dummy_e2e_summary_is_concise_and_deterministic() -> None:
    command = [str(CLI_PATH), "dummy-e2e", "--seed", "42"]
    first = subprocess.run(command, check=True, capture_output=True, text=True)
    second = subprocess.run(command, check=True, capture_output=True, text=True)

    assert first.stderr == ""
    assert first.stdout == second.stdout
    assert first.stdout == format_dummy_e2e_summary(dummy_e2e(42))
    assert first.stdout.endswith("\n")
    assert "dummy_e2e: ok\n" in first.stdout
    assert "seed: 42\n" in first.stdout
    assert "tokens: 6\n" in first.stdout
    assert "offline: board=false ssh=false hf=false network=false\n" in first.stdout


def test_source_has_offline_claim_guard() -> None:
    source = read_text(MODULE_PATH)
    cli = read_text(CLI_PATH)
    combined = source + "\n" + cli

    forbidden_runtime_terms = [
        "huggingface_hub",
        "hf_hub_download",
        ".safetensors",
        ".gguf",
        ".pt",
        ".pth",
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "paramiko",
        "fabric",
        "os.environ",
        "getenv",
    ]
    lowered = combined.lower()
    for term in forbidden_runtime_terms:
        assert term not in lowered, term

    forbidden_private_patterns = [
        r"/home/[^\s\"']+",
        r"/Users/[^\s\"']+",
        r"[A-Za-z]:\\Users\\",
        r"\b(?:api[_-]?key|authorization|bearer|password|secret|token)\b\s*[:=]",
    ]
    summary = format_dummy_e2e_summary(dummy_e2e(42))
    for pattern in forbidden_private_patterns:
        assert not re.search(pattern, summary, re.IGNORECASE), pattern


def test_source_headers_for_touched_code_files() -> None:
    expected_headers = {
        MODULE_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        CLI_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        TEST_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
    }
    for path, header in expected_headers.items():
        assert read_text(path).splitlines()[: len(header)] == header, path


test_dummy_e2e_is_deterministic_for_same_seed()
test_dummy_e2e_wires_manifest_axi_mock_and_result_stream()
test_cli_dummy_e2e_summary_is_concise_and_deterministic()
test_source_has_offline_claim_guard()
test_source_headers_for_touched_code_files()

print("dummy e2e contract tests ok")
