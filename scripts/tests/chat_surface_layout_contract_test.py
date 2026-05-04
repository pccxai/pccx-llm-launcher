#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the standalone chat surface-layout contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "chat_surface_layout_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "chat-surface-layout.gemma3n-e4b-kv260-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "chat-surface-layout-stub.sh"
STATUS_TEST_PATH = ROOT / "scripts" / "tests" / "status-chat-surface-layout.sh"
DOC_PATH = ROOT / "docs" / "STANDALONE_CHAT_SESSION_CONTRACT.md"
README_PATH = ROOT / "README.md"
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "chat_surface_layout_contract",
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


def test_chat_surface_layout_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_chat_surface_layout()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert (
        module.chat_surface_layout_json(generated)
        == module.chat_surface_layout_json(generated)
    )
    assert module.chat_surface_layout_json(generated).endswith("\n")
    assert json.loads(module.chat_surface_layout_json(generated)) == fixture


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
    layout = module.create_gemma3n_e4b_kv260_chat_surface_layout()
    allowed = set(module.CHAT_SURFACE_LAYOUT_STATE_VALUES)

    assert tuple(layout.keys()) == module.CHAT_SURFACE_LAYOUT_FIELDS
    assert layout["schemaVersion"] == "pccx.chatSurfaceLayout.v0"
    assert tuple(layout["layoutPolicy"].keys()) == module.LAYOUT_POLICY_FIELDS

    states = list(iter_state_values(layout))
    assert states
    for state in states:
        assert state in allowed, state

    for region in layout["surfaceRegions"]:
        assert tuple(region.keys()) == module.SURFACE_REGION_FIELDS
    for item in layout["navigationItems"]:
        assert tuple(item.keys()) == module.NAVIGATION_ITEM_FIELDS
    for reason in layout["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in layout["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_chat_surface_layout_covers_issue_9_shell_boundary() -> None:
    layout = load_module().create_gemma3n_e4b_kv260_chat_surface_layout()
    flags = layout["safetyFlags"]
    regions = {region["regionId"]: region for region in layout["surfaceRegions"]}
    items = {item["navId"]: item for item in layout["navigationItems"]}
    reasons = {reason["reasonId"]: reason for reason in layout["blockedReasons"]}
    refs = {ref["refId"]: ref for ref in layout["handoffRefs"]}

    assert layout["layoutState"] == "blocked"
    assert layout["shellState"] == "placeholder"
    assert layout["navigationState"] == "available_as_data"
    assert layout["primaryRegionState"] == "empty_not_captured"
    assert layout["contentState"] == "empty_not_captured"
    assert layout["privacyState"] == "summary_only"
    assert set(regions) == {
        "session_index_sidebar",
        "model_status_header",
        "readiness_banner",
        "transcript_region",
        "composer_bar",
        "send_result_region",
        "audit_footer",
    }
    assert regions["session_index_sidebar"]["enabled"] is True
    assert regions["transcript_region"]["state"] == "empty_not_captured"
    assert regions["composer_bar"]["enabled"] is False
    assert set(items) == {
        "open_chat_surface",
        "open_session_index",
        "open_model_status",
        "open_readiness",
        "focus_composer",
    }
    assert items["open_chat_surface"]["enabled"] is True
    assert items["focus_composer"]["state"] == "disabled"
    assert {
        "runtime_readiness_blocked",
        "chat_runtime_not_started",
        "composer_send_disabled",
        "transcript_content_absent",
        "session_store_not_configured",
    } <= set(reasons)
    assert set(refs) == {
        "chat_session",
        "chat_session_index",
        "chat_model_status",
        "chat_readiness",
        "chat_composer",
        "chat_transcript_policy",
    }
    assert flags["readOnly"] is True
    assert flags["surfaceLayoutDisplayOnly"] is True
    assert flags["readsArtifacts"] is False
    assert flags["writesArtifacts"] is False
    assert flags["sessionStoreRead"] is False
    assert flags["promptCapture"] is False
    assert flags["promptContentIncluded"] is False
    assert flags["responseContentIncluded"] is False
    assert flags["transcriptContentIncluded"] is False
    assert flags["sessionTitleIncluded"] is False
    assert flags["summaryIncluded"] is False
    assert flags["inputAccepted"] is False
    assert flags["sendAttempted"] is False
    assert flags["modelExecution"] is False
    assert flags["runtimeExecution"] is False
    assert flags["kv260Access"] is False
    assert flags["providerCalls"] is False
    assert flags["executesPccxLab"] is False


def test_contract_avoids_runtime_or_private_data() -> None:
    module_source = read_text(MODULE_PATH)
    fixture_text = read_text(FIXTURE_PATH)
    fixture = json.loads(fixture_text)

    assert_no_runtime_implementation_terms(module_source)
    assert_no_private_or_generated_data(fixture_text)
    assert_no_provider_configs(fixture)
    assert_no_unsupported_claims(fixture_text)
    assert "hello" not in fixture_text.lower()
    assert "promptText" not in fixture_text
    assert "responseText" not in fixture_text
    assert "sessionTitleText" not in fixture_text


def test_docs_readme_status_tests_and_ci_reference_surface_layout() -> None:
    docs = read_text(DOC_PATH)
    readme = read_text(README_PATH)
    status_test = read_text(STATUS_TEST_PATH)
    ci = read_text(CI_PATH)

    assert "chat_surface_layout_contract.py" in docs
    assert "chat-surface-layout-stub.sh" in docs
    assert "chat-surface-layout.gemma3n-e4b-kv260-placeholder.json" in docs
    assert "chat surface layout" in docs
    assert "--include-chat-surface-layout" in docs
    assert "chat-surface-layout-stub.sh" in readme
    assert "--include-chat-surface-layout" in readme
    assert "status-chat-surface-layout" in ci
    assert "chat_surface_layout_contract_test.py" in ci
    assert "no prompt/response/transcript/session-store" in status_test


if __name__ == "__main__":
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
    print("chat surface layout contract tests ok")
