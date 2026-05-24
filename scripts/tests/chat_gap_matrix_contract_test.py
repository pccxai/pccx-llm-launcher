#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat gap-matrix contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_gap_matrix_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-gap-matrix.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-gap-matrix-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-gap-matrix.sh"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_gap_matrix_contract",
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
        "ge" + "mini",
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


def test_chat_gap_matrix_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_gap_matrix()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_gap_matrix_json(generated) == (
        module.chat_gap_matrix_json(generated)
    )
    assert module.chat_gap_matrix_json(generated).endswith("\n")
    assert json.loads(module.chat_gap_matrix_json(generated)) == fixture


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
    matrix = module.create_gemma3n_e4b_kv260_chat_gap_matrix()
    allowed = set(module.CHAT_GAP_MATRIX_STATE_VALUES)

    assert tuple(matrix.keys()) == module.CHAT_GAP_MATRIX_FIELDS
    assert matrix["schemaVersion"] == "pccx.chatGapMatrix.v0"

    states = list(iter_state_values(matrix))
    assert states
    for state in states:
        assert state in allowed, state

    for row in matrix["gapRows"]:
        assert tuple(row.keys()) == module.GAP_ROW_FIELDS
    for ref in matrix["dependencyRefs"]:
        assert tuple(ref.keys()) == module.DEPENDENCY_REF_FIELDS
    for criteria in matrix["exitCriteria"]:
        assert tuple(criteria.keys()) == module.EXIT_CRITERIA_FIELDS
    for reason in matrix["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS


def test_chat_gap_matrix_tracks_unresolved_blockers_without_closing_them() -> None:
    matrix = load_module().create_gemma3n_e4b_kv260_chat_gap_matrix()
    rows = {row["gapId"]: row for row in matrix["gapRows"]}
    refs = {ref["refId"]: ref for ref in matrix["dependencyRefs"]}
    criteria = {item["criteriaId"]: item for item in matrix["exitCriteria"]}
    reasons = {reason["reasonId"]: reason for reason in matrix["blockedReasons"]}

    assert matrix["matrixState"] == "available_as_data"
    assert matrix["standaloneChatState"] == "blocked"
    assert matrix["reviewState"] == "not_approved"
    assert matrix["evidenceState"] == "requires_evidence"
    assert matrix["readinessState"] == "blocked"
    assert set(rows) == {
        "runtime_device_evidence",
        "model_asset_boundary",
        "prompt_input_boundary",
        "response_generation_boundary",
        "session_store_boundary",
        "transcript_export_boundary",
        "privacy_content_policy",
        "attachment_clipboard_boundary",
        "audit_persistence_boundary",
        "ui_enablement_boundary",
    }
    assert rows["runtime_device_evidence"]["state"] == "requires_evidence"
    assert rows["model_asset_boundary"]["state"] == "not_loaded"
    assert rows["prompt_input_boundary"]["sideEffectPolicy"] == (
        "no_prompt_capture_or_input_acceptance"
    )
    assert rows["attachment_clipboard_boundary"]["sideEffectPolicy"] == (
        "no_file_clipboard_or_directory_access"
    )
    assert set(refs) == {
        "chat_review_packet",
        "chat_status_summary",
        "chat_readiness",
        "chat_model_load_request",
        "chat_session_store_policy",
        "chat_redaction_policy",
    }
    assert refs["chat_review_packet"]["state"] == "not_approved"
    assert refs["chat_status_summary"]["state"] == "summary_only"
    assert set(criteria) == {
        "runtime_and_device_evidence_accepted",
        "model_and_session_boundaries_reviewed",
        "content_privacy_boundaries_reviewed",
    }
    for item in criteria.values():
        assert item["accepted"] is False
    assert set(reasons) == {
        "standalone_chat_not_enabled",
        "review_packet_not_approved",
        "runtime_evidence_absent",
        "content_paths_disabled",
    }


def test_safety_flags_preserve_gap_matrix_only_boundary() -> None:
    matrix = load_module().create_gemma3n_e4b_kv260_chat_gap_matrix()
    flags = matrix["safetyFlags"]

    assert flags["dataOnly"] is True
    assert flags["readOnly"] is True
    assert flags["deterministic"] is True
    assert flags["gapMatrixOnly"] is True
    assert flags["referencesCheckedFixturesOnly"] is True
    assert flags["reviewPacketReferencedOnly"] is True
    assert flags["statusSummaryReferencedOnly"] is True
    for name in [
        "gapClosed",
        "approvalGranted",
        "promptCapture",
        "promptRead",
        "promptContentIncluded",
        "promptEchoed",
        "inputAccepted",
        "responseContentIncluded",
        "responseGenerated",
        "responseChunksEmitted",
        "tokenCountMeasured",
        "transcriptContentIncluded",
        "messageBodiesIncluded",
        "sessionStoreRead",
        "sessionStoreWrite",
        "sessionPersistence",
        "summaryGenerated",
        "transcriptExported",
        "clipboardRead",
        "clipboardWrite",
        "attachmentReads",
        "fileMetadataRead",
        "fileContentRead",
        "directoryScan",
        "redactionRulesLoaded",
        "contentScan",
        "redactionApplied",
        "auditLogWritten",
        "configRead",
        "environmentRead",
        "providerConfigRead",
        "modelAssetRead",
        "modelPathIncluded",
        "modelLoadAttempted",
        "modelExecution",
        "runtimeExecution",
        "sendEnabled",
        "readsArtifacts",
        "writesArtifacts",
        "kv260Access",
        "hardwareAccess",
        "networkCalls",
        "providerCalls",
        "cloudCalls",
        "executesPccxLab",
        "executesSystemverilogIde",
        "commandDispatch",
        "actionExecution",
        "focusChanged",
        "telemetry",
        "writeBack",
        "releaseOrTagAction",
        "settingsChange",
        "compatibilityClaim",
    ]:
        assert flags[name] is False, name


def test_docs_and_sources_avoid_private_data_runtime_calls_or_overclaims() -> None:
    module_source = read_text(MODULE_PATH)
    script_source = read_text(SCRIPT_PATH)
    status_test_source = read_text(STATUS_TEST_PATH)
    matrix = load_module().create_gemma3n_e4b_kv260_chat_gap_matrix()
    scan_text = "\n".join([
        read_text(FIXTURE_PATH),
        read_text(README_PATH),
        flatten(matrix),
        module_source,
        script_source,
        status_test_source,
    ])
    runtime_source = "\n".join([module_source, script_source])

    assert_no_runtime_implementation_terms(runtime_source)
    assert_no_private_or_generated_data(scan_text)
    assert_no_provider_configs(matrix)
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


test_chat_gap_matrix_matches_fixture_and_is_deterministic()
test_cli_stub_outputs_deterministic_json()
test_required_fields_and_allowed_states()
test_chat_gap_matrix_tracks_unresolved_blockers_without_closing_them()
test_safety_flags_preserve_gap_matrix_only_boundary()
test_docs_and_sources_avoid_private_data_runtime_calls_or_overclaims()
test_source_headers_for_touched_code_files()

print("chat gap matrix contract tests ok")
