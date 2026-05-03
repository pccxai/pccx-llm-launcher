#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat readiness contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_readiness_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-readiness.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-readiness-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-readiness.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_readiness_contract",
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

    asserted_claim_patterns = [
        r"\bMCP\s+(?:server|client)\s+(?:is\s+)?implemented\b",
        r"\bLSP\s+(?:server|client)\s+(?:is\s+)?implemented\b",
        r"\bAI\s+provider\s+(?:is\s+)?implemented\b",
        r"\bKV260\s+run\s+(?:is\s+)?claimed\b",
    ]
    for pattern in asserted_claim_patterns:
        assert not re.search(pattern, text, re.IGNORECASE), pattern


def assert_no_chat_invocation_flags(source: str) -> None:
    forbidden_patterns = [
        r"--backend\s+pccx-lab",
        r"\bPCCX_LAB_BIN\b",
        r"\bpccx-lab\s+(?:status|diagnostics|validate)\b",
        r"\bsystemverilog-ide\s+--",
        r"\bsystemverilog-ide\s+(?:open|run|status|validate|launch)\b",
        r"\b(?:curl|wget)\b",
        r"\b(?:upload|telemetry|write-back)\s+(?:enabled|true)\b",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, source, re.IGNORECASE), pattern


def test_chat_readiness_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_readiness()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_readiness_json(generated) == module.chat_readiness_json(generated)
    assert module.chat_readiness_json(generated).endswith("\n")
    assert json.loads(module.chat_readiness_json(generated)) == fixture


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
    first = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    second = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )

    assert first.stderr == ""
    assert first.stdout == second.stdout
    assert first.stdout.endswith("\n")
    assert json.loads(first.stdout) == fixture


def test_required_fields_and_allowed_states() -> None:
    module = load_module()
    readiness = module.create_gemma3n_e4b_kv260_chat_readiness()
    allowed = set(module.CHAT_READINESS_STATE_VALUES)

    assert tuple(readiness.keys()) == module.CHAT_READINESS_FIELDS
    assert readiness["schemaVersion"] == "pccx.chatReadiness.v0"

    states = list(iter_state_values(readiness))
    assert states
    for state in states:
        assert state in allowed, state

    for check in readiness["readinessChecks"]:
        assert tuple(check.keys()) == module.READINESS_CHECK_FIELDS
    for error in readiness["errorTaxonomy"]:
        assert tuple(error.keys()) == module.ERROR_TAXONOMY_FIELDS
    for action in readiness["recoveryActions"]:
        assert tuple(action.keys()) == module.RECOVERY_ACTION_FIELDS
    for ref in readiness["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_readiness_covers_issue_9_readiness_boundary() -> None:
    readiness = load_module().create_gemma3n_e4b_kv260_chat_readiness()
    checks = {check["checkId"]: check for check in readiness["readinessChecks"]}
    errors = {error["errorId"]: error for error in readiness["errorTaxonomy"]}
    actions = {action["actionId"]: action for action in readiness["recoveryActions"]}
    refs = {ref["refId"]: ref for ref in readiness["handoffRefs"]}

    assert readiness["overallState"] == "blocked"
    assert readiness["inputReadinessState"] == "available_as_data"
    assert readiness["sendReadinessState"] == "disabled"
    assert readiness["recoveryState"] == "requires_evidence"
    assert readiness["evidenceState"] == "blocked"
    assert set(checks) == {
        "chat_surface_fixture",
        "model_target",
        "model_assets",
        "runtime_readiness",
        "device_session",
        "chat_runtime",
        "session_store",
        "provider_mode",
    }
    assert checks["chat_surface_fixture"]["state"] == "available_as_data"
    assert checks["model_target"]["state"] == "target_selected"
    assert checks["model_assets"]["state"] == "external_not_configured"
    assert checks["runtime_readiness"]["state"] == "blocked"
    assert checks["device_session"]["state"] == "inactive"
    assert checks["chat_runtime"]["state"] == "not_started"
    assert checks["session_store"]["state"] == "not_configured"
    assert checks["provider_mode"]["state"] == "not_used"
    assert set(errors) == {
        "runtime_not_ready",
        "model_assets_missing",
        "device_session_absent",
        "chat_runtime_absent",
        "session_store_absent",
    }
    assert set(actions) == {
        "review_runtime_readiness",
        "configure_model_assets_future",
        "review_device_session_status",
        "wait_for_runtime_boundary",
        "review_session_store_policy",
    }
    for action in actions.values():
        assert action["enabled"] is False
    assert actions["wait_for_runtime_boundary"]["state"] == "requires_evidence"
    assert set(refs) == {
        "chat_session",
        "chat_model_status",
        "chat_session_lifecycle",
        "runtime_readiness",
        "device_session_status",
    }


def test_safety_flags_preserve_data_only_boundary() -> None:
    readiness = load_module().create_gemma3n_e4b_kv260_chat_readiness()
    flags = readiness["safetyFlags"]

    assert flags["dataOnly"] is True
    assert flags["readOnly"] is True
    assert flags["deterministic"] is True
    assert flags["readinessDisplayOnly"] is True
    for name in [
        "writesArtifacts",
        "readsArtifacts",
        "promptContentIncluded",
        "responseContentIncluded",
        "transcriptPersistence",
        "sessionPersistence",
        "modelAssetPathsIncluded",
        "modelWeightPathsIncluded",
        "modelLoadAttempted",
        "modelLoaded",
        "modelExecution",
        "runtimeExecution",
        "responseGenerated",
        "touchesHardware",
        "kv260Access",
        "opensSerialPort",
        "networkCalls",
        "networkScan",
        "sshExecution",
        "providerCalls",
        "cloudCalls",
        "privatePathsIncluded",
        "secretsIncluded",
        "tokensIncluded",
        "generatedBlobsIncluded",
        "hardwareDumpsIncluded",
        "telemetry",
        "automaticUpload",
        "writeBack",
        "executesPccxLab",
        "executesSystemverilogIde",
        "mcpServerImplemented",
        "lspImplemented",
        "stableApiAbiClaim",
    ]:
        assert flags[name] is False, name


def test_docs_and_sources_avoid_private_data_runtime_calls_or_overclaims() -> None:
    module_source = read_text(MODULE_PATH)
    script_source = read_text(SCRIPT_PATH)
    status_test_source = read_text(STATUS_TEST_PATH)
    readiness = load_module().create_gemma3n_e4b_kv260_chat_readiness()
    scan_text = "\n".join([
        read_text(FIXTURE_PATH),
        read_text(DOC_PATH),
        read_text(README_PATH),
        flatten(readiness),
        module_source,
        script_source,
        status_test_source,
    ])
    runtime_source = "\n".join([module_source, script_source])

    assert_no_runtime_implementation_terms(runtime_source)
    assert_no_private_or_generated_data(scan_text)
    assert_no_provider_configs(readiness)
    assert_no_unsupported_claims(scan_text)
    assert_no_chat_invocation_flags(runtime_source)


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


test_chat_readiness_matches_fixture_and_is_deterministic()
test_cli_stub_outputs_deterministic_json()
test_required_fields_and_allowed_states()
test_chat_readiness_covers_issue_9_readiness_boundary()
test_safety_flags_preserve_data_only_boundary()
test_docs_and_sources_avoid_private_data_runtime_calls_or_overclaims()
test_source_headers_for_touched_code_files()

print("chat readiness contract tests ok")
