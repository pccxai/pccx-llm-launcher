#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat clipboard-policy contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_clipboard_policy_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-clipboard-policy.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-clipboard-policy-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-clipboard-policy.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_clipboard_policy_contract",
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


def test_chat_clipboard_policy_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_clipboard_policy()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.chat_clipboard_policy_json(generated) == (
        module.chat_clipboard_policy_json(generated)
    )
    assert module.chat_clipboard_policy_json(generated).endswith("\n")
    assert json.loads(module.chat_clipboard_policy_json(generated)) == fixture


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
    clipboard_policy = module.create_gemma3n_e4b_kv260_chat_clipboard_policy()
    allowed = set(module.CHAT_CLIPBOARD_POLICY_STATE_VALUES)

    assert tuple(clipboard_policy.keys()) == module.CHAT_CLIPBOARD_POLICY_FIELDS
    assert clipboard_policy["schemaVersion"] == "pccx.chatClipboardPolicy.v0"
    assert (
        tuple(clipboard_policy["clipboardPolicy"].keys())
        == module.CLIPBOARD_POLICY_FIELDS
    )

    states = list(iter_state_values(clipboard_policy))
    assert states
    for state in states:
        assert state in allowed, state

    for surface in clipboard_policy["clipboardSurfaces"]:
        assert tuple(surface.keys()) == module.CLIPBOARD_SURFACE_FIELDS
    for control in clipboard_policy["clipboardControls"]:
        assert tuple(control.keys()) == module.CLIPBOARD_CONTROL_FIELDS
    for reason in clipboard_policy["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in clipboard_policy["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_clipboard_policy_keeps_clipboard_disabled() -> None:
    clipboard_policy = load_module().create_gemma3n_e4b_kv260_chat_clipboard_policy()
    policy = clipboard_policy["clipboardPolicy"]
    flags = clipboard_policy["safetyFlags"]
    surfaces = {
        surface["surfaceId"]: surface
        for surface in clipboard_policy["clipboardSurfaces"]
    }
    controls = {
        control["controlId"]: control
        for control in clipboard_policy["clipboardControls"]
    }
    reasons = {
        reason["reasonId"]: reason for reason in clipboard_policy["blockedReasons"]
    }
    refs = {ref["refId"]: ref for ref in clipboard_policy["handoffRefs"]}

    assert clipboard_policy["clipboardPolicyState"] == "blocked"
    assert clipboard_policy["clipboardReadState"] == "disabled"
    assert clipboard_policy["clipboardWriteState"] == "disabled"
    assert clipboard_policy["copyActionState"] == "disabled"
    assert clipboard_policy["pasteActionState"] == "disabled"
    assert clipboard_policy["clipboardImportState"] == "disabled"
    assert clipboard_policy["clipboardExportState"] == "disabled"
    assert clipboard_policy["selectionState"] == "empty_not_captured"
    assert clipboard_policy["messageContentState"] == "empty_not_captured"
    assert policy["sideEffectPolicy"] == "local_render_only"
    assert policy["readEnabled"] is False
    assert policy["writeEnabled"] is False
    assert policy["copyEnabled"] is False
    assert policy["pasteEnabled"] is False
    assert policy["importEnabled"] is False
    assert policy["exportEnabled"] is False
    assert set(surfaces) == {
        "message_actions",
        "composer_input",
        "attachment_input",
        "transcript_export",
    }
    assert all(surface["enabled"] is False for surface in surfaces.values())
    assert set(controls) == {
        "copy_message",
        "copy_transcript",
        "paste_prompt",
        "paste_attachment",
        "import_clipboard_payload",
        "export_to_clipboard",
    }
    assert all(control["enabled"] is False for control in controls.values())
    assert controls["copy_message"]["sideEffectPolicy"] == "no_clipboard_write"
    assert controls["copy_transcript"]["sideEffectPolicy"] == (
        "no_transcript_read_no_clipboard_write"
    )
    assert controls["paste_prompt"]["sideEffectPolicy"] == "no_clipboard_read"
    assert controls["paste_attachment"]["sideEffectPolicy"] == (
        "no_clipboard_attachment_read"
    )
    assert controls["import_clipboard_payload"]["sideEffectPolicy"] == (
        "no_clipboard_import"
    )
    assert controls["export_to_clipboard"]["sideEffectPolicy"] == (
        "no_clipboard_export"
    )
    assert set(reasons) == {
        "clipboard_api_boundary_absent",
        "message_content_absent",
        "transcript_export_not_reviewed",
        "attachment_clipboard_boundary_absent",
        "privacy_redaction_not_reviewed",
    }
    assert set(refs) == {
        "chat_composer",
        "chat_action_bar",
        "chat_message_list",
        "chat_attachment_policy",
        "chat_transcript_policy",
        "chat_local_only_policy",
    }
    assert flags["readOnly"] is True
    assert flags["dataOnly"] is True
    assert flags["clipboardPolicyDisplayOnly"] is True
    assert flags["clipboardMetadataOnly"] is True
    assert flags["clipboardRead"] is False
    assert flags["clipboardWrite"] is False
    assert flags["clipboardCopy"] is False
    assert flags["clipboardPaste"] is False
    assert flags["clipboardImport"] is False
    assert flags["clipboardExport"] is False
    assert flags["clipboardAttachmentRead"] is False
    assert flags["clipboardEventListenerInstalled"] is False
    assert flags["selectionRead"] is False
    assert flags["messageBodiesIncluded"] is False
    assert flags["promptCapture"] is False
    assert flags["promptRead"] is False
    assert flags["promptContentIncluded"] is False
    assert flags["responseContentIncluded"] is False
    assert flags["transcriptContentIncluded"] is False
    assert flags["readsTranscript"] is False
    assert flags["transcriptExport"] is False
    assert flags["readsSessionStore"] is False
    assert flags["sessionStoreRead"] is False
    assert flags["sessionStoreWrite"] is False
    assert flags["attachmentReads"] is False
    assert flags["fileUpload"] is False
    assert flags["fileImport"] is False
    assert flags["filePreview"] is False
    assert flags["writesArtifacts"] is False
    assert flags["readsArtifacts"] is False
    assert flags["modelAssetRead"] is False
    assert flags["modelExecution"] is False
    assert flags["runtimeExecution"] is False
    assert flags["kv260Access"] is False
    assert flags["hardwareAccess"] is False
    assert flags["networkCalls"] is False
    assert flags["providerCalls"] is False
    assert flags["cloudCalls"] is False
    assert flags["executesPccxLab"] is False


def test_chat_clipboard_policy_docs_and_ci_are_wired() -> None:
    doc = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "contracts/chat_clipboard_policy_contract.py" in doc
    assert (
        "contracts/fixtures/chat-clipboard-policy.gemma3n-e4b-kv260-placeholder.json"
        in doc
    )
    assert "scripts/chat-clipboard-policy-stub.sh" in doc
    assert "scripts/tests/chat_clipboard_policy_contract_test.py" in doc
    assert "scripts/tests/status-chat-clipboard-policy.sh" in doc
    assert "chat-clipboard-policy-stub.sh" in readme
    assert "--include-chat-clipboard-policy" in readme
    assert "chat_clipboard_policy_contract_test.py" in ci
    assert "status-chat-clipboard-policy.sh" in ci
    assert "--include-chat-clipboard-policy" in status_test


def test_chat_clipboard_policy_has_no_runtime_or_private_surface() -> None:
    module = load_module()
    clipboard_policy = module.create_gemma3n_e4b_kv260_chat_clipboard_policy()
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

    assert_no_provider_configs(clipboard_policy)
    assert_no_private_or_generated_data(docs)
    assert_no_unsupported_claims(docs)
    assert_no_runtime_implementation_terms(contract_source)
    assert_no_runtime_implementation_terms(stub_source)


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
    print("chat clipboard-policy contract tests ok")
