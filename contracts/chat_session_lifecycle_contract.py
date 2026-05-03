#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat session lifecycle contract for the planned launcher UI.

The contract describes future session lifecycle operations such as create,
restore, clear, close, and export-summary while keeping every operation
disabled or blocked. It does not persist prompts, read or write artifacts,
load models, touch KV260 hardware, call providers, invoke pccx-lab, or start
runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatSessionLifecycle.v0"

LIFECYCLE_FIELDS = (
    "schemaVersion",
    "lifecycleId",
    "fixtureVersion",
    "lastUpdatedSource",
    "parentChatSessionRef",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "lifecycleState",
    "activeSessionState",
    "storageState",
    "restoreState",
    "exportState",
    "sessionIdentityPolicy",
    "sessionStoragePolicy",
    "lifecycleOperations",
    "stateTransitions",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

SESSION_IDENTITY_POLICY_FIELDS = (
    "state",
    "idScope",
    "idSource",
    "pathPolicy",
    "reusePolicy",
)

SESSION_STORAGE_POLICY_FIELDS = (
    "state",
    "scope",
    "pathPolicy",
    "promptPolicy",
    "responsePolicy",
    "transcriptPolicy",
    "artifactPolicy",
    "retentionPolicy",
)

OPERATION_FIELDS = (
    "operationId",
    "label",
    "state",
    "enabled",
    "userAction",
    "launcherAction",
    "requiredEvidence",
    "sideEffectPolicy",
    "contentPolicy",
)

TRANSITION_FIELDS = (
    "transitionId",
    "fromState",
    "event",
    "toState",
    "state",
    "guard",
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

LIFECYCLE_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "inactive",
    "not_configured",
    "not_loaded",
    "placeholder",
    "planned",
    "requires_evidence",
    "unavailable",
)

_CHAT_SESSION_LIFECYCLE = {
    "schemaVersion": SCHEMA_VERSION,
    "lifecycleId": "chat_session_lifecycle_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-session-lifecycle.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_lifecycle_boundary_2026-05-04",
    "parentChatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "lifecycleState": "blocked",
    "activeSessionState": "inactive",
    "storageState": "not_configured",
    "restoreState": "unavailable",
    "exportState": "disabled",
    "sessionIdentityPolicy": {
        "state": "placeholder",
        "idScope": "future_local_session_only",
        "idSource": "deterministic_fixture_identifier_only",
        "pathPolicy": "no user, model, or workspace paths are emitted by this fixture",
        "reusePolicy": "future session reuse requires a reviewed lifecycle boundary",
    },
    "sessionStoragePolicy": {
        "state": "not_configured",
        "scope": "launcher_local_future_store",
        "pathPolicy": "no filesystem path is configured, read, or emitted by this fixture",
        "promptPolicy": "prompt bodies are not accepted, stored, summarized, or exported",
        "responsePolicy": "response bodies are not generated, stored, summarized, or exported",
        "transcriptPolicy": "no transcript exists and transcript persistence is disabled",
        "artifactPolicy": "no manifest, transcript, summary, or lifecycle artifact is written",
        "retentionPolicy": "future retention must be explicit, local, and user controlled",
    },
    "lifecycleOperations": [
        {
            "operationId": "create_session",
            "label": "create session",
            "state": "blocked",
            "enabled": False,
            "userAction": "Request a new local chat session after readiness exists.",
            "launcherAction": "Render placeholder lifecycle state only.",
            "requiredEvidence": [
                "runtime_readiness_available",
                "model_load_reviewed",
                "session_store_boundary_reviewed",
            ],
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_prompt_response_or_transcript_content",
        },
        {
            "operationId": "restore_session",
            "label": "restore session",
            "state": "unavailable",
            "enabled": False,
            "userAction": "Select a prior local session only after a reviewed store exists.",
            "launcherAction": "Refuse restore because no session manifest exists.",
            "requiredEvidence": [
                "local_session_store_configured",
                "session_manifest_schema_reviewed",
            ],
            "sideEffectPolicy": "no_artifact_read_no_write",
            "contentPolicy": "no_session_manifest_or_transcript_content",
        },
        {
            "operationId": "clear_session",
            "label": "clear session",
            "state": "inactive",
            "enabled": False,
            "userAction": "Clear only an active future session owned by the launcher.",
            "launcherAction": "No-op because no local chat session exists.",
            "requiredEvidence": [
                "active_session_exists",
                "clear_boundary_reviewed",
            ],
            "sideEffectPolicy": "no_write",
            "contentPolicy": "no_prompt_response_or_transcript_content",
        },
        {
            "operationId": "close_session",
            "label": "close session",
            "state": "inactive",
            "enabled": False,
            "userAction": "Close an active future session without altering artifacts.",
            "launcherAction": "No-op because no runtime session exists.",
            "requiredEvidence": [
                "active_session_exists",
            ],
            "sideEffectPolicy": "no_runtime_execution",
            "contentPolicy": "no_transcript_mutation",
        },
        {
            "operationId": "export_summary",
            "label": "export summary",
            "state": "blocked",
            "enabled": False,
            "userAction": "Export only a bounded local summary after explicit review.",
            "launcherAction": "Refuse export because no chat session or summary schema exists.",
            "requiredEvidence": [
                "summary_schema_reviewed",
                "redaction_policy_reviewed",
                "explicit_user_export_request",
            ],
            "sideEffectPolicy": "no_artifact_write",
            "contentPolicy": "no_generated_summary_or_transcript_content",
        },
    ],
    "stateTransitions": [
        {
            "transitionId": "open_surface",
            "fromState": "inactive",
            "event": "open_chat_surface",
            "toState": "placeholder",
            "state": "placeholder",
            "guard": "checked chat/session fixture data is available",
            "sideEffectPolicy": "local_render_only",
        },
        {
            "transitionId": "request_create",
            "fromState": "placeholder",
            "event": "create_session",
            "toState": "blocked",
            "state": "blocked",
            "guard": "runtime readiness, model load, and session store evidence are absent",
            "sideEffectPolicy": "no_runtime_execution",
        },
        {
            "transitionId": "request_restore",
            "fromState": "inactive",
            "event": "restore_session",
            "toState": "unavailable",
            "state": "unavailable",
            "guard": "no local session manifest boundary exists",
            "sideEffectPolicy": "no_artifact_read_no_write",
        },
        {
            "transitionId": "request_clear",
            "fromState": "inactive",
            "event": "clear_session",
            "toState": "inactive",
            "state": "inactive",
            "guard": "no active session exists",
            "sideEffectPolicy": "no_write",
        },
        {
            "transitionId": "request_export",
            "fromState": "inactive",
            "event": "export_summary",
            "toState": "disabled",
            "state": "disabled",
            "guard": "no transcript summary boundary exists",
            "sideEffectPolicy": "no_artifact_write",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "runtime_readiness_blocked",
            "state": "blocked",
            "summary": "Runtime readiness remains blocked for the Gemma 3N E4B plus KV260 target.",
            "requiredBefore": "create_session_enabled",
        },
        {
            "reasonId": "model_load_not_available",
            "state": "not_loaded",
            "summary": "Model assets are not loaded and no model runtime session exists.",
            "requiredBefore": "create_session_enabled",
        },
        {
            "reasonId": "session_store_not_configured",
            "state": "not_configured",
            "summary": "No local session store, retention rule, or manifest schema is configured.",
            "requiredBefore": "restore_or_clear_enabled",
        },
        {
            "reasonId": "summary_export_boundary_absent",
            "state": "planned",
            "summary": "A reviewed redaction and summary schema is required before export can exist.",
            "requiredBefore": "export_summary_enabled",
        },
        {
            "reasonId": "active_session_absent",
            "state": "inactive",
            "summary": "No launcher-owned local chat session is active.",
            "requiredBefore": "clear_or_close_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_session",
            "schemaVersion": "pccx.chatSession.v0",
            "fixturePath": "contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Base chat/session surface is consumed as local data only.",
        },
        {
            "refId": "runtime_readiness",
            "schemaVersion": "pccx.runtimeReadiness.v0",
            "fixturePath": "contracts/fixtures/runtime-readiness.gemma3n-e4b-kv260.json",
            "state": "blocked",
            "summary": "Runtime readiness remains a prerequisite for lifecycle changes.",
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
        "writesArtifacts": False,
        "readsArtifacts": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptPersistence": False,
        "sessionPersistence": False,
        "sessionRestoreImplemented": False,
        "sessionClearImplemented": False,
        "summaryExportImplemented": False,
        "touchesHardware": False,
        "kv260Access": False,
        "opensSerialPort": False,
        "networkCalls": False,
        "networkScan": False,
        "runtimeExecution": False,
        "modelLoaded": False,
        "modelExecution": False,
        "modelWeightPathsIncluded": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
        "generatedBlobsIncluded": False,
        "hardwareDumpsIncluded": False,
        "providerCalls": False,
        "cloudCalls": False,
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
        "Data-only chat session lifecycle fixture; no lifecycle operation is enabled.",
        "No prompts, responses, transcripts, manifests, summaries, model paths, generated artifacts, private paths, secrets, or tokens are stored.",
        "No artifacts are read or written and no retention policy is active.",
        "No KV260 hardware access, serial access, network call, provider call, telemetry, upload, or write-back is performed.",
        "Create, restore, clear, close, and export controls remain disabled or blocked until explicit evidence and reviewed boundaries exist.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_session_lifecycle() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 lifecycle fixture."""
    return copy.deepcopy(_CHAT_SESSION_LIFECYCLE)


def chat_session_lifecycle_json(status: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        status
        if status is not None
        else create_gemma3n_e4b_kv260_chat_session_lifecycle(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat session lifecycle JSON.",
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
    sys.stdout.write(chat_session_lifecycle_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
