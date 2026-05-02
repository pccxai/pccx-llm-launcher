#!/usr/bin/env python3
"""Data-only diagnostics handoff contract placeholder.

The contract describes a future read-only handoff from pccx-llm-launcher
to pccx-lab. It does not execute pccx-lab, start launcher runtime code,
probe hardware, load models, call providers, or write artifacts.
"""

from __future__ import annotations

import copy
import json
import sys


SCHEMA_VERSION = "pccx.diagnosticsHandoff.v0"

HANDOFF_FIELDS = (
    "schemaVersion",
    "handoffId",
    "handoffKind",
    "producer",
    "consumer",
    "createdAt",
    "sessionId",
    "launcherStatusRef",
    "modelDescriptorRef",
    "runtimeDescriptorRef",
    "targetKind",
    "targetDevice",
    "diagnostics",
    "evidenceRefs",
    "artifactRefs",
    "privacyFlags",
    "safetyFlags",
    "transport",
    "limitations",
    "issueRefs",
)

DIAGNOSTIC_ITEM_FIELDS = (
    "diagnosticId",
    "severity",
    "category",
    "source",
    "title",
    "summary",
    "relatedContractRefs",
    "suggestedNextAction",
    "evidenceState",
    "redactionState",
)

SEVERITY_VALUES = (
    "info",
    "warning",
    "blocked",
    "error",
)

CATEGORY_VALUES = (
    "configuration",
    "model_descriptor",
    "runtime_descriptor",
    "target_device",
    "evidence",
    "safety",
    "diagnostics_handoff",
)

