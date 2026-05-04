#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat model-load request contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_model_load_request_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-model-load-request.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-model-load-request-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-model-load-request.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_model_load_request_contract",
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
        "import " + "requests",
        "from " + "requests",
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


def test_chat_model_load_request_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_model_load_request()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_model_load_request_json(generated) == (
        module.chat_model_load_request_json(generated)
    )
    assert module.chat_model_load_request_json(generated).endswith("\n")
    assert json.loads(module.chat_model_load_request_json(generated)) == fixture


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
    request = module.create_gemma3n_e4b_kv260_chat_model_load_request()
    allowed = set(module.CHAT_MODEL_LOAD_REQUEST_STATE_VALUES)

    assert tuple(request.keys()) == module.CHAT_MODEL_LOAD_REQUEST_FIELDS
    assert request["schemaVersion"] == "pccx.chatModelLoadRequest.v0"
    assert tuple(request["loadRequestPolicy"].keys()) == (
        module.LOAD_REQUEST_POLICY_FIELDS
    )

    states = list(iter_state_values(request))
    assert states
    for state in states:
        assert state in allowed, state

    for load_input in request["loadInputs"]:
        assert tuple(load_input.keys()) == module.LOAD_INPUT_FIELDS
    for control in request["loadControls"]:
        assert tuple(control.keys()) == module.LOAD_CONTROL_FIELDS
    for reason in request["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in request["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_model_load_request_keeps_load_disabled() -> None:
    request = load_module().create_gemma3n_e4b_kv260_chat_model_load_request()
    policy = request["loadRequestPolicy"]
    load_inputs = {item["inputId"]: item for item in request["loadInputs"]}
    controls = {control["controlId"]: control for control in request["loadControls"]}
    reasons = {reason["reasonId"]: reason for reason in request["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in request["handoffRefs"]}
    flags = request["safetyFlags"]

    assert request["loadRequestState"] == "blocked"
    assert request["selectedModelState"] == "target_selected"
    assert request["descriptorState"] == "available_as_data"
    assert request["assetInputState"] == "blocked"
    assert request["assetPathState"] == "not_configured"
    assert request["checksumState"] == "not_configured"
    assert request["loadPlanState"] == "blocked"
    assert request["runtimePreflightState"] == "blocked"
    assert request["deviceSessionState"] == "inactive"
    assert request["warmupState"] == "disabled"
    assert request["unloadState"] == "disabled"
    assert policy["descriptorSelected"] is True
    assert policy["modelAssetsConfigured"] is False
    assert policy["assetPathsConfigured"] is False
    assert policy["checksumsAvailable"] is False
    assert policy["runtimeReady"] is False
    assert policy["deviceSessionReady"] is False
    assert policy["loadEnabled"] is False
    assert policy["warmupEnabled"] is False
    assert policy["unloadEnabled"] is False
    assert set(load_inputs) == {
        "model_descriptor",
        "local_asset_path",
        "model_weight_file",
        "tokenizer_asset",
        "checksum_manifest",
        "runtime_profile",
        "device_session",
    }
    assert all(item["enabled"] is False for item in load_inputs.values())
    assert set(controls) == {
        "select_model_descriptor",
        "configure_asset_path",
        "validate_assets",
        "build_load_plan",
        "start_runtime",
        "load_model",
        "warmup_model",
        "unload_model",
        "persist_load_request",
    }
    assert all(control["enabled"] is False for control in controls.values())
    assert controls["configure_asset_path"]["sideEffectPolicy"] == "no_config_or_path_read"
    assert controls["validate_assets"]["sideEffectPolicy"] == "no_model_asset_read"
    assert controls["load_model"]["sideEffectPolicy"] == "no_model_load"
    assert set(reasons) == {
        "model_asset_input_boundary_absent",
        "model_asset_path_boundary_absent",
        "model_integrity_evidence_absent",
        "runtime_readiness_blocked",
        "device_session_inactive",
        "model_load_executor_absent",
        "unload_policy_absent",
        "local_only_policy_required",
    }
    assert set(refs) == {
        "chat_model_status",
        "runtime_readiness",
        "device_session_status",
        "chat_readiness",
        "chat_local_only_policy",
    }
    assert flags["readOnly"] is True
    assert flags["dataOnly"] is True
    assert flags["loadRequestDisplayOnly"] is True
    assert flags["modelDescriptorMetadataOnly"] is True
    for name in [
        "modelAssetsConfigured",
        "modelAssetPathsConfigured",
        "modelAssetPathsIncluded",
        "modelWeightPathsIncluded",
        "modelAssetRead",
        "modelWeightRead",
        "tokenizerRead",
        "checksumManifestRead",
        "checksumValuesIncluded",
        "modelIntegrityChecked",
        "configRead",
        "configWrite",
        "environmentRead",
        "promptContentIncluded",
        "responseContentIncluded",
        "runtimePreflightExecuted",
        "runtimeStarted",
        "runtimeExecution",
        "modelLoadAttempted",
        "modelLoaded",
        "modelUnloadAttempted",
        "modelExecution",
        "warmupAttempted",
        "kv260Access",
        "hardwareAccess",
        "networkCalls",
        "providerCalls",
        "cloudCalls",
        "writesArtifacts",
        "readsArtifacts",
        "executesPccxLab",
    ]:
        assert flags[name] is False, name


def test_chat_model_load_request_docs_and_ci_are_wired() -> None:
    doc = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "contracts/chat_model_load_request_contract.py" in doc
    assert (
        "contracts/fixtures/chat-model-load-request.gemma3n-e4b-kv260-placeholder.json"
        in doc
    )
    assert "scripts/chat-model-load-request-stub.sh" in doc
    assert "scripts/tests/chat_model_load_request_contract_test.py" in doc
    assert "scripts/tests/status-chat-model-load-request.sh" in doc
    assert "chat-model-load-request-stub.sh" in readme
    assert "--include-chat-model-load-request" in readme
    assert "chat_model_load_request_contract_test.py" in ci
    assert "status-chat-model-load-request.sh" in ci
    assert "--include-chat-model-load-request" in status_test
    assert "no model asset path/read/load/runtime" in status_test


def test_chat_model_load_request_has_no_runtime_or_private_surface() -> None:
    module = load_module()
    request = module.create_gemma3n_e4b_kv260_chat_model_load_request()
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

    assert_no_provider_configs(request)
    assert_no_private_or_generated_data(docs)
    assert_no_unsupported_claims(docs)
    assert_no_runtime_implementation_terms(contract_source)
    assert_no_runtime_implementation_terms(stub_source)
    assert "modelPathValue" not in fixture_text
    assert "assetPathValue" not in fixture_text
    assert "weightFilename" not in fixture_text
    assert '"checksumValue"' not in fixture_text
    assert "promptText" not in fixture_text
    assert "responseText" not in fixture_text
    assert "transcriptText" not in fixture_text


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

    for path, headers in expected_headers.items():
        assert read_text(path).splitlines()[: len(headers)] == headers, path


if __name__ == "__main__":
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
    print("chat model-load request contract tests ok")
