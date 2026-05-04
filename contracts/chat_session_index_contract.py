#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat session index contract for the planned launcher UI.

The contract describes the future session list/sidebar boundary while every
store-backed operation remains disabled or blocked. It does not read session
manifests, titles, prompts, transcripts, model assets, private paths, or logs;
it does not write artifacts, load models, touch KV260 hardware, call providers,
invoke pccx-lab, or start runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatSessionIndex.v0"

CHAT_SESSION_INDEX_FIELDS = (
    "schemaVersion",
    "sessionIndexId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "indexState",
    "sessionStoreState",
    "manifestState",
    "selectionState",
    "restoreState",
    "contentState",
    "privacyState",
    "parentChatSessionRef",
    "chatSessionLifecycleRef",
    "chatTranscriptPolicyRef",
    "indexPolicy",
    "emptyState",
    "indexControls",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

INDEX_POLICY_FIELDS = (
    "state",
    "localStoreConfigured",
    "manifestReadEnabled",
    "transcriptReadEnabled",
    "titlePolicy",
    "pathPolicy",
    "refreshPolicy",
    "sideEffectPolicy",
)

EMPTY_STATE_FIELDS = (
    "state",
    "itemCount",
    "displayKind",
    "userVisibleSummary",
    "sideEffectPolicy",
    "contentPolicy",
)

INDEX_CONTROL_FIELDS = (
    "controlId",
    "label",
    "state",
    "enabled",
    "userAction",
    "launcherAction",
    "sideEffectPolicy",
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

CHAT_SESSION_INDEX_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "inactive",
    "not_configured",
    "not_loaded",
    "not_started",
    "placeholder",
    "planned",
    "redacted",
    "requires_evidence",
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_SESSION_INDEX = {
    "schemaVersion": SCHEMA_VERSION,
    "sessionIndexId": "chat_session_index_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-session-index.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_session_index_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "indexState": "not_configured",
    "sessionStoreState": "not_configured",
    "manifestState": "unavailable",
    "selectionState": "disabled",
    "restoreState": "unavailable",
    "contentState": "empty_not_captured",
    "privacyState": "summary_only",
    "parentChatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "chatSessionLifecycleRef": "chat_session_lifecycle_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "indexPolicy": {
        "state": "not_configured",
        "localStoreConfigured": False,
        "manifestReadEnabled": False,
        "transcriptReadEnabled": False,
        "titlePolicy": "session titles are not read, generated, summarized, or emitted by this fixture",
        "pathPolicy": "no session-store, transcript, model, user, or workspace paths are configured, read, or emitted",
        "refreshPolicy": "future refresh requires an explicit reviewed local session-store boundary",
        "sideEffectPolicy": "local_render_only",
    },
    "emptyState": {
        "state": "placeholder",
        "itemCount": 0,
        "displayKind": "no_sessions_available",
        "userVisibleSummary": "Show an empty local session index without reading a store.",
        "sideEffectPolicy": "local_render_only",
        "contentPolicy": "no_session_titles_summaries_prompts_responses_or_transcripts",
    },
    "indexControls": [
        {
            "controlId": "open_session_index",
            "label": "open session index",
            "state": "available_as_data",
            "enabled": True,
            "userAction": "Open the local chat session list surface.",
            "launcherAction": "Render deterministic empty index state from checked fixture data.",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "metadata_only_no_session_content",
        },
        {
            "controlId": "refresh_session_index",
            "label": "refresh session index",
            "state": "blocked",
            "enabled": False,
            "userAction": "Refresh only after a reviewed local session-store boundary exists.",
            "launcherAction": "Refuse refresh because no manifest read boundary exists.",
            "sideEffectPolicy": "no_artifact_read_no_write",
            "contentPolicy": "no_manifest_title_or_transcript_content",
        },
        {
            "controlId": "select_session",
            "label": "select session",
            "state": "disabled",
            "enabled": False,
            "userAction": "Select only a future indexed local session.",
            "launcherAction": "Keep selection disabled because the index is empty.",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_session_identifier_from_user_store",
        },
        {
            "controlId": "restore_selected_session",
            "label": "restore selected session",
            "state": "unavailable",
            "enabled": False,
            "userAction": "Restore only after a session manifest boundary exists.",
            "launcherAction": "Refuse restore because no indexed session exists.",
            "sideEffectPolicy": "no_artifact_read_no_write",
            "contentPolicy": "no_session_manifest_or_transcript_content",
        },
        {
            "controlId": "rename_session",
            "label": "rename session",
            "state": "disabled",
            "enabled": False,
            "userAction": "Rename only after explicit local store and title policy review.",
            "launcherAction": "Keep rename disabled because no session title exists.",
            "sideEffectPolicy": "no_write",
            "contentPolicy": "no_title_capture_or_generation",
        },
        {
            "controlId": "delete_session",
            "label": "delete session",
            "state": "inactive",
            "enabled": False,
            "userAction": "Delete only a future launcher-owned local session.",
            "launcherAction": "No-op because no indexed session or local store exists.",
            "sideEffectPolicy": "no_artifact_delete",
            "contentPolicy": "no_transcript_mutation",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "session_store_not_configured",
            "state": "not_configured",
            "summary": "No reviewed local chat session store exists.",
            "requiredBefore": "session_index_refresh_enabled",
        },
        {
            "reasonId": "session_manifest_boundary_absent",
            "state": "planned",
            "summary": "A checked session manifest shape is required before list items can be read.",
            "requiredBefore": "session_list_items_available",
        },
        {
            "reasonId": "session_titles_not_captured",
            "state": "empty_not_captured",
            "summary": "Session titles, summaries, prompts, and responses remain outside checked fixture data.",
            "requiredBefore": "session_display_names_available",
        },
        {
            "reasonId": "active_session_absent",
            "state": "inactive",
            "summary": "No launcher-owned local chat session is active or selectable.",
            "requiredBefore": "selection_or_restore_enabled",
        },
        {
            "reasonId": "artifact_read_boundary_absent",
            "state": "requires_evidence",
            "summary": "Refreshing a real index requires an explicit artifact-read boundary and tests.",
            "requiredBefore": "refresh_session_index_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_session",
            "schemaVersion": "pccx.chatSession.v0",
            "fixturePath": "contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Base chat/session surface is referenced without message content.",
        },
        {
            "refId": "chat_session_lifecycle",
            "schemaVersion": "pccx.chatSessionLifecycle.v0",
            "fixturePath": "contracts/fixtures/chat-session-lifecycle.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Lifecycle restore, clear, close, and export actions remain disabled or blocked.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Transcript persistence and export remain disabled.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Readiness gates stay separate from index display state.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "sessionIndexDisplayOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "readsSessionManifest": False,
        "readsTranscript": False,
        "sessionPersistence": False,
        "transcriptPersistence": False,
        "transcriptExport": False,
        "sessionRestoreImplemented": False,
        "sessionDeleteImplemented": False,
        "sessionRenameImplemented": False,
        "localStoreConfigured": False,
        "sessionTitleIncluded": False,
        "sessionTitleGenerated": False,
        "messageBodiesIncluded": False,
        "summaryIncluded": False,
        "summaryGenerated": False,
        "promptCapture": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "promptPersistence": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "attachmentReads": False,
        "fileUpload": False,
        "clipboardRead": False,
        "clipboardWrite": False,
        "modelAssetPathsIncluded": False,
        "modelWeightPathsIncluded": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "runtimeExecution": False,
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
        "Data-only chat session index fixture; no real session store is configured or read.",
        "No session titles, summaries, prompts, responses, transcripts, manifests, model paths, generated artifacts, private paths, secrets, or tokens are stored.",
        "No artifacts are read, written, deleted, refreshed, imported, exported, or persisted.",
        "No KV260 hardware access, serial access, network call, provider call, telemetry, upload, or write-back is performed.",
        "Selection, restore, rename, delete, and refresh controls remain disabled, unavailable, inactive, or blocked until explicit evidence and reviewed boundaries exist.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, or session-store implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_session_index() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 session-index fixture."""
    return copy.deepcopy(_CHAT_SESSION_INDEX)


def chat_session_index_json(status: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        status
        if status is not None
        else create_gemma3n_e4b_kv260_chat_session_index(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat session index JSON.",
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
    sys.stdout.write(chat_session_index_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
