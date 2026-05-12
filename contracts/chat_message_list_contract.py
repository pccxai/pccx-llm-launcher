#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat message-list contract for the planned launcher UI.

The contract describes the empty conversation viewport for the standalone
chat surface. It does not read prompts, responses, transcripts, session
stores, summaries, model assets, private paths, logs, or artifacts; it does
not capture input, generate responses, start runtime code, load models, touch
KV260 hardware, call providers, invoke pccx-lab, or persist anything.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatMessageList.v0"
MESSAGE_COLLECTION_SCHEMA_VERSION = "pccx.chatMessageCollection.v0"

CHAT_MESSAGE_LIST_FIELDS = (
    "schemaVersion",
    "messageListId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "listState",
    "viewportState",
    "transcriptState",
    "messageContentState",
    "emptyState",
    "selectionState",
    "scrollState",
    "chatSessionRef",
    "chatReadinessRef",
    "chatSendResultRef",
    "chatResponseStreamRef",
    "chatTranscriptPolicyRef",
    "listPolicy",
    "messageCollection",
    "viewportSlots",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

LIST_POLICY_FIELDS = (
    "state",
    "renderMode",
    "sourcePolicy",
    "contentPolicy",
    "interactionPolicy",
    "sideEffectPolicy",
    "persistencePolicy",
)

MESSAGE_COLLECTION_FIELDS = (
    "schemaVersion",
    "collectionId",
    "state",
    "itemCount",
    "promptMessagesIncluded",
    "assistantMessagesIncluded",
    "systemNoticesIncluded",
    "messageBodiesIncluded",
    "transcriptReadEnabled",
    "sortOrder",
    "summary",
)

VIEWPORT_SLOT_FIELDS = (
    "slotId",
    "label",
    "state",
    "visible",
    "enabled",
    "sourceRef",
    "displayPolicy",
    "contentPolicy",
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

CHAT_MESSAGE_LIST_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty",
    "empty_not_captured",
    "inactive",
    "not_configured",
    "not_generated",
    "not_loaded",
    "not_started",
    "placeholder",
    "planned",
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_MESSAGE_LIST = {
    "schemaVersion": SCHEMA_VERSION,
    "messageListId": "chat_message_list_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-message-list.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_message_list_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "listState": "empty_not_captured",
    "viewportState": "placeholder",
    "transcriptState": "not_started",
    "messageContentState": "empty_not_captured",
    "emptyState": "available_as_data",
    "selectionState": "disabled",
    "scrollState": "disabled",
    "chatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "chatSendResultRef": "chat_send_result_gemma3n_e4b_kv260_placeholder",
    "chatResponseStreamRef": "chat_response_stream_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "listPolicy": {
        "state": "placeholder",
        "renderMode": "future_local_message_viewport",
        "sourcePolicy": "checked fixture only; no session store, transcript, prompt, response, summary, or model path is read",
        "contentPolicy": "empty message collection metadata only; no message bodies are included",
        "interactionPolicy": "selection, scrolling, transcript append, and message actions remain disabled",
        "sideEffectPolicy": "local_render_only",
        "persistencePolicy": "no transcript persistence or export",
    },
    "messageCollection": {
        "schemaVersion": MESSAGE_COLLECTION_SCHEMA_VERSION,
        "collectionId": "empty_message_collection_gemma3n_e4b_kv260_placeholder",
        "state": "empty",
        "itemCount": 0,
        "promptMessagesIncluded": False,
        "assistantMessagesIncluded": False,
        "systemNoticesIncluded": False,
        "messageBodiesIncluded": False,
        "transcriptReadEnabled": False,
        "sortOrder": "future_session_local_order",
        "summary": "No conversation messages are present or read by this fixture.",
    },
    "viewportSlots": [
        {
            "slotId": "empty_conversation_notice",
            "label": "empty conversation notice",
            "state": "available_as_data",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_session",
            "displayPolicy": "show empty local conversation state only",
            "contentPolicy": "no_prompt_response_transcript_or_summary_content",
        },
        {
            "slotId": "assistant_response_placeholder",
            "label": "assistant response placeholder",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_response_stream",
            "displayPolicy": "show blocked response-stream state only",
            "contentPolicy": "no_generated_response_content",
        },
        {
            "slotId": "send_feedback_placeholder",
            "label": "send feedback placeholder",
            "state": "blocked",
            "visible": False,
            "enabled": False,
            "sourceRef": "chat_send_result",
            "displayPolicy": "hidden until a reviewed send-result exists",
            "contentPolicy": "no_prompt_echo_or_response_content",
        },
        {
            "slotId": "transcript_policy_notice",
            "label": "transcript policy notice",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_transcript_policy",
            "displayPolicy": "show disabled persistence/export state",
            "contentPolicy": "policy_metadata_only",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "session_inactive",
            "state": "inactive",
            "summary": "No launcher-owned chat session exists for message rendering.",
            "requiredBefore": "message_collection_loaded",
        },
        {
            "reasonId": "transcript_source_not_configured",
            "state": "not_configured",
            "summary": "No reviewed transcript or session-store reader exists.",
            "requiredBefore": "message_bodies_available",
        },
        {
            "reasonId": "send_result_blocked",
            "state": "blocked",
            "summary": "The checked send-result boundary reports no accepted input.",
            "requiredBefore": "user_message_appended",
        },
        {
            "reasonId": "response_stream_blocked",
            "state": "blocked",
            "summary": "The checked response-stream boundary reports no generated response.",
            "requiredBefore": "assistant_message_appended",
        },
        {
            "reasonId": "message_content_policy_disabled",
            "state": "disabled",
            "summary": "Prompt, response, transcript, and summary content remain outside checked fixtures.",
            "requiredBefore": "message_content_displayed",
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
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Readiness data keeps message actions disabled.",
        },
        {
            "refId": "chat_send_result",
            "schemaVersion": "pccx.chatSendResult.v0",
            "fixturePath": "contracts/fixtures/chat-send-result.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Blocked send-result data prevents user-message append.",
        },
        {
            "refId": "chat_response_stream",
            "schemaVersion": "pccx.chatResponseStream.v0",
            "fixturePath": "contracts/fixtures/chat-response-stream.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Blocked response-stream data prevents assistant-message append.",
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
        "messageListDisplayOnly": True,
        "messageMetadataOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "readsSessionStore": False,
        "readsTranscript": False,
        "transcriptPersistence": False,
        "transcriptExport": False,
        "sessionPersistence": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
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
        "responseContentIncluded": False,
        "responseGenerated": False,
        "responseChunksEmitted": False,
        "messageBodiesIncluded": False,
        "messageCountFromStore": False,
        "summaryIncluded": False,
        "summaryGenerated": False,
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
        "Data-only empty chat message-list fixture; no prompt, response, transcript, summary, session title, model path, or runtime log content is read or written.",
        "No transcript or session-store reader is implemented, no message bodies are included, and item count is fixed to zero.",
        "No send attempt, response stream, model load, runtime execution, provider call, network call, or KV260 hardware access is performed.",
        "No artifacts, private paths, secrets, tokens, stores, logs, or hardware dumps are read or written.",
        "This is not a release, tag, compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, or runtime implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_message_list() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat message-list fixture."""
    return copy.deepcopy(_CHAT_MESSAGE_LIST)


def chat_message_list_json(message_list: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        message_list
        if message_list is not None
        else create_gemma3n_e4b_kv260_chat_message_list(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat message-list JSON.",
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
    sys.stdout.write(chat_message_list_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
