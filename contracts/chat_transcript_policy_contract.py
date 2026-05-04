#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only transcript policy contract for the planned launcher chat UI.

The contract describes retention, export, and privacy policy state for future
chat transcripts. It does not read, accept, echo, store, persist, summarize, or
export prompt or response content. It also does not load models, start runtime
code, touch KV260 hardware, call providers, invoke pccx-lab, or read/write
artifacts.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatTranscriptPolicy.v0"

CHAT_TRANSCRIPT_POLICY_FIELDS = (
    "schemaVersion",
    "transcriptPolicyId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "transcriptState",
    "messageContentState",
    "retentionState",
    "exportState",
    "storageState",
    "privacyState",
    "parentChatSessionRef",
    "chatSessionLifecycleRef",
    "chatSendResultRef",
    "retentionPolicy",
    "contentPolicy",
    "exportPolicy",
    "uiSurfaces",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

RETENTION_POLICY_FIELDS = (
    "state",
    "localStoreConfigured",
    "sessionPersistence",
    "transcriptPersistence",
    "retentionDays",
    "deleteOnClose",
    "summary",
)

CONTENT_POLICY_FIELDS = (
    "state",
    "contentIncluded",
    "promptContentIncluded",
    "responseContentIncluded",
    "messageBodiesIncluded",
    "summaryIncluded",
    "redactionPolicy",
)

EXPORT_POLICY_FIELDS = (
    "state",
    "exportEnabled",
    "exportFormats",
    "summaryExportState",
    "contentExportState",
    "requiresExplicitUserAction",
    "summary",
)

UI_SURFACE_FIELDS = (
    "surfaceId",
    "state",
    "enabled",
    "userVisibleSummary",
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

CHAT_TRANSCRIPT_POLICY_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "inactive",
    "not_configured",
    "not_generated",
    "not_loaded",
    "not_started",
    "not_used",
    "placeholder",
    "planned",
    "requires_evidence",
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_TRANSCRIPT_POLICY = {
    "schemaVersion": SCHEMA_VERSION,
    "transcriptPolicyId": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-transcript-policy.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_transcript_policy_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "transcriptState": "disabled",
    "messageContentState": "empty_not_captured",
    "retentionState": "not_configured",
    "exportState": "disabled",
    "storageState": "not_configured",
    "privacyState": "available_as_data",
    "parentChatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "chatSessionLifecycleRef": "chat_session_lifecycle_gemma3n_e4b_kv260_placeholder",
    "chatSendResultRef": "chat_send_result_gemma3n_e4b_kv260_placeholder",
    "retentionPolicy": {
        "state": "not_configured",
        "localStoreConfigured": False,
        "sessionPersistence": False,
        "transcriptPersistence": False,
        "retentionDays": None,
        "deleteOnClose": False,
        "summary": "No reviewed local transcript store, retention period, or deletion rule exists.",
    },
    "contentPolicy": {
        "state": "empty_not_captured",
        "contentIncluded": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "messageBodiesIncluded": False,
        "summaryIncluded": False,
        "redactionPolicy": "checked fixtures and status summaries contain policy metadata only",
    },
    "exportPolicy": {
        "state": "disabled",
        "exportEnabled": False,
        "exportFormats": [],
        "summaryExportState": "blocked",
        "contentExportState": "unavailable",
        "requiresExplicitUserAction": True,
        "summary": "Transcript export stays disabled until storage, redaction, and explicit user-action boundaries exist.",
    },
    "uiSurfaces": [
        {
            "surfaceId": "transcript_panel",
            "state": "placeholder",
            "enabled": False,
            "userVisibleSummary": "Show transcript policy status without message content.",
            "sideEffectPolicy": "local_render_only",
        },
        {
            "surfaceId": "retention_notice",
            "state": "available_as_data",
            "enabled": True,
            "userVisibleSummary": "Report that transcript persistence is not configured.",
            "sideEffectPolicy": "local_render_only",
        },
        {
            "surfaceId": "export_transcript",
            "state": "disabled",
            "enabled": False,
            "userVisibleSummary": "Export remains disabled.",
            "sideEffectPolicy": "no_artifact_write",
        },
        {
            "surfaceId": "delete_transcript",
            "state": "inactive",
            "enabled": False,
            "userVisibleSummary": "Delete remains inactive because no transcript is stored.",
            "sideEffectPolicy": "no_artifact_delete",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "session_store_not_configured",
            "state": "not_configured",
            "summary": "No reviewed local session or transcript store exists.",
            "requiredBefore": "transcript_persistence_enabled",
        },
        {
            "reasonId": "prompt_capture_disabled",
            "state": "disabled",
            "summary": "Prompt capture, echo, and persistence remain disabled.",
            "requiredBefore": "message_content_can_exist",
        },
        {
            "reasonId": "response_generation_absent",
            "state": "not_generated",
            "summary": "No assistant response is generated by the launcher fixture.",
            "requiredBefore": "response_content_can_exist",
        },
        {
            "reasonId": "redaction_export_rule_missing",
            "state": "planned",
            "summary": "Export requires a reviewed redaction and explicit user-action policy.",
            "requiredBefore": "summary_or_content_export_enabled",
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
            "refId": "chat_session_lifecycle",
            "schemaVersion": "pccx.chatSessionLifecycle.v0",
            "fixturePath": "contracts/fixtures/chat-session-lifecycle.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Lifecycle export-summary and persistence actions remain disabled or blocked.",
        },
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Composer input remains empty and not captured.",
        },
        {
            "refId": "chat_send_result",
            "schemaVersion": "pccx.chatSendResult.v0",
            "fixturePath": "contracts/fixtures/chat-send-result.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Send result contains no prompt or response content.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "transcriptPolicyDisplayOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "attachmentReads": False,
        "fileUpload": False,
        "clipboardRead": False,
        "clipboardWrite": False,
        "promptCapture": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "promptPersistence": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "messageBodiesIncluded": False,
        "summaryGenerated": False,
        "transcriptPersistence": False,
        "sessionPersistence": False,
        "transcriptExport": False,
        "localStoreConfigured": False,
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
        "Data-only transcript policy fixture; no prompt, response, message, transcript, or summary content is read, generated, exported, stored, or persisted.",
        "No reviewed local session store, retention period, redaction rule, or transcript export path exists in this boundary.",
        "No model path, generated artifact, private path, secret, token, raw log, or hardware dump is read or written.",
        "No KV260 hardware access, serial access, SSH execution, network call, provider call, telemetry, upload, or write-back is performed.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_transcript_policy() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 transcript policy fixture."""
    return copy.deepcopy(_CHAT_TRANSCRIPT_POLICY)


def chat_transcript_policy_json(policy: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        policy if policy is not None else create_gemma3n_e4b_kv260_chat_transcript_policy(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat transcript policy JSON.",
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
    sys.stdout.write(chat_transcript_policy_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
