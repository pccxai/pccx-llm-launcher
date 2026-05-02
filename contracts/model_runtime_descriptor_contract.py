#!/usr/bin/env python3
"""Data-only model/runtime descriptor contract placeholder.

The contract describes model and runtime vocabulary for future launcher
integration work. It does not load model assets, inspect devices, execute
runtime commands, read local paths, or call providers.
"""

from __future__ import annotations

import copy
import json
import sys


MODEL_SCHEMA_VERSION = "pccx.modelDescriptor.v0"
RUNTIME_SCHEMA_VERSION = "pccx.runtimeDescriptor.v0"
COMPATIBILITY_SCHEMA_VERSION = "pccx.modelRuntimeCompatibility.v0"
EXAMPLE_SCHEMA_VERSION = "pccx.modelRuntimeDescriptorExample.v0"

MODEL_DESCRIPTOR_FIELDS = (
    "schemaVersion",
    "modelId",
    "modelFamily",
    "modelVariant",
    "parameterScale",
    "tokenizerKind",
    "weightFormat",
    "weightLocationKind",
    "weightPresence",
    "loadState",
    "quantization",
    "expectedRuntimeKinds",
    "measurementState",
    "evidenceState",
    "limitations",
    "safetyFlags",
)

RUNTIME_DESCRIPTOR_FIELDS = (
    "schemaVersion",
    "runtimeId",
    "runtimeKind",
    "targetKind",
    "targetDevice",
    "acceleratorKind",
    "availabilityState",
    "configurationState",
    "lifecycleStates",
    "supportedModelFamilies",
    "requiredArtifacts",
    "statusChecks",
    "evidenceRequirements",
    "compatibilityNotes",
    "safetyFlags",
)

COMPATIBILITY_RESULT_FIELDS = (
    "schemaVersion",
    "modelId",
    "runtimeId",
    "compatible",
    "compatibilityState",
    "reason",
    "requiredEvidence",
    "missingArtifacts",
    "warnings",
    "nextActionKind",
)

_GEMMA3N_E4B_MODEL_DESCRIPTOR = {
    "schemaVersion": MODEL_SCHEMA_VERSION,
    "modelId": "gemma3n_e4b_placeholder",
    "modelFamily": "gemma3n",
    "modelVariant": "e4b",
    "parameterScale": "e4b",
    "tokenizerKind": "gemma3n_placeholder",
    "weightFormat": "external_user_provided",
    "weightLocationKind": "external_user_provided",
    "weightPresence": "not_bundled",
    "loadState": "not_loaded",
    "quantization": {
        "kind": "planned",
        "state": "not_measured",
        "execution": "descriptor_only",
    },
    "expectedRuntimeKinds": [
        "kv260_pccx_placeholder",
        "cpu_reference_placeholder",
    ],
    "measurementState": "not_measured",
    "evidenceState": "evidence_required",
    "limitations": [
        "Descriptor only; no model assets are bundled.",
        "Model assets are expected to be external/user-provided.",
        "No model load or runtime execution is performed.",
        "Performance and hardware evidence are required before stronger claims.",
    ],
    "safetyFlags": {
        "dataOnly": True,
        "descriptorOnly": True,
        "weightsBundled": False,
        "modelLoaded": False,
        "modelExecution": False,
        "modelWeightPathsIncluded": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "providerCalls": False,
        "networkCalls": False,
    },
}

