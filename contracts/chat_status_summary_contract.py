#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat status summary contract for the planned launcher UI.

The contract aggregates existing checked chat surface references into a
display-only blocked status summary. It does not read prompts, transcripts,
session stores, model assets, runtime logs, provider configuration, artifacts,
or hardware state; it does not start runtime code or invoke other PCCX tools.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatStatusSummary.v0"

CHAT_STATUS_SUMMARY_FIELDS = (
    "schemaVersion",
    "statusSummaryId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "overallState",
    "surfaceState",
    "sessionState",
    "modelState",
    "runtimeState",
    "sendState",
    "contentState",
    "privacyState",
    "evidenceState",
    "statusCards",
    "blockedReasons",
    "nextActions",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

STATUS_CARD_FIELDS = (
    "cardId",
    "label",
    "sourceRef",
    "schemaVersion",
    "state",
    "severity",
    "summary",
    "contentPolicy",
    "requiredBefore",
)

BLOCKED_REASON_FIELDS = (
    "reasonId",
    "state",
    "summary",
    "requiredBefore",
)

NEXT_ACTION_FIELDS = (
    "actionId",
    "label",
    "state",
    "enabled",
    "summary",
    "sideEffectPolicy",
)

HANDOFF_REF_FIELDS = (
    "refId",
    "schemaVersion",
    "fixturePath",
    "state",
    "summary",
)

CHAT_STATUS_SUMMARY_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "inactive",
    "not_configured",
    "not_loaded",
    "not_started",
    "not_used",
    "placeholder",
    "planned",
    "requires_evidence",
    "requires_review",
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_STATUS_SUMMARY = {
    "schemaVersion": SCHEMA_VERSION,
    "statusSummaryId": "chat_status_summary_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-status-summary.gemma3n-e4b-kv260.2026-05-05",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_status_summary_boundary_2026-05-05",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "overallState": "blocked",
    "surfaceState": "available_as_data",
    "sessionState": "inactive",
    "modelState": "blocked",
    "runtimeState": "blocked",
    "sendState": "disabled",
    "contentState": "empty_not_captured",
    "privacyState": "summary_only",
    "evidenceState": "blocked",
    "statusCards": [
        {
            "cardId": "surface_layout",
            "label": "surface layout",
            "sourceRef": "chat_surface_layout",
            "schemaVersion": "pccx.chatSurfaceLayout.v0",
            "state": "available_as_data",
            "severity": "info",
            "summary": "The planned chat shell regions can be rendered from checked local data.",
            "contentPolicy": "no_prompt_response_transcript_or_session_content",
            "requiredBefore": "chat_shell_enabled",
        },
        {
            "cardId": "session_state",
            "label": "session state",
            "sourceRef": "chat_session",
            "schemaVersion": "pccx.chatSession.v0",
            "state": "inactive",
            "severity": "blocked",
            "summary": "No active launcher-owned chat session exists.",
            "contentPolicy": "no_session_store_title_summary_or_path_content",
            "requiredBefore": "session_restore_or_export_enabled",
        },
        {
            "cardId": "model_status",
            "label": "model status",
            "sourceRef": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "state": "blocked",
            "severity": "blocked",
            "summary": "Model status remains descriptor-only with no local asset or runtime load.",
            "contentPolicy": "no_model_path_weight_tokenizer_or_checksum_content",
            "requiredBefore": "model_load_enabled",
        },
        {
            "cardId": "readiness",
            "label": "chat readiness",
            "sourceRef": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "state": "blocked",
            "severity": "blocked",
            "summary": "Chat readiness is blocked until runtime, device, model, and store evidence exist.",
            "contentPolicy": "summary_only_no_runtime_log_or_artifact_content",
            "requiredBefore": "send_message_enabled",
        },
        {
            "cardId": "composer",
            "label": "composer",
            "sourceRef": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "state": "available_as_data",
            "severity": "info",
            "summary": "Composer controls can be displayed as disabled/local data without prompt capture.",
            "contentPolicy": "no_prompt_text_or_attachment_content",
            "requiredBefore": "prompt_capture_enabled",
        },
        {
            "cardId": "send_result",
            "label": "send result",
            "sourceRef": "chat_send_result",
            "schemaVersion": "pccx.chatSendResult.v0",
            "state": "disabled",
            "severity": "blocked",
            "summary": "Send remains disabled and no input is accepted by this boundary.",
            "contentPolicy": "no_prompt_echo_or_generated_response",
            "requiredBefore": "assistant_response_available",
        },
        {
            "cardId": "message_list",
            "label": "message list",
            "sourceRef": "chat_message_list",
            "schemaVersion": "pccx.chatMessageList.v0",
            "state": "empty_not_captured",
            "severity": "info",
            "summary": "The conversation viewport is empty because no messages are captured.",
            "contentPolicy": "no_message_body_transcript_or_summary_content",
            "requiredBefore": "conversation_history_displayed",
        },
        {
            "cardId": "response_stream",
            "label": "response stream",
            "sourceRef": "chat_response_stream",
            "schemaVersion": "pccx.chatResponseStream.v0",
            "state": "disabled",
            "severity": "blocked",
            "summary": "Assistant streaming remains disabled and no token stream exists.",
            "contentPolicy": "no_response_chunk_token_or_runtime_log_content",
            "requiredBefore": "stream_transport_enabled",
        },
        {
            "cardId": "privacy_controls",
            "label": "privacy controls",
            "sourceRef": "chat_redaction_policy",
            "schemaVersion": "pccx.chatRedactionPolicy.v0",
            "state": "summary_only",
            "severity": "blocked",
            "summary": "Privacy and redaction controls are summary-only with content scanning disabled.",
            "contentPolicy": "no_raw_content_detector_match_or_redaction_result",
            "requiredBefore": "content_scan_or_redaction_enabled",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "runtime_evidence_absent",
            "state": "blocked",
            "summary": "No reviewed runtime readiness evidence exists for local chat execution.",
            "requiredBefore": "send_message_enabled",
        },
        {
            "reasonId": "model_load_absent",
            "state": "blocked",
            "summary": "No reviewed model asset, validation, load, warmup, or unload boundary is enabled.",
            "requiredBefore": "model_status_ready",
        },
        {
            "reasonId": "device_session_absent",
            "state": "inactive",
            "summary": "No active device session is represented by this local fixture.",
            "requiredBefore": "runtime_session_started",
        },
        {
            "reasonId": "session_store_absent",
            "state": "not_configured",
            "summary": "No reviewed session store, retention, restore, or export path exists.",
            "requiredBefore": "session_management_enabled",
        },
        {
            "reasonId": "content_boundary_absent",
            "state": "requires_review",
            "summary": "Prompt, response, transcript, attachment, clipboard, and redaction content boundaries remain disabled or summary-only.",
            "requiredBefore": "prompt_or_response_content_displayed",
        },
    ],
    "nextActions": [
        {
            "actionId": "review_readiness_data",
            "label": "review readiness data",
            "state": "available_as_data",
            "enabled": False,
            "summary": "Render existing checked readiness, model, session, and policy fixtures.",
            "sideEffectPolicy": "read_only_data",
        },
        {
            "actionId": "keep_send_disabled",
            "label": "keep send disabled",
            "state": "blocked",
            "enabled": False,
            "summary": "Do not accept prompts or dispatch runtime work from this summary.",
            "sideEffectPolicy": "no_prompt_capture_no_runtime_execution",
        },
        {
            "actionId": "wait_for_runtime_boundary",
            "label": "wait for runtime boundary",
            "state": "requires_evidence",
            "enabled": False,
            "summary": "Enable chat execution only after separate reviewed runtime and evidence boundaries exist.",
            "sideEffectPolicy": "no_model_or_hardware_action",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_surface_layout",
            "schemaVersion": "pccx.chatSurfaceLayout.v0",
            "fixturePath": "contracts/fixtures/chat-surface-layout.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Planned layout is consumed as local display data only.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Readiness stays blocked until evidence-backed runtime and session paths exist.",
        },
        {
            "refId": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "fixturePath": "contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Model status remains descriptor-only and blocked.",
        },
        {
            "refId": "chat_session",
            "schemaVersion": "pccx.chatSession.v0",
            "fixturePath": "contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json",
            "state": "inactive",
            "summary": "Base session state remains inactive local data.",
        },
        {
            "refId": "chat_redaction_policy",
            "schemaVersion": "pccx.chatRedactionPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-redaction-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "summary_only",
            "summary": "Redaction policy is referenced without loading rules or scanning content.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "statusSummaryOnly": True,
        "aggregatesCheckedFixturesOnly": True,
        "promptCapture": False,
        "promptRead": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptContentIncluded": False,
        "messageBodiesIncluded": False,
        "sessionStoreRead": False,
        "sessionPersistence": False,
        "configRead": False,
        "environmentRead": False,
        "providerConfigRead": False,
        "modelAssetRead": False,
        "modelPathIncluded": False,
        "modelLoadAttempted": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "responseGenerated": False,
        "sendEnabled": False,
        "clipboardRead": False,
        "clipboardWrite": False,
        "attachmentReads": False,
        "fileContentRead": False,
        "readsArtifacts": False,
        "writesArtifacts": False,
        "kv260Access": False,
        "hardwareAccess": False,
        "networkCalls": False,
        "providerCalls": False,
        "cloudCalls": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "telemetry": False,
        "writeBack": False,
        "releaseOrTagAction": False,
        "settingsChange": False,
        "compatibilityClaim": False,
    },
    "limitations": [
        "Data-only chat status summary over checked local fixture references.",
        "No prompt, response, transcript, message, session-store, config, provider, model-path, runtime-log, artifact, private-path, secret, token, or hardware content is read.",
        "No model load, runtime execution, provider call, network call, hardware access, telemetry, write-back, release, tag, settings, or repository action is performed.",
        "Send and response streaming remain disabled until separate reviewed runtime, model, device-session, content, and persistence boundaries exist.",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_status_summary() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat status summary."""
    return copy.deepcopy(_CHAT_STATUS_SUMMARY)


def chat_status_summary_json(status: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        status
        if status is not None
        else create_gemma3n_e4b_kv260_chat_status_summary(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat status summary JSON.",
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
    sys.stdout.write(chat_status_summary_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
