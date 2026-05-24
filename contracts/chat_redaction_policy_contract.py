#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat redaction policy contract for the planned launcher UI.

The contract describes disabled redaction and content-scan gates for the
standalone chat surface. It does not load redaction rules, scan prompts,
responses, transcripts, messages, attachments, clipboard payloads, audit
events, session stores, model assets, or logs; it does not detect PII or
secrets, apply redactions, persist redaction results, touch KV260 hardware,
call providers, invoke pccx-lab, or start runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatRedactionPolicy.v0"

CHAT_REDACTION_POLICY_FIELDS = (
    "schemaVersion",
    "redactionPolicyId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "redactionPolicyState",
    "contentScanState",
    "promptRedactionState",
    "responseRedactionState",
    "transcriptRedactionState",
    "messageRedactionState",
    "attachmentRedactionState",
    "clipboardRedactionState",
    "auditRedactionState",
    "piiDetectionState",
    "secretDetectionState",
    "persistenceState",
    "privacyState",
    "chatComposerRef",
    "chatMessageListRef",
    "chatTranscriptPolicyRef",
    "chatAttachmentPolicyRef",
    "chatClipboardPolicyRef",
    "chatAuditEventRef",
    "chatLocalOnlyPolicyRef",
    "redactionPolicy",
    "redactionSurfaces",
    "redactionControls",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

REDACTION_POLICY_FIELDS = (
    "state",
    "mode",
    "sourcePolicy",
    "contentPolicy",
    "scannerEnabled",
    "promptRedactionEnabled",
    "responseRedactionEnabled",
    "transcriptRedactionEnabled",
    "messageRedactionEnabled",
    "attachmentRedactionEnabled",
    "clipboardRedactionEnabled",
    "auditRedactionEnabled",
    "piiDetectionEnabled",
    "secretDetectionEnabled",
    "persistenceEnabled",
    "sideEffectPolicy",
)

REDACTION_SURFACE_FIELDS = (
    "surfaceId",
    "label",
    "state",
    "enabled",
    "summary",
    "contentPolicy",
    "sideEffectPolicy",
)

REDACTION_CONTROL_FIELDS = (
    "controlId",
    "label",
    "state",
    "enabled",
    "userAction",
    "launcherAction",
    "sideEffectPolicy",
    "contentPolicy",
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

CHAT_REDACTION_POLICY_STATE_VALUES = (
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

_CHAT_REDACTION_POLICY = {
    "schemaVersion": SCHEMA_VERSION,
    "redactionPolicyId": "chat_redaction_policy_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-redaction-policy.gemma3n-e4b-kv260.2026-05-05",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_redaction_policy_boundary_2026-05-05",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "redactionPolicyState": "blocked",
    "contentScanState": "disabled",
    "promptRedactionState": "disabled",
    "responseRedactionState": "disabled",
    "transcriptRedactionState": "not_configured",
    "messageRedactionState": "empty_not_captured",
    "attachmentRedactionState": "blocked",
    "clipboardRedactionState": "disabled",
    "auditRedactionState": "blocked",
    "piiDetectionState": "disabled",
    "secretDetectionState": "disabled",
    "persistenceState": "disabled",
    "privacyState": "summary_only",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatMessageListRef": "chat_message_list_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "chatAttachmentPolicyRef": "chat_attachment_policy_gemma3n_e4b_kv260_placeholder",
    "chatClipboardPolicyRef": "chat_clipboard_policy_gemma3n_e4b_kv260_placeholder",
    "chatAuditEventRef": "chat_audit_event_gemma3n_e4b_kv260_placeholder",
    "chatLocalOnlyPolicyRef": "chat_local_only_policy_gemma3n_e4b_kv260_placeholder",
    "redactionPolicy": {
        "state": "blocked",
        "mode": "disabled_until_reviewed_redaction_rules_and_content_boundaries_exist",
        "sourcePolicy": "checked fixture only; no prompt, response, transcript, message, attachment, clipboard, audit, session-store, file, artifact, model path, or runtime log is read",
        "contentPolicy": "redaction policy metadata only; no raw content, detector matches, replacement text, identifiers, file names, paths, bytes, prompts, responses, transcripts, or messages are included",
        "scannerEnabled": False,
        "promptRedactionEnabled": False,
        "responseRedactionEnabled": False,
        "transcriptRedactionEnabled": False,
        "messageRedactionEnabled": False,
        "attachmentRedactionEnabled": False,
        "clipboardRedactionEnabled": False,
        "auditRedactionEnabled": False,
        "piiDetectionEnabled": False,
        "secretDetectionEnabled": False,
        "persistenceEnabled": False,
        "sideEffectPolicy": "local_render_only",
    },
    "redactionSurfaces": [
        {
            "surfaceId": "composer_prompt",
            "label": "composer prompt",
            "state": "blocked",
            "enabled": False,
            "summary": "Prompt redaction remains disabled because prompt capture is not enabled.",
            "contentPolicy": "no_prompt_text",
            "sideEffectPolicy": "no_prompt_scan",
        },
        {
            "surfaceId": "assistant_response",
            "label": "assistant response",
            "state": "disabled",
            "enabled": False,
            "summary": "Response redaction remains disabled because no generated response exists.",
            "contentPolicy": "no_response_text",
            "sideEffectPolicy": "no_response_scan",
        },
        {
            "surfaceId": "message_list",
            "label": "message list",
            "state": "empty_not_captured",
            "enabled": False,
            "summary": "Message redaction remains unavailable because message bodies are not captured.",
            "contentPolicy": "no_message_body",
            "sideEffectPolicy": "no_message_scan",
        },
        {
            "surfaceId": "transcript_export",
            "label": "transcript export",
            "state": "not_configured",
            "enabled": False,
            "summary": "Transcript redaction requires a reviewed store, retention, and export policy.",
            "contentPolicy": "no_transcript_text",
            "sideEffectPolicy": "no_transcript_scan_or_export",
        },
        {
            "surfaceId": "attachment_payload",
            "label": "attachment payload",
            "state": "blocked",
            "enabled": False,
            "summary": "Attachment redaction remains blocked until file and artifact input boundaries exist.",
            "contentPolicy": "no_file_name_path_metadata_or_bytes",
            "sideEffectPolicy": "no_attachment_scan",
        },
        {
            "surfaceId": "clipboard_payload",
            "label": "clipboard payload",
            "state": "disabled",
            "enabled": False,
            "summary": "Clipboard redaction remains disabled because clipboard reads are unavailable.",
            "contentPolicy": "no_clipboard_content",
            "sideEffectPolicy": "no_clipboard_scan",
        },
        {
            "surfaceId": "audit_event",
            "label": "audit event",
            "state": "blocked",
            "enabled": False,
            "summary": "Audit redaction remains blocked because audit persistence is not configured.",
            "contentPolicy": "no_actor_identifier_prompt_response_or_raw_event",
            "sideEffectPolicy": "no_audit_scan_or_persistence",
        },
    ],
    "redactionControls": [
        {
            "controlId": "review_redaction_rules",
            "label": "review redaction rules",
            "state": "not_configured",
            "enabled": False,
            "userAction": "Review rules only after a separate local policy source is defined.",
            "launcherAction": "Keep rules unavailable and do not load policy files.",
            "sideEffectPolicy": "no_rule_load",
            "contentPolicy": "no_rule_content_or_private_path",
            "blockedReasonRef": "redaction_rules_absent",
        },
        {
            "controlId": "scan_prompt_content",
            "label": "scan prompt content",
            "state": "disabled",
            "enabled": False,
            "userAction": "Scan prompts only after prompt capture and redaction review exists.",
            "launcherAction": "Do not capture, inspect, or scan prompt text.",
            "sideEffectPolicy": "no_prompt_scan",
            "contentPolicy": "no_prompt_text",
            "blockedReasonRef": "content_boundary_absent",
        },
        {
            "controlId": "scan_response_content",
            "label": "scan response content",
            "state": "disabled",
            "enabled": False,
            "userAction": "Scan responses only after a reviewed response stream exists.",
            "launcherAction": "Do not generate, inspect, or scan response text.",
            "sideEffectPolicy": "no_response_scan",
            "contentPolicy": "no_response_text",
            "blockedReasonRef": "content_boundary_absent",
        },
        {
            "controlId": "scan_transcript_content",
            "label": "scan transcript content",
            "state": "not_configured",
            "enabled": False,
            "userAction": "Scan transcripts only after local storage and retention policy exists.",
            "launcherAction": "Do not read, export, inspect, or scan transcripts.",
            "sideEffectPolicy": "no_transcript_scan",
            "contentPolicy": "no_transcript_text",
            "blockedReasonRef": "transcript_policy_not_reviewed",
        },
        {
            "controlId": "detect_sensitive_content",
            "label": "detect sensitive content",
            "state": "disabled",
            "enabled": False,
            "userAction": "Run detectors only after local detector scope and review rules exist.",
            "launcherAction": "Do not run PII, secret, token, path, or identifier detection.",
            "sideEffectPolicy": "no_detector_execution",
            "contentPolicy": "no_detector_matches_or_raw_content",
            "blockedReasonRef": "scanner_not_reviewed",
        },
        {
            "controlId": "redact_attachment_payload",
            "label": "redact attachment payload",
            "state": "blocked",
            "enabled": False,
            "userAction": "Redact attachments only after file input, parsing, and redaction rules are reviewed.",
            "launcherAction": "Do not open, read, parse, scan, or redact file or artifact payloads.",
            "sideEffectPolicy": "no_attachment_read_or_redaction",
            "contentPolicy": "no_file_name_path_metadata_preview_or_bytes",
            "blockedReasonRef": "content_boundary_absent",
        },
        {
            "controlId": "redact_clipboard_payload",
            "label": "redact clipboard payload",
            "state": "disabled",
            "enabled": False,
            "userAction": "Redact clipboard data only after clipboard read and redaction boundaries are reviewed.",
            "launcherAction": "Do not read, scan, redact, import, or write clipboard data.",
            "sideEffectPolicy": "no_clipboard_read_or_redaction",
            "contentPolicy": "no_clipboard_content",
            "blockedReasonRef": "content_boundary_absent",
        },
        {
            "controlId": "persist_redaction_result",
            "label": "persist redaction result",
            "state": "disabled",
            "enabled": False,
            "userAction": "Persist redaction results only after local store and retention policy exists.",
            "launcherAction": "Do not write redaction reports, artifacts, transcripts, or session records.",
            "sideEffectPolicy": "no_redaction_result_persistence",
            "contentPolicy": "no_redacted_content_or_report",
            "blockedReasonRef": "persistence_not_configured",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "redaction_rules_absent",
            "state": "not_configured",
            "summary": "No reviewed local redaction rule source exists.",
            "requiredBefore": "redaction_rule_review_enabled",
        },
        {
            "reasonId": "content_boundary_absent",
            "state": "blocked",
            "summary": "Prompt, response, message, attachment, and clipboard content boundaries remain unavailable.",
            "requiredBefore": "content_scan_enabled",
        },
        {
            "reasonId": "transcript_policy_not_reviewed",
            "state": "not_configured",
            "summary": "Transcript storage, retention, export, and redaction policy is not configured.",
            "requiredBefore": "transcript_redaction_enabled",
        },
        {
            "reasonId": "scanner_not_reviewed",
            "state": "requires_review",
            "summary": "Detector scope, match handling, and replacement policy require review.",
            "requiredBefore": "sensitive_content_detection_enabled",
        },
        {
            "reasonId": "persistence_not_configured",
            "state": "disabled",
            "summary": "Redaction results are not persisted or exported.",
            "requiredBefore": "redaction_result_persistence_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Composer data keeps prompt capture and prompt redaction disabled.",
        },
        {
            "refId": "chat_message_list",
            "schemaVersion": "pccx.chatMessageList.v0",
            "fixturePath": "contracts/fixtures/chat-message-list.gemma3n-e4b-kv260-placeholder.json",
            "state": "empty_not_captured",
            "summary": "Empty message-list data prevents message redaction.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Transcript persistence and export remain unavailable.",
        },
        {
            "refId": "chat_attachment_policy",
            "schemaVersion": "pccx.chatAttachmentPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-attachment-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Attachment policy keeps attachment payload reads disabled.",
        },
        {
            "refId": "chat_clipboard_policy",
            "schemaVersion": "pccx.chatClipboardPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-clipboard-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Clipboard policy keeps clipboard payload reads and writes disabled.",
        },
        {
            "refId": "chat_audit_event",
            "schemaVersion": "pccx.chatAuditEvent.v0",
            "fixturePath": "contracts/fixtures/chat-audit-event.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Audit-event data keeps audit redaction and persistence disabled.",
        },
        {
            "refId": "chat_local_only_policy",
            "schemaVersion": "pccx.chatLocalOnlyPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-local-only-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Local-only policy keeps provider, cloud, network, and upload paths unavailable.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "redactionPolicyDisplayOnly": True,
        "redactionMetadataOnly": True,
        "redactionRulesLoaded": False,
        "redactionRulesPersisted": False,
        "contentScan": False,
        "piiDetection": False,
        "secretDetection": False,
        "identifierDetection": False,
        "promptRedaction": False,
        "responseRedaction": False,
        "transcriptRedaction": False,
        "messageRedaction": False,
        "attachmentRedaction": False,
        "clipboardRedaction": False,
        "auditRedaction": False,
        "redactionApplied": False,
        "redactionResultPersisted": False,
        "redactionReportGenerated": False,
        "promptCapture": False,
        "promptRead": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptContentIncluded": False,
        "messageBodiesIncluded": False,
        "readsTranscript": False,
        "readsSessionStore": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
        "clipboardRead": False,
        "clipboardWrite": False,
        "attachmentReads": False,
        "fileNameIncluded": False,
        "filePathIncluded": False,
        "fileMetadataRead": False,
        "fileContentRead": False,
        "directoryScan": False,
        "fileImport": False,
        "fileUpload": False,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "modelAssetRead": False,
        "modelAssetPathsIncluded": False,
        "modelLoadAttempted": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "touchesHardware": False,
        "hardwareAccess": False,
        "kv260Access": False,
        "networkCalls": False,
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
        "Data-only chat redaction-policy fixture; no redaction rules, prompt, response, transcript, message body, attachment, clipboard data, audit content, file, artifact, model path, runtime log, or private path is read or written.",
        "Content scanning, sensitive-content detection, prompt redaction, response redaction, transcript redaction, message redaction, attachment redaction, clipboard redaction, audit redaction, and result persistence remain disabled or blocked.",
        "No PII, secret, token, path, identifier, or detector match is produced or included.",
        "No model load, runtime execution, provider call, network call, upload, artifact access, or KV260 hardware access is performed.",
        "This is not a release, tag, compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, or runtime implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_redaction_policy() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat redaction fixture."""
    return copy.deepcopy(_CHAT_REDACTION_POLICY)


def chat_redaction_policy_json(redaction_policy: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        redaction_policy
        if redaction_policy is not None
        else create_gemma3n_e4b_kv260_chat_redaction_policy(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat redaction-policy JSON.",
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
    sys.stdout.write(chat_redaction_policy_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
