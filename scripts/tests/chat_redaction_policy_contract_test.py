#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat redaction-policy contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_redaction_policy_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-redaction-policy.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-redaction-policy-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-redaction-policy.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_redaction_policy_contract",
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


def test_chat_redaction_policy_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_redaction_policy()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_redaction_policy_json(generated) == (
        module.chat_redaction_policy_json(generated)
    )
    assert module.chat_redaction_policy_json(generated).endswith("\n")
    assert json.loads(module.chat_redaction_policy_json(generated)) == fixture


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
    redaction_policy = module.create_gemma3n_e4b_kv260_chat_redaction_policy()
    allowed = set(module.CHAT_REDACTION_POLICY_STATE_VALUES)

    assert tuple(redaction_policy.keys()) == module.CHAT_REDACTION_POLICY_FIELDS
    assert redaction_policy["schemaVersion"] == "pccx.chatRedactionPolicy.v0"
    assert (
        tuple(redaction_policy["redactionPolicy"].keys())
        == module.REDACTION_POLICY_FIELDS
    )

    states = list(iter_state_values(redaction_policy))
    assert states
    for state in states:
        assert state in allowed, state

    for surface in redaction_policy["redactionSurfaces"]:
        assert tuple(surface.keys()) == module.REDACTION_SURFACE_FIELDS
    for control in redaction_policy["redactionControls"]:
        assert tuple(control.keys()) == module.REDACTION_CONTROL_FIELDS
    for reason in redaction_policy["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in redaction_policy["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_redaction_policy_keeps_scanning_and_redaction_disabled() -> None:
    redaction_policy = load_module().create_gemma3n_e4b_kv260_chat_redaction_policy()
    policy = redaction_policy["redactionPolicy"]
    flags = redaction_policy["safetyFlags"]
    surfaces = {
        surface["surfaceId"]: surface
        for surface in redaction_policy["redactionSurfaces"]
    }
    controls = {
        control["controlId"]: control
        for control in redaction_policy["redactionControls"]
    }
    reasons = {
        reason["reasonId"]: reason for reason in redaction_policy["blockedReasons"]
    }
    refs = {ref["refId"]: ref for ref in redaction_policy["handoffRefs"]}

    assert redaction_policy["redactionPolicyState"] == "blocked"
    assert redaction_policy["contentScanState"] == "disabled"
    assert redaction_policy["promptRedactionState"] == "disabled"
    assert redaction_policy["responseRedactionState"] == "disabled"
    assert redaction_policy["transcriptRedactionState"] == "not_configured"
    assert redaction_policy["messageRedactionState"] == "empty_not_captured"
    assert redaction_policy["attachmentRedactionState"] == "blocked"
    assert redaction_policy["clipboardRedactionState"] == "disabled"
    assert redaction_policy["auditRedactionState"] == "blocked"
    assert redaction_policy["piiDetectionState"] == "disabled"
    assert redaction_policy["secretDetectionState"] == "disabled"
    assert redaction_policy["persistenceState"] == "disabled"
    assert redaction_policy["privacyState"] == "summary_only"
    assert policy["sideEffectPolicy"] == "local_render_only"
    assert policy["scannerEnabled"] is False
    assert policy["promptRedactionEnabled"] is False
    assert policy["responseRedactionEnabled"] is False
    assert policy["transcriptRedactionEnabled"] is False
    assert policy["messageRedactionEnabled"] is False
    assert policy["attachmentRedactionEnabled"] is False
    assert policy["clipboardRedactionEnabled"] is False
    assert policy["auditRedactionEnabled"] is False
    assert policy["piiDetectionEnabled"] is False
    assert policy["secretDetectionEnabled"] is False
    assert policy["persistenceEnabled"] is False
    assert set(surfaces) == {
        "composer_prompt",
        "assistant_response",
        "message_list",
        "transcript_export",
        "attachment_payload",
        "clipboard_payload",
        "audit_event",
    }
    assert all(surface["enabled"] is False for surface in surfaces.values())
    assert set(controls) == {
        "review_redaction_rules",
        "scan_prompt_content",
        "scan_response_content",
        "scan_transcript_content",
        "detect_sensitive_content",
        "redact_attachment_payload",
        "redact_clipboard_payload",
        "persist_redaction_result",
    }
    assert all(control["enabled"] is False for control in controls.values())
    assert controls["review_redaction_rules"]["sideEffectPolicy"] == "no_rule_load"
    assert controls["scan_prompt_content"]["sideEffectPolicy"] == "no_prompt_scan"
    assert controls["scan_response_content"]["sideEffectPolicy"] == "no_response_scan"
    assert controls["scan_transcript_content"]["sideEffectPolicy"] == (
        "no_transcript_scan"
    )
    assert controls["detect_sensitive_content"]["sideEffectPolicy"] == (
        "no_detector_execution"
    )
    assert controls["redact_attachment_payload"]["sideEffectPolicy"] == (
        "no_attachment_read_or_redaction"
    )
    assert controls["redact_clipboard_payload"]["sideEffectPolicy"] == (
        "no_clipboard_read_or_redaction"
    )
    assert controls["persist_redaction_result"]["sideEffectPolicy"] == (
        "no_redaction_result_persistence"
    )
    assert set(reasons) == {
        "redaction_rules_absent",
        "content_boundary_absent",
        "transcript_policy_not_reviewed",
        "scanner_not_reviewed",
        "persistence_not_configured",
    }
    assert set(refs) == {
        "chat_composer",
        "chat_message_list",
        "chat_transcript_policy",
        "chat_attachment_policy",
        "chat_clipboard_policy",
        "chat_audit_event",
        "chat_local_only_policy",
    }
    assert flags["readOnly"] is True
    assert flags["dataOnly"] is True
    assert flags["redactionPolicyDisplayOnly"] is True
    assert flags["redactionMetadataOnly"] is True
    assert flags["redactionRulesLoaded"] is False
    assert flags["redactionRulesPersisted"] is False
    assert flags["contentScan"] is False
    assert flags["piiDetection"] is False
    assert flags["secretDetection"] is False
    assert flags["identifierDetection"] is False
    assert flags["promptRedaction"] is False
    assert flags["responseRedaction"] is False
    assert flags["transcriptRedaction"] is False
    assert flags["messageRedaction"] is False
    assert flags["attachmentRedaction"] is False
    assert flags["clipboardRedaction"] is False
    assert flags["auditRedaction"] is False
    assert flags["redactionApplied"] is False
    assert flags["redactionResultPersisted"] is False
    assert flags["redactionReportGenerated"] is False
    assert flags["promptCapture"] is False
    assert flags["promptRead"] is False
    assert flags["promptContentIncluded"] is False
    assert flags["responseContentIncluded"] is False
    assert flags["transcriptContentIncluded"] is False
    assert flags["messageBodiesIncluded"] is False
    assert flags["readsTranscript"] is False
    assert flags["sessionStoreRead"] is False
    assert flags["sessionStoreWrite"] is False
    assert flags["clipboardRead"] is False
    assert flags["clipboardWrite"] is False
    assert flags["attachmentReads"] is False
    assert flags["fileMetadataRead"] is False
    assert flags["fileContentRead"] is False
    assert flags["directoryScan"] is False
    assert flags["fileImport"] is False
    assert flags["fileUpload"] is False
    assert flags["writesArtifacts"] is False
    assert flags["readsArtifacts"] is False
    assert flags["modelAssetRead"] is False
    assert flags["modelLoadAttempted"] is False
    assert flags["modelExecution"] is False
    assert flags["runtimeExecution"] is False
    assert flags["kv260Access"] is False
    assert flags["hardwareAccess"] is False
    assert flags["networkCalls"] is False
    assert flags["providerCalls"] is False
    assert flags["cloudCalls"] is False
    assert flags["executesPccxLab"] is False
    assert flags["executesSystemverilogIde"] is False


def test_chat_redaction_policy_docs_and_ci_are_wired() -> None:
    doc = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "contracts/chat_redaction_policy_contract.py" in doc
    assert (
        "contracts/fixtures/chat-redaction-policy.gemma3n-e4b-kv260-placeholder.json"
        in doc
    )
    assert "scripts/chat-redaction-policy-stub.sh" in doc
    assert "scripts/tests/chat_redaction_policy_contract_test.py" in doc
    assert "scripts/tests/status-chat-redaction-policy.sh" in doc
    assert "chat-redaction-policy-stub.sh" in readme
    assert "--include-chat-redaction-policy" in readme
    assert "chat_redaction_policy_contract_test.py" in ci
    assert "status-chat-redaction-policy.sh" in ci
    assert "--include-chat-redaction-policy" in status_test


def test_chat_redaction_policy_has_no_runtime_or_private_surface() -> None:
    module = load_module()
    redaction_policy = module.create_gemma3n_e4b_kv260_chat_redaction_policy()
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

    assert_no_provider_configs(redaction_policy)
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
    print("chat redaction-policy contract tests ok")
