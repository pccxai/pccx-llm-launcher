#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat session-index contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_session_index_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-session-index.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-session-index-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-session-index.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_session_index_contract",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_state_values(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            if (
                key == "state"
                or key.endswith("State")
                or key.endswith("Status")
            ) and isinstance(nested, str):
                yield nested
            yield from iter_state_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_state_values(nested)


def iter_keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key
            yield from iter_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_keys(nested)


def assert_no_private_or_generated_data(text: str) -> None:
    forbidden_patterns = [
        r"/home/[^\s\"']+",
        r"/Users/[^\s\"']+",
        r"[A-Za-z]:\\Users\\",
        r"\b(?:api[_-]?key|authorization|bearer|client[_-]?secret|password|private[_-]?key|secret|token)\b\s*[:=]",
        r"\.(?:gguf|safetensors|ckpt|pt|pth|onnx)\b",
        r"(?:weights|model_weights|model-cache)/(?:[^\"'\s]+)",
        r"(?:raw[_-]?full[_-]?logs|hardware[_-]?dump|generated[_-]?blob)\s*[:=]",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, text, re.IGNORECASE), pattern


def assert_no_runtime_implementation_terms(source: str) -> None:
    forbidden = [
        "subprocess",
        "os.system",
        "popen",
        "socket",
        "urllib",
        "requests",
        "http.client",
        "openai",
        "anthropic",
        "gemini",
        "modelcontextprotocol",
        "websocket",
        "xmutil",
        "xrt-smi",
        "lsusb",
        "dmesg",
    ]
    lowered = source.lower()
    for term in forbidden:
        assert term not in lowered, term


def assert_no_provider_configs(value) -> None:
    forbidden_keys = {
        "apiKey",
        "accessToken",
        "refreshToken",
        "authorization",
        "bearerToken",
        "provider",
        "providers",
        "providerConfig",
        "providerConfigs",
    }
    for key in iter_keys(value):
        assert key not in forbidden_keys, key


def assert_no_unsupported_claims(text: str) -> None:
    literal_claims = [
        "production-ready",
        "marketplace-ready",
        "stable API",
        "stable ABI",
        "KV260 inference works",
        "Gemma 3N E4B runs on KV260",
        "20 tok/s achieved",
        "timing closed",
        "bitstream ready",
        "launcher executes pccx-lab",
        "IDE controls launcher",
        "AI provider integration is live",
    ]
    lowered = text.lower()
    for claim in literal_claims:
        assert claim.lower() not in lowered, claim


def test_chat_session_index_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_session_index()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert (
        module.chat_session_index_json(generated)
        == module.chat_session_index_json(generated)
    )
    assert module.chat_session_index_json(generated).endswith("\n")
    assert json.loads(module.chat_session_index_json(generated)) == fixture


def test_cli_stub_outputs_deterministic_json() -> None:
    fixture = json.loads(read_text(FIXTURE_PATH))
    command = [
        "bash",
        str(SCRIPT_PATH),
        "--model",
        "gemma3n-e4b",
        "--target",
        "kv260",
    ]
    first = subprocess.run(command, check=True, capture_output=True, text=True)
    second = subprocess.run(command, check=True, capture_output=True, text=True)

    assert first.stderr == ""
    assert first.stdout == second.stdout
    assert first.stdout.endswith("\n")
    assert json.loads(first.stdout) == fixture


