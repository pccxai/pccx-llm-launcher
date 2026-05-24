#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat review packet contract for the planned launcher UI.

The contract gathers existing checked chat fixture references into a
review-only packet for maintainer handoff. It does not accept prompts, read
transcripts, read session stores, load models, start runtime code, call
providers, invoke PCCX tools, touch hardware, or mutate repository state.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatReviewPacket.v0"

CHAT_REVIEW_PACKET_FIELDS = (
    "schemaVersion",
    "reviewPacketId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "reviewState",
    "approvalState",
    "executionState",
    "contentState",
    "privacyState",
    "evidenceState",
    "reviewSections",
    "requiredReviews",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

REVIEW_SECTION_FIELDS = (
    "sectionId",
    "label",
    "sourceRefs",
    "state",
    "summary",
    "contentPolicy",
    "requiredBefore",
)

REQUIRED_REVIEW_FIELDS = (
    "reviewId",
    "label",
    "state",
    "accepted",
    "summary",
    "requiredEvidence",
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

CHAT_REVIEW_PACKET_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "inactive",
    "not_approved",
    "not_configured",
    "not_loaded",
    "not_started",
    "not_used",
    "planned",
    "requires_evidence",
    "requires_review",
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_REVIEW_PACKET = {
    "schemaVersion": SCHEMA_VERSION,
    "reviewPacketId": "chat_review_packet_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-review-packet.gemma3n-e4b-kv260.2026-05-05",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_review_packet_boundary_2026-05-05",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "reviewState": "blocked",
    "approvalState": "not_approved",
    "executionState": "not_started",
    "contentState": "empty_not_captured",
    "privacyState": "requires_review",
    "evidenceState": "requires_evidence",
    "reviewSections": [
        {
            "sectionId": "surface_and_controls",
            "label": "surface and controls",
            "sourceRefs": [
                "chat_surface_layout",
                "chat_composer",
                "chat_action_bar",
                "chat_shortcut_map",
            ],
            "state": "available_as_data",
            "summary": "The chat shell, input controls, actions, and shortcuts are display data only.",
            "contentPolicy": "no_prompt_text_message_body_clipboard_or_file_content",
            "requiredBefore": "chat_shell_enabled",
        },
        {
            "sectionId": "session_management",
            "label": "session management",
            "sourceRefs": [
                "chat_session",
                "chat_session_lifecycle",
                "chat_session_index",
                "chat_session_store_policy",
                "chat_session_title_policy",
                "chat_transcript_policy",
            ],
            "state": "blocked",
            "summary": "Session create, restore, clear, close, title, store, transcript, and export paths remain disabled or unavailable.",
            "contentPolicy": "no_store_manifest_session_record_title_summary_transcript_prompt_or_response_content",
            "requiredBefore": "session_management_enabled",
        },
        {
            "sectionId": "model_runtime_and_device",
            "label": "model runtime and device",
            "sourceRefs": [
                "chat_model_status",
                "chat_model_selection_policy",
                "chat_model_load_request",
                "runtime_readiness",
                "device_session_status",
            ],
            "state": "requires_evidence",
            "summary": "Model selection and load metadata remain blocked until separate runtime and device evidence exists.",
            "contentPolicy": "no_model_path_weight_tokenizer_checksum_runtime_log_or_device_dump_content",
            "requiredBefore": "model_load_or_runtime_session_enabled",
        },
        {
            "sectionId": "content_flow",
            "label": "content flow",
            "sourceRefs": [
                "chat_send_result",
                "chat_message_list",
                "chat_response_stream",
                "chat_context_policy",
                "chat_empty_state",
            ],
            "state": "disabled",
            "summary": "Prompt acceptance, message append, response streaming, token context, and generated output remain disabled.",
            "contentPolicy": "no_prompt_response_transcript_message_summary_token_or_context_content",
            "requiredBefore": "send_or_response_enabled",
        },
        {
            "sectionId": "privacy_and_local_only_policy",
            "label": "privacy and local-only policy",
            "sourceRefs": [
                "chat_local_only_policy",
                "chat_redaction_policy",
                "chat_attachment_policy",
                "chat_clipboard_policy",
                "chat_audit_event",
                "chat_error_taxonomy",
            ],
            "state": "requires_review",
            "summary": "Local-only, redaction, attachment, clipboard, audit, and error policy metadata remain review-only.",
            "contentPolicy": "no_provider_config_secret_token_clipboard_attachment_audit_or_raw_error_payload",
            "requiredBefore": "privacy_or_attachment_paths_enabled",
        },
        {
            "sectionId": "aggregate_status",
            "label": "aggregate status",
            "sourceRefs": [
                "chat_status_summary",
            ],
            "state": "summary_only",
            "summary": "The existing status summary is referenced as a checked display summary, not copied into this packet.",
            "contentPolicy": "status_summary_reference_only_no_status_card_duplication",
            "requiredBefore": "review_packet_approved",
        },
    ],
    "requiredReviews": [
        {
            "reviewId": "runtime_evidence_review",
            "label": "runtime evidence review",
            "state": "requires_evidence",
            "accepted": False,
            "summary": "Runtime readiness and device session evidence are not approved by this packet.",
            "requiredEvidence": [
                "reviewed_runtime_readiness_fixture",
                "reviewed_device_session_status_fixture",
            ],
            "sideEffectPolicy": "no_runtime_or_hardware_action",
        },
        {
            "reviewId": "model_asset_review",
            "label": "model asset review",
            "state": "not_approved",
            "accepted": False,
            "summary": "Model asset location, checksum, tokenizer, load, warmup, unload, and persistence remain unapproved.",
            "requiredEvidence": [
                "reviewed_model_asset_input_boundary",
                "reviewed_model_load_request_boundary",
            ],
            "sideEffectPolicy": "no_model_path_read_or_model_load",
        },
        {
            "reviewId": "session_store_review",
            "label": "session store review",
            "state": "not_approved",
            "accepted": False,
            "summary": "Session store path, manifest, read, write, retention, migration, and export remain unapproved.",
            "requiredEvidence": [
                "reviewed_session_store_policy",
                "reviewed_transcript_retention_policy",
            ],
            "sideEffectPolicy": "no_session_store_or_transcript_access",
        },
        {
            "reviewId": "content_privacy_review",
            "label": "content privacy review",
            "state": "requires_review",
            "accepted": False,
            "summary": "Prompt, response, transcript, attachment, clipboard, redaction, audit, and error content boundaries remain review-only.",
            "requiredEvidence": [
                "reviewed_redaction_policy",
                "reviewed_attachment_policy",
                "reviewed_clipboard_policy",
            ],
            "sideEffectPolicy": "no_content_scan_redaction_clipboard_or_file_action",
        },
        {
            "reviewId": "send_enablement_review",
            "label": "send enablement review",
            "state": "blocked",
            "accepted": False,
            "summary": "Send, response streaming, context assembly, stop, retry, copy, and export controls remain disabled.",
            "requiredEvidence": [
                "reviewed_prompt_capture_boundary",
                "reviewed_response_stream_boundary",
                "reviewed_action_execution_boundary",
            ],
            "sideEffectPolicy": "no_prompt_capture_or_runtime_dispatch",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "review_packet_not_approved",
            "state": "not_approved",
            "summary": "This packet records review blockers only; it does not approve runtime or UI behavior.",
            "requiredBefore": "standalone_chat_enabled",
        },
        {
            "reasonId": "runtime_and_device_evidence_absent",
            "state": "requires_evidence",
            "summary": "Runtime readiness and target device session evidence are not present in this launcher boundary.",
            "requiredBefore": "model_or_runtime_execution_enabled",
        },
        {
            "reasonId": "model_asset_boundary_absent",
            "state": "not_loaded",
            "summary": "No reviewed local model asset path, tokenizer, checksum, load, warmup, or unload path exists.",
            "requiredBefore": "model_status_ready",
        },
        {
            "reasonId": "session_store_boundary_absent",
            "state": "not_configured",
            "summary": "No reviewed local session store, transcript retention, title, manifest, restore, or export path exists.",
            "requiredBefore": "session_management_enabled",
        },
        {
            "reasonId": "content_privacy_boundary_absent",
            "state": "requires_review",
            "summary": "Prompt, response, transcript, attachment, clipboard, redaction, audit, and error payload boundaries remain disabled or summary-only.",
            "requiredBefore": "prompt_or_response_content_displayed",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_status_summary",
            "schemaVersion": "pccx.chatStatusSummary.v0",
            "fixturePath": "contracts/fixtures/chat-status-summary.gemma3n-e4b-kv260-placeholder.json",
            "state": "summary_only",
            "summary": "Aggregate UI status remains a separate checked display summary.",
        },
        {
            "refId": "chat_local_only_policy",
            "schemaVersion": "pccx.chatLocalOnlyPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-local-only-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Local-only policy keeps cloud and provider fallback paths disabled.",
        },
        {
            "refId": "chat_redaction_policy",
            "schemaVersion": "pccx.chatRedactionPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-redaction-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "summary_only",
            "summary": "Redaction policy is referenced without loading rules or scanning content.",
        },
        {
            "refId": "chat_session_store_policy",
            "schemaVersion": "pccx.chatSessionStorePolicy.v0",
            "fixturePath": "contracts/fixtures/chat-session-store-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "not_configured",
            "summary": "Session store policy remains disabled and no store is read.",
        },
        {
            "refId": "chat_model_load_request",
            "schemaVersion": "pccx.chatModelLoadRequest.v0",
            "fixturePath": "contracts/fixtures/chat-model-load-request.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Model load request remains blocked with no asset path read or load attempt.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Readiness stays blocked until runtime, device, model, store, and privacy evidence exists.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "reviewPacketOnly": True,
        "aggregatesCheckedFixturesOnly": True,
        "statusSummaryReferencedOnly": True,
        "approvalGranted": False,
        "promptCapture": False,
        "promptRead": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptContentIncluded": False,
        "messageBodiesIncluded": False,
        "sessionStoreRead": False,
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
        "responseGenerated": False,
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
        "telemetry": False,
        "writeBack": False,
        "releaseOrTagAction": False,
        "settingsChange": False,
        "compatibilityClaim": False,
    },
    "limitations": [
        "Data-only chat review packet over existing checked fixture references.",
        "No prompt, response, transcript, message, session-store, config, provider, model-path, runtime-log, artifact, private-path, secret, token, or hardware content is read.",
        "No model load, runtime execution, provider call, network call, hardware access, telemetry, write-back, release, tag, settings, or repository action is performed.",
        "This packet does not approve standalone chat enablement; it records remaining review and evidence gates only.",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_review_packet() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat review packet."""
    return copy.deepcopy(_CHAT_REVIEW_PACKET)


def chat_review_packet_json(packet: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        packet
        if packet is not None
        else create_gemma3n_e4b_kv260_chat_review_packet(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat review packet JSON.",
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
    sys.stdout.write(chat_review_packet_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
