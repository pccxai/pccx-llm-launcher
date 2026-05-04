#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat surface layout contract for the planned launcher UI.

The contract describes the future standalone chat shell regions and navigation
items while keeping every runtime, model, store, and content path disabled or
blocked. It does not read prompts, responses, transcripts, session stores,
session titles, model assets, private paths, or logs; it does not write
artifacts, load models, touch KV260 hardware, call providers, invoke pccx-lab,
or start runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatSurfaceLayout.v0"

CHAT_SURFACE_LAYOUT_FIELDS = (
    "schemaVersion",
    "layoutId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "layoutState",
    "shellState",
    "navigationState",
    "primaryRegionState",
    "sideRegionState",
    "footerState",
    "contentState",
    "privacyState",
    "chatSessionRef",
    "chatSessionIndexRef",
    "chatModelStatusRef",
    "chatReadinessRef",
    "chatComposerRef",
    "chatSendResultRef",
    "chatTranscriptPolicyRef",
    "chatAuditEventRef",
    "layoutPolicy",
    "surfaceRegions",
    "navigationItems",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

LAYOUT_POLICY_FIELDS = (
    "state",
    "renderMode",
    "shellPolicy",
    "contentPolicy",
    "interactionPolicy",
    "sideEffectPolicy",
    "externalDependencyPolicy",
)

SURFACE_REGION_FIELDS = (
    "regionId",
    "label",
    "state",
    "visible",
    "enabled",
    "sourceRef",
    "layoutRole",
    "sideEffectPolicy",
    "contentPolicy",
)

NAVIGATION_ITEM_FIELDS = (
    "navId",
    "label",
    "state",
    "enabled",
    "targetRegion",
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

CHAT_SURFACE_LAYOUT_STATE_VALUES = (
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
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_SURFACE_LAYOUT = {
    "schemaVersion": SCHEMA_VERSION,
    "layoutId": "chat_surface_layout_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-surface-layout.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_surface_layout_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "layoutState": "blocked",
    "shellState": "placeholder",
    "navigationState": "available_as_data",
    "primaryRegionState": "empty_not_captured",
    "sideRegionState": "placeholder",
    "footerState": "available_as_data",
    "contentState": "empty_not_captured",
    "privacyState": "summary_only",
    "chatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "chatSessionIndexRef": "chat_session_index_gemma3n_e4b_kv260_placeholder",
    "chatModelStatusRef": "chat_model_status_gemma3n_e4b_kv260_placeholder",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatSendResultRef": "chat_send_result_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "chatAuditEventRef": "chat_audit_event_gemma3n_e4b_kv260_placeholder",
    "layoutPolicy": {
        "state": "placeholder",
        "renderMode": "future_local_shell_layout",
        "shellPolicy": "deterministic layout metadata only; no app shell implementation is started",
        "contentPolicy": "no_prompt_response_transcript_summary_session_title_or_model_path_content",
        "interactionPolicy": "navigation metadata may be rendered while runtime and content actions remain disabled",
        "sideEffectPolicy": "local_render_only",
        "externalDependencyPolicy": "no provider, network, hardware, pccx-lab, or IDE dependency is used",
    },
    "surfaceRegions": [
        {
            "regionId": "session_index_sidebar",
            "label": "session index sidebar",
            "state": "placeholder",
            "visible": True,
            "enabled": True,
            "sourceRef": "chat_session_index",
            "layoutRole": "side_navigation",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_session_titles_summaries_prompts_responses_or_transcripts",
        },
        {
            "regionId": "model_status_header",
            "label": "model status header",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_model_status",
            "layoutRole": "status",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "descriptor_metadata_only_no_model_paths",
        },
        {
            "regionId": "readiness_banner",
            "label": "readiness banner",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_readiness",
            "layoutRole": "readiness",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "readiness_metadata_only",
        },
        {
            "regionId": "transcript_region",
            "label": "transcript region",
            "state": "empty_not_captured",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_transcript_policy",
            "layoutRole": "primary",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_message_transcript_or_summary_content",
        },
        {
            "regionId": "composer_bar",
            "label": "composer bar",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_composer",
            "layoutRole": "input",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_prompt_capture_echo_or_persistence",
        },
        {
            "regionId": "send_result_region",
            "label": "send result region",
            "state": "blocked",
            "visible": False,
            "enabled": False,
            "sourceRef": "chat_send_result",
            "layoutRole": "feedback",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_prompt_or_response_content",
        },
        {
            "regionId": "audit_footer",
            "label": "audit footer",
            "state": "summary_only",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_audit_event",
            "layoutRole": "footer",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "summary_metadata_only_no_actor_identifier",
        },
    ],
    "navigationItems": [
        {
            "navId": "open_chat_surface",
            "label": "open chat surface",
            "state": "available_as_data",
            "enabled": True,
            "targetRegion": "transcript_region",
            "userAction": "Open the planned standalone chat surface.",
            "launcherAction": "Render blocked local layout metadata only.",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_prompt_response_or_transcript_content",
        },
        {
            "navId": "open_session_index",
            "label": "open session index",
            "state": "available_as_data",
            "enabled": True,
            "targetRegion": "session_index_sidebar",
            "userAction": "Open the empty local session index surface.",
            "launcherAction": "Render the checked session-index fixture reference.",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_session_store_read",
        },
        {
            "navId": "open_model_status",
            "label": "open model status",
            "state": "blocked",
            "enabled": False,
            "targetRegion": "model_status_header",
            "userAction": "Review model status after a separate readiness boundary changes.",
            "launcherAction": "Keep the model-status region as blocked metadata.",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_model_path_or_weight_content",
        },
        {
            "navId": "open_readiness",
            "label": "open readiness",
            "state": "blocked",
            "enabled": False,
            "targetRegion": "readiness_banner",
            "userAction": "Review readiness metadata without starting runtime code.",
            "launcherAction": "Show blocked readiness state only.",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "readiness_metadata_only",
        },
        {
            "navId": "focus_composer",
            "label": "focus composer",
            "state": "disabled",
            "enabled": False,
            "targetRegion": "composer_bar",
            "userAction": "Focus input only after prompt-capture boundaries are reviewed.",
            "launcherAction": "Keep composer focus disabled.",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_prompt_capture",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "runtime_readiness_blocked",
            "state": "blocked",
            "summary": "Runtime readiness remains blocked for the Gemma 3N E4B plus KV260 target.",
            "requiredBefore": "chat_surface_enabled",
        },
        {
            "reasonId": "chat_runtime_not_started",
            "state": "not_started",
            "summary": "No local chat runtime has started.",
            "requiredBefore": "transcript_region_active",
        },
        {
            "reasonId": "composer_send_disabled",
            "state": "disabled",
            "summary": "Composer and send controls remain disabled.",
            "requiredBefore": "composer_focus_or_send_enabled",
        },
        {
            "reasonId": "transcript_content_absent",
            "state": "empty_not_captured",
            "summary": "No prompt, response, transcript, or summary content exists in checked data.",
            "requiredBefore": "message_region_contains_content",
        },
        {
            "reasonId": "session_store_not_configured",
            "state": "not_configured",
            "summary": "No local session store or session title source exists.",
            "requiredBefore": "session_navigation_restores_content",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_session",
            "schemaVersion": "pccx.chatSession.v0",
            "fixturePath": "contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Base chat/session state is referenced for blocked surface state.",
        },
        {
            "refId": "chat_session_index",
            "schemaVersion": "pccx.chatSessionIndex.v0",
            "fixturePath": "contracts/fixtures/chat-session-index.gemma3n-e4b-kv260-placeholder.json",
            "state": "placeholder",
            "summary": "Empty session index data can be rendered without store reads.",
        },
        {
            "refId": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "fixturePath": "contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Model status remains display-only and blocked.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Readiness gates stay separate from layout rendering.",
        },
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Composer input remains disabled with no prompt capture.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Transcript persistence and export remain disabled.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "surfaceLayoutDisplayOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "sessionStoreRead": False,
        "readsSessionManifest": False,
        "readsTranscript": False,
        "sessionPersistence": False,
        "transcriptPersistence": False,
        "transcriptExport": False,
        "sessionTitleIncluded": False,
        "sessionTitleGenerated": False,
        "messageBodiesIncluded": False,
        "summaryIncluded": False,
        "summaryGenerated": False,
        "promptCapture": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "promptPersistence": False,
        "inputAccepted": False,
        "sendAttempted": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "transcriptContentIncluded": False,
        "auditEventPersisted": False,
        "localStoreConfigured": False,
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
        "Data-only chat surface layout fixture; no app shell implementation is started.",
        "No prompts, responses, transcripts, session titles, summaries, manifests, model paths, generated artifacts, private paths, secrets, or tokens are stored.",
        "No artifacts are read, written, deleted, refreshed, imported, exported, or persisted.",
        "No KV260 hardware access, serial access, network call, provider call, telemetry, upload, or write-back is performed.",
        "Navigation and surface regions remain local metadata until explicit runtime, model-load, prompt-capture, session-store, and transcript boundaries exist.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, or app-shell implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_surface_layout() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 surface-layout fixture."""
    return copy.deepcopy(_CHAT_SURFACE_LAYOUT)


def chat_surface_layout_json(status: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        status
        if status is not None
        else create_gemma3n_e4b_kv260_chat_surface_layout(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat surface layout JSON.",
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
    sys.stdout.write(chat_surface_layout_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
