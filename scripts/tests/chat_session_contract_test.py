#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat/session contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_session_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-session.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-session-stub.sh"
PREVIEW_SCRIPT_PATH = ROOT / "scripts" / "chat-surface-preview.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_session_contract",
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


def test_chat_session_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_session()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_session_json(generated) == module.chat_session_json(generated)
    assert module.chat_session_json(generated).endswith("\n")
    assert json.loads(module.chat_session_json(generated)) == fixture


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
    status = module.create_gemma3n_e4b_kv260_chat_session()
    allowed = set(module.CHAT_SESSION_STATE_VALUES)

    assert tuple(status.keys()) == module.CHAT_SESSION_FIELDS
    assert status["schemaVersion"] == "pccx.chatSession.v0"
    assert status["messageEnvelope"]["schemaVersion"] == "pccx.chatMessage.v0"

    states = list(iter_state_values(status))
    assert states
    for state in states:
        assert state in allowed, state

    for control in status["sessionControls"]:
        assert tuple(control.keys()) == module.CONTROL_FIELDS
    for reason in status["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in status["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_contract_covers_issue_9_surface() -> None:
    status = load_module().create_gemma3n_e4b_kv260_chat_session()
    controls = {control["controlId"]: control for control in status["sessionControls"]}
    reasons = {reason["reasonId"]: reason for reason in status["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in status["handoffRefs"]}

    assert status["surfaceState"] == "blocked"
    assert status["chatState"] == "inactive"
    assert status["modelStatus"] == "not_loaded"
    assert status["inputState"] == "ready_for_inputs"
    assert status["sendState"] == "disabled"
    assert set(controls) == {
        "new_session",
        "model_status",
        "send_message",
        "clear_session",
        "export_summary",
    }
    assert controls["send_message"]["enabled"] is False
    assert controls["send_message"]["state"] == "disabled"
    assert status["messageEnvelope"]["responseState"] == "unavailable"
    assert status["transcriptPolicy"]["promptCapture"] == "disabled"
    assert status["transcriptPolicy"]["responseCapture"] == "disabled"
    assert {
        "runtime_readiness_blocked",
        "model_assets_not_configured",
        "chat_runtime_not_implemented",
        "kv260_session_absent",
    } <= set(reasons)
    assert set(refs) == {"runtime_readiness", "device_session_status"}


def test_safety_flags_preserve_data_only_boundary() -> None:
    status = load_module().create_gemma3n_e4b_kv260_chat_session()
    flags = status["safetyFlags"]

    assert flags["dataOnly"] is True
    assert flags["readOnly"] is True
    assert flags["deterministic"] is True
    for name in [
        "writesArtifacts",
        "promptContentIncluded",
        "responseContentIncluded",
        "transcriptPersistence",
        "touchesHardware",
        "kv260Access",
        "opensSerialPort",
        "networkCalls",
        "networkScan",
        "runtimeExecution",
        "modelLoaded",
        "modelExecution",
        "modelWeightPathsIncluded",
        "privatePathsIncluded",
        "secretsIncluded",
        "tokensIncluded",
        "generatedBlobsIncluded",
        "hardwareDumpsIncluded",
        "providerCalls",
        "cloudCalls",
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
    preview_script_source = read_text(PREVIEW_SCRIPT_PATH)
    status = load_module().create_gemma3n_e4b_kv260_chat_session()
    scan_text = "\n".join([
        read_text(FIXTURE_PATH),
        read_text(DOC_PATH),
        read_text(README_PATH),
        flatten(status),
        module_source,
        script_source,
        preview_script_source,
    ])
    runtime_source = "\n".join([module_source, script_source, preview_script_source])

    assert_no_runtime_implementation_terms(runtime_source)
    assert_no_private_or_generated_data(scan_text)
    assert_no_provider_configs(status)
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
        PREVIEW_SCRIPT_PATH: [
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


test_chat_session_matches_fixture_and_is_deterministic()
test_cli_stub_outputs_deterministic_json()
test_required_fields_and_allowed_states()
test_chat_contract_covers_issue_9_surface()
test_safety_flags_preserve_data_only_boundary()
test_docs_and_sources_avoid_private_data_runtime_calls_or_overclaims()
test_source_headers_for_touched_code_files()

print("chat/session contract tests ok")
