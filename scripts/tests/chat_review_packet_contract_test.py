#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat review-packet contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_review_packet_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-review-packet.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-review-packet-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-review-packet.sh"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_review_packet_contract",
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


def test_chat_review_packet_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_review_packet()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_review_packet_json(generated) == (
        module.chat_review_packet_json(generated)
    )
    assert module.chat_review_packet_json(generated).endswith("\n")
    assert json.loads(module.chat_review_packet_json(generated)) == fixture


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
    packet = module.create_gemma3n_e4b_kv260_chat_review_packet()
    allowed = set(module.CHAT_REVIEW_PACKET_STATE_VALUES)

    assert tuple(packet.keys()) == module.CHAT_REVIEW_PACKET_FIELDS
    assert packet["schemaVersion"] == "pccx.chatReviewPacket.v0"

    states = list(iter_state_values(packet))
    assert states
    for state in states:
        assert state in allowed, state

    for section in packet["reviewSections"]:
        assert tuple(section.keys()) == module.REVIEW_SECTION_FIELDS
    for review in packet["requiredReviews"]:
        assert tuple(review.keys()) == module.REQUIRED_REVIEW_FIELDS
    for reason in packet["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in packet["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_review_packet_covers_review_gates_without_approval() -> None:
    packet = load_module().create_gemma3n_e4b_kv260_chat_review_packet()
    sections = {section["sectionId"]: section for section in packet["reviewSections"]}
    reviews = {review["reviewId"]: review for review in packet["requiredReviews"]}
    reasons = {reason["reasonId"]: reason for reason in packet["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in packet["handoffRefs"]}

    assert packet["reviewState"] == "blocked"
    assert packet["approvalState"] == "not_approved"
    assert packet["executionState"] == "not_started"
    assert packet["contentState"] == "empty_not_captured"
    assert packet["privacyState"] == "requires_review"
    assert packet["evidenceState"] == "requires_evidence"
    assert set(sections) == {
        "surface_and_controls",
        "session_management",
        "model_runtime_and_device",
        "content_flow",
        "privacy_and_local_only_policy",
        "aggregate_status",
    }
    assert sections["aggregate_status"]["contentPolicy"] == (
        "status_summary_reference_only_no_status_card_duplication"
    )
    assert set(reviews) == {
        "runtime_evidence_review",
        "model_asset_review",
        "session_store_review",
        "content_privacy_review",
        "send_enablement_review",
    }
    for review in reviews.values():
        assert review["accepted"] is False
    assert set(reasons) == {
        "review_packet_not_approved",
        "runtime_and_device_evidence_absent",
        "model_asset_boundary_absent",
        "session_store_boundary_absent",
        "content_privacy_boundary_absent",
    }
    assert set(refs) == {
        "chat_status_summary",
        "chat_local_only_policy",
        "chat_redaction_policy",
        "chat_session_store_policy",
        "chat_model_load_request",
        "chat_readiness",
    }


def test_safety_flags_preserve_review_only_boundary() -> None:
    packet = load_module().create_gemma3n_e4b_kv260_chat_review_packet()
    flags = packet["safetyFlags"]

    assert flags["dataOnly"] is True
    assert flags["readOnly"] is True
    assert flags["deterministic"] is True
    assert flags["reviewPacketOnly"] is True
    assert flags["aggregatesCheckedFixturesOnly"] is True
    assert flags["statusSummaryReferencedOnly"] is True
    for name in [
        "approvalGranted",
        "promptCapture",
        "promptRead",
        "promptContentIncluded",
        "responseContentIncluded",
        "transcriptContentIncluded",
        "messageBodiesIncluded",
        "sessionStoreRead",
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
        "responseGenerated",
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
    packet = load_module().create_gemma3n_e4b_kv260_chat_review_packet()
    scan_text = "\n".join([
        read_text(FIXTURE_PATH),
        read_text(README_PATH),
        flatten(packet),
        module_source,
        script_source,
        status_test_source,
    ])
    runtime_source = "\n".join([module_source, script_source])

    assert_no_runtime_implementation_terms(runtime_source)
    assert_no_private_or_generated_data(scan_text)
    assert_no_provider_configs(packet)
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


test_chat_review_packet_matches_fixture_and_is_deterministic()
test_cli_stub_outputs_deterministic_json()
test_required_fields_and_allowed_states()
test_chat_review_packet_covers_review_gates_without_approval()
test_safety_flags_preserve_review_only_boundary()
test_docs_and_sources_avoid_private_data_runtime_calls_or_overclaims()
test_source_headers_for_touched_code_files()

print("chat review packet contract tests ok")
