#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat model-selection policy contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_model_selection_policy_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-model-selection-policy.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-model-selection-policy-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-model-selection-policy.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_model_selection_policy_contract",
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
        "import " + "requests",
        "from " + "requests",
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


def test_chat_model_selection_policy_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_model_selection_policy()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_model_selection_policy_json(generated) == (
        module.chat_model_selection_policy_json(generated)
    )
    assert module.chat_model_selection_policy_json(generated).endswith("\n")
    assert json.loads(module.chat_model_selection_policy_json(generated)) == fixture


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
    policy = module.create_gemma3n_e4b_kv260_chat_model_selection_policy()
    allowed = set(module.CHAT_MODEL_SELECTION_POLICY_STATE_VALUES)

    assert tuple(policy.keys()) == module.CHAT_MODEL_SELECTION_POLICY_FIELDS
    assert policy["schemaVersion"] == "pccx.chatModelSelectionPolicy.v0"
    assert tuple(policy["selectionPolicy"].keys()) == (
        module.SELECTION_POLICY_FIELDS
    )

    states = list(iter_state_values(policy))
    assert states
    for state in states:
        assert state in allowed, state

    for option in policy["modelOptions"]:
        assert tuple(option.keys()) == module.MODEL_OPTION_FIELDS
    for control in policy["selectionControls"]:
        assert tuple(control.keys()) == module.SELECTION_CONTROL_FIELDS
    for reason in policy["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in policy["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_model_selection_policy_keeps_picker_disabled() -> None:
    policy = load_module().create_gemma3n_e4b_kv260_chat_model_selection_policy()
    selection_policy = policy["selectionPolicy"]
    options = {option["optionId"]: option for option in policy["modelOptions"]}
    controls = {
        control["controlId"]: control for control in policy["selectionControls"]
    }
    reasons = {reason["reasonId"]: reason for reason in policy["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in policy["handoffRefs"]}
    flags = policy["safetyFlags"]

    assert policy["selectionState"] == "blocked"
    assert policy["catalogState"] == "static_placeholder"
    assert policy["pickerState"] == "disabled"
    assert policy["selectedModelState"] == "target_selected"
    assert policy["descriptorState"] == "available_as_data"
    assert policy["assetDiscoveryState"] == "blocked"
    assert policy["assetPathState"] == "not_configured"
    assert policy["providerFallbackState"] == "disabled"
    assert policy["loadRequestState"] == "blocked"
    assert selection_policy["staticOptionCount"] == 1
    assert selection_policy["dynamicCatalogConfigured"] is False
    assert selection_policy["localCatalogRead"] is False
    assert selection_policy["assetDiscoveryEnabled"] is False
    assert selection_policy["selectionEnabled"] is False
    assert selection_policy["selectionPersistenceEnabled"] is False
    assert selection_policy["providerFallbackEnabled"] is False
    assert selection_policy["loadRequestEnabled"] is False

    option = options["gemma3n_e4b_kv260_placeholder"]
    assert option["selected"] is True
    assert option["enabled"] is False
    assert option["assetPolicy"] == "placeholder_descriptor_only_no_asset_path"

    for control in controls.values():
        assert control["enabled"] is False
    assert controls["open_model_catalog"]["state"] == "blocked"
    assert controls["select_model_option"]["state"] == "disabled"
    assert controls["discover_local_assets"]["state"] == "blocked"
    assert controls["handoff_to_load_request"]["state"] == "blocked"

    assert reasons["dynamic_catalog_boundary_absent"]["state"] == "not_configured"
    assert reasons["selection_executor_absent"]["state"] == "disabled"
    assert reasons["model_asset_discovery_blocked"]["state"] == "blocked"
    assert reasons["provider_fallback_disabled"]["state"] == "disabled"
    assert reasons["load_request_blocked"]["state"] == "blocked"
    assert refs["chat_model_load_request"]["state"] == "blocked"

    true_flags = {
        "dataOnly",
        "readOnly",
        "deterministic",
        "selectionPolicyDisplayOnly",
        "staticOptionOnly",
    }
    false_flags = set(flags) - true_flags
    for flag in true_flags:
        assert flags[flag] is True, flag
    for flag in false_flags:
        assert flags[flag] is False, flag


def test_chat_model_selection_policy_docs_and_ci_are_wired() -> None:
    doc = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "contracts/chat_model_selection_policy_contract.py" in doc
    assert (
        "contracts/fixtures/chat-model-selection-policy.gemma3n-e4b-kv260-placeholder.json"
        in doc
    )
    assert "scripts/chat-model-selection-policy-stub.sh" in doc
    assert "scripts/tests/chat_model_selection_policy_contract_test.py" in doc
    assert "scripts/tests/status-chat-model-selection-policy.sh" in doc
    assert "chat-model-selection-policy-stub.sh" in readme
    assert "--include-chat-model-selection-policy" in readme
    assert "chat_model_selection_policy_contract_test.py" in ci
    assert "status-chat-model-selection-policy.sh" in ci
    assert "--include-chat-model-selection-policy" in status_test
    assert "no catalog/config/model asset path/read/load/runtime" in status_test


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
        "modelPath",
        "assetPath",
        "tokenizerPath",
        "checksumValue",
        "runtimeLog",
        "privatePath",
    ]
    for key in forbidden_fixture_keys:
        assert f'"{key}"' not in fixture_text, key


if __name__ == "__main__":
    test_chat_model_selection_policy_matches_fixture_and_is_deterministic()
    test_cli_stub_outputs_deterministic_json()
    test_required_fields_and_allowed_states()
    test_chat_model_selection_policy_keeps_picker_disabled()
    test_chat_model_selection_policy_docs_and_ci_are_wired()
    test_contract_does_not_read_runtime_provider_hardware_or_private_data()
    print("chat model-selection policy contract tests passed")
