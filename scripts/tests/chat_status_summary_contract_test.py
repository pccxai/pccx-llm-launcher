#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat status-summary contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_status_summary_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-status-summary.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-status-summary-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-status-summary.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_status_summary_contract",
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
        "IDE controls " + "launcher",
        "AI provider integration " + "is live",
    ]
    lowered = text.lower()
    for claim in literal_claims:
        assert claim.lower() not in lowered, claim


def test_chat_status_summary_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_status_summary()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_status_summary_json(generated) == (
        module.chat_status_summary_json(generated)
    )
    assert module.chat_status_summary_json(generated).endswith("\n")
    assert json.loads(module.chat_status_summary_json(generated)) == fixture


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
    summary = module.create_gemma3n_e4b_kv260_chat_status_summary()
    allowed = set(module.CHAT_STATUS_SUMMARY_STATE_VALUES)

    assert tuple(summary.keys()) == module.CHAT_STATUS_SUMMARY_FIELDS
    assert summary["schemaVersion"] == "pccx.chatStatusSummary.v0"

    states = list(iter_state_values(summary))
    assert states
    for state in states:
        assert state in allowed, state

    for card in summary["statusCards"]:
        assert tuple(card.keys()) == module.STATUS_CARD_FIELDS
    for reason in summary["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for action in summary["nextActions"]:
        assert tuple(action.keys()) == module.NEXT_ACTION_FIELDS
    for ref in summary["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_status_summary_covers_blocked_status_boundary() -> None:
    summary = load_module().create_gemma3n_e4b_kv260_chat_status_summary()
    cards = {card["cardId"]: card for card in summary["statusCards"]}
    reasons = {reason["reasonId"]: reason for reason in summary["blockedReasons"]}
    actions = {action["actionId"]: action for action in summary["nextActions"]}
    refs = {ref["refId"]: ref for ref in summary["handoffRefs"]}

    assert summary["overallState"] == "blocked"
    assert summary["surfaceState"] == "available_as_data"
    assert summary["sessionState"] == "inactive"
    assert summary["modelState"] == "blocked"
    assert summary["runtimeState"] == "blocked"
    assert summary["sendState"] == "disabled"
    assert summary["contentState"] == "empty_not_captured"
    assert summary["privacyState"] == "summary_only"
    assert set(cards) == {
        "surface_layout",
        "session_state",
        "model_status",
        "readiness",
        "composer",
        "send_result",
        "message_list",
        "response_stream",
        "privacy_controls",
    }
    assert cards["surface_layout"]["state"] == "available_as_data"
    assert cards["session_state"]["state"] == "inactive"
    assert cards["model_status"]["state"] == "blocked"
    assert cards["readiness"]["state"] == "blocked"
    assert cards["send_result"]["state"] == "disabled"
    assert cards["message_list"]["state"] == "empty_not_captured"
    assert set(reasons) == {
        "runtime_evidence_absent",
        "model_load_absent",
        "device_session_absent",
        "session_store_absent",
        "content_boundary_absent",
    }
    assert set(actions) == {
        "review_readiness_data",
        "keep_send_disabled",
        "wait_for_runtime_boundary",
    }
    for action in actions.values():
        assert action["enabled"] is False
    assert set(refs) == {
        "chat_surface_layout",
        "chat_readiness",
        "chat_model_status",
        "chat_session",
        "chat_redaction_policy",
    }


def test_safety_flags_preserve_summary_only_boundary() -> None:
    summary = load_module().create_gemma3n_e4b_kv260_chat_status_summary()
    flags = summary["safetyFlags"]

    assert flags["dataOnly"] is True
    assert flags["readOnly"] is True
    assert flags["deterministic"] is True
    assert flags["statusSummaryOnly"] is True
    assert flags["aggregatesCheckedFixturesOnly"] is True
    for name in [
        "promptCapture",
        "promptRead",
        "promptContentIncluded",
        "responseContentIncluded",
        "transcriptContentIncluded",
        "messageBodiesIncluded",
        "sessionStoreRead",
        "sessionPersistence",
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
        "clipboardRead",
        "clipboardWrite",
        "attachmentReads",
        "fileContentRead",
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
    summary = load_module().create_gemma3n_e4b_kv260_chat_status_summary()
    scan_text = "\n".join([
        read_text(FIXTURE_PATH),
        read_text(DOC_PATH),
        read_text(README_PATH),
        flatten(summary),
        module_source,
        script_source,
        status_test_source,
    ])
    runtime_source = "\n".join([module_source, script_source])

    assert_no_runtime_implementation_terms(runtime_source)
    assert_no_private_or_generated_data(scan_text)
    assert_no_provider_configs(summary)
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


test_chat_status_summary_matches_fixture_and_is_deterministic()
test_cli_stub_outputs_deterministic_json()
test_required_fields_and_allowed_states()
test_chat_status_summary_covers_blocked_status_boundary()
test_safety_flags_preserve_summary_only_boundary()
test_docs_and_sources_avoid_private_data_runtime_calls_or_overclaims()
test_source_headers_for_touched_code_files()

print("chat status summary contract tests ok")
