#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat session-store policy contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_session_store_policy_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-session-store-policy.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-session-store-policy-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-session-store-policy.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_session_store_policy_contract",
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


def test_chat_session_store_policy_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_session_store_policy()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_session_store_policy_json(generated) == (
        module.chat_session_store_policy_json(generated)
    )
    assert module.chat_session_store_policy_json(generated).endswith("\n")
    assert json.loads(module.chat_session_store_policy_json(generated)) == fixture


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
    policy = module.create_gemma3n_e4b_kv260_chat_session_store_policy()
    allowed = set(module.CHAT_SESSION_STORE_POLICY_STATE_VALUES)

    assert tuple(policy.keys()) == module.CHAT_SESSION_STORE_POLICY_FIELDS
    assert policy["schemaVersion"] == "pccx.chatSessionStorePolicy.v0"
    assert tuple(policy["sessionStorePolicy"].keys()) == (
        module.SESSION_STORE_POLICY_FIELDS
    )

    states = list(iter_state_values(policy))
    assert states
    for state in states:
        assert state in allowed, state

    for surface in policy["storeSurfaces"]:
        assert tuple(surface.keys()) == module.STORE_SURFACE_FIELDS
    for control in policy["storeControls"]:
        assert tuple(control.keys()) == module.STORE_CONTROL_FIELDS
    for reason in policy["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in policy["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_session_store_policy_keeps_store_disabled() -> None:
    policy = load_module().create_gemma3n_e4b_kv260_chat_session_store_policy()
    store_policy = policy["sessionStorePolicy"]
    surfaces = {
        surface["surfaceId"]: surface
        for surface in policy["storeSurfaces"]
    }
    controls = {
        control["controlId"]: control
        for control in policy["storeControls"]
    }
    reasons = {reason["reasonId"]: reason for reason in policy["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in policy["handoffRefs"]}
    flags = policy["safetyFlags"]

    assert policy["sessionStorePolicyState"] == "blocked"
    assert policy["storeState"] == "not_configured"
    assert policy["storePathState"] == "not_configured"
    assert policy["manifestState"] == "not_configured"
    assert policy["readState"] == "blocked"
    assert policy["writeState"] == "disabled"
    assert policy["deleteState"] == "disabled"
    assert policy["retentionState"] == "not_configured"
    assert policy["migrationState"] == "disabled"
    assert store_policy["storeConfigured"] is False
    assert store_policy["storePathConfigured"] is False
    assert store_policy["manifestSchemaConfigured"] is False
    assert store_policy["readEnabled"] is False
    assert store_policy["writeEnabled"] is False
    assert store_policy["deleteEnabled"] is False
    assert store_policy["retentionEnabled"] is False
    assert store_policy["migrationEnabled"] is False
    assert set(surfaces) == {
        "local_store_path",
        "session_manifest",
        "session_record",
        "title_record",
        "transcript_record",
        "retention_rule",
    }
    assert all(surface["enabled"] is False for surface in surfaces.values())
    assert set(controls) == {
        "configure_store",
        "read_store_path",
        "read_manifest",
        "read_session_record",
        "write_session_record",
        "delete_session_record",
        "migrate_store",
        "persist_store_policy",
    }
    assert all(control["enabled"] is False for control in controls.values())
    assert controls["read_store_path"]["sideEffectPolicy"] == "no_config_or_path_read"
    assert controls["read_manifest"]["sideEffectPolicy"] == "no_manifest_read"
    assert controls["write_session_record"]["sideEffectPolicy"] == "no_session_store_write"
    assert set(reasons) == {
        "store_not_configured",
        "store_path_boundary_absent",
        "manifest_schema_absent",
        "session_store_read_boundary_absent",
        "session_store_write_boundary_absent",
        "deletion_retention_policy_absent",
        "migration_policy_absent",
        "redaction_policy_absent",
    }
    assert set(refs) == {
        "chat_session",
        "chat_session_index",
        "chat_session_lifecycle",
        "chat_session_title_policy",
        "chat_transcript_policy",
        "chat_preferences",
    }
    assert flags["readOnly"] is True
    assert flags["dataOnly"] is True
    assert flags["sessionStorePolicyDisplayOnly"] is True
    assert flags["storeMetadataOnly"] is True
    assert flags["storeConfigured"] is False
    assert flags["storePathConfigured"] is False
    assert flags["storePathIncluded"] is False
    assert flags["configRead"] is False
    assert flags["configWrite"] is False
    assert flags["readsSessionStore"] is False
    assert flags["sessionStoreRead"] is False
    assert flags["sessionStoreWrite"] is False
    assert flags["readsSessionManifest"] is False
    assert flags["manifestContentIncluded"] is False
    assert flags["sessionRecordIncluded"] is False
    assert flags["sessionPersistence"] is False
    assert flags["sessionDeletion"] is False
    assert flags["retentionPolicyActive"] is False
    assert flags["migrationAttempted"] is False
    assert flags["readsSessionTitle"] is False
    assert flags["sessionTitleIncluded"] is False
    assert flags["readsTranscript"] is False
    assert flags["promptContentIncluded"] is False
    assert flags["responseContentIncluded"] is False
    assert flags["writesArtifacts"] is False
    assert flags["readsArtifacts"] is False
    assert flags["modelExecution"] is False
    assert flags["runtimeExecution"] is False
    assert flags["kv260Access"] is False
    assert flags["networkCalls"] is False
    assert flags["providerCalls"] is False
    assert flags["executesPccxLab"] is False


def test_chat_session_store_policy_docs_and_ci_are_wired() -> None:
    doc = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "contracts/chat_session_store_policy_contract.py" in doc
    assert (
        "contracts/fixtures/chat-session-store-policy.gemma3n-e4b-kv260-placeholder.json"
        in doc
    )
    assert "scripts/chat-session-store-policy-stub.sh" in doc
    assert "scripts/tests/chat_session_store_policy_contract_test.py" in doc
    assert "scripts/tests/status-chat-session-store-policy.sh" in doc
    assert "chat-session-store-policy-stub.sh" in readme
    assert "--include-chat-session-store-policy" in readme
    assert "chat_session_store_policy_contract_test.py" in ci
    assert "status-chat-session-store-policy.sh" in ci
    assert "--include-chat-session-store-policy" in status_test
    assert "no config/path/manifest/session-store" in status_test


def test_chat_session_store_policy_has_no_runtime_or_private_surface() -> None:
    module = load_module()
    policy = module.create_gemma3n_e4b_kv260_chat_session_store_policy()
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

    assert_no_provider_configs(policy)
    assert_no_private_or_generated_data(docs)
    assert_no_unsupported_claims(docs)
    assert_no_runtime_implementation_terms(contract_source)
    assert_no_runtime_implementation_terms(stub_source)
    assert "promptText" not in fixture_text
    assert "responseText" not in fixture_text
    assert "transcriptText" not in fixture_text
    assert "sessionTitleText" not in fixture_text
    assert "storePathValue" not in fixture_text
    assert "manifestBody" not in fixture_text


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
    print("chat session-store policy contract tests ok")
