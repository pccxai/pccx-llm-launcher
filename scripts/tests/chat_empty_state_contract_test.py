#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat empty-state contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_empty_state_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-empty-state.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-empty-state-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-empty-state.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_empty_state_contract",
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
        "gem" + "ini",
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
        "production" + "-ready",
        "marketplace" + "-ready",
        "stable " + "API",
        "stable " + "ABI",
        "KV260 inference " + "works",
        "Gemma 3N E4B " + "runs on KV260",
        "20 tok/s " + "achieved",
        "timing " + "closed",
        "bitstream " + "ready",
        "launcher executes " + "pccx-lab",
        "IDE controls " + "launcher",
        "AI provider integration " + "is live",
    ]
    lowered = text.lower()
    for claim in literal_claims:
        assert claim.lower() not in lowered, claim


def test_chat_empty_state_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_empty_state()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_empty_state_json(generated) == (
        module.chat_empty_state_json(generated)
    )
    assert module.chat_empty_state_json(generated).endswith("\n")
    assert json.loads(module.chat_empty_state_json(generated)) == fixture


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
    state = module.create_gemma3n_e4b_kv260_chat_empty_state()
    allowed = set(module.CHAT_EMPTY_STATE_VALUES)

    assert tuple(state.keys()) == module.CHAT_EMPTY_STATE_FIELDS
    assert state["schemaVersion"] == "pccx.chatEmptyState.v0"
    assert tuple(state["emptyStatePolicy"].keys()) == (
        module.EMPTY_STATE_POLICY_FIELDS
    )

    states = list(iter_state_values(state))
    assert states
    for value in states:
        assert value in allowed, value

    for slot in state["displaySlots"]:
        assert tuple(slot.keys()) == module.DISPLAY_SLOT_FIELDS
    for hint in state["affordanceHints"]:
        assert tuple(hint.keys()) == module.AFFORDANCE_HINT_FIELDS
    for reason in state["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in state["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_empty_state_keeps_surface_display_only() -> None:
    state = load_module().create_gemma3n_e4b_kv260_chat_empty_state()
    policy = state["emptyStatePolicy"]
    flags = state["safetyFlags"]
    slots = {slot["slotId"]: slot for slot in state["displaySlots"]}
    hints = {hint["hintId"]: hint for hint in state["affordanceHints"]}
    reasons = {reason["reasonId"]: reason for reason in state["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in state["handoffRefs"]}

    assert state["emptyStateState"] == "available_as_data"
    assert state["surfaceState"] == "placeholder"
    assert state["sessionState"] == "inactive"
    assert state["modelState"] == "not_loaded"
    assert state["readinessState"] == "blocked"
    assert state["promptState"] == "empty_not_captured"
    assert state["transcriptState"] == "empty_not_captured"
    assert state["actionState"] == "disabled"
    assert state["runtimeState"] == "not_started"
    assert policy["sideEffectPolicy"] == "local_render_only"

    assert set(slots) == {
        "target_banner",
        "empty_transcript_notice",
        "readiness_notice",
        "composer_disabled_notice",
        "local_only_notice",
    }
    assert slots["target_banner"]["state"] == "target_selected"
    assert slots["empty_transcript_notice"]["state"] == "empty_not_captured"
    assert slots["readiness_notice"]["state"] == "blocked"
    assert slots["composer_disabled_notice"]["state"] == "disabled"
    assert slots["local_only_notice"]["state"] == "summary_only"
    for slot in slots.values():
        assert slot["visible"] is True
        assert slot["enabled"] is True

    assert hints["start_new_session_hint"]["state"] == "disabled"
    assert hints["select_model_hint"]["state"] == "blocked"
    assert hints["review_readiness_hint"]["state"] == "available_as_data"
    assert hints["focus_composer_hint"]["state"] == "disabled"
    for hint in hints.values():
        assert hint["enabled"] is False

    assert reasons["runtime_evidence_absent"]["state"] == "blocked"
    assert reasons["model_asset_boundary_absent"]["state"] == "not_configured"
    assert reasons["session_store_not_configured"]["state"] == "not_configured"
    assert reasons["prompt_capture_blocked"]["state"] == "empty_not_captured"
    assert reasons["transcript_content_absent"]["state"] == "empty_not_captured"
    assert reasons["action_execution_disabled"]["state"] == "disabled"
    assert refs["chat_surface_layout"]["state"] == "placeholder"
    assert refs["chat_readiness"]["state"] == "blocked"
    assert refs["chat_composer"]["state"] == "blocked"
    assert refs["chat_action_bar"]["state"] == "disabled"

    true_flags = {
        "dataOnly",
        "readOnly",
        "deterministic",
        "emptyStateDisplayOnly",
        "emptyStateTextOnly",
        "localRenderOnly",
    }
    false_flags = set(flags) - true_flags
    for flag in true_flags:
        assert flags[flag] is True, flag
    for flag in false_flags:
        assert flags[flag] is False, flag


def test_chat_empty_state_docs_and_ci_are_wired() -> None:
    doc = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "contracts/chat_empty_state_contract.py" in doc
    assert (
        "contracts/fixtures/chat-empty-state.gemma3n-e4b-kv260-placeholder.json"
        in doc
    )
    assert "scripts/chat-empty-state-stub.sh" in doc
    assert "scripts/tests/chat_empty_state_contract_test.py" in doc
    assert "scripts/tests/status-chat-empty-state.sh" in doc
    assert "chat-empty-state-stub.sh" in readme
    assert "--include-chat-empty-state" in readme
    assert "chat_empty_state_contract_test.py" in ci
    assert "status-chat-empty-state.sh" in ci
    assert "--include-chat-empty-state" in status_test
    assert "no prompt/response/transcript/session-store" in status_test


def test_contract_does_not_read_runtime_provider_hardware_or_private_data() -> None:
    source = read_text(MODULE_PATH)
    fixture_text = read_text(FIXTURE_PATH)
    fixture = json.loads(fixture_text)
    combined = (
        source
        + fixture_text
        + read_text(SCRIPT_PATH)
        + read_text(STATUS_TEST_PATH)
        + read_text(DOC_PATH)
        + read_text(README_PATH)
    )

    assert_no_runtime_implementation_terms(source)
    assert_no_private_or_generated_data(fixture_text)
    assert_no_provider_configs(fixture)
    assert_no_unsupported_claims(combined)

    forbidden_fixture_keys = [
        "promptText",
        "responseText",
        "transcriptText",
        "messageBody",
        "summaryText",
        "sessionTitle",
        "commandId",
        "launcherAction",
        "userAction",
        "modelPath",
        "tokenizerPath",
        "runtimePayload",
        "runtimeLog",
        "privatePath",
    ]
    for key in forbidden_fixture_keys:
        assert f'"{key}"' not in fixture_text, key


if __name__ == "__main__":
    test_chat_empty_state_matches_fixture_and_is_deterministic()
    test_cli_stub_outputs_deterministic_json()
    test_required_fields_and_allowed_states()
    test_chat_empty_state_keeps_surface_display_only()
    test_chat_empty_state_docs_and_ci_are_wired()
    test_contract_does_not_read_runtime_provider_hardware_or_private_data()
    print("chat empty-state contract tests passed")
