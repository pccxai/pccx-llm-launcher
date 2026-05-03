#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat model status contract for the planned launcher UI.

The contract describes the model-status display and blocked model-load state
for the local chat surface without loading weights, starting runtime code,
touching KV260 hardware, calling providers, invoking pccx-lab, or writing
artifacts.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatModelStatus.v0"

CHAT_MODEL_STATUS_FIELDS = (
    "schemaVersion",
    "statusId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "displayState",
    "modelSelectionState",
    "descriptorState",
    "assetState",
    "loadState",
    "runtimeState",
    "contextState",
    "responseState",
    "providerState",
    "statusRows",
    "loadActions",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

STATUS_ROW_FIELDS = (
    "rowId",
    "label",
    "state",
    "severity",
    "summary",
    "displayPolicy",
)

LOAD_ACTION_FIELDS = (
    "actionId",
    "label",
    "state",
    "enabled",
    "userAction",
    "launcherAction",
    "requiredEvidence",
    "sideEffectPolicy",
)

BLOCKED_REASON_FIELDS = (
    "reasonId",
    "state",
    "summary",
    "requiredBefore",
)

HANDOFF_REF_FIELDS = (
    "refId",
    "schemaVersion",
    "fixturePath",
    "state",
    "summary",
)

CHAT_MODEL_STATUS_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "external_not_configured",
    "inactive",
    "not_loaded",
    "not_started",
    "not_used",
    "placeholder",
    "planned",
    "target_selected",
    "unavailable",
)

