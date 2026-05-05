#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat evidence manifest for the planned launcher UI.

The manifest records which checked fixture references still need reviewed
evidence before standalone chat paths can be enabled. It does not accept
prompts, read transcripts, read session stores, read artifacts, load models,
start runtime code, call providers, invoke PCCX tools, touch hardware, or
mutate repository state.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatEvidenceManifest.v0"

CHAT_EVIDENCE_MANIFEST_FIELDS = (
    "schemaVersion",
    "evidenceManifestId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "manifestState",
    "reviewState",
    "gapState",
    "evidenceState",
    "artifactState",
    "evidenceRefs",
    "reviewLinks",
    "blockedReasons",
    "nextActions",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

EVIDENCE_REF_FIELDS = (
    "refId",
    "schemaVersion",
    "fixturePath",
    "state",
    "summary",
    "contentPolicy",
    "requiredBefore",
)

REVIEW_LINK_FIELDS = (
    "linkId",
    "refId",
    "state",
    "summary",
)

BLOCKED_REASON_FIELDS = (
    "reasonId",
    "state",
    "summary",
    "requiredBefore",
)

NEXT_ACTION_FIELDS = (
    "actionId",
    "state",
    "enabled",
    "summary",
    "requiredBefore",
)

CHAT_EVIDENCE_MANIFEST_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "not_approved",
    "not_configured",
    "planned",
    "requires_evidence",
    "requires_review",
    "summary_only",
    "unavailable",
)