def test_required_fields_and_allowed_states() -> None:
    module = load_module()
    index = module.create_gemma3n_e4b_kv260_chat_session_index()
    allowed = set(module.CHAT_SESSION_INDEX_STATE_VALUES)

    assert tuple(index.keys()) == module.CHAT_SESSION_INDEX_FIELDS
    assert index["schemaVersion"] == "pccx.chatSessionIndex.v0"
    assert tuple(index["indexPolicy"].keys()) == module.INDEX_POLICY_FIELDS
    assert tuple(index["emptyState"].keys()) == module.EMPTY_STATE_FIELDS

    states = list(iter_state_values(index))
    assert states
    for state in states:
        assert state in allowed, state

    for control in index["indexControls"]:
        assert tuple(control.keys()) == module.INDEX_CONTROL_FIELDS
    for reason in index["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in index["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_session_index_covers_issue_9_session_sidebar_boundary() -> None:
    index = load_module().create_gemma3n_e4b_kv260_chat_session_index()
    flags = index["safetyFlags"]
    policy = index["indexPolicy"]
    controls = {control["controlId"]: control for control in index["indexControls"]}
    reasons = {reason["reasonId"]: reason for reason in index["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in index["handoffRefs"]}

    assert index["indexState"] == "not_configured"
    assert index["sessionStoreState"] == "not_configured"
    assert index["manifestState"] == "unavailable"
    assert index["selectionState"] == "disabled"
    assert index["restoreState"] == "unavailable"
    assert index["contentState"] == "empty_not_captured"
    assert index["privacyState"] == "summary_only"
    assert policy["localStoreConfigured"] is False
    assert policy["manifestReadEnabled"] is False
    assert policy["transcriptReadEnabled"] is False
    assert index["emptyState"]["itemCount"] == 0
    assert set(controls) == {
        "open_session_index",
        "refresh_session_index",
        "select_session",
        "restore_selected_session",
        "rename_session",
        "delete_session",
    }
    assert controls["open_session_index"]["enabled"] is True
    assert controls["refresh_session_index"]["enabled"] is False
    assert controls["restore_selected_session"]["state"] == "unavailable"
    assert {
        "session_store_not_configured",
        "session_manifest_boundary_absent",
        "session_titles_not_captured",
        "active_session_absent",
        "artifact_read_boundary_absent",
    } <= set(reasons)
    assert set(refs) == {
        "chat_session",
        "chat_session_lifecycle",
        "chat_transcript_policy",
        "chat_readiness",
    }
    assert flags["readOnly"] is True
    assert flags["sessionIndexDisplayOnly"] is True
    assert flags["readsArtifacts"] is False
    assert flags["writesArtifacts"] is False
    assert flags["readsSessionManifest"] is False
    assert flags["readsTranscript"] is False
    assert flags["sessionPersistence"] is False
    assert flags["transcriptPersistence"] is False
    assert flags["sessionTitleIncluded"] is False
    assert flags["summaryIncluded"] is False
    assert flags["promptContentIncluded"] is False
    assert flags["responseContentIncluded"] is False
    assert flags["modelExecution"] is False
    assert flags["runtimeExecution"] is False
    assert flags["kv260Access"] is False
    assert flags["providerCalls"] is False
    assert flags["executesPccxLab"] is False


def test_contract_avoids_runtime_or_private_data() -> None:
    module_source = read_text(MODULE_PATH)
    fixture_text = read_text(FIXTURE_PATH)
    fixture = json.loads(fixture_text)

    assert_no_runtime_implementation_terms(module_source)
    assert_no_private_or_generated_data(fixture_text)
    assert_no_provider_configs(fixture)
    assert_no_unsupported_claims(fixture_text)
    assert "hello" not in fixture_text.lower()
    assert "promptText" not in fixture_text
    assert "responseText" not in fixture_text
    assert "sessionTitleText" not in fixture_text


def test_docs_readme_status_tests_and_ci_reference_session_index() -> None:
    docs = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "chat_session_index_contract.py" in docs
    assert "chat-session-index-stub.sh" in docs
    assert "chat-session-index.gemma3n-e4b-kv260-placeholder.json" in docs
    assert "chat session index" in docs
    assert "--include-chat-session-index" in docs
    assert "chat-session-index-stub.sh" in readme
    assert "--include-chat-session-index" in readme
    assert "status-chat-session-index" in ci
    assert "chat_session_index_contract_test.py" in ci
    assert "no session-store/transcript/prompt" in status_test


if __name__ == "__main__":
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
    print("chat session index contract tests ok")
