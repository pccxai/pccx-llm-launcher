#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat attachment-policy contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_attachment_policy_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-attachment-policy.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-attachment-policy-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-attachment-policy.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_attachment_policy_contract",
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


def flatten(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from flatten(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from flatten(nested)
    else:
        yield str(value)


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


def test_chat_attachment_policy_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_attachment_policy()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_attachment_policy_json(generated) == (
        module.chat_attachment_policy_json(generated)
    )
    assert module.chat_attachment_policy_json(generated).endswith("\n")
    assert json.loads(module.chat_attachment_policy_json(generated)) == fixture


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
    policy = module.create_gemma3n_e4b_kv260_chat_attachment_policy()
    allowed = set(module.CHAT_ATTACHMENT_POLICY_STATE_VALUES)

    assert tuple(policy.keys()) == module.CHAT_ATTACHMENT_POLICY_FIELDS
    assert policy["schemaVersion"] == "pccx.chatAttachmentPolicy.v0"
    assert tuple(policy["attachmentPolicy"].keys()) == (
        module.ATTACHMENT_POLICY_FIELDS
    )

    states = list(iter_state_values(policy))
    assert states
    for state in states:
        assert state in allowed, state

    for input_item in policy["attachmentInputs"]:
        assert tuple(input_item.keys()) == module.ATTACHMENT_INPUT_FIELDS
    for control in policy["attachmentControls"]:
        assert tuple(control.keys()) == module.ATTACHMENT_CONTROL_FIELDS
    for reason in policy["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in policy["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_attachment_policy_keeps_file_inputs_disabled() -> None:
    policy = load_module().create_gemma3n_e4b_kv260_chat_attachment_policy()
    attachment_policy = policy["attachmentPolicy"]
    inputs = {
        input_item["inputKind"]: input_item
        for input_item in policy["attachmentInputs"]
    }
    controls = {
        control["controlId"]: control
        for control in policy["attachmentControls"]
    }
    reasons = {reason["reasonId"]: reason for reason in policy["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in policy["handoffRefs"]}
    flags = policy["safetyFlags"]

    assert policy["attachmentPolicyState"] == "blocked"
    assert policy["attachmentState"] == "disabled"
    assert policy["filePickerState"] == "disabled"
    assert policy["fileReadState"] == "blocked"
    assert policy["uploadState"] == "disabled"
    assert policy["importState"] == "disabled"
    assert policy["previewState"] == "disabled"
    assert policy["persistenceState"] == "disabled"
    assert policy["privacyState"] == "summary_only"
    assert attachment_policy["allowedInputKinds"] == []
    assert attachment_policy["maxAttachmentCount"] == 0
    assert attachment_policy["filePickerEnabled"] is False
    assert attachment_policy["fileMetadataReadEnabled"] is False
    assert attachment_policy["fileContentReadEnabled"] is False
    assert attachment_policy["uploadEnabled"] is False
    assert attachment_policy["importEnabled"] is False
    assert attachment_policy["previewEnabled"] is False
    assert attachment_policy["persistenceEnabled"] is False
    assert set(inputs) == {
        "local_file",
        "local_directory",
        "clipboard_payload",
        "generated_artifact",
        "transcript_export",
    }
    assert all(input_item["enabled"] is False for input_item in inputs.values())
    assert inputs["local_file"]["sideEffectPolicy"] == "no_file_picker_no_file_read"
    assert inputs["local_directory"]["sideEffectPolicy"] == "no_directory_scan"
    assert inputs["clipboard_payload"]["sideEffectPolicy"] == "no_clipboard_read"
    assert set(controls) == {
        "open_file_picker",
        "read_file_metadata",
        "read_file_content",
        "import_attachment",
        "upload_attachment",
        "preview_attachment",
        "persist_attachment",
    }
    assert all(control["enabled"] is False for control in controls.values())
    assert controls["open_file_picker"]["sideEffectPolicy"] == "no_file_picker"
    assert controls["read_file_metadata"]["sideEffectPolicy"] == "no_file_metadata_read"
    assert controls["read_file_content"]["sideEffectPolicy"] == "no_file_content_read"
    assert controls["upload_attachment"]["sideEffectPolicy"] == "no_upload_no_network"
    assert set(reasons) == {
        "attachment_runtime_not_reviewed",
        "file_picker_boundary_absent",
        "metadata_read_boundary_absent",
        "file_content_read_boundary_absent",
        "import_export_boundary_absent",
        "attachment_persistence_boundary_absent",
        "local_only_upload_block",
        "clipboard_boundary_absent",
    }
    assert set(refs) == {
        "chat_composer",
        "chat_action_bar",
        "chat_shortcut_map",
        "chat_local_only_policy",
        "chat_transcript_policy",
    }
    assert flags["readOnly"] is True
    assert flags["dataOnly"] is True
    assert flags["attachmentPolicyDisplayOnly"] is True
    assert flags["attachmentMetadataOnly"] is True
    assert flags["attachmentsEnabled"] is False
    assert flags["filePickerOpened"] is False
    assert flags["fileMetadataRead"] is False
    assert flags["fileContentRead"] is False
    assert flags["fileNameIncluded"] is False
    assert flags["filePathIncluded"] is False
    assert flags["fileBytesIncluded"] is False
    assert flags["directoryScan"] is False
    assert flags["attachmentReads"] is False
    assert flags["attachmentPersistence"] is False
    assert flags["fileUpload"] is False
    assert flags["fileImport"] is False
    assert flags["filePreview"] is False
    assert flags["clipboardRead"] is False
    assert flags["writesArtifacts"] is False
    assert flags["readsArtifacts"] is False
    assert flags["readsTranscript"] is False
    assert flags["transcriptExport"] is False
    assert flags["promptContentIncluded"] is False
    assert flags["responseContentIncluded"] is False
    assert flags["modelExecution"] is False
    assert flags["runtimeExecution"] is False
    assert flags["kv260Access"] is False
    assert flags["networkCalls"] is False
    assert flags["providerCalls"] is False
    assert flags["executesPccxLab"] is False


def test_chat_attachment_policy_docs_and_ci_are_wired() -> None:
    doc = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "contracts/chat_attachment_policy_contract.py" in doc
    assert (
        "contracts/fixtures/chat-attachment-policy.gemma3n-e4b-kv260-placeholder.json"
        in doc
    )
    assert "scripts/chat-attachment-policy-stub.sh" in doc
    assert "scripts/tests/chat_attachment_policy_contract_test.py" in doc
    assert "scripts/tests/status-chat-attachment-policy.sh" in doc
    assert "chat-attachment-policy-stub.sh" in readme
    assert "--include-chat-attachment-policy" in readme
    assert "chat_attachment_policy_contract_test.py" in ci
    assert "status-chat-attachment-policy.sh" in ci
    assert "--include-chat-attachment-policy" in status_test
    assert "no file picker/file metadata/file content/upload" in status_test


def test_chat_attachment_policy_has_no_runtime_or_private_surface() -> None:
    module = load_module()
    policy = module.create_gemma3n_e4b_kv260_chat_attachment_policy()
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
    assert "fileNameValue" not in fixture_text
    assert "filePathValue" not in fixture_text
    assert "fileContentText" not in fixture_text
    assert "previewBody" not in fixture_text
    assert all(
        "attachment:" not in item.lower()
        for item in flatten(policy)
    )


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
    print("chat attachment policy contract tests ok")