_CHAT_EVIDENCE_MANIFEST = {
    "schemaVersion": SCHEMA_VERSION,
    "evidenceManifestId": "chat_evidence_manifest_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-evidence-manifest.gemma3n-e4b-kv260.2026-05-06-session-store-ref",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_session_store_evidence_ref_2026-05-06",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "manifestState": "available_as_data",
    "reviewState": "not_approved",
    "gapState": "blocked",
    "evidenceState": "requires_evidence",
    "artifactState": "unavailable",
    "evidenceRefs": [
        {
            "refId": "runtime_readiness",
            "schemaVersion": "pccx.runtimeReadiness.v0",
            "fixturePath": "contracts/fixtures/runtime-readiness.gemma3n-e4b-kv260.json",
            "state": "requires_evidence",
            "summary": "Runtime readiness remains blocked and this manifest records only the checked fixture reference.",
            "contentPolicy": "fixture_reference_only_no_runtime_logs_or_device_dumps",
            "requiredBefore": "model_or_runtime_execution_enabled",
        },
        {
            "refId": "device_session_status",
            "schemaVersion": "pccx.deviceSessionStatus.v0",
            "fixturePath": "contracts/fixtures/device-session-status.gemma3n-e4b-kv260.json",
            "state": "requires_evidence",
            "summary": "Device/session status is referenced as local checked data and does not prove a runtime session.",
            "contentPolicy": "fixture_reference_only_no_hardware_dump_or_board_log",
            "requiredBefore": "target_session_enabled",
        },
        {
            "refId": "chat_review_packet",
            "schemaVersion": "pccx.chatReviewPacket.v0",
            "fixturePath": "contracts/fixtures/chat-review-packet.gemma3n-e4b-kv260-placeholder.json",
            "state": "not_approved",
            "summary": "Review packet remains a blocked handoff reference with no approval granted.",
            "contentPolicy": "fixture_reference_only_no_prompt_response_transcript_or_summary_content",
            "requiredBefore": "review_gate_closed",
        },
        {
            "refId": "chat_gap_matrix",
            "schemaVersion": "pccx.chatGapMatrix.v0",
            "fixturePath": "contracts/fixtures/chat-gap-matrix.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Gap matrix remains unresolved and is referenced without closing any blocker row.",
            "contentPolicy": "fixture_reference_only_no_gap_closure_or_runtime_handoff",
            "requiredBefore": "standalone_chat_enabled",
        },
        {
            "refId": "chat_status_summary",
            "schemaVersion": "pccx.chatStatusSummary.v0",
            "fixturePath": "contracts/fixtures/chat-status-summary.gemma3n-e4b-kv260-placeholder.json",
            "state": "summary_only",
            "summary": "Status summary is referenced as display data and is not duplicated in this manifest.",
            "contentPolicy": "fixture_reference_only_no_status_card_duplication",
            "requiredBefore": "launcher_status_enabled",
        },
        {
            "refId": "chat_redaction_policy",
            "schemaVersion": "pccx.chatRedactionPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-redaction-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "summary_only",
            "summary": "Redaction policy is referenced without loading rules, scanning content, or persisting results.",
            "contentPolicy": "fixture_reference_only_no_content_scan_or_redaction_action",
            "requiredBefore": "privacy_sensitive_content_paths_enabled",
        },
        {
            "refId": "chat_session_store_policy",
            "schemaVersion": "pccx.chatSessionStorePolicy.v0",
            "fixturePath": "contracts/fixtures/chat-session-store-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "requires_review",
            "summary": "Session-store policy metadata is referenced as a checked fixture and still needs review before any local store path, manifest, session record, or persistence path is treated as implemented.",
            "contentPolicy": "fixture_reference_only_no_store_path_manifest_session_record_read_or_persistence",
            "requiredBefore": "session_store_enabled",
        },
        {
            "refId": "chat_shortcut_map",
            "schemaVersion": "pccx.chatShortcutMap.v0",
            "fixturePath": "contracts/fixtures/chat-shortcut-map.gemma3n-e4b-kv260-placeholder.json",
            "state": "requires_review",
            "summary": "Shortcut-map metadata is referenced as a checked fixture and still needs review before keyboard shortcuts are treated as implemented.",
            "contentPolicy": "fixture_reference_only_no_keyboard_listener_capture_dispatch_focus_change_or_action_execution",
            "requiredBefore": "keyboard_shortcuts_enabled",
        },
        {
            "refId": "chat_clipboard_policy",
            "schemaVersion": "pccx.chatClipboardPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-clipboard-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "requires_review",
            "summary": "Clipboard policy metadata is referenced as a checked fixture and still needs review before clipboard controls are treated as implemented.",
            "contentPolicy": "fixture_reference_only_no_clipboard_read_write_paste_copy_import_or_export",
            "requiredBefore": "clipboard_controls_enabled",
        },
        {
            "refId": "chat_attachment_policy",
            "schemaVersion": "pccx.chatAttachmentPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-attachment-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "requires_review",
            "summary": "Attachment policy metadata is referenced as a checked fixture and still needs review before any attachment control is treated as implemented.",
            "contentPolicy": "fixture_reference_only_no_file_picker_file_read_upload_import_or_preview",
            "requiredBefore": "attachment_controls_enabled",
        },
        {
            "refId": "chat_accessibility",
            "schemaVersion": "pccx.chatAccessibility.v0",
            "fixturePath": "contracts/fixtures/chat-accessibility.gemma3n-e4b-kv260-placeholder.json",
            "state": "requires_review",
            "summary": "Accessibility metadata is referenced as a checked fixture and still needs UI review before any chat surface is treated as implemented.",
            "contentPolicy": "fixture_reference_only_no_ui_focus_keyboard_or_live_region_execution",
            "requiredBefore": "accessibility_review_closed",
        },
    ],
    "reviewLinks": [
        {
            "linkId": "review_packet_gate",
            "refId": "chat_review_packet",
            "state": "not_approved",
            "summary": "The review packet must be approved separately before any chat enablement work.",
        },
        {
            "linkId": "gap_matrix_gate",
            "refId": "chat_gap_matrix",
            "state": "blocked",
            "summary": "The gap matrix remains blocked; this manifest does not close gaps.",
        },
        {
            "linkId": "runtime_evidence_gate",
            "refId": "runtime_readiness",
            "state": "requires_evidence",
            "summary": "Runtime evidence must be reviewed in a later evidence-backed change.",
        },
        {
            "linkId": "session_store_policy_gate",
            "refId": "chat_session_store_policy",
            "state": "requires_review",
            "summary": "Session-store metadata remains a review reference and does not enable store path, manifest, session record, retention, migration, deletion, or persistence behavior.",
        },
        {
            "linkId": "accessibility_review_gate",
            "refId": "chat_accessibility",
            "state": "requires_review",
            "summary": "Accessibility metadata remains a review reference and does not enable UI behavior.",
        },
        {
            "linkId": "attachment_policy_gate",
            "refId": "chat_attachment_policy",
            "state": "requires_review",
            "summary": "Attachment metadata remains a review reference and does not enable file picker, upload, import, preview, or persistence behavior.",
        },
        {
            "linkId": "clipboard_policy_gate",
            "refId": "chat_clipboard_policy",
            "state": "requires_review",
            "summary": "Clipboard metadata remains a review reference and does not enable clipboard read, write, paste, copy, import, or export behavior.",
        },
        {
            "linkId": "shortcut_map_gate",
            "refId": "chat_shortcut_map",
            "state": "requires_review",
            "summary": "Shortcut metadata remains a review reference and does not enable keyboard listeners, key capture, command dispatch, focus changes, or shortcut actions.",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "runtime_evidence_absent",
            "state": "requires_evidence",
            "summary": "Runtime and device evidence are referenced only as checked placeholder data.",
            "requiredBefore": "model_or_runtime_execution_enabled",
        },
        {
            "reasonId": "review_not_approved",
            "state": "not_approved",
            "summary": "No chat review gate is approved by this manifest.",
            "requiredBefore": "review_gate_closed",
        },
        {
            "reasonId": "artifact_evidence_not_read",
            "state": "unavailable",
            "summary": "Logs, generated blobs, model assets, reports, and board dumps are not read by this boundary.",
            "requiredBefore": "evidence_artifact_review",
        },
        {
            "reasonId": "standalone_chat_still_blocked",
            "state": "blocked",
            "summary": "Standalone chat remains blocked by unresolved runtime, model, content, store, privacy, and UI gaps.",
            "requiredBefore": "standalone_chat_enabled",
        },
        {
            "reasonId": "session_store_review_pending",
            "state": "requires_review",
            "summary": "Local store configuration, path lookup, manifest reads, session-record reads/writes, deletion, retention, migration, and persistence still require review.",
            "requiredBefore": "session_store_enabled",
        },
        {
            "reasonId": "accessibility_review_pending",
            "state": "requires_review",
            "summary": "Accessibility labels, focus order, live-region behavior, contrast, and motion metadata still require UI review.",
            "requiredBefore": "accessibility_review_closed",
        },
        {
            "reasonId": "attachment_review_pending",
            "state": "requires_review",
            "summary": "Attachment file picker, file metadata, file content, upload, import, preview, and persistence behavior still require review.",
            "requiredBefore": "attachment_controls_enabled",
        },
        {
            "reasonId": "clipboard_review_pending",
            "state": "requires_review",
            "summary": "Clipboard read, write, paste, copy, import, export, transcript copy, message copy, and clipboard-backed attachment behavior still require review.",
            "requiredBefore": "clipboard_controls_enabled",
        },
        {
            "reasonId": "shortcut_review_pending",
            "state": "requires_review",
            "summary": "Keyboard listener installation, key-event capture, command dispatch, focus changes, shortcut execution, send, retry, stop, copy, attach, clear, export, and session actions still require review.",
            "requiredBefore": "keyboard_shortcuts_enabled",
        },
    ],
    "nextActions": [
        {
            "actionId": "collect_runtime_evidence",
            "state": "disabled",
            "enabled": False,
            "summary": "Collecting runtime evidence is outside this data-only launcher contract.",
            "requiredBefore": "runtime_evidence_review",
        },
        {
            "actionId": "review_manifest_refs",
            "state": "requires_review",
            "enabled": False,
            "summary": "Maintainers may review these fixture references, but this contract performs no reads or approvals.",
            "requiredBefore": "review_gate_closed",
        },
        {
            "actionId": "keep_chat_blocked",
            "state": "blocked",
            "enabled": False,
            "summary": "Standalone chat controls must remain blocked until reviewed evidence and gap closure land separately.",
            "requiredBefore": "standalone_chat_enabled",
        },
        {
            "actionId": "review_session_store_policy",
            "state": "requires_review",
            "enabled": False,
            "summary": "Review the checked session-store policy fixture separately before enabling local store configuration, path lookup, manifest reads, session-record reads/writes, retention, migration, deletion, or persistence.",
            "requiredBefore": "session_store_enabled",
        },
        {
            "actionId": "review_accessibility_metadata",
            "state": "requires_review",
            "enabled": False,
            "summary": "Review the checked accessibility fixture separately before enabling any labels, focus behavior, live-region updates, contrast tokens, or motion behavior.",
            "requiredBefore": "accessibility_review_closed",
        },
        {
            "actionId": "review_attachment_policy",
            "state": "requires_review",
            "enabled": False,
            "summary": "Review the checked attachment policy fixture separately before enabling file picker, file read, upload, import, preview, or persistence paths.",
            "requiredBefore": "attachment_controls_enabled",
        },
        {
            "actionId": "review_clipboard_policy",
            "state": "requires_review",
            "enabled": False,
            "summary": "Review the checked clipboard policy fixture separately before enabling clipboard read, write, paste, copy, import, export, or clipboard-backed attachment paths.",
            "requiredBefore": "clipboard_controls_enabled",
        },
        {
            "actionId": "review_shortcut_map",
            "state": "requires_review",
            "enabled": False,
            "summary": "Review the checked shortcut-map fixture separately before enabling keyboard listeners, key capture, focus changes, command dispatch, shortcut execution, or action paths.",
            "requiredBefore": "keyboard_shortcuts_enabled",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "evidenceManifestOnly": True,
        "referencesCheckedFixturesOnly": True,
        "reviewPacketReferencedOnly": True,
        "gapMatrixReferencedOnly": True,
        "statusSummaryReferencedOnly": True,
        "sessionStorePolicyReferencedOnly": True,
        "evidenceAccepted": False,
        "gapClosed": False,
        "approvalGranted": False,
        "artifactRead": False,
        "artifactWrite": False,
        "rawLogRead": False,
        "hardwareDumpRead": False,
        "promptCapture": False,
        "promptRead": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptContentIncluded": False,
        "messageBodiesIncluded": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
        "sessionPersistence": False,
        "configRead": False,
        "environmentRead": False,
        "providerConfigRead": False,
        "providerCalls": False,
        "cloudCalls": False,
        "networkCalls": False,
        "modelAssetRead": False,
        "modelPathIncluded": False,
        "modelLoadAttempted": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "responseGenerated": False,
        "sendEnabled": False,
        "clipboardRead": False,
        "attachmentReads": False,
        "fileMetadataRead": False,
        "fileContentRead": False,
        "directoryScan": False,
        "redactionRulesLoaded": False,
        "contentScan": False,
        "redactionApplied": False,
        "auditLogWritten": False,
        "kv260Access": False,
        "hardwareAccess": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "releaseOrTagAction": False,
        "settingsChange": False,
        "compatibilityClaim": False,
    },
    "limitations": [
        "Data-only chat evidence manifest over existing checked fixture references.",
        "No prompt, response, transcript, message, session-store, config, provider, model-path, runtime-log, artifact, private-path, secret, token, file, clipboard, or hardware content is read.",
        "No artifact read/write, model load, runtime execution, provider call, network call, hardware access, pccx-lab execution, IDE execution, release, tag, settings, or repository action is performed.",
        "This manifest does not close issue #9, approve review gates, accept evidence, close gaps, or enable standalone chat.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_evidence_manifest() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat evidence manifest."""
    return copy.deepcopy(_CHAT_EVIDENCE_MANIFEST)


def chat_evidence_manifest_json(manifest: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        manifest
        if manifest is not None
        else create_gemma3n_e4b_kv260_chat_evidence_manifest(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat evidence manifest JSON.",
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
    sys.stdout.write(chat_evidence_manifest_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