_DIAGNOSTICS_HANDOFF = {
    "schemaVersion": SCHEMA_VERSION,
    "handoffId": "launcher_diagnostics_handoff_gemma3n_e4b_kv260_placeholder",
    "handoffKind": "read_only_handoff",
    "producer": {
        "id": "pccx-llm-launcher",
        "role": "launcher_generated_summary",
        "execution": "data_only",
    },
    "consumer": {
        "id": "pccx-lab",
        "role": "pccx_lab_future_consumer",
        "boundary": "cli_core_future_consumer",
        "state": "planned",
    },
    "createdAt": "1970-01-01T00:00:00Z",
    "sessionId": "placeholder_session",
    "launcherStatusRef": {
        "schemaVersion": "pccx.launcherIdeStatus.v0",
        "fixture": "contracts/fixtures/launcher-ide-status.placeholder.json",
        "operationId": "pccxlab.diagnostics.handoff",
        "referenceKind": "descriptor_ref_only",
        "coupling": "data_reference_only",
    },
    "modelDescriptorRef": {
        "schemaVersion": "pccx.modelDescriptor.v0",
        "fixture": "contracts/fixtures/model-runtime-descriptor.gemma3n-e4b-kv260-placeholder.json",
        "modelId": "gemma3n_e4b_placeholder",
        "referenceKind": "descriptor_ref_only",
    },
    "runtimeDescriptorRef": {
        "schemaVersion": "pccx.runtimeDescriptor.v0",
        "fixture": "contracts/fixtures/model-runtime-descriptor.gemma3n-e4b-kv260-placeholder.json",
        "runtimeId": "kv260_pccx_placeholder",
        "referenceKind": "descriptor_ref_only",
    },
    "targetKind": "kv260",
    "targetDevice": {
        "id": "kv260_pccx_placeholder",
        "label": "KV260 PCCX placeholder",
        "configurationState": "not_configured",
        "accessState": "no_hardware_access",
    },
    "diagnostics": [
        {
            "diagnosticId": "launcher_target_not_configured",
            "severity": "warning",
            "category": "configuration",
            "source": "pccx-llm-launcher",
            "title": "Launcher target is not configured",
            "summary": "The handoff records a placeholder target state only.",
            "relatedContractRefs": [
                "pccx.launcherIdeStatus.v0",
            ],
            "suggestedNextAction": "Keep the handoff read-only until target configuration evidence exists.",
            "evidenceState": "evidence_required",
            "redactionState": "sanitized_summary",
        },
        {
            "diagnosticId": "gemma3n_e4b_descriptor_reference_only",
            "severity": "info",
            "category": "model_descriptor",
            "source": "pccx-llm-launcher",
            "title": "Model descriptor is referenced by id",
            "summary": "Gemma 3N E4B is represented as descriptor_ref_only with no bundled assets.",
            "relatedContractRefs": [
                "pccx.modelDescriptor.v0",
            ],
            "suggestedNextAction": "Collect descriptor and asset evidence before runtime claims.",
            "evidenceState": "evidence_required",
            "redactionState": "sanitized_summary",
        },
        {
            "diagnosticId": "kv260_runtime_placeholder_not_configured",
            "severity": "blocked",
            "category": "runtime_descriptor",
            "source": "pccx-llm-launcher",
            "title": "KV260 runtime remains placeholder",
            "summary": "The runtime descriptor is planned, unavailable, and not configured.",
            "relatedContractRefs": [
                "pccx.runtimeDescriptor.v0",
                "pccx.modelRuntimeCompatibility.v0",
            ],
            "suggestedNextAction": "Require pccx-lab/core evidence before enabling runtime integration.",
            "evidenceState": "evidence_required",
            "redactionState": "sanitized_summary",
        },
        {
            "diagnosticId": "hardware_and_measurement_evidence_missing",
            "severity": "blocked",
            "category": "evidence",
            "source": "pccx-llm-launcher",
            "title": "Hardware and measurement evidence are missing",
            "summary": "Compatibility stays provisional until checked evidence exists.",
            "relatedContractRefs": [
                "pccx.modelRuntimeCompatibility.v0",
            ],
            "suggestedNextAction": "Treat all hardware and performance claims as not measured.",
            "evidenceState": "not_measured",
            "redactionState": "sanitized_summary",
        },
        {
            "diagnosticId": "read_only_privacy_boundary",
            "severity": "info",
            "category": "safety",
            "source": "pccx-llm-launcher",
            "title": "Read-only privacy boundary is active",
            "summary": "The fixture carries no telemetry, upload, write-back, raw logs, prompts, or private paths.",
            "relatedContractRefs": [
                "pccx.diagnosticsHandoff.v0",
            ],
            "suggestedNextAction": "Keep future consumer behavior explicit and opt-in.",
            "evidenceState": "placeholder",
            "redactionState": "sanitized_summary",
        },
    ],
    "evidenceRefs": [
        {
            "evidenceId": "model_descriptor_evidence",
            "state": "evidence_required",
            "referenceKind": "descriptor_ref_only",
        },
        {
            "evidenceId": "kv260_hardware_evidence",
            "state": "evidence_required",
            "referenceKind": "descriptor_ref_only",
        },
        {
            "evidenceId": "measurement_evidence",
            "state": "not_measured",
            "referenceKind": "descriptor_ref_only",
        },
    ],
    "artifactRefs": [
        {
            "artifactId": "launcher_status_contract_fixture",
            "artifactKind": "json_fixture",
            "reference": "contracts/fixtures/launcher-ide-status.placeholder.json",
            "referenceKind": "read_only_local_artifact_reference",
        },
        {
            "artifactId": "model_runtime_descriptor_fixture",
            "artifactKind": "json_fixture",
            "reference": "contracts/fixtures/model-runtime-descriptor.gemma3n-e4b-kv260-placeholder.json",
            "referenceKind": "read_only_local_artifact_reference",
        },
    ],
    "privacyFlags": {
        "uploadPolicy": "no_user_data_upload",
        "telemetryPolicy": "no_telemetry",
        "automaticUpload": False,
        "rawFullLogsIncluded": False,
        "userPromptsIncluded": False,
        "userSourceCodeIncluded": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
        "providerConfigsIncluded": False,
        "modelWeightPathsIncluded": False,
        "generatedBlobsIncluded": False,
    },
    "safetyFlags": {
        "contractKind": "read_only_handoff",
        "descriptorPolicy": "descriptor_ref_only",
        "writeBackPolicy": "no_auto_writeback",
        "runtimePolicy": "no_runtime_execution",
        "hardwarePolicy": "no_hardware_access",
        "evidencePolicy": "evidence_required",
        "dataOnly": True,
        "readOnly": True,
        "executesPccxLab": False,
        "executesLauncher": False,
        "runtimeExecution": False,
        "touchesHardware": False,
        "kv260Access": False,
        "modelExecution": False,
        "networkCalls": False,
        "providerCalls": False,
        "shellExecution": False,
        "mcpServerImplemented": False,
        "lspImplemented": False,
        "marketplaceFlow": False,
        "telemetry": False,
        "automaticUpload": False,
        "writeBack": False,
    },
    "transport": [
        {
            "transportKind": "json_file",
            "state": "sketch",
            "direction": "launcher_to_pccx_lab_future_consumer",
            "mode": "read_only_handoff",
            "execution": "no_pccx_lab_execution",
        },
        {
            "transportKind": "stdout_json",
            "state": "sketch",
            "direction": "launcher_to_pccx_lab_future_consumer",
            "mode": "read_only_handoff",
            "execution": "no_pccx_lab_execution",
        },
        {
            "transportKind": "read_only_local_artifact_reference",
            "state": "sketch",
            "direction": "launcher_to_pccx_lab_future_consumer",
            "mode": "read_only_handoff",
            "execution": "no_pccx_lab_execution",
        },
    ],
    "limitations": [
        "Data-only placeholder; no pccx-lab execution is performed.",
        "No launcher runtime execution, model execution, provider call, or network call is performed.",
        "No KV260 hardware access is performed.",
        "No telemetry, automatic upload, or auto write-back is included.",
        "No raw full logs, prompts, source code, private paths, secrets, tokens, provider configuration, generated blobs, or model weight paths are included.",
        "The contract is not a versioned compatibility commitment.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#5",
        "pccxai/pccx-llm-launcher#3",
        "pccxai/pccx-llm-launcher#12",
    ],
}


def create_diagnostics_handoff_contract() -> dict:
    """Return a defensive copy of the placeholder handoff contract."""
    return copy.deepcopy(_DIAGNOSTICS_HANDOFF)


def handoff_json(handoff: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        handoff if handoff is not None else create_diagnostics_handoff_contract(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def main() -> int:
    sys.stdout.write(handoff_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
