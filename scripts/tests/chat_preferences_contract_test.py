#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat preferences contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_preferences_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-preferences.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-preferences-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-preferences.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_preferences_contract",
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
        "cloud provider " + "ready",
    ]
    lowered = text.lower()
    for claim in literal_claims:
        assert claim.lower() not in lowered, claim


def test_chat_preferences_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_preferences()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_preferences_json(generated) == module.chat_preferences_json(generated)
    assert module.chat_preferences_json(generated).endswith("\n")
    assert json.loads(module.chat_preferences_json(generated)) == fixture


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
    preferences = module.create_gemma3n_e4b_kv260_chat_preferences()
    allowed = set(module.CHAT_PREFERENCES_STATE_VALUES)

    assert tuple(preferences.keys()) == module.CHAT_PREFERENCES_FIELDS
    assert preferences["schemaVersion"] == "pccx.chatPreferences.v0"

    states = list(iter_state_values(preferences))
    assert states
    for state in states:
        assert state in allowed, state

    for panel in preferences["preferencePanels"]:
        assert tuple(panel.keys()) == module.PREFERENCE_PANEL_FIELDS
    for control in preferences["preferenceControls"]:
        assert tuple(control.keys()) == module.PREFERENCE_CONTROL_FIELDS
    for reason in preferences["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS


def test_chat_preferences_covers_issue_9_settings_boundary() -> None:
    preferences = load_module().create_gemma3n_e4b_kv260_chat_preferences()
    flags = preferences["safetyFlags"]
    panels = {panel["panelId"]: panel for panel in preferences["preferencePanels"]}
    controls = {
        control["controlId"]: control
        for control in preferences["preferenceControls"]
    }
    reasons = {reason["reasonId"]: reason for reason in preferences["blockedReasons"]}

    assert preferences["preferencesState"] == "available_as_data"
    assert preferences["storageState"] == "not_configured"
    assert preferences["privacyState"] == "summary_only"
    assert set(panels) == {
        "model_target_preferences",
        "privacy_preferences",
        "local_only_preferences",
        "transcript_preferences",
        "session_preferences",
    }
    assert panels["local_only_preferences"]["enabled"] is False
    assert set(controls) == {
        "target_model_display",
        "target_device_display",
        "model_asset_picker",
        "local_only_mode",
        "cloud_fallback",
        "transcript_retention",
        "transcript_export",
        "session_store_location",
        "diagnostics_verbosity",
    }
    assert controls["target_model_display"]["currentValue"] == "gemma3n-e4b"
    assert controls["target_device_display"]["currentValue"] == "kv260"
    assert controls["model_asset_picker"]["state"] == "disabled"
    assert controls["local_only_mode"]["currentValue"] is True
    assert controls["cloud_fallback"]["currentValue"] is False
    assert controls["transcript_retention"]["currentValue"] == "not_configured"
    assert controls["session_store_location"]["state"] == "unavailable"
    assert {
        "preferences_persistence_not_reviewed",
        "model_asset_picker_not_reviewed",
        "session_store_not_configured",
        "provider_and_network_paths_blocked",
    } <= set(reasons)
    assert flags["readOnly"] is True
    assert flags["preferencesDisplayOnly"] is True
    assert flags["preferencePersistence"] is False
    assert flags["preferenceWrite"] is False
    assert flags["configRead"] is False
    assert flags["environmentRead"] is False
    assert flags["secretsRead"] is False
    assert flags["tokensRead"] is False
    assert flags["providerConfigRead"] is False
    assert flags["providerCalls"] is False
    assert flags["cloudCalls"] is False
    assert flags["networkCalls"] is False
    assert flags["modelAssetRead"] is False
    assert flags["modelPathIncluded"] is False
    assert flags["modelExecution"] is False
    assert flags["runtimeExecution"] is False
    assert flags["kv260Access"] is False
    assert flags["sessionStoreRead"] is False
    assert flags["sessionStoreWrite"] is False
    assert flags["promptContentIncluded"] is False
    assert flags["responseContentIncluded"] is False
    assert flags["transcriptContentIncluded"] is False
    assert flags["transcriptPersistence"] is False
    assert flags["transcriptExport"] is False
    assert flags["readsArtifacts"] is False
    assert flags["writesArtifacts"] is False
    assert flags["executesPccxLab"] is False
    assert flags["executesSystemverilogIde"] is False
    assert flags["compatibilityClaim"] is False


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
    assert '"modelPath":' not in fixture_text
    assert '"privatePath":' not in fixture_text


def test_docs_readme_status_tests_and_ci_reference_preferences() -> None:
    docs = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "chat_preferences_contract.py" in docs
    assert "chat-preferences-stub.sh" in docs
    assert "chat-preferences.gemma3n-e4b-kv260-placeholder.json" in docs
    assert "chat preferences" in docs
    assert "--include-chat-preferences" in docs
    assert "chat-preferences-stub.sh" in readme
    assert "--include-chat-preferences" in readme
    assert "status-chat-preferences" in ci
    assert "chat_preferences_contract_test.py" in ci
    assert "no config/provider/session-store/model path" in status_test


if __name__ == "__main__":
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
    print("chat preferences contract tests ok")
