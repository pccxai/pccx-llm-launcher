#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat readiness contract for the planned launcher UI.

The contract describes the readiness checks, blocked reasons, and recovery
actions that gate the standalone chat surface. It does not read prompts, load
models, start runtime code, touch KV260 hardware, call providers, invoke
pccx-lab, or read/write artifacts.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatReadiness.v0"

CHAT_READINESS_FIELDS = (
    "schemaVersion",
    "readinessId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "overallState",
    "inputReadinessState",
    "sendReadinessState",
    "recoveryState",
    "evidenceState",
    "parentChatSessionRef",
    "chatModelStatusRef",
    "chatSessionLifecycleRef",
    "readinessChecks",
    "errorTaxonomy",
    "recoveryActions",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

READINESS_CHECK_FIELDS = (
    "checkId",
    "label",
    "state",
    "severity",
    "summary",
    "requiredBefore",
    "displayPolicy",
)

ERROR_TAXONOMY_FIELDS = (
    "errorId",
    "state",
    "severity",
    "userMessage",
    "diagnosticHint",
    "recoveryActionId",
    "contentPolicy",
)

RECOVERY_ACTION_FIELDS = (
    "actionId",
    "label",
    "state",
    "enabled",
    "userAction",
    "launcherAction",
    "requiredEvidence",
    "sideEffectPolicy",
)

HANDOFF_REF_FIELDS = (
    "refId",
    "schemaVersion",
    "fixturePath",
    "state",
    "summary",
)

CHAT_READINESS_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "external_not_configured",
    "inactive",
    "not_configured",
    "not_loaded",
    "not_started",
    "not_used",
    "placeholder",
    "planned",
    "requires_evidence",
    "target_selected",
    "unavailable",
)

