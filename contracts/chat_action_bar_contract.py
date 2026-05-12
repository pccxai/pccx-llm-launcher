#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat action-bar contract for the planned launcher UI.

The contract describes disabled conversation action controls for the
standalone chat surface. It does not read prompts, responses, transcripts,
session stores, summaries, model assets, private paths, logs, or artifacts;
it does not copy to the clipboard, export transcripts, attach files, create
sessions, clear conversations, stop streams, start runtime code, load models,
touch KV260 hardware, call providers, invoke pccx-lab, or persist anything.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatActionBar.v0"

CHAT_ACTION_BAR_FIELDS = (
    "schemaVersion",
    "actionBarId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "actionBarState",
    "conversationState",
    "selectionState",
    "transcriptState",
    "responseState",
    "attachmentState",
    "clipboardState",
    "exportState",
    "stopControlState",
    "chatSessionRef",
    "chatReadinessRef",
    "chatComposerRef",
    "chatSendResultRef",
    "chatResponseStreamRef",
    "chatMessageListRef",
    "actionPolicy",
    "actionGroups",
    "actionControls",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

ACTION_POLICY_FIELDS = (
    "state",
    "renderMode",
    "sourcePolicy",
    "contentPolicy",
    "interactionPolicy",
    "sideEffectPolicy",
    "persistencePolicy",
)

ACTION_GROUP_FIELDS = (
    "groupId",
    "label",
    "state",
    "visible",
    "enabled",
    "summary",
)

ACTION_CONTROL_FIELDS = (
    "actionId",
    "label",
    "groupId",
    "state",
    "visible",
    "enabled",
    "requiresExplicitUserAction",
    "sourceRef",
    "resultState",
    "sideEffectPolicy",
    "blockedReasonRef",
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

CHAT_ACTION_BAR_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "inactive",
    "not_configured",
    "not_generated",
    "not_loaded",
    "not_started",
    "placeholder",
    "planned",
    "requires_evidence",
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_ACTION_BAR = {
    "schemaVersion": SCHEMA_VERSION,
    "actionBarId": "chat_action_bar_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-action-bar.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_action_bar_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "actionBarState": "blocked",
    "conversationState": "inactive",
    "selectionState": "disabled",
    "transcriptState": "not_started",
    "responseState": "not_generated",
    "attachmentState": "disabled",
    "clipboardState": "disabled",
    "exportState": "disabled",
    "stopControlState": "disabled",
    "chatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatSendResultRef": "chat_send_result_gemma3n_e4b_kv260_placeholder",
    "chatResponseStreamRef": "chat_response_stream_gemma3n_e4b_kv260_placeholder",
    "chatMessageListRef": "chat_message_list_gemma3n_e4b_kv260_placeholder",
    "actionPolicy": {
        "state": "placeholder",
        "renderMode": "future_local_chat_action_bar",
        "sourcePolicy": "checked fixture only; no session store, transcript, prompt, response, summary, file, clipboard, or model path is read",
        "contentPolicy": "action metadata only; no message bodies, prompt text, response text, transcript text, or session titles are included",
        "interactionPolicy": "all conversation actions remain disabled until reviewed runtime, session-store, transcript, clipboard, and attachment boundaries exist",
        "sideEffectPolicy": "local_render_only",
        "persistencePolicy": "no session creation, clear, export, copy, retry, stop, attachment, transcript, or artifact write",
    },
    "actionGroups": [
        {
            "groupId": "conversation_actions",
            "label": "conversation actions",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "summary": "New, clear, and session actions remain disabled.",
        },
        {
            "groupId": "message_actions",
            "label": "message actions",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "summary": "Retry and copy actions remain unavailable because no message content is present.",
        },
        {
            "groupId": "transcript_actions",
            "label": "transcript actions",
            "state": "not_configured",
            "visible": True,
            "enabled": False,
            "summary": "Export and transcript controls remain disabled until a reviewed local store exists.",
        },
        {
            "groupId": "runtime_actions",
            "label": "runtime actions",
            "state": "not_started",
            "visible": True,
            "enabled": False,
            "summary": "Stop and retry controls remain disabled because no local response stream exists.",
        },
        {
            "groupId": "attachment_actions",
            "label": "attachment actions",
            "state": "planned",
            "visible": True,
            "enabled": False,
            "summary": "Attachment controls require a separate reviewed artifact input boundary.",
        },
    ],
    "actionControls": [
        {
            "actionId": "new_chat",
            "label": "new chat",
            "groupId": "conversation_actions",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_session_lifecycle",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_session_create",
            "blockedReasonRef": "session_lifecycle_not_enabled",
        },
        {
            "actionId": "clear_conversation",
            "label": "clear conversation",
            "groupId": "conversation_actions",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_transcript_policy",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_transcript_delete",
            "blockedReasonRef": "transcript_store_not_configured",
        },
        {
            "actionId": "export_transcript",
            "label": "export transcript",
            "groupId": "transcript_actions",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_transcript_policy",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_transcript_export",
            "blockedReasonRef": "transcript_export_not_reviewed",
        },
        {
            "actionId": "retry_response",
            "label": "retry response",
            "groupId": "message_actions",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_send_result",
            "resultState": "not_generated",
            "sideEffectPolicy": "no_send_or_runtime_execution",
            "blockedReasonRef": "response_stream_blocked",
        },
        {
            "actionId": "copy_response",
            "label": "copy response",
            "groupId": "message_actions",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_message_list",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_clipboard_write",
            "blockedReasonRef": "message_content_absent",
        },
        {
            "actionId": "stop_response",
            "label": "stop response",
            "groupId": "runtime_actions",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_response_stream",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_stop_signal",
            "blockedReasonRef": "runtime_stream_not_started",
        },
        {
            "actionId": "attach_context",
            "label": "attach context",
            "groupId": "attachment_actions",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_composer",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_file_or_artifact_read",
            "blockedReasonRef": "attachment_boundary_absent",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "session_lifecycle_not_enabled",
            "state": "blocked",
            "summary": "Session creation and lifecycle actions remain disabled.",
            "requiredBefore": "new_chat_enabled",
        },
        {
            "reasonId": "transcript_store_not_configured",
            "state": "not_configured",
            "summary": "No reviewed transcript store or retention rule exists.",
            "requiredBefore": "clear_conversation_enabled",
        },
        {
            "reasonId": "transcript_export_not_reviewed",
            "state": "not_configured",
            "summary": "Transcript export needs explicit storage and redaction boundaries.",
            "requiredBefore": "export_transcript_enabled",
        },
        {
            "reasonId": "message_content_absent",
            "state": "empty_not_captured",
            "summary": "No prompt, response, transcript, or message body content is present.",
            "requiredBefore": "copy_or_retry_enabled",
        },
        {
            "reasonId": "response_stream_blocked",
            "state": "blocked",
            "summary": "The checked response-stream boundary reports no generated chunks.",
            "requiredBefore": "retry_response_enabled",
        },
        {
            "reasonId": "runtime_stream_not_started",
            "state": "not_started",
            "summary": "No local response stream exists, so stop cannot send a signal.",
            "requiredBefore": "stop_response_enabled",
        },
        {
            "reasonId": "attachment_boundary_absent",
            "state": "planned",
            "summary": "No reviewed local artifact input boundary exists for attachments.",
            "requiredBefore": "attach_context_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_session",
            "schemaVersion": "pccx.chatSession.v0",
            "fixturePath": "contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json",
            "state": "inactive",
            "summary": "Session state is consumed as local metadata only.",
        },
        {
            "refId": "chat_session_lifecycle",
            "schemaVersion": "pccx.chatSessionLifecycle.v0",
            "fixturePath": "contracts/fixtures/chat-session-lifecycle.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Session lifecycle actions remain disabled or blocked.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Readiness data keeps action controls disabled.",
        },
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Composer data keeps attach and send-adjacent actions disabled.",
        },
        {
            "refId": "chat_send_result",
            "schemaVersion": "pccx.chatSendResult.v0",
            "fixturePath": "contracts/fixtures/chat-send-result.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Blocked send-result data prevents retry actions.",
        },
        {
            "refId": "chat_response_stream",
            "schemaVersion": "pccx.chatResponseStream.v0",
            "fixturePath": "contracts/fixtures/chat-response-stream.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Blocked stream data prevents stop and retry controls.",
        },
        {
            "refId": "chat_message_list",
            "schemaVersion": "pccx.chatMessageList.v0",
            "fixturePath": "contracts/fixtures/chat-message-list.gemma3n-e4b-kv260-placeholder.json",
            "state": "empty_not_captured",
            "summary": "Empty message-list data prevents copy actions.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Transcript persistence and export remain unavailable.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "actionBarDisplayOnly": True,
        "actionMetadataOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "readsSessionStore": False,
        "readsTranscript": False,
        "transcriptPersistence": False,
        "transcriptExport": False,
        "sessionPersistence": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
        "conversationCreated": False,
        "conversationCleared": False,
        "messageDeleted": False,
        "attachmentReads": False,
        "fileUpload": False,
        "clipboardRead": False,
        "clipboardWrite": False,
        "promptCapture": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "promptPersistence": False,
        "inputAccepted": False,
        "sendAttempted": False,
        "retryAttempted": False,
        "stopSignalSent": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "responseChunksEmitted": False,
        "messageBodiesIncluded": False,
        "modelAssetRead": False,
        "modelAssetPathsIncluded": False,
        "modelWeightPathsIncluded": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "touchesHardware": False,
        "hardwareAccess": False,
        "kv260Access": False,
        "opensSerialPort": False,
        "networkCalls": False,
        "networkScan": False,
        "sshExecution": False,
        "providerCalls": False,
        "cloudCalls": False,
        "configRead": False,
        "environmentRead": False,
        "providerConfigRead": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
        "generatedBlobsIncluded": False,
        "hardwareDumpsIncluded": False,
        "runtimeLogsIncluded": False,
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
        "Data-only chat action-bar fixture; no prompt, response, transcript, summary, session title, model path, runtime log, file, or clipboard content is read or written.",
        "New chat, clear, export, retry, copy, stop, and attach controls remain disabled, blocked, unavailable, or planned.",
        "No session store, transcript, message bodies, attachments, artifacts, private paths, secrets, tokens, logs, or hardware dumps are read or written.",
        "No send attempt, retry, stop signal, response stream, model load, runtime execution, provider call, network call, or KV260 hardware access is performed.",
        "This is not a release, tag, compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, or runtime implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_action_bar() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat action-bar fixture."""
    return copy.deepcopy(_CHAT_ACTION_BAR)


def chat_action_bar_json(action_bar: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        action_bar
        if action_bar is not None
        else create_gemma3n_e4b_kv260_chat_action_bar(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat action-bar JSON.",
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
    sys.stdout.write(chat_action_bar_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
