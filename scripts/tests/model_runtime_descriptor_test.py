#!/usr/bin/env python3
"""Fixture tests for the model/runtime descriptor boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "model_runtime_descriptor_contract.py"
STATUS_MODULE_PATH = ROOT / "contracts" / "launcher_ide_status_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "model-runtime-descriptor.gemma3n-e4b-kv260-placeholder.json"
)
DOC_PATH = ROOT / "docs" / "MODEL_RUNTIME_DESCRIPTOR_BOUNDARY.md"
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
        "/proc/device-tree",
        "xrt",
        "xbutil",
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
        "20 tok/s achieved",
        "timing closed",
        "vibe coding",
        "autonomous coding",
        "model support completed",
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


def test_descriptor_matches_fixture_and_is_deterministic() -> None:
    module = load_module(MODULE_PATH, "model_runtime_descriptor_contract")
    generated = module.create_gemma3n_e4b_kv260_placeholder_example()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.descriptor_json(generated) == module.descriptor_json(generated)
    assert module.descriptor_json(generated).endswith("\n")
    assert json.loads(module.descriptor_json(generated)) == fixture


def test_model_descriptor_schema_shape() -> None:
    module = load_module(MODULE_PATH, "model_runtime_descriptor_contract")
    descriptor = module.create_gemma3n_e4b_model_descriptor()

    assert tuple(descriptor.keys()) == module.MODEL_DESCRIPTOR_FIELDS
    assert descriptor["schemaVersion"] == "pccx.modelDescriptor.v0"
    assert descriptor["modelId"] == "gemma3n_e4b_placeholder"
    assert descriptor["modelFamily"] == "gemma3n"
    assert descriptor["modelVariant"] == "e4b"
    assert descriptor["parameterScale"] == "e4b"
    assert descriptor["tokenizerKind"] == "gemma3n_placeholder"
    assert descriptor["weightFormat"] == "external_user_provided"
    assert descriptor["weightLocationKind"] == "external_user_provided"
    assert descriptor["weightPresence"] == "not_bundled"
    assert descriptor["loadState"] == "not_loaded"
    assert descriptor["measurementState"] == "not_measured"
    assert descriptor["evidenceState"] == "evidence_required"
    assert descriptor["quantization"]["state"] == "not_measured"
    assert descriptor["quantization"]["execution"] == "descriptor_only"
    assert "kv260_pccx_placeholder" in descriptor["expectedRuntimeKinds"]
    assert "cpu_reference_placeholder" in descriptor["expectedRuntimeKinds"]


def test_runtime_descriptor_schema_shape() -> None:
    module = load_module(MODULE_PATH, "model_runtime_descriptor_contract")
    descriptor = module.create_kv260_pccx_runtime_descriptor()

    assert tuple(descriptor.keys()) == module.RUNTIME_DESCRIPTOR_FIELDS
    assert descriptor["schemaVersion"] == "pccx.runtimeDescriptor.v0"
    assert descriptor["runtimeId"] == "kv260_pccx_placeholder"
    assert descriptor["runtimeKind"] == "kv260_pccx_placeholder"
    assert descriptor["targetKind"] == "kv260"
    assert descriptor["targetDevice"]["id"] == "kv260_pccx_placeholder"
    assert descriptor["targetDevice"]["configurationState"] == "not_configured"
    assert descriptor["acceleratorKind"] == "planned"
    assert descriptor["availabilityState"] == "unavailable"
    assert descriptor["configurationState"] == "not_configured"
    assert descriptor["supportedModelFamilies"] == ["gemma3n"]

    lifecycle = descriptor["lifecycleStates"]
    assert [state["state"] for state in lifecycle] == ["load", "warm", "run", "unload"]
    assert {state["supportState"] for state in lifecycle} == {"planned"}
    assert {state["execution"] for state in lifecycle} == {"descriptor_only"}

    status_checks = {check["checkId"]: check for check in descriptor["statusChecks"]}
    assert status_checks["hardware_access"]["execution"] == "no_hardware_access"
    assert status_checks["runtime_execution"]["execution"] == "no_runtime_execution"


def test_resolver_compatibility_result() -> None:
    module = load_module(MODULE_PATH, "model_runtime_descriptor_contract")
    model = module.create_gemma3n_e4b_model_descriptor()
    runtime = module.create_kv260_pccx_runtime_descriptor()
    result = module.resolve_model_runtime_compatibility(model, runtime)

    assert tuple(result.keys()) == module.COMPATIBILITY_RESULT_FIELDS
    assert result == module.resolve_model_runtime_compatibility(model, runtime)
    assert result["schemaVersion"] == "pccx.modelRuntimeCompatibility.v0"
    assert result["compatible"] is False
    assert result["compatibilityState"] == "provisional"
    assert result["reason"] == "descriptor_match_evidence_required"
    assert result["nextActionKind"] == "collect_evidence_before_runtime_claim"
    assert "external_user_provided_model_assets" in result["missingArtifacts"]
    assert "runtime_adapter" in result["missingArtifacts"]
    assert "kv260_hardware_evidence" in result["missingArtifacts"]
    assert "measurement_evidence" in result["missingArtifacts"]
    assert "descriptor_only" in result["warnings"]
    assert "no_runtime_execution" in result["warnings"]
    assert "no_hardware_access" in result["warnings"]
    assert "compatibility_is_provisional" in result["warnings"]

    mismatch = copy.deepcopy(runtime)
    mismatch["supportedModelFamilies"] = ["other_family"]
    mismatch_result = module.resolve_model_runtime_compatibility(model, mismatch)
    assert mismatch_result["compatible"] is False
    assert mismatch_result["compatibilityState"] == "not_compatible"
    assert mismatch_result["reason"] == "model_family_not_supported"


def test_no_bundled_weights_private_paths_secrets_or_provider_configs() -> None:
    module = load_module(MODULE_PATH, "model_runtime_descriptor_contract")
    example = module.create_gemma3n_e4b_kv260_placeholder_example()
    fixture_text = read_text(FIXTURE_PATH)
    source_text = read_text(MODULE_PATH)

    model = example["modelDescriptor"]
    runtime = example["runtimeDescriptor"]
    assert model["weightLocationKind"] == "external_user_provided"
    assert model["weightPresence"] == "not_bundled"
    assert model["loadState"] == "not_loaded"
    assert model["safetyFlags"]["weightsBundled"] is False
    assert model["safetyFlags"]["modelWeightPathsIncluded"] is False
    assert runtime["requiredArtifacts"][0]["locationKind"] == "external_user_provided"
    assert runtime["requiredArtifacts"][0]["presence"] == "not_bundled"
    assert runtime["safetyFlags"]["modelWeightPathsIncluded"] is False

    assert_no_private_or_generated_data("\n".join([fixture_text, source_text]))
    assert_no_provider_configs(example)


def test_no_runtime_execution_hardware_access_or_unsupported_claims() -> None:
    module = load_module(MODULE_PATH, "model_runtime_descriptor_contract")
    example = module.create_gemma3n_e4b_kv260_placeholder_example()
    source_text = read_text(MODULE_PATH)
    scan_text = "\n".join([
        read_text(FIXTURE_PATH),
        read_text(DOC_PATH),
        read_text(README_PATH),
        flatten(example),
        source_text,
    ])

    assert_no_runtime_implementation_terms(source_text)
    assert_no_private_or_generated_data(scan_text)
    assert_no_unsupported_claims(scan_text)

    model_flags = example["modelDescriptor"]["safetyFlags"]
    runtime_flags = example["runtimeDescriptor"]["safetyFlags"]
    reference = example["launcherIdeStatusReference"]
    assert model_flags["modelExecution"] is False
    assert runtime_flags["runtimeExecution"] is False
    assert runtime_flags["touchesHardware"] is False
    assert runtime_flags["kv260Access"] is False
    assert runtime_flags["shellExecution"] is False
    assert runtime_flags["providerCalls"] is False
    assert runtime_flags["networkCalls"] is False
    assert reference["executesRuntime"] is False
    assert reference["touchesHardware"] is False


def test_gemma3n_e4b_kv260_placeholder_is_not_measured() -> None:
    module = load_module(MODULE_PATH, "model_runtime_descriptor_contract")
    example = module.create_gemma3n_e4b_kv260_placeholder_example()

    assert example["modelDescriptor"]["modelId"] == "gemma3n_e4b_placeholder"
    assert example["runtimeDescriptor"]["runtimeId"] == "kv260_pccx_placeholder"
    assert example["modelDescriptor"]["measurementState"] == "not_measured"
    assert example["modelDescriptor"]["quantization"]["state"] == "not_measured"
    assert example["runtimeDescriptor"]["availabilityState"] == "unavailable"
    assert example["runtimeDescriptor"]["configurationState"] == "not_configured"
    assert example["compatibility"]["compatible"] is False
    assert example["compatibility"]["compatibilityState"] == "provisional"
    assert "no_performance_measurement" in example["compatibility"]["warnings"]


def test_descriptor_reference_matches_launcher_ide_status_without_coupling() -> None:
    descriptor_module = load_module(MODULE_PATH, "model_runtime_descriptor_contract")
    status_module = load_module(STATUS_MODULE_PATH, "launcher_ide_status_contract")
    status_contract = status_module.create_launcher_ide_status_contract()
    reference = descriptor_module.create_gemma3n_e4b_kv260_placeholder_example()[
        "launcherIdeStatusReference"
    ]

    operation_ids = {operation["id"] for operation in status_contract["supportedOperations"]}
    assert reference["operationId"] == "model.runtime.descriptor"
    assert reference["operationId"] in operation_ids
    assert reference["coupling"] == "data_reference_only"
    assert reference["referenceKind"] == "descriptor_only"
    assert reference["executesRuntime"] is False
    assert reference["touchesHardware"] is False

    status_source = read_text(STATUS_MODULE_PATH)
    assert "model_runtime_descriptor_contract" not in status_source
    assert status_contract["safetyFlags"]["modelExecution"] is False
    assert status_contract["safetyFlags"]["touchesHardware"] is False


test_descriptor_matches_fixture_and_is_deterministic()
test_model_descriptor_schema_shape()
test_runtime_descriptor_schema_shape()
test_resolver_compatibility_result()
test_no_bundled_weights_private_paths_secrets_or_provider_configs()
test_no_runtime_execution_hardware_access_or_unsupported_claims()
test_gemma3n_e4b_kv260_placeholder_is_not_measured()
test_descriptor_reference_matches_launcher_ide_status_without_coupling()

print("model/runtime descriptor tests ok")