_CHAT_MODEL_STATUS = {
    "schemaVersion": SCHEMA_VERSION,
    "statusId": "chat_model_status_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-model-status.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_model_status_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "displayState": "blocked",
    "modelSelectionState": "target_selected",
    "descriptorState": "available_as_data",
    "assetState": "external_not_configured",
    "loadState": "blocked",
    "runtimeState": "not_started",
    "contextState": "unavailable",
    "responseState": "unavailable",
    "providerState": "not_used",
    "statusRows": [
        {
            "rowId": "model_descriptor",
            "label": "model descriptor",
            "state": "available_as_data",
            "severity": "info",
            "summary": "Gemma 3N E4B is represented by the checked descriptor fixture only.",
            "displayPolicy": "show descriptor id and target label without model paths",
        },
        {
            "rowId": "model_assets",
            "label": "model assets",
            "state": "external_not_configured",
            "severity": "blocked",
            "summary": "Model assets are user-provided future inputs and are not configured here.",
            "displayPolicy": "show blocked state without local paths or filenames",
        },
        {
            "rowId": "runtime_readiness",
            "label": "runtime readiness",
            "state": "blocked",
            "severity": "blocked",
            "summary": "Runtime readiness remains blocked and not yet evidence-backed.",
            "displayPolicy": "show conservative readiness summary only",
        },
        {
            "rowId": "device_session",
            "label": "device session",
            "state": "inactive",
            "severity": "blocked",
            "summary": "No KV260 target session exists in this fixture.",
            "displayPolicy": "show inactive target state without probing hardware",
        },
        {
            "rowId": "load_operation",
            "label": "load operation",
            "state": "disabled",
            "severity": "blocked",
            "summary": "Model load controls stay disabled until readiness evidence exists.",
            "displayPolicy": "show disabled action state only",
        },
        {
            "rowId": "chat_context",
            "label": "chat context",
            "state": "unavailable",
            "severity": "blocked",
            "summary": "No runtime context window or token state exists.",
            "displayPolicy": "show unavailable context state without token data",
        },
        {
            "rowId": "assistant_response",
            "label": "assistant response",
            "state": "unavailable",
            "severity": "blocked",
            "summary": "No response can be generated because no model runtime is active.",
            "displayPolicy": "show response unavailable state only",
        },
    ],
    "loadActions": [
        {
            "actionId": "select_model_target",
            "label": "select model target",
            "state": "target_selected",
            "enabled": False,
            "userAction": "Review the target model descriptor in the future chat UI.",
            "launcherAction": "Render target metadata from checked fixtures only.",
            "requiredEvidence": [
                "descriptor_fixture_available",
            ],
            "sideEffectPolicy": "local_render_only",
        },
        {
            "actionId": "configure_model_assets",
            "label": "configure model assets",
            "state": "blocked",
            "enabled": False,
            "userAction": "Provide model assets only after a reviewed local input boundary exists.",
            "launcherAction": "Do not read or echo local asset paths.",
            "requiredEvidence": [
                "local_model_asset_input_boundary_reviewed",
                "redaction_policy_reviewed",
            ],
            "sideEffectPolicy": "no_artifact_read_no_write",
        },
        {
            "actionId": "load_model",
            "label": "load model",
            "state": "disabled",
            "enabled": False,
            "userAction": "Load only after runtime readiness and model asset checks are evidence-backed.",
            "launcherAction": "Refuse model load while runtime readiness is blocked.",
            "requiredEvidence": [
                "runtime_readiness_available",
                "model_assets_configured",
                "kv260_session_available",
            ],
            "sideEffectPolicy": "no_runtime_execution",
        },
        {
            "actionId": "refresh_status",
            "label": "refresh status",
            "state": "available_as_data",
            "enabled": False,
            "userAction": "Refresh the model status display from checked local fixtures.",
            "launcherAction": "Render deterministic fixture data only.",
            "requiredEvidence": [
                "checked_fixture_data_available",
            ],
            "sideEffectPolicy": "read_only_data",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "runtime_readiness_blocked",
            "state": "blocked",
            "summary": "Runtime readiness remains blocked for the Gemma 3N E4B plus KV260 target.",
            "requiredBefore": "load_model_enabled",
        },
        {
            "reasonId": "model_assets_external",
            "state": "external_not_configured",
            "summary": "Model assets are external and no reviewed local asset input boundary exists.",
            "requiredBefore": "configure_model_assets_enabled",
        },
        {
            "reasonId": "kv260_session_inactive",
            "state": "inactive",
            "summary": "No target device session exists and no board runtime status is measured.",
            "requiredBefore": "load_model_enabled",
        },
        {
            "reasonId": "chat_runtime_not_started",
            "state": "not_started",
            "summary": "The local chat runtime is not implemented or started.",
            "requiredBefore": "assistant_response_available",
        },
    ],
    "handoffRefs": [
        {
            "refId": "model_runtime_descriptor",
            "schemaVersion": "pccx.modelRuntimeDescriptorBundle.v0",
            "fixturePath": "contracts/fixtures/model-runtime-descriptor.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Model/runtime descriptor data is consumed by reference only.",
        },
        {
            "refId": "runtime_readiness",
            "schemaVersion": "pccx.runtimeReadiness.v0",
            "fixturePath": "contracts/fixtures/runtime-readiness.gemma3n-e4b-kv260.json",
            "state": "blocked",
            "summary": "Runtime readiness is consumed as local data only.",
        },
        {
            "refId": "device_session_status",
            "schemaVersion": "pccx.deviceSessionStatus.v0",
            "fixturePath": "contracts/fixtures/device-session-status.gemma3n-e4b-kv260.json",
            "state": "available_as_data",
            "summary": "Device/session status is consumed as local data only.",
        },
        {
            "refId": "chat_session",
            "schemaVersion": "pccx.chatSession.v0",
            "fixturePath": "contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Base chat/session state is consumed as local data only.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "statusDisplayOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "modelAssetPathsIncluded": False,
        "modelWeightPathsIncluded": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "responseGenerated": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptPersistence": False,
        "touchesHardware": False,
        "kv260Access": False,
        "opensSerialPort": False,
        "networkCalls": False,
        "networkScan": False,
        "providerCalls": False,
        "cloudCalls": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
        "generatedBlobsIncluded": False,
        "hardwareDumpsIncluded": False,
        "telemetry": False,
        "automaticUpload": False,
        "writeBack": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "mcpServerImplemented": False,
        "lspImplemented": False,
        "stableApiAbiClaim": False,
    },
    "limitations": [
        "Data-only chat model status fixture; no model load is attempted.",
        "No prompts, responses, transcripts, model paths, generated artifacts, private paths, secrets, or tokens are stored.",
        "No KV260 hardware access, serial access, network call, provider call, telemetry, upload, or write-back is performed.",
        "Model load controls remain disabled until runtime readiness, model asset, and device/session evidence are available.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_model_status() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat model status fixture."""
    return copy.deepcopy(_CHAT_MODEL_STATUS)


def chat_model_status_json(status: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        status
        if status is not None
        else create_gemma3n_e4b_kv260_chat_model_status(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat model status JSON.",
    )
    parser.add_argument(
        "--model",
        default="gemma3n-e4b",
        choices=("gemma3n-e4b",),
        help="model descriptor target",
    )
    parser.add_argument(
        "--target",
        default="kv260",
        choices=("kv260",),
        help="target board/device",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    parse_args(sys.argv[1:] if argv is None else argv)
    sys.stdout.write(chat_model_status_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
