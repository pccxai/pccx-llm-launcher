#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat evidence-manifest contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_evidence_manifest_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-evidence-manifest.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-evidence-manifest-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-evidence-manifest.sh"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_evidence_manifest_contract",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def flatten(value) -> str:
    return json.dumps(value, sort_keys=True)


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
        "AI provider integration " + "is live",
    ]
    lowered = text.lower()
    for claim in literal_claims:
        assert claim.lower() not in lowered, claim


def test_chat_evidence_manifest_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_evidence_manifest()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_evidence_manifest_json(generated) == (
        module.chat_evidence_manifest_json(generated)
    )
    assert module.chat_evidence_manifest_json(generated).endswith("\n")
    assert json.loads(module.chat_evidence_manifest_json(generated)) == fixture


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
    manifest = module.create_gemma3n_e4b_kv260_chat_evidence_manifest()
    allowed = set(module.CHAT_EVIDENCE_MANIFEST_STATE_VALUES)

    assert tuple(manifest.keys()) == module.CHAT_EVIDENCE_MANIFEST_FIELDS
    assert manifest["schemaVersion"] == "pccx.chatEvidenceManifest.v0"

    states = list(iter_state_values(manifest))
    assert states
    for state in states:
        assert state in allowed, state

    for ref in manifest["evidenceRefs"]:
        assert tuple(ref.keys()) == module.EVIDENCE_REF_FIELDS
    for link in manifest["reviewLinks"]:
        assert tuple(link.keys()) == module.REVIEW_LINK_FIELDS
    for reason in manifest["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for action in manifest["nextActions"]:
        assert tuple(action.keys()) == module.NEXT_ACTION_FIELDS


def test_manifest_tracks_references_without_accepting_evidence() -> None:
    manifest = load_module().create_gemma3n_e4b_kv260_chat_evidence_manifest()
    refs = {ref["refId"]: ref for ref in manifest["evidenceRefs"]}
    links = {link["linkId"]: link for link in manifest["reviewLinks"]}
    reasons = {reason["reasonId"]: reason for reason in manifest["blockedReasons"]}
    actions = {action["actionId"]: action for action in manifest["nextActions"]}

    assert manifest["manifestState"] == "available_as_data"
    assert manifest["reviewState"] == "not_approved"
    assert manifest["gapState"] == "blocked"
    assert manifest["evidenceState"] == "requires_evidence"
    assert manifest["artifactState"] == "unavailable"
    assert set(refs) == {
        "runtime_readiness",
        "device_session_status",
        "chat_review_packet",
        "chat_gap_matrix",
        "chat_status_summary",
        "chat_redaction_policy",
        "chat_accessibility",
    }
    assert refs["runtime_readiness"]["state"] == "requires_evidence"
    assert refs["device_session_status"]["contentPolicy"] == (
        "fixture_reference_only_no_hardware_dump_or_board_log"
    )
    assert refs["chat_review_packet"]["state"] == "not_approved"
    assert refs["chat_gap_matrix"]["state"] == "blocked"
    assert refs["chat_accessibility"]["schemaVersion"] == "pccx.chatAccessibility.v0"
    assert refs["chat_accessibility"]["state"] == "requires_review"
    assert refs["chat_accessibility"]["contentPolicy"] == (
        "fixture_reference_only_no_ui_focus_keyboard_or_live_region_execution"
    )
    assert set(links) == {
        "review_packet_gate",
        "gap_matrix_gate",
        "runtime_evidence_gate",
        "accessibility_review_gate",
    }
    assert set(reasons) == {
        "runtime_evidence_absent",
        "review_not_approved",
        "artifact_evidence_not_read",
        "standalone_chat_still_blocked",
        "accessibility_review_pending",
    }
    assert set(actions) == {
        "collect_runtime_evidence",
        "review_manifest_refs",
        "keep_chat_blocked",
        "review_accessibility_metadata",
    }
    for action in actions.values():
        assert action["enabled"] is False


def test_safety_flags_preserve_manifest_only_boundary() -> None:
    manifest = load_module().create_gemma3n_e4b_kv260_chat_evidence_manifest()
    flags = manifest["safetyFlags"]

    assert flags["dataOnly"] is True
    assert flags["readOnly"] is True
    assert flags["deterministic"] is True
    assert flags["evidenceManifestOnly"] is True
    assert flags["referencesCheckedFixturesOnly"] is True
    assert flags["reviewPacketReferencedOnly"] is True
    assert flags["gapMatrixReferencedOnly"] is True
    assert flags["statusSummaryReferencedOnly"] is True
    for name in [
        "evidenceAccepted",
        "gapClosed",
        "approvalGranted",
        "artifactRead",
        "artifactWrite",
        "rawLogRead",
        "hardwareDumpRead",
        "promptCapture",
        "promptRead",
        "promptContentIncluded",
        "responseContentIncluded",
        "transcriptContentIncluded",
        "messageBodiesIncluded",
        "sessionStoreRead",
        "configRead",
        "environmentRead",
        "providerConfigRead",
        "providerCalls",
        "cloudCalls",
        "networkCalls",
        "modelAssetRead",
        "modelPathIncluded",
        "modelLoadAttempted",
        "modelExecution",
        "runtimeExecution",
        "responseGenerated",
        "sendEnabled",
        "clipboardRead",
        "attachmentReads",
        "fileMetadataRead",
        "fileContentRead",
        "directoryScan",
        "redactionRulesLoaded",
        "contentScan",
        "redactionApplied",
        "auditLogWritten",
        "kv260Access",
        "hardwareAccess",
        "executesPccxLab",
        "executesSystemverilogIde",
        "releaseOrTagAction",
        "settingsChange",
        "compatibilityClaim",
    ]:
        assert flags[name] is False, name


def test_docs_and_sources_avoid_private_data_runtime_calls_or_overclaims() -> None:
    module_source = read_text(MODULE_PATH)
    script_source = read_text(SCRIPT_PATH)
    status_test_source = read_text(STATUS_TEST_PATH)
    manifest = load_module().create_gemma3n_e4b_kv260_chat_evidence_manifest()
    scan_text = "\n".join([
        read_text(FIXTURE_PATH),
        read_text(README_PATH),
        flatten(manifest),
        module_source,
        script_source,
        status_test_source,
    ])
    runtime_source = "\n".join([module_source, script_source])

    assert_no_runtime_implementation_terms(runtime_source)
    assert_no_private_or_generated_data(scan_text)
    assert_no_provider_configs(manifest)
    assert_no_unsupported_claims(scan_text)


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


test_chat_evidence_manifest_matches_fixture_and_is_deterministic()
test_cli_stub_outputs_deterministic_json()
test_required_fields_and_allowed_states()
test_manifest_tracks_references_without_accepting_evidence()
test_safety_flags_preserve_manifest_only_boundary()
test_docs_and_sources_avoid_private_data_runtime_calls_or_overclaims()
test_source_headers_for_touched_code_files()

print("chat evidence manifest contract tests ok")