_CHAT_READINESS = {
    "schemaVersion": SCHEMA_VERSION,
    "readinessId": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-readiness.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_readiness_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "overallState": "blocked",
    "inputReadinessState": "available_as_data",
    "sendReadinessState": "disabled",
    "recoveryState": "requires_evidence",
    "evidenceState": "blocked",
    "parentChatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "chatModelStatusRef": "chat_model_status_gemma3n_e4b_kv260_placeholder",
    "chatSessionLifecycleRef": "chat_session_lifecycle_gemma3n_e4b_kv260_placeholder",
    "readinessChecks": [
        {
            "checkId": "chat_surface_fixture",
            "label": "chat surface fixture",
            "state": "available_as_data",
            "severity": "info",
            "summary": "The checked chat/session fixture can be rendered as local data only.",
            "requiredBefore": "surface_preview_rendered",
            "displayPolicy": "show local fixture availability without accepting prompts",
        },
        {
            "checkId": "model_target",
            "label": "model target",
            "state": "target_selected",
            "severity": "info",
            "summary": "Gemma 3N E4B is selected as a planned target descriptor.",
            "requiredBefore": "model_status_displayed",
            "displayPolicy": "show target label without model paths",
        },
        {
            "checkId": "model_assets",
            "label": "model assets",
            "state": "external_not_configured",
            "severity": "blocked",
            "summary": "Model assets are external and no reviewed local asset input boundary exists.",
            "requiredBefore": "model_load_enabled",
            "displayPolicy": "show blocked state without filenames or paths",
        },
        {
            "checkId": "runtime_readiness",
            "label": "runtime readiness",
            "state": "blocked",
            "severity": "blocked",
            "summary": "Runtime readiness remains blocked and not yet evidence-backed.",
            "requiredBefore": "send_message_enabled",
            "displayPolicy": "show conservative readiness summary only",
        },
        {
            "checkId": "device_session",
            "label": "device session",
            "state": "inactive",
            "severity": "blocked",
            "summary": "No KV260 target session exists in this fixture.",
            "requiredBefore": "runtime_session_started",
            "displayPolicy": "show inactive state without probing hardware",
        },
        {
            "checkId": "chat_runtime",
            "label": "chat runtime",
            "state": "not_started",
            "severity": "blocked",
            "summary": "No local chat runtime has been implemented or started.",
            "requiredBefore": "assistant_response_available",
            "displayPolicy": "show blocked state without executing runtime code",
        },
        {
            "checkId": "session_store",
            "label": "session store",
            "state": "not_configured",
            "severity": "blocked",
            "summary": "No reviewed local session store or retention policy exists.",
            "requiredBefore": "session_restore_or_export_enabled",
            "displayPolicy": "show unavailable storage state without reading artifacts",
        },
        {
            "checkId": "provider_mode",
            "label": "provider mode",
            "state": "not_used",
            "severity": "info",
            "summary": "External provider state is not used for this local launcher boundary.",
            "requiredBefore": "core_chat_available",
            "displayPolicy": "show no-provider state without provider configuration",
        },
    ],
    "errorTaxonomy": [
        {
            "errorId": "runtime_not_ready",
            "state": "blocked",
            "severity": "blocked",
            "userMessage": "Local chat is blocked until runtime readiness evidence exists.",
            "diagnosticHint": "Review the runtime readiness data contract before enabling send.",
            "recoveryActionId": "review_runtime_readiness",
            "contentPolicy": "no_prompt_response_or_log_content",
        },
        {
            "errorId": "model_assets_missing",
            "state": "external_not_configured",
            "severity": "blocked",
            "userMessage": "Model assets are not configured by this launcher fixture.",
            "diagnosticHint": "A future reviewed asset input boundary must redact local paths.",
            "recoveryActionId": "configure_model_assets_future",
            "contentPolicy": "no_model_paths_or_weight_names",
        },
        {
            "errorId": "device_session_absent",
            "state": "inactive",
            "severity": "blocked",
            "userMessage": "No target device session is active.",
            "diagnosticHint": "Use device/session status data only; this fixture does not probe hardware.",
            "recoveryActionId": "review_device_session_status",
            "contentPolicy": "no_serial_ssh_or_network_output",
        },
        {
            "errorId": "chat_runtime_absent",
            "state": "not_started",
            "severity": "blocked",
            "userMessage": "No local chat runtime is available for assistant responses.",
            "diagnosticHint": "Runtime execution requires a separate reviewed implementation boundary.",
            "recoveryActionId": "wait_for_runtime_boundary",
            "contentPolicy": "no_generated_response_content",
        },
        {
            "errorId": "session_store_absent",
            "state": "not_configured",
            "severity": "blocked",
            "userMessage": "Session restore and export are unavailable.",
            "diagnosticHint": "A future local session store must define retention and redaction rules.",
            "recoveryActionId": "review_session_store_policy",
            "contentPolicy": "no_manifest_transcript_or_summary_content",
        },
    ],
    "recoveryActions": [
        {
            "actionId": "review_runtime_readiness",
            "label": "review runtime readiness",
            "state": "available_as_data",
            "enabled": False,
            "userAction": "Review the checked runtime readiness summary.",
            "launcherAction": "Render local readiness data only.",
            "requiredEvidence": [
                "runtime_readiness_fixture_available",
            ],
            "sideEffectPolicy": "read_only_data",
        },
        {
            "actionId": "configure_model_assets_future",
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
            "actionId": "review_device_session_status",
            "label": "review device session status",
            "state": "available_as_data",
            "enabled": False,
            "userAction": "Review target status as deterministic local fixture data.",
            "launcherAction": "Render the checked device/session status fixture.",
            "requiredEvidence": [
                "device_session_fixture_available",
            ],
            "sideEffectPolicy": "read_only_data",
        },
        {
            "actionId": "wait_for_runtime_boundary",
            "label": "wait for runtime boundary",
            "state": "requires_evidence",
            "enabled": False,
            "userAction": "Keep send disabled until a runtime boundary is reviewed.",
            "launcherAction": "Refuse runtime execution from this fixture.",
            "requiredEvidence": [
                "runtime_boundary_reviewed",
                "model_load_evidence_available",
                "device_session_evidence_available",
            ],
            "sideEffectPolicy": "no_runtime_execution",
        },
        {
            "actionId": "review_session_store_policy",
            "label": "review session store policy",
            "state": "planned",
            "enabled": False,
            "userAction": "Enable restore or export only after explicit retention rules exist.",
            "launcherAction": "Do not read, write, or summarize session artifacts.",
            "requiredEvidence": [
                "session_store_boundary_reviewed",
                "summary_redaction_policy_reviewed",
            ],
            "sideEffectPolicy": "no_artifact_read_no_write",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_session",
            "schemaVersion": "pccx.chatSession.v0",
            "fixturePath": "contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Base chat/session state is consumed as local data only.",
        },
        {
            "refId": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "fixturePath": "contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Model display status is consumed as local data only.",
        },
        {
            "refId": "chat_session_lifecycle",
            "schemaVersion": "pccx.chatSessionLifecycle.v0",
            "fixturePath": "contracts/fixtures/chat-session-lifecycle.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Session lifecycle state remains disabled or blocked.",
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
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "readinessDisplayOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptPersistence": False,
        "sessionPersistence": False,
        "modelAssetPathsIncluded": False,
        "modelWeightPathsIncluded": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "responseGenerated": False,
        "touchesHardware": False,
        "kv260Access": False,
        "opensSerialPort": False,
        "networkCalls": False,
        "networkScan": False,
        "sshExecution": False,
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
        "Data-only chat readiness fixture; no readiness check executes runtime code.",
        "No prompts, responses, transcripts, model paths, generated artifacts, private paths, secrets, or tokens are stored.",
        "No KV260 hardware access, serial access, SSH execution, network call, provider call, telemetry, upload, or write-back is performed.",
        "Send controls remain disabled until runtime readiness, model-load, device-session, and local session evidence are available.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_readiness() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat readiness fixture."""
    return copy.deepcopy(_CHAT_READINESS)


def chat_readiness_json(status: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        status
        if status is not None
        else create_gemma3n_e4b_kv260_chat_readiness(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat readiness JSON.",
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
    sys.stdout.write(chat_readiness_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