_KV260_PCCX_RUNTIME_DESCRIPTOR = {
    "schemaVersion": RUNTIME_SCHEMA_VERSION,
    "runtimeId": "kv260_pccx_placeholder",
    "runtimeKind": "kv260_pccx_placeholder",
    "targetKind": "kv260",
    "targetDevice": {
        "id": "kv260_pccx_placeholder",
        "label": "KV260 PCCX placeholder",
        "configurationState": "not_configured",
    },
    "acceleratorKind": "planned",
    "availabilityState": "unavailable",
    "configurationState": "not_configured",
    "lifecycleStates": [
        {
            "state": "load",
            "supportState": "planned",
            "execution": "descriptor_only",
        },
        {
            "state": "warm",
            "supportState": "planned",
            "execution": "descriptor_only",
        },
        {
            "state": "run",
            "supportState": "planned",
            "execution": "descriptor_only",
        },
        {
            "state": "unload",
            "supportState": "planned",
            "execution": "descriptor_only",
        },
    ],
    "supportedModelFamilies": [
        "gemma3n",
    ],
    "requiredArtifacts": [
        {
            "artifactKind": "model_assets",
            "locationKind": "external_user_provided",
            "presence": "not_bundled",
        },
        {
            "artifactKind": "runtime_adapter",
            "locationKind": "future_launcher_runtime_integration",
            "presence": "planned",
        },
        {
            "artifactKind": "kv260_hardware_evidence",
            "locationKind": "future_pccx_lab_or_core_handoff",
            "presence": "evidence_required",
        },
        {
            "artifactKind": "measurement_evidence",
            "locationKind": "future_pccx_lab_or_core_handoff",
            "presence": "not_measured",
        },
    ],
    "statusChecks": [
        {
            "checkId": "target_configuration",
            "state": "not_configured",
            "execution": "descriptor_only",
        },
        {
            "checkId": "hardware_access",
            "state": "unavailable",
            "execution": "no_hardware_access",
        },
        {
            "checkId": "runtime_execution",
            "state": "unavailable",
            "execution": "no_runtime_execution",
        },
    ],
    "evidenceRequirements": [
        "external_user_provided_model_assets",
        "runtime_adapter_integration_evidence",
        "kv260_hardware_evidence",
        "measurement_evidence",
    ],
    "compatibilityNotes": [
        "Gemma 3N E4B is represented as a descriptor target only.",
        "The KV260 PCCX runtime path is planned and not configured.",
        "Compatibility is provisional until evidence exists.",
    ],
    "safetyFlags": {
        "dataOnly": True,
        "descriptorOnly": True,
        "touchesHardware": False,
        "kv260Access": False,
        "runtimeExecution": False,
        "modelExecution": False,
        "providerCalls": False,
        "networkCalls": False,
        "shellExecution": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "modelWeightPathsIncluded": False,
    },
}


def create_gemma3n_e4b_model_descriptor() -> dict:
    """Return a defensive copy of the Gemma 3N E4B placeholder descriptor."""
    return copy.deepcopy(_GEMMA3N_E4B_MODEL_DESCRIPTOR)


def create_kv260_pccx_runtime_descriptor() -> dict:
    """Return a defensive copy of the KV260 PCCX placeholder descriptor."""
    return copy.deepcopy(_KV260_PCCX_RUNTIME_DESCRIPTOR)


