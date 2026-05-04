#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat action-bar contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_action_bar_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-action-bar.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-action-bar-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-action-bar.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_action_bar_contract",
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


def test_chat_action_bar_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_action_bar()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_action_bar_json(generated) == (
        module.chat_action_bar_json(generated)
    )
    assert module.chat_action_bar_json(generated).endswith("\n")
    assert json.loads(module.chat_action_bar_json(generated)) == fixture


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
    action_bar = module.create_gemma3n_e4b_kv260_chat_action_bar()
    allowed = set(module.CHAT_ACTION_BAR_STATE_VALUES)

    assert tuple(action_bar.keys()) == module.CHAT_ACTION_BAR_FIELDS
    assert action_bar["schemaVersion"] == "pccx.chatActionBar.v0"
    assert tuple(action_bar["actionPolicy"].keys()) == module.ACTION_POLICY_FIELDS

    states = list(iter_state_values(action_bar))
    assert states
    for state in states:
        assert state in allowed, state

    for group in action_bar["actionGroups"]:
        assert tuple(group.keys()) == module.ACTION_GROUP_FIELDS
    for control in action_bar["actionControls"]:
        assert tuple(control.keys()) == module.ACTION_CONTROL_FIELDS
    for reason in action_bar["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in action_bar["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_action_bar_keeps_actions_disabled() -> None:
    action_bar = load_module().create_gemma3n_e4b_kv260_chat_action_bar()
    policy = action_bar["actionPolicy"]
    flags = action_bar["safetyFlags"]
    groups = {group["groupId"]: group for group in action_bar["actionGroups"]}
    controls = {
        control["actionId"]: control
        for control in action_bar["actionControls"]
    }
    reasons = {reason["reasonId"]: reason for reason in action_bar["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in action_bar["handoffRefs"]}

    assert action_bar["actionBarState"] == "blocked"
    assert action_bar["conversationState"] == "inactive"
    assert action_bar["selectionState"] == "disabled"
    assert action_bar["transcriptState"] == "not_started"
    assert action_bar["responseState"] == "not_generated"
    assert action_bar["attachmentState"] == "disabled"
    assert action_bar["clipboardState"] == "disabled"
    assert action_bar["exportState"] == "disabled"
    assert action_bar["stopControlState"] == "disabled"
    assert policy["sideEffectPolicy"] == "local_render_only"
    assert set(groups) == {
        "conversation_actions",
        "message_actions",
        "transcript_actions",
        "runtime_actions",
        "attachment_actions",
    }
    assert all(group["enabled"] is False for group in groups.values())
    assert set(controls) == {
        "new_chat",
        "clear_conversation",
        "export_transcript",
        "retry_response",
        "copy_response",
        "stop_response",
        "attach_context",
    }
    assert all(control["enabled"] is False for control in controls.values())
    assert controls["new_chat"]["state"] == "blocked"
    assert controls["clear_conversation"]["state"] == "disabled"
    assert controls["export_transcript"]["sideEffectPolicy"] == "no_transcript_export"
    assert controls["retry_response"]["resultState"] == "not_generated"
    assert controls["copy_response"]["sideEffectPolicy"] == "no_clipboard_write"
    assert controls["stop_response"]["sideEffectPolicy"] == "no_stop_signal"
    assert controls["attach_context"]["sideEffectPolicy"] == "no_file_or_artifact_read"
    assert set(reasons) == {
        "session_lifecycle_not_enabled",
        "transcript_store_not_configured",
        "transcript_export_not_reviewed",
        "message_content_absent",
        "response_stream_blocked",
        "runtime_stream_not_started",
        "attachment_boundary_absent",
    }
    assert set(refs) == {
        "chat_session",
        "chat_session_lifecycle",
        "chat_readiness",
        "chat_composer",
        "chat_send_result",
        "chat_response_stream",
        "chat_message_list",
        "chat_transcript_policy",
    }
    assert flags["readOnly"] is True
    assert flags["dataOnly"] is True
    assert flags["actionBarDisplayOnly"] is True
    assert flags["actionMetadataOnly"] is True
    assert flags["readsSessionStore"] is False
    assert flags["readsTranscript"] is False
    assert flags["transcriptExport"] is False
    assert flags["sessionStoreRead"] is False
    assert flags["sessionStoreWrite"] is False
    assert flags["conversationCreated"] is False
    assert flags["conversationCleared"] is False
    assert flags["attachmentReads"] is False
    assert flags["fileUpload"] is False
    assert flags["clipboardWrite"] is False
    assert flags["sendAttempted"] is False
    assert flags["retryAttempted"] is False
    assert flags["stopSignalSent"] is False
    assert flags["responseGenerated"] is False
    assert flags["modelExecution"] is False
    assert flags["runtimeExecution"] is False
    assert flags["kv260Access"] is False
    assert flags["networkCalls"] is False
    assert flags["providerCalls"] is False
    assert flags["executesPccxLab"] is False


def test_chat_action_bar_docs_and_ci_are_wired() -> None:
    doc = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "contracts/chat_action_bar_contract.py" in doc
    assert (
        "contracts/fixtures/chat-action-bar.gemma3n-e4b-kv260-placeholder.json"
        in doc
    )
    assert "scripts/chat-action-bar-stub.sh" in doc
    assert "scripts/tests/chat_action_bar_contract_test.py" in doc
    assert "scripts/tests/status-chat-action-bar.sh" in doc
    assert "chat-action-bar-stub.sh" in readme
    assert "--include-chat-action-bar" in readme
    assert "chat_action_bar_contract_test.py" in ci
    assert "status-chat-action-bar.sh" in ci
    assert "--include-chat-action-bar" in status_test


def test_chat_action_bar_has_no_runtime_or_private_surface() -> None:
    module = load_module()
    action_bar = module.create_gemma3n_e4b_kv260_chat_action_bar()
    fixture_text = read_text(FIXTURE_PATH)
    contract_source = read_text(MODULE_PATH)
    stub_source = read_text(SCRIPT_PATH)
    docs = "\n".join(
        [
            fixture_text,
            contract_source,
            stub_source,
            read_text(DOC_PATH),
            read_text(README_PATH),
            read_text(STATUS_TEST_PATH),
        ]
    )

    assert_no_provider_configs(action_bar)
    assert_no_private_or_generated_data(docs)
    assert_no_unsupported_claims(docs)
    assert_no_runtime_implementation_terms(contract_source)
    assert_no_runtime_implementation_terms(stub_source)


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
    print("chat action-bar contract tests ok")
