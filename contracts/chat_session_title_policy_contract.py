#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat session-title policy contract for the planned launcher UI.

The contract describes placeholder session display names and blocked title
generation/rename behavior for the future standalone chat surface. It does
not read session stores, manifests, titles, summaries, prompts, transcripts,
model assets, private paths, or logs; it does not write artifacts, load
models, touch KV260 hardware, call providers, invoke pccx-lab, or start
runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatSessionTitlePolicy.v0"

CHAT_SESSION_TITLE_POLICY_FIELDS = (
    "schemaVersion",
    "titlePolicyId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "titlePolicyState",
    "titleSourceState",
    "titleDisplayState",
    "generationState",
    "renameState",
    "privacyState",
    "parentChatSessionRef",
    "chatSessionIndexRef",
    "chatSessionLifecycleRef",
    "chatTranscriptPolicyRef",
    "titlePolicy",
    "placeholderTitle",
    "titleControls",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

TITLE_POLICY_FIELDS = (
    "state",
    "displayMode",
    "placeholderSource",
    "titleReadEnabled",
    "titleGenerationEnabled",
    "titleRenameEnabled",
    "titlePersistenceEnabled",
    "summaryReadEnabled",
    "sideEffectPolicy",
    "contentPolicy",
)

PLACEHOLDER_TITLE_FIELDS = (
    "state",
    "placeholderId",
    "displayKind",
    "labelTemplate",
    "source",
    "contentIncluded",
    "userVisibleSummary",
    "sideEffectPolicy",
)

TITLE_CONTROL_FIELDS = (
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

CHAT_SESSION_TITLE_POLICY_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "inactive",
    "not_configured",
    "placeholder",
    "planned",
    "redacted",
    "requires_evidence",
    "summary_only",
    "unavailable",
)

_CHAT_SESSION_TITLE_POLICY = {
    "schemaVersion": SCHEMA_VERSION,
    "titlePolicyId": "chat_session_title_policy_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-session-title-policy.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_session_title_policy_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "titlePolicyState": "available_as_data",
    "titleSourceState": "not_configured",
    "titleDisplayState": "placeholder",
    "generationState": "blocked",
    "renameState": "disabled",
    "privacyState": "summary_only",
    "parentChatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "chatSessionIndexRef": "chat_session_index_gemma3n_e4b_kv260_placeholder",
    "chatSessionLifecycleRef": "chat_session_lifecycle_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "titlePolicy": {
        "state": "available_as_data",
        "displayMode": "placeholder_only",
        "placeholderSource": "deterministic_fixture_label",
        "titleReadEnabled": False,
        "titleGenerationEnabled": False,
        "titleRenameEnabled": False,
        "titlePersistenceEnabled": False,
        "summaryReadEnabled": False,
        "sideEffectPolicy": "local_render_only",
        "contentPolicy": "no_stored_titles_summaries_prompts_responses_or_transcripts",
    },
    "placeholderTitle": {
        "state": "placeholder",
        "placeholderId": "untitled_local_chat_placeholder",
        "displayKind": "static_placeholder_label",
        "labelTemplate": "Untitled local chat",
        "source": "fixture_static_value_not_session_store",
        "contentIncluded": False,
        "userVisibleSummary": "Render a deterministic placeholder label without reading a session title.",
        "sideEffectPolicy": "local_render_only",
    },
    "titleControls": [
        {
            "controlId": "render_placeholder_title",
            "label": "render placeholder title",
            "state": "available_as_data",
            "enabled": True,
            "userAction": "Open the chat surface or session sidebar.",
            "launcherAction": "Render the static placeholder label from checked fixture data.",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "static_placeholder_only",
        },
        {
            "controlId": "read_stored_title",
            "label": "read stored title",
            "state": "blocked",
            "enabled": False,
            "userAction": "Read stored titles only after a reviewed local session-store boundary exists.",
            "launcherAction": "Refuse session-title reads because no manifest/title boundary exists.",
            "sideEffectPolicy": "no_artifact_read_no_write",
            "contentPolicy": "no_title_summary_or_transcript_content",
        },
        {
            "controlId": "generate_title",
            "label": "generate title",
            "state": "blocked",
            "enabled": False,
            "userAction": "Generate a title only after prompt/response redaction and model boundaries are reviewed.",
            "launcherAction": "Refuse title generation because no prompt, response, summary, or model path may be read.",
            "sideEffectPolicy": "no_model_or_runtime_execution",
            "contentPolicy": "no_prompt_response_summary_or_title_generation",
        },
        {
            "controlId": "rename_title",
            "label": "rename title",
            "state": "disabled",
            "enabled": False,
            "userAction": "Rename only after explicit local store and write policy review.",
            "launcherAction": "Keep rename disabled because no write boundary exists.",
            "sideEffectPolicy": "no_write",
            "contentPolicy": "no_title_capture_or_persistence",
        },
        {
            "controlId": "persist_title",
            "label": "persist title",
            "state": "disabled",
            "enabled": False,
            "userAction": "Persist only a reviewed title value after a local session-store boundary exists.",
            "launcherAction": "Refuse persistence because no session-store write boundary exists.",
            "sideEffectPolicy": "no_artifact_write",
            "contentPolicy": "no_title_storage",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "session_store_not_configured",
            "state": "not_configured",
            "summary": "No reviewed local chat session store exists.",
            "requiredBefore": "stored_session_title_available",
        },
        {
            "reasonId": "session_title_read_boundary_absent",
            "state": "planned",
            "summary": "A checked session-title read shape is required before stored display names can be shown.",
            "requiredBefore": "read_stored_title_enabled",
        },
        {
            "reasonId": "title_generation_not_reviewed",
            "state": "blocked",
            "summary": "Title generation would require prompt/response redaction, model, runtime, and persistence review.",
            "requiredBefore": "generate_title_enabled",
        },
        {
            "reasonId": "rename_write_boundary_absent",
            "state": "requires_evidence",
            "summary": "Renaming needs an explicit local write boundary, validation, and rollback policy.",
            "requiredBefore": "rename_title_enabled",
        },
        {
            "reasonId": "summary_content_unavailable",
            "state": "empty_not_captured",
            "summary": "No prompt, response, transcript, or summary content is available for title derivation.",
            "requiredBefore": "title_summary_source_available",
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
            "refId": "chat_session_index",
            "schemaVersion": "pccx.chatSessionIndex.v0",
            "fixturePath": "contracts/fixtures/chat-session-index.gemma3n-e4b-kv260-placeholder.json",
            "state": "not_configured",
            "summary": "Session index remains empty and does not read stored titles.",
        },
        {
            "refId": "chat_session_lifecycle",
            "schemaVersion": "pccx.chatSessionLifecycle.v0",
            "fixturePath": "contracts/fixtures/chat-session-lifecycle.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Lifecycle create, restore, clear, close, and export actions remain disabled or blocked.",
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
            "summary": "Readiness remains separate from title display policy.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "sessionTitlePolicyDisplayOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "readsSessionManifest": False,
        "readsSessionTitle": False,
        "readsTranscript": False,
        "sessionStoreRead": False,
        "sessionPersistence": False,
        "titleContentIncluded": False,
        "sessionTitleIncluded": False,
        "sessionTitleGenerated": False,
        "titleRenameImplemented": False,
        "titlePersistence": False,
        "transcriptPersistence": False,
        "transcriptExport": False,
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
        "Data-only chat session-title policy fixture; no real session store is configured or read.",
        "Only a static placeholder label is present; no stored title, generated title, summary, prompt, response, transcript, manifest, model path, private path, secret, or token content is included.",
        "No title is generated, renamed, persisted, imported, exported, refreshed, or written.",
        "No artifacts are read, written, deleted, or persisted.",
        "No KV260 hardware access, serial access, network call, provider call, telemetry, upload, or write-back is performed.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, runtime, model, or session-store implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_session_title_policy() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 title-policy fixture."""
    return copy.deepcopy(_CHAT_SESSION_TITLE_POLICY)


def chat_session_title_policy_json(status: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        status
        if status is not None
        else create_gemma3n_e4b_kv260_chat_session_title_policy(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat session-title policy JSON.",
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
    sys.stdout.write(chat_session_title_policy_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
