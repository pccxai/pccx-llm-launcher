#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat accessibility contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_accessibility_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-accessibility.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-accessibility-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-accessibility.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_accessibility_contract",
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


def test_chat_accessibility_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_accessibility()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_accessibility_json(generated) == (
        module.chat_accessibility_json(generated)
    )
    assert module.chat_accessibility_json(generated).endswith("\n")
    assert json.loads(module.chat_accessibility_json(generated)) == fixture


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
    state = module.create_gemma3n_e4b_kv260_chat_accessibility()
    allowed = set(module.CHAT_ACCESSIBILITY_VALUES)

    assert tuple(state.keys()) == module.CHAT_ACCESSIBILITY_FIELDS
    assert state["schemaVersion"] == "pccx.chatAccessibility.v0"
    assert tuple(state["accessibilityPolicy"].keys()) == (
        module.ACCESSIBILITY_POLICY_FIELDS
    )

    states = list(iter_state_values(state))
    assert states
    for value in states:
        assert value in allowed, value

    for region in state["landmarkRegions"]:
        assert tuple(region.keys()) == module.LANDMARK_REGION_FIELDS
    for binding in state["ariaBindings"]:
        assert tuple(binding.keys()) == module.ARIA_BINDING_FIELDS
    for item in state["focusOrderItems"]:
        assert tuple(item.keys()) == module.FOCUS_ORDER_ITEM_FIELDS
    for gate in state["reviewGates"]:
        assert tuple(gate.keys()) == module.REVIEW_GATE_FIELDS
    for reason in state["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in state["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_accessibility_keeps_ui_accessibility_metadata_only() -> None:
    state = load_module().create_gemma3n_e4b_kv260_chat_accessibility()
    policy = state["accessibilityPolicy"]
    flags = state["safetyFlags"]
    regions = {region["regionId"]: region for region in state["landmarkRegions"]}
    bindings = {binding["bindingId"]: binding for binding in state["ariaBindings"]}
    order_items = {item["orderId"]: item for item in state["focusOrderItems"]}
    gates = {gate["gateId"]: gate for gate in state["reviewGates"]}
    reasons = {reason["reasonId"]: reason for reason in state["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in state["handoffRefs"]}

    assert state["accessibilityState"] == "available_as_data"
    assert state["surfaceState"] == "placeholder"
    assert state["semanticState"] == "planned"
    assert state["announcementState"] == "disabled"
    assert state["focusOrderState"] == "inactive"
    assert state["contrastState"] == "requires_review"
    assert state["motionState"] == "requires_review"
    assert state["inputState"] == "disabled"
    assert state["runtimeState"] == "not_started"
    assert policy["sideEffectPolicy"] == "local_render_only"

    assert set(regions) == {
        "chat_shell",
        "model_status_header",
        "readiness_banner",
        "conversation_region",
        "composer_region",
        "action_bar_region",
    }
    assert regions["chat_shell"]["role"] == "application_region"
    assert regions["conversation_region"]["state"] == "empty_not_captured"
    assert regions["composer_region"]["state"] == "disabled"
    assert all(region["visible"] is True for region in regions.values())
    assert all(region["enabled"] is False for region in regions.values())

    assert set(bindings) == {
        "surface_landmark_label",
        "model_status_label",
        "readiness_status_label",
        "transcript_region_label",
        "composer_disabled_label",
        "actions_disabled_label",
    }
    assert bindings["transcript_region_label"]["ariaRole"] == "log"
    assert bindings["composer_disabled_label"]["state"] == "disabled"
    assert all(binding["enabled"] is False for binding in bindings.values())

    assert [item["orderIndex"] for item in state["focusOrderItems"]] == [
        1,
        2,
        3,
        4,
        5,
    ]
    assert all(item["tabStop"] is False for item in order_items.values())
    assert all(
        item["sideEffectPolicy"] == "no_focus_change"
        for item in order_items.values()
    )

    assert gates["semantic_labels_reviewed"]["state"] == "requires_review"
    assert gates["contrast_tokens_reviewed"]["state"] == "requires_review"
    assert gates["reduced_motion_reviewed"]["state"] == "requires_review"
    assert gates["live_region_behavior_reviewed"]["state"] == "disabled"
    assert gates["keyboard_path_reviewed"]["state"] == "blocked"
    assert all(gate["enabled"] is False for gate in gates.values())

    assert reasons["focus_manager_not_installed"]["state"] == "not_installed"
    assert reasons["live_regions_disabled"]["state"] == "disabled"
    assert reasons["contrast_review_missing"]["state"] == "requires_review"
    assert reasons["content_boundaries_blocked"]["state"] == "blocked"
    assert refs["chat_surface_layout"]["state"] == "placeholder"
    assert refs["chat_shortcut_map"]["state"] == "blocked"

    true_flags = {
        "dataOnly",
        "readOnly",
        "deterministic",
        "accessibilityMetadataOnly",
        "semanticLabelsOnly",
        "localRenderOnly",
    }
    false_flags = set(flags) - true_flags
    for flag in true_flags:
        assert flags[flag] is True, flag
    for flag in false_flags:
        assert flags[flag] is False, flag


def test_chat_accessibility_docs_and_ci_are_wired() -> None:
    doc = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "contracts/chat_accessibility_contract.py" in doc
    assert (
        "contracts/fixtures/chat-accessibility.gemma3n-e4b-kv260-placeholder.json"
        in doc
    )
    assert "scripts/chat-accessibility-stub.sh" in doc
    assert "scripts/tests/chat_accessibility_contract_test.py" in doc
    assert "scripts/tests/status-chat-accessibility.sh" in doc
    assert "chat-accessibility-stub.sh" in readme
    assert "--include-chat-accessibility" in readme
    assert "chat_accessibility_contract_test.py" in ci
    assert "status-chat-accessibility.sh" in ci
    assert "--include-chat-accessibility" in status_test
    assert "no prompt/response/transcript/session-store" in status_test


def test_contract_has_no_runtime_provider_hardware_or_private_surface() -> None:
    state = load_module().create_gemma3n_e4b_kv260_chat_accessibility()
    source = read_text(MODULE_PATH)
    fixture_text = read_text(FIXTURE_PATH)
    combined = "\n".join(
        [
            source,
            fixture_text,
            read_text(SCRIPT_PATH),
            read_text(STATUS_TEST_PATH),
            read_text(DOC_PATH),
            read_text(README_PATH),
        ]
    )

    assert_no_runtime_implementation_terms(source)
    assert_no_private_or_generated_data(fixture_text)
    assert_no_provider_configs(state)
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


def test_source_headers_for_touched_code_files() -> None:
    expected_headers = {
        MODULE_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        SCRIPT_PATH: [
            "#!/usr/bin/env bash",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        STATUS_TEST_PATH: [
            "#!/usr/bin/env bash",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        TEST_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        CI_PATH: [
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
    }

    for path, header in expected_headers.items():
        assert read_text(path).splitlines()[: len(header)] == header, path


if __name__ == "__main__":
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
    print("chat accessibility contract tests ok")
