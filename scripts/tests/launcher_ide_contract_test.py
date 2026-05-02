#!/usr/bin/env python3
"""Fixture tests for the launcher/IDE status contract."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "launcher_ide_status_contract.py"
FIXTURE_PATH = ROOT / "contracts" / "fixtures" / "launcher-ide-status.placeholder.json"
DOC_PATH = ROOT / "docs" / "LAUNCHER_IDE_BRIDGE_CONTRACT.md"
README_PATH = ROOT / "README.md"


def load_module():
    spec = importlib.util.spec_from_file_location("launcher_ide_status_contract", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def flatten(value) -> str:
    return json.dumps(value, sort_keys=True)


def assert_no_private_or_generated_data(text: str) -> None:
    forbidden_patterns = [
        r"/home/[^\s\"']+",
        r"/Users/[^\s\"']+",
        r"[A-Za-z]:\\Users\\",
        r"\b(?:api[_-]?key|authorization|bearer|client[_-]?secret|password|private[_-]?key|secret|token)\b\s*[:=]",
        r"\.(?:gguf|safetensors|ckpt|pt|pth|onnx)\b",
        r"(?:weights|model_weights|model-cache)/(?:[^\"'\s]+)",
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
    ]
    lowered = source.lower()
    for term in forbidden:
        assert term not in lowered, term


def assert_no_unsupported_claims(text: str) -> None:
    literal_claims = [
        "production-ready",
        "marketplace-ready",
        "stable API",
        "stable ABI",
        "KV260 inference works",
        "20 tok/s achieved",
        "timing closed",
        "vibe coding",
        "autonomous coding",
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
    ]
    for pattern in asserted_claim_patterns:
        assert not re.search(pattern, text, re.IGNORECASE), pattern


def test_contract_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_launcher_ide_status_contract()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.contract_json(generated) == module.contract_json(generated)
    assert module.contract_json(generated).endswith("\n")
    assert json.loads(module.contract_json(generated)) == fixture


def test_contract_shape_and_status_values() -> None:
    module = load_module()
    contract = module.create_launcher_ide_status_contract()

    assert contract["schemaVersion"] == "pccx.launcherIdeStatus.v0"
    assert contract["launcherMode"] == "placeholder"
    assert contract["configuredTarget"]["id"] == "not_configured"
    assert contract["targetKind"] == "not_configured"
    assert contract["availabilityState"] == "unavailable"
    assert contract["runtimeState"] == "planned"
    assert contract["modelState"] == "not_configured"
    assert contract["evidenceState"] == "evidence_required"
    assert contract["diagnosticsHandoff"]["mode"] == "read_only_handoff"
    assert contract["diagnosticsHandoff"]["lowerBoundary"] == "pccx-lab CLI/core"

    operation_labels = {operation["label"] for operation in contract["supportedOperations"]}
    assert "local launcher status" in operation_labels
    assert "model/runtime descriptor availability" in operation_labels
    assert "device/session status placeholder" in operation_labels
    assert "pccx-lab diagnostics handoff placeholder" in operation_labels
    assert "future editor bridge consumer" in operation_labels
    assert "local coding-assistant mode consumer" in operation_labels

    operation_states = {operation["state"] for operation in contract["supportedOperations"]}
    assert operation_states <= {"planned", "placeholder"}
    assert any(operation.get("execution") == "disabled_by_default" for operation in contract["supportedOperations"])


def test_safety_flags_are_boundary_only() -> None:
    contract = load_module().create_launcher_ide_status_contract()
    flags = contract["safetyFlags"]

    assert flags["dataOnly"] is True
    assert flags["disabledByDefault"] is True
    for name in [
        "executesLauncher",
        "touchesHardware",
        "kv260Access",
        "modelExecution",
        "networkCalls",
        "providerCalls",
        "mcpServerImplemented",
        "lspImplemented",
        "marketplaceFlow",
        "shellExecution",
        "rawLogsIncluded",
        "privatePathsIncluded",
        "secretsIncluded",
        "modelWeightPathsIncluded",
    ]:
        assert flags[name] is False, name


def test_no_private_data_runtime_calls_or_overclaims() -> None:
    module_source = read_text(MODULE_PATH)
    contract = load_module().create_launcher_ide_status_contract()
    contract_text = flatten(contract)
    docs_text = "\n".join([
        read_text(DOC_PATH),
        read_text(README_PATH),
        contract_text,
        module_source,
        read_text(FIXTURE_PATH),
    ])

    assert_no_private_or_generated_data(docs_text)
    assert_no_runtime_implementation_terms(module_source)
    assert_no_unsupported_claims(docs_text)
    assert "future editor integration consumer" in contract_text
    assert "planned" in contract_text
    assert "placeholder" in contract_text
    assert "evidence_required" in contract_text


test_contract_matches_fixture_and_is_deterministic()
test_contract_shape_and_status_values()
test_safety_flags_are_boundary_only()
test_no_private_data_runtime_calls_or_overclaims()

print("launcher/IDE status contract tests ok")
