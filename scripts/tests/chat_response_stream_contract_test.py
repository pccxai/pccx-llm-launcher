#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat response stream contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_response_stream_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-response-stream.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-response-stream-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-response-stream.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_response_stream_contract",
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


def test_chat_response_stream_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_response_stream()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_response_stream_json(generated) == (
        module.chat_response_stream_json(generated)
    )
    assert module.chat_response_stream_json(generated).endswith("\n")
    assert json.loads(module.chat_response_stream_json(generated)) == fixture


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
    stream = module.create_gemma3n_e4b_kv260_chat_response_stream()
    allowed = set(module.CHAT_RESPONSE_STREAM_STATE_VALUES)

    assert tuple(stream.keys()) == module.CHAT_RESPONSE_STREAM_FIELDS
    assert stream["schemaVersion"] == "pccx.chatResponseStream.v0"
    assert tuple(stream["streamEnvelope"].keys()) == module.STREAM_ENVELOPE_FIELDS

    states = list(iter_state_values(stream))
    assert states
    for state in states:
        assert state in allowed, state

    for phase in stream["streamPhases"]:
        assert tuple(phase.keys()) == module.STREAM_PHASE_FIELDS
    for slot in stream["displaySlots"]:
        assert tuple(slot.keys()) == module.DISPLAY_SLOT_FIELDS
    for reason in stream["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in stream["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_response_stream_keeps_streaming_blocked() -> None:
    stream = load_module().create_gemma3n_e4b_kv260_chat_response_stream()
    envelope = stream["streamEnvelope"]
    phases = {phase["phaseId"]: phase for phase in stream["streamPhases"]}
    slots = {slot["slotId"]: slot for slot in stream["displaySlots"]}
    reasons = {reason["reasonId"]: reason for reason in stream["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in stream["handoffRefs"]}

    assert stream["streamState"] == "blocked"
    assert stream["responseState"] == "not_generated"
    assert stream["streamTransportState"] == "not_started"
    assert stream["tokenState"] == "unavailable"
    assert stream["progressState"] == "disabled"
    assert stream["cancelState"] == "disabled"
    assert envelope["streamStarted"] is False
    assert envelope["transportOpened"] is False
    assert envelope["chunksEmitted"] is False
    assert envelope["tokenContentIncluded"] is False
    assert envelope["responseContentIncluded"] is False
    assert envelope["tokenCount"] is None
    assert envelope["stopSignalSent"] is False
    assert phases["wait_for_send_result"]["state"] == "blocked"
    assert phases["open_stream_transport"]["state"] == "not_started"
    assert phases["emit_response_chunks"]["state"] == "not_generated"
    assert phases["complete_stream"]["state"] == "unavailable"
    assert slots["assistant_response_placeholder"]["state"] == "available_as_data"
    assert slots["token_counter"]["visible"] is False
    assert slots["stop_generation_control"]["enabled"] is False
    assert reasons["send_result_blocked"]["requiredBefore"] == "response_stream_started"
    assert reasons["runtime_not_started"]["requiredBefore"] == "stream_transport_opened"
    assert refs["chat_send_result"]["schemaVersion"] == "pccx.chatSendResult.v0"
    assert refs["chat_transcript_policy"]["state"] == "disabled"


def test_safety_flags_prevent_runtime_provider_content_and_store_paths() -> None:
    flags = load_module().create_gemma3n_e4b_kv260_chat_response_stream()[
        "safetyFlags"
    ]

    assert flags["readOnly"] is True
    assert flags["dataOnly"] is True
    assert flags["deterministic"] is True
    assert flags["responseStreamDisplayOnly"] is True
    assert flags["promptCapture"] is False
    assert flags["promptContentIncluded"] is False
    assert flags["inputAccepted"] is False
    assert flags["sendAttempted"] is False
    assert flags["responseContentIncluded"] is False
    assert flags["responseGenerated"] is False
    assert flags["responseChunkContentIncluded"] is False
    assert flags["responseChunksEmitted"] is False
    assert flags["tokenContentIncluded"] is False
    assert flags["tokenCountMeasured"] is False
    assert flags["streamStarted"] is False
    assert flags["streamTransportOpened"] is False
    assert flags["streamCancellationAttempted"] is False
    assert flags["sessionStoreRead"] is False
    assert flags["sessionStoreWrite"] is False
    assert flags["modelAssetRead"] is False
    assert flags["modelLoadAttempted"] is False
    assert flags["modelExecution"] is False
    assert flags["runtimeExecution"] is False
    assert flags["kv260Access"] is False
    assert flags["hardwareAccess"] is False
    assert flags["providerCalls"] is False
    assert flags["cloudCalls"] is False
    assert flags["networkCalls"] is False
    assert flags["executesPccxLab"] is False
    assert flags["executesSystemverilogIde"] is False


def test_contract_avoids_private_data_runtime_terms_and_provider_config() -> None:
    module_text = read_text(MODULE_PATH)
    fixture_text = read_text(FIXTURE_PATH)
    fixture = json.loads(fixture_text)

    assert_no_private_or_generated_data(module_text)
    assert_no_private_or_generated_data(fixture_text)
    assert_no_runtime_implementation_terms(module_text)
    assert_no_provider_configs(fixture)
    assert_no_unsupported_claims(module_text)
    assert_no_unsupported_claims(fixture_text)


def test_docs_scripts_and_ci_reference_chat_response_stream() -> None:
    assert "chat_response_stream_contract.py" in read_text(TEST_PATH)
    assert "chat-response-stream-stub.sh" in read_text(TEST_PATH)
    assert "status-chat-response-stream.sh" in read_text(TEST_PATH)
    assert "chat-response-stream-stub.sh" in read_text(README_PATH)
    assert "chat_response_stream_contract.py" in read_text(README_PATH)
    assert "chat response stream" in read_text(DOC_PATH)
    assert "chat_response_stream_contract_test.py" in read_text(CI_PATH)
    assert "status-chat-response-stream.sh" in read_text(CI_PATH)
    assert_no_chat_invocation_flags(read_text(SCRIPT_PATH))


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
    print("chat response stream contract tests ok")
