#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat implementation gap matrix for the planned launcher UI.

The matrix records remaining standalone chat gaps over existing checked
fixture references. It does not accept prompts, read transcripts, read
session stores, load models, start runtime code, call providers, invoke
PCCX tools, touch hardware, read artifacts, or mutate repository state.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatGapMatrix.v0"

CHAT_GAP_MATRIX_FIELDS = (
    "schemaVersion",
    "gapMatrixId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "matrixState",
    "standaloneChatState",
    "reviewState",
    "evidenceState",
    "readinessState",
    "gapRows",
    "dependencyRefs",
    "exitCriteria",
    "blockedReasons",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

GAP_ROW_FIELDS = (
    "gapId",
    "label",
    "area",
    "sourceRefs",
    "state",
    "severity",
    "summary",
    "requiredBefore",
    "sideEffectPolicy",
)

DEPENDENCY_REF_FIELDS = (
    "refId",
    "schemaVersion",
    "fixturePath",
    "state",
    "summary",
)

EXIT_CRITERIA_FIELDS = (
    "criteriaId",
    "state",
    "accepted",
    "summary",
    "requiredEvidence",
    "blockedBy",
)

BLOCKED_REASON_FIELDS = (
    "reasonId",
    "state",
    "summary",
    "requiredBefore",
)

CHAT_GAP_MATRIX_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "inactive",
    "not_approved",
    "not_configured",
    "not_loaded",
    "not_started",
    "planned",
    "requires_evidence",
    "requires_review",
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_GAP_MATRIX = {
    "schemaVersion": SCHEMA_VERSION,
    "gapMatrixId": "chat_gap_matrix_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-gap-matrix.gemma3n-e4b-kv260.2026-05-05",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_gap_matrix_boundary_2026-05-05",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "matrixState": "available_as_data",
    "standaloneChatState": "blocked",
    "reviewState": "not_approved",
    "evidenceState": "requires_evidence",
    "readinessState": "blocked",
    "gapRows": [
        {
            "gapId": "runtime_device_evidence",
            "label": "runtime and device evidence",
            "area": "runtime",
            "sourceRefs": [
                "runtime_readiness",
                "device_session_status",
                "chat_review_packet",
            ],
            "state": "requires_evidence",
            "severity": "blocker",
            "summary": "Runtime readiness and target device session evidence are still absent from this launcher boundary.",
            "requiredBefore": "model_or_runtime_execution_enabled",
            "sideEffectPolicy": "no_runtime_or_hardware_action",
        },
        {
            "gapId": "model_asset_boundary",
            "label": "model asset boundary",
            "area": "model",
            "sourceRefs": [
                "model_runtime_descriptor",
                "chat_model_selection_policy",
                "chat_model_load_request",
            ],
            "state": "not_loaded",
            "severity": "blocker",
            "summary": "Model path, asset discovery, checksum, tokenizer, load, warmup, unload, and persistence remain disabled.",
            "requiredBefore": "model_status_ready",
            "sideEffectPolicy": "no_model_path_read_or_model_load",
        },
        {
            "gapId": "prompt_input_boundary",
            "label": "prompt input boundary",
            "area": "content",
            "sourceRefs": [
                "chat_composer",
                "chat_send_result",
                "chat_review_packet",
            ],
            "state": "disabled",
            "severity": "blocker",
            "summary": "Prompt capture, prompt read, prompt echo, accepted input, validation handoff, and send dispatch remain disabled.",
            "requiredBefore": "send_control_enabled",
            "sideEffectPolicy": "no_prompt_capture_or_input_acceptance",
        },
        {
            "gapId": "response_generation_boundary",
            "label": "response generation boundary",
            "area": "content",
            "sourceRefs": [
                "chat_response_stream",
                "chat_message_list",
                "chat_context_policy",
            ],
            "state": "disabled",
            "severity": "blocker",
            "summary": "Response generation, response chunks, token counts, context assembly, and transcript append remain disabled.",
            "requiredBefore": "assistant_response_enabled",
            "sideEffectPolicy": "no_response_generation_or_stream_transport",
        },
        {
            "gapId": "session_store_boundary",
            "label": "session store boundary",
            "area": "session",
            "sourceRefs": [
                "chat_session",
                "chat_session_lifecycle",
                "chat_session_store_policy",
                "chat_session_index",
                "chat_session_title_policy",
            ],
            "state": "not_configured",
            "severity": "blocker",
            "summary": "Session store path, manifest, read, write, delete, restore, title, retention, migration, and export remain unconfigured.",
            "requiredBefore": "session_management_enabled",
            "sideEffectPolicy": "no_session_store_or_title_access",
        },
        {
            "gapId": "transcript_export_boundary",
            "label": "transcript and export boundary",
            "area": "session",
            "sourceRefs": [
                "chat_transcript_policy",
                "chat_action_bar",
                "chat_session_lifecycle",
            ],
            "state": "disabled",
            "severity": "blocker",
            "summary": "Transcript reads, transcript persistence, export summary, raw export, and action-bar export controls remain disabled.",
            "requiredBefore": "transcript_or_export_enabled",
            "sideEffectPolicy": "no_transcript_read_write_or_export",
        },
        {
            "gapId": "privacy_content_policy",
            "label": "privacy and content policy",
            "area": "privacy",
            "sourceRefs": [
                "chat_local_only_policy",
                "chat_redaction_policy",
                "chat_error_taxonomy",
            ],
            "state": "requires_review",
            "severity": "blocker",
            "summary": "Local-only policy, redaction, content scanning, detector execution, result persistence, and raw error payload handling remain review-only.",
            "requiredBefore": "privacy_sensitive_content_paths_enabled",
            "sideEffectPolicy": "no_content_scan_redaction_or_provider_call",
        },
        {
            "gapId": "attachment_clipboard_boundary",
            "label": "attachment and clipboard boundary",
            "area": "input_output",
            "sourceRefs": [
                "chat_attachment_policy",
                "chat_clipboard_policy",
                "chat_action_bar",
            ],
            "state": "disabled",
            "severity": "blocker",
            "summary": "File picker, file metadata, file content, upload, import, preview, clipboard read, and clipboard write remain disabled.",
            "requiredBefore": "attachment_or_clipboard_paths_enabled",
            "sideEffectPolicy": "no_file_clipboard_or_directory_access",
        },
        {
            "gapId": "audit_persistence_boundary",
            "label": "audit persistence boundary",
            "area": "audit",
            "sourceRefs": [
                "chat_audit_event",
                "chat_redaction_policy",
                "chat_review_packet",
            ],
            "state": "not_configured",
            "severity": "blocker",
            "summary": "Audit logging, event persistence, actor identifiers, raw logs, private paths, and generated blobs remain absent.",
            "requiredBefore": "audit_logging_enabled",
            "sideEffectPolicy": "no_audit_write_or_raw_log_read",
        },
        {
            "gapId": "ui_enablement_boundary",
            "label": "UI enablement boundary",
            "area": "surface",
            "sourceRefs": [
                "chat_surface_layout",
                "chat_empty_state",
                "chat_action_bar",
                "chat_shortcut_map",
                "chat_status_summary",
            ],
            "state": "blocked",
            "severity": "blocker",
            "summary": "Surface layout, empty state, action-bar controls, shortcuts, and status cards remain display-only until the blocker rows close.",
            "requiredBefore": "standalone_chat_ui_enabled",
            "sideEffectPolicy": "no_action_execution_command_dispatch_or_focus_change",
        },
    ],
    "dependencyRefs": [
        {
            "refId": "chat_review_packet",
            "schemaVersion": "pccx.chatReviewPacket.v0",
            "fixturePath": "contracts/fixtures/chat-review-packet.gemma3n-e4b-kv260-placeholder.json",
            "state": "not_approved",
            "summary": "Review packet remains blocked and records review gates only.",
        },
        {
            "refId": "chat_status_summary",
            "schemaVersion": "pccx.chatStatusSummary.v0",
            "fixturePath": "contracts/fixtures/chat-status-summary.gemma3n-e4b-kv260-placeholder.json",
            "state": "summary_only",
            "summary": "Status summary remains a checked display aggregate and is not duplicated here.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Chat readiness remains blocked until runtime, device, model, store, and privacy evidence exists.",
        },
        {
            "refId": "chat_model_load_request",
            "schemaVersion": "pccx.chatModelLoadRequest.v0",
            "fixturePath": "contracts/fixtures/chat-model-load-request.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Model load request remains blocked with no model asset path read or load attempt.",
        },
        {
            "refId": "chat_session_store_policy",
            "schemaVersion": "pccx.chatSessionStorePolicy.v0",
            "fixturePath": "contracts/fixtures/chat-session-store-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "not_configured",
            "summary": "Session store policy remains disabled and no local store is read.",
        },
        {
            "refId": "chat_redaction_policy",
            "schemaVersion": "pccx.chatRedactionPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-redaction-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "summary_only",
            "summary": "Redaction policy is referenced without loading rules, scanning content, or persisting results.",
        },
    ],
    "exitCriteria": [
        {
            "criteriaId": "runtime_and_device_evidence_accepted",
            "state": "requires_evidence",
            "accepted": False,
            "summary": "Runtime and device session evidence must be reviewed before runtime paths are enabled.",
            "requiredEvidence": [
                "runtime_readiness_with_reviewed_evidence",
                "device_session_status_with_reviewed_target_state",
            ],
            "blockedBy": [
                "runtime_device_evidence",
            ],
        },
        {
            "criteriaId": "model_and_session_boundaries_reviewed",
            "state": "not_approved",
            "accepted": False,
            "summary": "Model asset and session-store boundaries must be reviewed before local chat state is enabled.",
            "requiredEvidence": [
                "reviewed_model_asset_boundary",
                "reviewed_session_store_boundary",
            ],
            "blockedBy": [
                "model_asset_boundary",
                "session_store_boundary",
            ],
        },
        {
            "criteriaId": "content_privacy_boundaries_reviewed",
            "state": "requires_review",
            "accepted": False,
            "summary": "Prompt, response, transcript, attachment, clipboard, redaction, and audit boundaries must be reviewed before content paths are enabled.",
            "requiredEvidence": [
                "reviewed_prompt_input_boundary",
                "reviewed_response_stream_boundary",
                "reviewed_privacy_policy_boundary",
            ],
            "blockedBy": [
                "prompt_input_boundary",
                "response_generation_boundary",
                "privacy_content_policy",
                "attachment_clipboard_boundary",
                "audit_persistence_boundary",
            ],
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "standalone_chat_not_enabled",
            "state": "blocked",
            "summary": "Standalone chat remains blocked because all gap rows are unresolved.",
            "requiredBefore": "standalone_chat_enabled",
        },
        {
            "reasonId": "review_packet_not_approved",
            "state": "not_approved",
            "summary": "The review packet is referenced but not approved by this matrix.",
            "requiredBefore": "review_gate_closed",
        },
        {
            "reasonId": "runtime_evidence_absent",
            "state": "requires_evidence",
            "summary": "Runtime, device, and hardware evidence remain outside this launcher boundary.",
            "requiredBefore": "model_or_runtime_execution_enabled",
        },
        {
            "reasonId": "content_paths_disabled",
            "state": "disabled",
            "summary": "Prompt, response, transcript, attachment, clipboard, redaction, audit, and export paths remain disabled.",
            "requiredBefore": "content_or_io_enabled",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "gapMatrixOnly": True,
        "referencesCheckedFixturesOnly": True,
        "reviewPacketReferencedOnly": True,
        "statusSummaryReferencedOnly": True,
        "gapClosed": False,
        "approvalGranted": False,
        "promptCapture": False,
        "promptRead": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "inputAccepted": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "responseChunksEmitted": False,
        "tokenCountMeasured": False,
        "transcriptContentIncluded": False,
        "messageBodiesIncluded": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
        "sessionPersistence": False,
        "summaryGenerated": False,
        "transcriptExported": False,
        "clipboardRead": False,
        "clipboardWrite": False,
        "attachmentReads": False,
        "fileMetadataRead": False,
        "fileContentRead": False,
        "directoryScan": False,
        "redactionRulesLoaded": False,
        "contentScan": False,
        "redactionApplied": False,
        "auditLogWritten": False,
        "configRead": False,
        "environmentRead": False,
        "providerConfigRead": False,
        "modelAssetRead": False,
        "modelPathIncluded": False,
        "modelLoadAttempted": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "sendEnabled": False,
        "readsArtifacts": False,
        "writesArtifacts": False,
        "kv260Access": False,
        "hardwareAccess": False,
        "networkCalls": False,
        "providerCalls": False,
        "cloudCalls": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "commandDispatch": False,
        "actionExecution": False,
        "focusChanged": False,
        "telemetry": False,
        "writeBack": False,
        "releaseOrTagAction": False,
        "settingsChange": False,
        "compatibilityClaim": False,
    },
    "limitations": [
        "Data-only chat implementation gap matrix over existing checked fixture references.",
        "No prompt, response, transcript, message, session-store, config, provider, model-path, runtime-log, artifact, private-path, secret, token, file, clipboard, or hardware content is read.",
        "No model load, runtime execution, provider call, network call, hardware access, pccx-lab execution, IDE execution, telemetry, write-back, release, tag, settings, or repository action is performed.",
        "This matrix does not close issue #9 or approve standalone chat enablement; it records remaining blocker rows only.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_gap_matrix() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat gap matrix."""
    return copy.deepcopy(_CHAT_GAP_MATRIX)


def chat_gap_matrix_json(matrix: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        matrix
        if matrix is not None
        else create_gemma3n_e4b_kv260_chat_gap_matrix(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat implementation gap matrix JSON.",
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
    sys.stdout.write(chat_gap_matrix_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
