#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat audit-event contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_audit_event_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-audit-event.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-audit-event-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-audit-event.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_audit_event_contract",
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
            if key == "state" or key.endswith("State") or key.endswith("Status"):
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


def test_chat_audit_event_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_audit_event()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert (
        module.chat_audit_event_json(generated)
        == module.chat_audit_event_json(generated)
    )
    assert module.chat_audit_event_json(generated).endswith("\n")
    assert json.loads(module.chat_audit_event_json(generated)) == fixture


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
    event = module.create_gemma3n_e4b_kv260_chat_audit_event()
    allowed = set(module.CHAT_AUDIT_EVENT_STATE_VALUES)

    assert tuple(event.keys()) == module.CHAT_AUDIT_EVENT_FIELDS
    assert event["schemaVersion"] == "pccx.chatAuditEvent.v0"
    assert tuple(event["eventEnvelope"].keys()) == module.EVENT_ENVELOPE_FIELDS
    assert tuple(event["redactionPolicy"].keys()) == module.REDACTION_POLICY_FIELDS

    states = list(iter_state_values(event))
    assert states
    for state in states:
        assert state in allowed, state

    for field in event["auditFields"]:
        assert tuple(field.keys()) == module.AUDIT_FIELD_FIELDS
    for reason in event["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in event["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_audit_event_covers_issue_9_blocked_audit_boundary() -> None:
    event = load_module().create_gemma3n_e4b_kv260_chat_audit_event()
    flags = event["safetyFlags"]
    envelope = event["eventEnvelope"]
    redaction = event["redactionPolicy"]
    fields = {field["fieldId"]: field for field in event["auditFields"]}
    reasons = {reason["reasonId"]: reason for reason in event["blockedReasons"]}

    assert event["auditState"] == "available_as_data"
    assert event["eventState"] == "blocked"
    assert event["loggingState"] == "not_configured"
    assert event["contentState"] == "empty_not_captured"
    assert event["persistenceState"] == "disabled"
    assert event["storageState"] == "not_configured"
    assert event["privacyState"] == "summary_only"
    assert envelope["state"] == "blocked"
    assert envelope["promptContentIncluded"] is False
    assert envelope["responseContentIncluded"] is False
    assert envelope["transcriptContentIncluded"] is False
    assert envelope["runtimeStarted"] is False
    assert envelope["modelLoaded"] is False
    assert envelope["writeAttempted"] is False
    assert redaction["state"] == "summary_only"
    assert redaction["promptContentIncluded"] is False
    assert redaction["responseContentIncluded"] is False
    assert redaction["transcriptContentIncluded"] is False
    assert redaction["actorIdentifiersIncluded"] is False
    assert fields["prompt_content"]["included"] is False
    assert fields["response_content"]["included"] is False
    assert fields["transcript_content"]["included"] is False
    assert fields["actor_identifier"]["included"] is False
    assert fields["runtime_trace"]["included"] is False
    assert reasons["audit_logger_not_configured"]["state"] == "not_configured"
    assert reasons["prompt_capture_disabled"]["state"] == "disabled"
    assert reasons["response_generation_absent"]["state"] == "not_generated"
    assert flags["readOnly"] is True
    assert flags["auditEventDisplayOnly"] is True
    assert flags["auditLoggerImplemented"] is False
    assert flags["writesArtifacts"] is False
    assert flags["readsArtifacts"] is False
    assert flags["promptCapture"] is False
    assert flags["promptPersistence"] is False
    assert flags["promptContentIncluded"] is False
    assert flags["responseContentIncluded"] is False
    assert flags["transcriptContentIncluded"] is False
    assert flags["auditEventPersisted"] is False
    assert flags["localStoreConfigured"] is False
    assert flags["eventTimestampRecorded"] is False
    assert flags["actorIdentifierIncluded"] is False
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
    assert "transcriptText" not in fixture_text


def test_docs_readme_status_tests_and_ci_reference_audit_event() -> None:
    docs = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "chat_audit_event_contract.py" in docs
    assert "chat-audit-event-stub.sh" in docs
    assert "chat-audit-event.gemma3n-e4b-kv260-placeholder.json" in docs
    assert "chat audit-event" in docs
    assert "--include-chat-audit-event" in docs
    assert "chat-audit-event-stub.sh" in readme
    assert "--include-chat-audit-event" in readme
    assert "status-chat-audit-event" in ci
    assert "chat_audit_event_contract_test.py" in ci
    assert "no prompt/response/transcript content" in status_test


if __name__ == "__main__":
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
    print("chat audit-event contract tests ok")