def _unique_ordered(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _artifact_is_missing(artifact: dict) -> bool:
    return artifact.get("presence") in {
        "not_bundled",
        "not_loaded",
        "not_measured",
        "planned",
        "evidence_required",
        "not_configured",
        "unavailable",
    }


def _missing_artifacts(model_descriptor: dict, runtime_descriptor: dict) -> list[str]:
    missing = []
    if model_descriptor.get("weightPresence") in {"not_bundled", "not_loaded"}:
        missing.append("external_user_provided_model_assets")

    for artifact in runtime_descriptor.get("requiredArtifacts", []):
        if _artifact_is_missing(artifact):
            missing.append(str(artifact.get("artifactKind", "unknown_artifact")))

    return _unique_ordered(missing)


def _required_evidence(model_descriptor: dict, runtime_descriptor: dict) -> list[str]:
    required = []
    if model_descriptor.get("evidenceState") == "evidence_required":
        required.append("model_descriptor_evidence")
    if model_descriptor.get("measurementState") == "not_measured":
        required.append("measurement_evidence")
    required.extend(
        str(item) for item in runtime_descriptor.get("evidenceRequirements", [])
    )
    return _unique_ordered(required)


def resolve_model_runtime_compatibility(
    model_descriptor: dict,
    runtime_descriptor: dict,
) -> dict:
    """Return a deterministic, data-only compatibility sketch.

    The resolver only compares descriptor values supplied by the caller.
    It does not inspect hardware, paths, model files, commands, networks,
    provider settings, or generated caches.
    """
    model_family = model_descriptor.get("modelFamily")
    runtime_kind = runtime_descriptor.get("runtimeKind")
    runtime_id = runtime_descriptor.get("runtimeId")
    expected_runtime_kinds = set(model_descriptor.get("expectedRuntimeKinds", []))
    supported_model_families = set(runtime_descriptor.get("supportedModelFamilies", []))

    family_match = model_family in supported_model_families
    runtime_match = runtime_kind in expected_runtime_kinds or runtime_id in expected_runtime_kinds
    missing_artifacts = _missing_artifacts(model_descriptor, runtime_descriptor)
    required_evidence = _required_evidence(model_descriptor, runtime_descriptor)

    unavailable = runtime_descriptor.get("availabilityState") != "available"
    not_configured = runtime_descriptor.get("configurationState") != "configured"
    not_measured = model_descriptor.get("measurementState") == "not_measured"
    evidence_required = bool(required_evidence)

    if not family_match:
        compatibility_state = "not_compatible"
        reason = "model_family_not_supported"
        next_action_kind = "choose_matching_descriptor"
    elif not runtime_match:
        compatibility_state = "not_compatible"
        reason = "runtime_kind_not_expected"
        next_action_kind = "choose_matching_descriptor"
    elif missing_artifacts or unavailable or not_configured or not_measured or evidence_required:
        compatibility_state = "provisional"
        reason = "descriptor_match_evidence_required"
        next_action_kind = "collect_evidence_before_runtime_claim"
    else:
        compatibility_state = "compatible"
        reason = "descriptor_match_with_evidence"
        next_action_kind = "ready_for_future_runtime_integration"

    compatible = compatibility_state == "compatible"
    warnings = [
        "descriptor_only",
        "no_runtime_execution",
        "no_hardware_access",
        "no_performance_measurement",
    ]
    if compatibility_state == "provisional":
        warnings.append("compatibility_is_provisional")

    return {
        "schemaVersion": COMPATIBILITY_SCHEMA_VERSION,
        "modelId": model_descriptor.get("modelId", "unknown_model"),
        "runtimeId": runtime_descriptor.get("runtimeId", "unknown_runtime"),
        "compatible": compatible,
        "compatibilityState": compatibility_state,
        "reason": reason,
        "requiredEvidence": required_evidence,
        "missingArtifacts": missing_artifacts,
        "warnings": warnings,
        "nextActionKind": next_action_kind,
    }


def create_launcher_ide_status_descriptor_reference(
    model_descriptor: dict | None = None,
    runtime_descriptor: dict | None = None,
    compatibility_result: dict | None = None,
) -> dict:
    """Return a data-only reference usable by the launcher/IDE status contract."""
    model = (
        model_descriptor
        if model_descriptor is not None
        else create_gemma3n_e4b_model_descriptor()
    )
    runtime = (
        runtime_descriptor
        if runtime_descriptor is not None
        else create_kv260_pccx_runtime_descriptor()
    )
    compatibility = (
        compatibility_result
        if compatibility_result is not None
        else resolve_model_runtime_compatibility(model, runtime)
    )

    return {
        "operationId": "model.runtime.descriptor",
        "referenceKind": "descriptor_only",
        "schemaVersion": EXAMPLE_SCHEMA_VERSION,
        "modelId": model["modelId"],
        "runtimeId": runtime["runtimeId"],
        "compatibilityState": compatibility["compatibilityState"],
        "evidenceState": model["evidenceState"],
        "coupling": "data_reference_only",
        "executesRuntime": False,
        "touchesHardware": False,
    }


def create_gemma3n_e4b_kv260_placeholder_example() -> dict:
    """Return the checked Gemma 3N E4B + KV260 descriptor example."""
    model = create_gemma3n_e4b_model_descriptor()
    runtime = create_kv260_pccx_runtime_descriptor()
    compatibility = resolve_model_runtime_compatibility(model, runtime)

    return {
        "schemaVersion": EXAMPLE_SCHEMA_VERSION,
        "exampleId": "gemma3n_e4b_kv260_pccx_placeholder",
        "modelDescriptor": model,
        "runtimeDescriptor": runtime,
        "compatibility": compatibility,
        "launcherIdeStatusReference": create_launcher_ide_status_descriptor_reference(
            model,
            runtime,
            compatibility,
        ),
        "issueRefs": [
            "pccxai/pccx-llm-launcher#3",
            "pccxai/pccx-llm-launcher#5",
            "pccxai/pccx-llm-launcher#12",
        ],
    }


def descriptor_json(descriptor: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        descriptor if descriptor is not None else create_gemma3n_e4b_kv260_placeholder_example(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def main() -> int:
    sys.stdout.write(descriptor_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
