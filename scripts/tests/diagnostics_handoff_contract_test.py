#!/usr/bin/env python3
"""Fixture tests for the launcher diagnostics handoff contract."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "diagnostics_handoff_contract.py"
STATUS_MODULE_PATH = ROOT / "contracts" / "launcher_ide_status_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "diagnostics-handoff.gemma3n-e4b-kv260-placeholder.json"
)
DOC_PATH = ROOT / "docs" / "DIAGNOSTICS_HANDOFF_CONTRACT.md"
STATUS_DOC_PATH = ROOT / "docs" / "LAUNCHER_IDE_BRIDGE_CONTRACT.md"
README_PATH = ROOT / "README.md"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def flatten(value) -> str:
    return json.dumps(value, sort_keys=True)


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
        r"(?:raw[_-]?full[_-]?logs|hardware[_-]?dump|bitstream|generated[_-]?blob)\s*[:=]",
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
        "vscode-languageclient",
        "vsce",
        "watchdog",
        "filewatcher",
        "websocket",
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
        "autonomous coding system",
        "Claude directly controls",
        "GPT directly controls",
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


def test_handoff_matches_fixture_and_is_deterministic() -> None:
    module = load_module(MODULE_PATH, "diagnostics_handoff_contract")
    generated = module.create_diagnostics_handoff_contract()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.handoff_json(generated) == module.handoff_json(generated)
    assert module.handoff_json(generated).endswith("\n")
    assert json.loads(module.handoff_json(generated)) == fixture


def test_handoff_shape_and_diagnostic_values() -> None:
    module = load_module(MODULE_PATH, "diagnostics_handoff_contract")
    handoff = module.create_diagnostics_handoff_contract()

    assert tuple(handoff.keys()) == module.HANDOFF_FIELDS
    assert handoff["schemaVersion"] == "pccx.diagnosticsHandoff.v0"
    assert handoff["handoffKind"] == "read_only_handoff"
    assert handoff["producer"]["role"] == "launcher_generated_summary"
    assert handoff["consumer"]["role"] == "pccx_lab_future_consumer"
    assert handoff["targetKind"] == "kv260"
    assert handoff["targetDevice"]["configurationState"] == "not_configured"
    assert handoff["targetDevice"]["accessState"] == "no_hardware_access"

    severities = set()
    categories = set()
    diagnostic_ids = set()
    for diagnostic in handoff["diagnostics"]:
        assert tuple(diagnostic.keys()) == module.DIAGNOSTIC_ITEM_FIELDS
        severities.add(diagnostic["severity"])
        categories.add(diagnostic["category"])
        diagnostic_ids.add(diagnostic["diagnosticId"])
        assert diagnostic["evidenceState"] in {
            "evidence_required",
            "not_measured",
            "placeholder",
        }
        assert diagnostic["redactionState"] == "sanitized_summary"

    assert severities <= set(module.SEVERITY_VALUES)
    assert categories <= set(module.CATEGORY_VALUES)
    assert {"info", "warning", "blocked"} <= severities
    assert "launcher_target_not_configured" in diagnostic_ids
    assert "kv260_runtime_placeholder_not_configured" in diagnostic_ids
    assert "read_only_privacy_boundary" in diagnostic_ids


def test_read_only_privacy_and_safety_flags() -> None:
    handoff = load_module(
        MODULE_PATH,
        "diagnostics_handoff_contract",
    ).create_diagnostics_handoff_contract()

    privacy = handoff["privacyFlags"]
    assert privacy["uploadPolicy"] == "no_user_data_upload"
    assert privacy["telemetryPolicy"] == "no_telemetry"
    for name in [
        "automaticUpload",
        "rawFullLogsIncluded",
        "userPromptsIncluded",
        "userSourceCodeIncluded",
        "privatePathsIncluded",
        "secretsIncluded",
        "tokensIncluded",
        "providerConfigsIncluded",
        "modelWeightPathsIncluded",
        "generatedBlobsIncluded",
    ]:
        assert privacy[name] is False, name

    flags = handoff["safetyFlags"]
    assert flags["contractKind"] == "read_only_handoff"
    assert flags["descriptorPolicy"] == "descriptor_ref_only"
    assert flags["writeBackPolicy"] == "no_auto_writeback"
    assert flags["runtimePolicy"] == "no_runtime_execution"
    assert flags["hardwarePolicy"] == "no_hardware_access"
    assert flags["evidencePolicy"] == "evidence_required"
    assert flags["dataOnly"] is True
    assert flags["readOnly"] is True
    for name in [
        "executesPccxLab",
        "executesLauncher",
        "runtimeExecution",
        "touchesHardware",
        "kv260Access",
        "modelExecution",
        "networkCalls",
        "providerCalls",
        "shellExecution",
        "mcpServerImplemented",
        "lspImplemented",
        "marketplaceFlow",
        "telemetry",
        "automaticUpload",
        "writeBack",
    ]:
        assert flags[name] is False, name


def test_transport_sketches_are_future_safe() -> None:
    handoff = load_module(
        MODULE_PATH,
        "diagnostics_handoff_contract",
    ).create_diagnostics_handoff_contract()
    transports = {item["transportKind"]: item for item in handoff["transport"]}

    assert set(transports) == {
        "json_file",
        "stdout_json",
        "read_only_local_artifact_reference",
    }
    for item in transports.values():
        assert item["state"] == "sketch"
        assert item["mode"] == "read_only_handoff"
        assert item["execution"] == "no_pccx_lab_execution"


def test_fixture_references_descriptors_without_runtime_coupling() -> None:
    handoff = load_module(
        MODULE_PATH,
        "diagnostics_handoff_contract",
    ).create_diagnostics_handoff_contract()

    assert "modelDescriptor" not in handoff
    assert "runtimeDescriptor" not in handoff
    assert handoff["modelDescriptorRef"]["modelId"] == "gemma3n_e4b_placeholder"
    assert handoff["runtimeDescriptorRef"]["runtimeId"] == "kv260_pccx_placeholder"
    assert handoff["modelDescriptorRef"]["referenceKind"] == "descriptor_ref_only"
    assert handoff["runtimeDescriptorRef"]["referenceKind"] == "descriptor_ref_only"
    assert handoff["launcherStatusRef"]["coupling"] == "data_reference_only"
    assert handoff["launcherStatusRef"]["operationId"] == "pccxlab.diagnostics.handoff"

    fixture_refs = flatten(handoff)
    assert "model-runtime-descriptor.gemma3n-e4b-kv260-placeholder.json" in fixture_refs
    assert "launcher-ide-status.placeholder.json" in fixture_refs


def test_handoff_can_be_referenced_by_launcher_status_contract() -> None:
    handoff = load_module(
        MODULE_PATH,
        "diagnostics_handoff_contract",
    ).create_diagnostics_handoff_contract()
    status = load_module(
        STATUS_MODULE_PATH,
        "launcher_ide_status_contract",
    ).create_launcher_ide_status_contract()

    operations = {operation["id"]: operation for operation in status["supportedOperations"]}
    operation = operations[handoff["launcherStatusRef"]["operationId"]]
    assert operation["handoffMode"] == "read_only_handoff"
    assert operation["lowerBoundary"] == "pccx-lab CLI/core"
    assert status["diagnosticsHandoff"]["mode"] == "read_only_handoff"
    assert status["diagnosticsHandoff"]["writeBack"] is False
    assert status["diagnosticsHandoff"]["automaticUpload"] is False


def test_no_private_data_runtime_calls_or_overclaims() -> None:
    module_source = read_text(MODULE_PATH)
    handoff = load_module(
        MODULE_PATH,
        "diagnostics_handoff_contract",
    ).create_diagnostics_handoff_contract()
    scan_text = "\n".join([
        read_text(FIXTURE_PATH),
        read_text(DOC_PATH),
        read_text(STATUS_DOC_PATH),
        read_text(README_PATH),
        flatten(handoff),
        module_source,
    ])

    assert_no_runtime_implementation_terms(module_source)
    assert_no_private_or_generated_data(scan_text)
    assert_no_provider_configs(handoff)
    assert_no_unsupported_claims(scan_text)


def test_docs_reference_pccx_lab_read_only_consumer_without_invocation() -> None:
    docs_text = read_text(DOC_PATH)
    readme_text = read_text(README_PATH)

    assert "pccx-lab diagnostics-handoff validate --file <path> --format json" in docs_text
    assert "matching read-only validation boundary" in docs_text
    assert "This launcher repository does not invoke it" in docs_text
    assert "does not invoke that command" in readme_text


test_handoff_matches_fixture_and_is_deterministic()
test_handoff_shape_and_diagnostic_values()
test_read_only_privacy_and_safety_flags()
test_transport_sketches_are_future_safe()
test_fixture_references_descriptors_without_runtime_coupling()
test_handoff_can_be_referenced_by_launcher_status_contract()
test_no_private_data_runtime_calls_or_overclaims()
test_docs_reference_pccx_lab_read_only_consumer_without_invocation()

print("diagnostics handoff contract tests ok")
