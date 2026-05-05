#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat clipboard policy contract for the planned launcher UI.

The contract describes disabled clipboard gates for the standalone chat
surface. It does not read from or write to the clipboard, paste prompt
content, copy messages, import clipboard payloads, export transcripts,
read session stores, read transcripts, load models, touch KV260 hardware,
call providers, invoke pccx-lab, or start runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatClipboardPolicy.v0"

CHAT_CLIPBOARD_POLICY_FIELDS = (
    "schemaVersion",
    "clipboardPolicyId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "clipboardPolicyState",
    "clipboardReadState",
    "clipboardWriteState",
    "copyActionState",
    "pasteActionState",
    "clipboardImportState",
    "clipboardExportState",
    "selectionState",
    "messageContentState",
    "transcriptState",
    "privacyState",
    "chatComposerRef",
    "chatActionBarRef",
    "chatMessageListRef",
    "chatAttachmentPolicyRef",
    "chatTranscriptPolicyRef",
    "chatLocalOnlyPolicyRef",
    "clipboardPolicy",
    "clipboardSurfaces",
    "clipboardControls",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

CLIPBOARD_POLICY_FIELDS = (
    "state",
    "mode",
    "sourcePolicy",
    "contentPolicy",
    "readEnabled",
    "writeEnabled",
    "copyEnabled",
    "pasteEnabled",
    "importEnabled",
    "exportEnabled",
    "selectionRequired",
    "userConsentRequired",
    "sideEffectPolicy",
    "persistencePolicy",
)

CLIPBOARD_SURFACE_FIELDS = (
    "surfaceId",
    "label",
    "state",
    "enabled",
    "summary",
    "sideEffectPolicy",
)

CLIPBOARD_CONTROL_FIELDS = (
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

CHAT_CLIPBOARD_POLICY_STATE_VALUES = (
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
    "requires_evidence",
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_CLIPBOARD_POLICY = {
    "schemaVersion": SCHEMA_VERSION,
    "clipboardPolicyId": "chat_clipboard_policy_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-clipboard-policy.gemma3n-e4b-kv260.2026-05-05",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_clipboard_policy_boundary_2026-05-05",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "clipboardPolicyState": "blocked",
    "clipboardReadState": "disabled",
    "clipboardWriteState": "disabled",
    "copyActionState": "disabled",
    "pasteActionState": "disabled",
    "clipboardImportState": "disabled",
    "clipboardExportState": "disabled",
    "selectionState": "empty_not_captured",
    "messageContentState": "empty_not_captured",
    "transcriptState": "not_started",
    "privacyState": "summary_only",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatActionBarRef": "chat_action_bar_gemma3n_e4b_kv260_placeholder",
    "chatMessageListRef": "chat_message_list_gemma3n_e4b_kv260_placeholder",
    "chatAttachmentPolicyRef": "chat_attachment_policy_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "chatLocalOnlyPolicyRef": "chat_local_only_policy_gemma3n_e4b_kv260_placeholder",
    "clipboardPolicy": {
        "state": "blocked",
        "mode": "disabled_until_reviewed_clipboard_boundary_exists",
        "sourcePolicy": "checked fixture only; no clipboard API, selection, message, transcript, prompt, attachment, file, artifact, session store, model path, or runtime log is read",
        "contentPolicy": "clipboard policy metadata only; no clipboard text, prompt text, response text, transcript text, selection text, file names, paths, bytes, or artifacts are included",
        "readEnabled": False,
        "writeEnabled": False,
        "copyEnabled": False,
        "pasteEnabled": False,
        "importEnabled": False,
        "exportEnabled": False,
        "selectionRequired": False,
        "userConsentRequired": True,
        "sideEffectPolicy": "local_render_only",
        "persistencePolicy": "no clipboard read, write, paste, copy, import, export, attachment, transcript, session, or artifact persistence",
    },
    "clipboardSurfaces": [
        {
            "surfaceId": "message_actions",
            "label": "message actions",
            "state": "disabled",
            "enabled": False,
            "summary": "Copy message controls remain disabled because no message content is captured.",
            "sideEffectPolicy": "no_clipboard_write",
        },
        {
            "surfaceId": "composer_input",
            "label": "composer input",
            "state": "blocked",
            "enabled": False,
            "summary": "Paste into the composer remains disabled until an explicit clipboard read boundary exists.",
            "sideEffectPolicy": "no_clipboard_read",
        },
        {
            "surfaceId": "attachment_input",
            "label": "attachment input",
            "state": "disabled",
            "enabled": False,
            "summary": "Clipboard-backed attachments remain disabled until attachment ingestion and redaction rules exist.",
            "sideEffectPolicy": "no_clipboard_attachment_read",
        },
        {
            "surfaceId": "transcript_export",
            "label": "transcript export",
            "state": "not_configured",
            "enabled": False,
            "summary": "Transcript copy/export remains disabled until retention and redaction boundaries are reviewed.",
            "sideEffectPolicy": "no_transcript_export_no_clipboard_write",
        },
    ],
    "clipboardControls": [
        {
            "controlId": "copy_message",
            "label": "copy message",
            "state": "disabled",
            "enabled": False,
            "userAction": "Copy only after message content, selection, redaction, and clipboard write boundaries are reviewed.",
            "launcherAction": "Keep copy disabled and do not request clipboard write permission.",
            "sideEffectPolicy": "no_clipboard_write",
            "contentPolicy": "no message body, selection text, response text, or prompt text",
            "blockedReasonRef": "message_content_absent",
        },
        {
            "controlId": "copy_transcript",
            "label": "copy transcript",
            "state": "disabled",
            "enabled": False,
            "userAction": "Copy transcripts only after storage, retention, and redaction policy exists.",
            "launcherAction": "Keep transcript copy disabled and do not read transcript data.",
            "sideEffectPolicy": "no_transcript_read_no_clipboard_write",
            "contentPolicy": "no transcript, prompt, response, session title, or summary content",
            "blockedReasonRef": "transcript_export_not_reviewed",
        },
        {
            "controlId": "paste_prompt",
            "label": "paste prompt",
            "state": "disabled",
            "enabled": False,
            "userAction": "Paste only after an explicit local clipboard read and prompt redaction boundary exists.",
            "launcherAction": "Keep paste disabled and do not inspect clipboard contents.",
            "sideEffectPolicy": "no_clipboard_read",
            "contentPolicy": "no clipboard text or prompt text",
            "blockedReasonRef": "clipboard_api_boundary_absent",
        },
        {
            "controlId": "paste_attachment",
            "label": "paste attachment",
            "state": "disabled",
            "enabled": False,
            "userAction": "Paste attachments only after local attachment and clipboard payload policies are reviewed.",
            "launcherAction": "Keep clipboard attachments disabled and do not read clipboard payloads.",
            "sideEffectPolicy": "no_clipboard_attachment_read",
            "contentPolicy": "no clipboard payload, file name, path, metadata, preview, or bytes",
            "blockedReasonRef": "attachment_clipboard_boundary_absent",
        },
        {
            "controlId": "import_clipboard_payload",
            "label": "import clipboard payload",
            "state": "disabled",
            "enabled": False,
            "userAction": "Import clipboard data only after type limits, redaction, and persistence review.",
            "launcherAction": "Do not import, parse, index, or persist clipboard data.",
            "sideEffectPolicy": "no_clipboard_import",
            "contentPolicy": "no clipboard text, image, file, path, metadata, preview, or bytes",
            "blockedReasonRef": "privacy_redaction_not_reviewed",
        },
        {
            "controlId": "export_to_clipboard",
            "label": "export to clipboard",
            "state": "disabled",
            "enabled": False,
            "userAction": "Export to clipboard only after explicit user action and redaction policy exists.",
            "launcherAction": "Do not write transcript, message, error, file, or artifact data to the clipboard.",
            "sideEffectPolicy": "no_clipboard_export",
            "contentPolicy": "no transcript, message, error detail, file, path, model, runtime, or artifact content",
            "blockedReasonRef": "privacy_redaction_not_reviewed",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "clipboard_api_boundary_absent",
            "state": "blocked",
            "summary": "No reviewed clipboard API permission, read, write, or paste boundary exists.",
            "requiredBefore": "clipboard_read_or_write_enabled",
        },
        {
            "reasonId": "message_content_absent",
            "state": "empty_not_captured",
            "summary": "No prompt, response, transcript, or message body content is present.",
            "requiredBefore": "copy_message_enabled",
        },
        {
            "reasonId": "transcript_export_not_reviewed",
            "state": "not_configured",
            "summary": "Transcript export needs explicit storage, retention, and redaction boundaries.",
            "requiredBefore": "copy_transcript_enabled",
        },
        {
            "reasonId": "attachment_clipboard_boundary_absent",
            "state": "disabled",
            "summary": "Clipboard-backed attachments require a reviewed attachment payload boundary.",
            "requiredBefore": "paste_attachment_enabled",
        },
        {
            "reasonId": "privacy_redaction_not_reviewed",
            "state": "not_configured",
            "summary": "Clipboard import and export need explicit redaction and persistence review.",
            "requiredBefore": "clipboard_import_or_export_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Composer data keeps paste controls disabled.",
        },
        {
            "refId": "chat_action_bar",
            "schemaVersion": "pccx.chatActionBar.v0",
            "fixturePath": "contracts/fixtures/chat-action-bar.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Action bar data keeps copy/export controls disabled.",
        },
        {
            "refId": "chat_message_list",
            "schemaVersion": "pccx.chatMessageList.v0",
            "fixturePath": "contracts/fixtures/chat-message-list.gemma3n-e4b-kv260-placeholder.json",
            "state": "empty_not_captured",
            "summary": "Empty message-list data prevents message copy actions.",
        },
        {
            "refId": "chat_attachment_policy",
            "schemaVersion": "pccx.chatAttachmentPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-attachment-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Attachment policy data keeps clipboard-backed attachment reads disabled.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Transcript persistence and export remain unavailable.",
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
        "clipboardPolicyDisplayOnly": True,
        "clipboardMetadataOnly": True,
        "clipboardRead": False,
        "clipboardWrite": False,
        "clipboardCopy": False,
        "clipboardPaste": False,
        "clipboardImport": False,
        "clipboardExport": False,
        "clipboardAttachmentRead": False,
        "clipboardEventListenerInstalled": False,
        "selectionRead": False,
        "messageBodiesIncluded": False,
        "promptCapture": False,
        "promptRead": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptContentIncluded": False,
        "readsTranscript": False,
        "transcriptExport": False,
        "readsSessionStore": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
        "attachmentReads": False,
        "fileUpload": False,
        "fileImport": False,
        "filePreview": False,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "modelAssetRead": False,
        "modelAssetPathsIncluded": False,
        "modelWeightPathsIncluded": False,
        "modelLoadAttempted": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "touchesHardware": False,
        "hardwareAccess": False,
        "kv260Access": False,
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
        "Data-only chat clipboard-policy fixture; no clipboard content, selection, prompt, response, transcript, message body, file, artifact, model path, runtime log, or private path is read or written.",
        "Clipboard read, write, paste, copy, import, export, transcript-copy, message-copy, and clipboard-backed attachment controls remain disabled or blocked.",
        "No session store, transcript, message body, attachment, artifact, private path, secret, token, log, or hardware dump is read or written.",
        "No clipboard API request, prompt capture, transcript export, upload, import, model load, runtime execution, provider call, network call, or KV260 hardware access is performed.",
        "This is not a release, tag, compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, or runtime implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_clipboard_policy() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat clipboard fixture."""
    return copy.deepcopy(_CHAT_CLIPBOARD_POLICY)


def chat_clipboard_policy_json(clipboard_policy: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        clipboard_policy
        if clipboard_policy is not None
        else create_gemma3n_e4b_kv260_chat_clipboard_policy(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat clipboard-policy JSON.",
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
    sys.stdout.write(chat_clipboard_policy_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
