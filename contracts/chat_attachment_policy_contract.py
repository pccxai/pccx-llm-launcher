#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat attachment policy contract for the planned launcher UI.

The contract describes the disabled local attachment boundary for the
standalone chat surface. It does not open file pickers, read file names,
read file metadata, read file contents, upload files, import artifacts,
read clipboard data, persist attachment state, load models, touch KV260
hardware, call providers, invoke pccx-lab, or start runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatAttachmentPolicy.v0"

CHAT_ATTACHMENT_POLICY_FIELDS = (
    "schemaVersion",
    "attachmentPolicyId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "attachmentPolicyState",
    "attachmentState",
    "filePickerState",
    "fileReadState",
    "uploadState",
    "importState",
    "previewState",
    "persistenceState",
    "privacyState",
    "chatComposerRef",
    "chatActionBarRef",
    "chatShortcutMapRef",
    "chatLocalOnlyPolicyRef",
    "chatTranscriptPolicyRef",
    "attachmentPolicy",
    "attachmentInputs",
    "attachmentControls",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

ATTACHMENT_POLICY_FIELDS = (
    "state",
    "mode",
    "sourcePolicy",
    "allowedInputKinds",
    "maxAttachmentCount",
    "filePickerEnabled",
    "fileMetadataReadEnabled",
    "fileContentReadEnabled",
    "uploadEnabled",
    "importEnabled",
    "previewEnabled",
    "persistenceEnabled",
    "sideEffectPolicy",
    "contentPolicy",
)

ATTACHMENT_INPUT_FIELDS = (
    "inputKind",
    "label",
    "state",
    "enabled",
    "summary",
    "sideEffectPolicy",
    "contentPolicy",
)

ATTACHMENT_CONTROL_FIELDS = (
    "controlId",
    "label",
    "state",
    "enabled",
    "userAction",
    "launcherAction",
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

CHAT_ATTACHMENT_POLICY_STATE_VALUES = (
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

_CHAT_ATTACHMENT_POLICY = {
    "schemaVersion": SCHEMA_VERSION,
    "attachmentPolicyId": "chat_attachment_policy_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-attachment-policy.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_attachment_policy_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "attachmentPolicyState": "blocked",
    "attachmentState": "disabled",
    "filePickerState": "disabled",
    "fileReadState": "blocked",
    "uploadState": "disabled",
    "importState": "disabled",
    "previewState": "disabled",
    "persistenceState": "disabled",
    "privacyState": "summary_only",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatActionBarRef": "chat_action_bar_gemma3n_e4b_kv260_placeholder",
    "chatShortcutMapRef": "chat_shortcut_map_gemma3n_e4b_kv260_placeholder",
    "chatLocalOnlyPolicyRef": "chat_local_only_policy_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "attachmentPolicy": {
        "state": "blocked",
        "mode": "disabled_until_reviewed_local_input_boundary_exists",
        "sourcePolicy": "checked fixture only; no file picker, path, metadata, content, clipboard, transcript, artifact, model path, or runtime log is read",
        "allowedInputKinds": [],
        "maxAttachmentCount": 0,
        "filePickerEnabled": False,
        "fileMetadataReadEnabled": False,
        "fileContentReadEnabled": False,
        "uploadEnabled": False,
        "importEnabled": False,
        "previewEnabled": False,
        "persistenceEnabled": False,
        "sideEffectPolicy": "local_render_only",
        "contentPolicy": "attachment policy metadata only; no file names, paths, bytes, previews, manifests, transcript text, prompt text, or response text are included",
    },
    "attachmentInputs": [
        {
            "inputKind": "local_file",
            "label": "local file",
            "state": "blocked",
            "enabled": False,
            "summary": "Local file attachments need a reviewed picker, metadata, content, redaction, and persistence boundary.",
            "sideEffectPolicy": "no_file_picker_no_file_read",
            "contentPolicy": "no_file_name_path_metadata_or_content",
        },
        {
            "inputKind": "local_directory",
            "label": "local directory",
            "state": "blocked",
            "enabled": False,
            "summary": "Directory attachments remain out of scope until recursive discovery and redaction rules are reviewed.",
            "sideEffectPolicy": "no_directory_scan",
            "contentPolicy": "no_directory_path_listing_or_content",
        },
        {
            "inputKind": "clipboard_payload",
            "label": "clipboard payload",
            "state": "disabled",
            "enabled": False,
            "summary": "Clipboard-backed attachments remain disabled because no clipboard read boundary exists.",
            "sideEffectPolicy": "no_clipboard_read",
            "contentPolicy": "no_clipboard_content",
        },
        {
            "inputKind": "generated_artifact",
            "label": "generated artifact",
            "state": "blocked",
            "enabled": False,
            "summary": "Generated artifacts are not read or attached until an artifact input boundary is reviewed.",
            "sideEffectPolicy": "no_artifact_read",
            "contentPolicy": "no_artifact_path_metadata_or_content",
        },
        {
            "inputKind": "transcript_export",
            "label": "transcript export",
            "state": "disabled",
            "enabled": False,
            "summary": "Transcript export as an attachment remains disabled until storage and redaction policy exists.",
            "sideEffectPolicy": "no_transcript_export",
            "contentPolicy": "no_transcript_content",
        },
    ],
    "attachmentControls": [
        {
            "controlId": "open_file_picker",
            "label": "open file picker",
            "state": "disabled",
            "enabled": False,
            "userAction": "Choose files only after a reviewed local file-input boundary exists.",
            "launcherAction": "Keep the picker disabled and do not ask the host for file handles.",
            "sideEffectPolicy": "no_file_picker",
            "blockedReasonRef": "file_picker_boundary_absent",
        },
        {
            "controlId": "read_file_metadata",
            "label": "read file metadata",
            "state": "blocked",
            "enabled": False,
            "userAction": "Read file metadata only after explicit consent, filtering, and redaction policy exists.",
            "launcherAction": "Refuse metadata reads because file input has not been reviewed.",
            "sideEffectPolicy": "no_file_metadata_read",
            "blockedReasonRef": "metadata_read_boundary_absent",
        },
        {
            "controlId": "read_file_content",
            "label": "read file content",
            "state": "blocked",
            "enabled": False,
            "userAction": "Read attachment content only after local parsing and redaction rules are reviewed.",
            "launcherAction": "Refuse content reads because no attachment ingestion boundary exists.",
            "sideEffectPolicy": "no_file_content_read",
            "blockedReasonRef": "file_content_read_boundary_absent",
        },
        {
            "controlId": "import_attachment",
            "label": "import attachment",
            "state": "disabled",
            "enabled": False,
            "userAction": "Import only after type limits, size limits, redaction, and persistence review.",
            "launcherAction": "Keep import disabled and do not copy, parse, or index any file.",
            "sideEffectPolicy": "no_import_no_copy_no_parse",
            "blockedReasonRef": "import_export_boundary_absent",
        },
        {
            "controlId": "upload_attachment",
            "label": "upload attachment",
            "state": "disabled",
            "enabled": False,
            "userAction": "Upload remains unavailable for the local-only chat surface.",
            "launcherAction": "Do not upload attachment data or call cloud/provider endpoints.",
            "sideEffectPolicy": "no_upload_no_network",
            "blockedReasonRef": "local_only_upload_block",
        },
        {
            "controlId": "preview_attachment",
            "label": "preview attachment",
            "state": "disabled",
            "enabled": False,
            "userAction": "Preview only after file read, rendering, and redaction boundaries exist.",
            "launcherAction": "Keep preview disabled because no attachment bytes may be read.",
            "sideEffectPolicy": "no_preview_no_file_read",
            "blockedReasonRef": "file_content_read_boundary_absent",
        },
        {
            "controlId": "persist_attachment",
            "label": "persist attachment",
            "state": "disabled",
            "enabled": False,
            "userAction": "Persist only after a reviewed local store and deletion policy exists.",
            "launcherAction": "Refuse attachment persistence because no storage boundary exists.",
            "sideEffectPolicy": "no_artifact_write",
            "blockedReasonRef": "attachment_persistence_boundary_absent",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "attachment_runtime_not_reviewed",
            "state": "blocked",
            "summary": "Attachment ingestion requires separate local parser, redaction, and storage review.",
            "requiredBefore": "attachment_enabled",
        },
        {
            "reasonId": "file_picker_boundary_absent",
            "state": "planned",
            "summary": "No reviewed file-picker or explicit user-selection boundary exists.",
            "requiredBefore": "open_file_picker_enabled",
        },
        {
            "reasonId": "metadata_read_boundary_absent",
            "state": "planned",
            "summary": "No reviewed file metadata read boundary exists.",
            "requiredBefore": "read_file_metadata_enabled",
        },
        {
            "reasonId": "file_content_read_boundary_absent",
            "state": "planned",
            "summary": "No reviewed file content read, parser, size-limit, or redaction boundary exists.",
            "requiredBefore": "read_file_content_enabled",
        },
        {
            "reasonId": "import_export_boundary_absent",
            "state": "not_configured",
            "summary": "No import, copy, export, or attachment manifest boundary is configured.",
            "requiredBefore": "import_attachment_enabled",
        },
        {
            "reasonId": "attachment_persistence_boundary_absent",
            "state": "requires_evidence",
            "summary": "Attachment persistence needs explicit local store, retention, deletion, and rollback policy.",
            "requiredBefore": "persist_attachment_enabled",
        },
        {
            "reasonId": "local_only_upload_block",
            "state": "disabled",
            "summary": "The standalone chat surface keeps upload and cloud/provider attachment handoff disabled.",
            "requiredBefore": "upload_attachment_enabled",
        },
        {
            "reasonId": "clipboard_boundary_absent",
            "state": "not_configured",
            "summary": "No clipboard-read boundary exists for attachment payloads.",
            "requiredBefore": "clipboard_attachment_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Composer attach controls remain disabled and do not read files.",
        },
        {
            "refId": "chat_action_bar",
            "schemaVersion": "pccx.chatActionBar.v0",
            "fixturePath": "contracts/fixtures/chat-action-bar.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Action-bar attach control remains disabled.",
        },
        {
            "refId": "chat_shortcut_map",
            "schemaVersion": "pccx.chatShortcutMap.v0",
            "fixturePath": "contracts/fixtures/chat-shortcut-map.gemma3n-e4b-kv260-placeholder.json",
            "state": "planned",
            "summary": "Shortcut-map attach binding remains disabled and dispatch-free.",
        },
        {
            "refId": "chat_local_only_policy",
            "schemaVersion": "pccx.chatLocalOnlyPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-local-only-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Local-only policy keeps cloud/provider fallback disabled.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Transcript export and persistence remain disabled.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "attachmentPolicyDisplayOnly": True,
        "attachmentMetadataOnly": True,
        "attachmentsEnabled": False,
        "attachmentListIncluded": False,
        "filePickerOpened": False,
        "fileMetadataRead": False,
        "fileContentRead": False,
        "fileNameIncluded": False,
        "filePathIncluded": False,
        "fileBytesIncluded": False,
        "directoryScan": False,
        "attachmentReads": False,
        "attachmentPersistence": False,
        "fileUpload": False,
        "fileImport": False,
        "filePreview": False,
        "clipboardRead": False,
        "clipboardWrite": False,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "artifactWrites": False,
        "artifactReads": False,
        "readsSessionStore": False,
        "readsTranscript": False,
        "transcriptExport": False,
        "transcriptPersistence": False,
        "promptCapture": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "promptPersistence": False,
        "inputAccepted": False,
        "sendAttempted": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
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
        "Data-only chat attachment-policy fixture; no real attachment input boundary is configured or read.",
        "Attachment controls remain disabled or blocked; no file picker opens and no file name, path, metadata, bytes, preview, transcript, prompt, response, model path, runtime log, private path, secret, or token content is included.",
        "No local file, directory, clipboard payload, generated artifact, transcript export, or attachment manifest is read, imported, uploaded, copied, parsed, indexed, persisted, deleted, or written.",
        "No model load, runtime execution, provider call, network call, pccx-lab invocation, systemverilog-ide invocation, or KV260 hardware access is performed.",
        "This is not a release, tag, compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, runtime, model, parser, file-input, or storage implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_attachment_policy() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 attachment-policy fixture."""
    return copy.deepcopy(_CHAT_ATTACHMENT_POLICY)


def chat_attachment_policy_json(policy: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        policy
        if policy is not None
        else create_gemma3n_e4b_kv260_chat_attachment_policy(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat attachment policy JSON.",
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
    sys.stdout.write(chat_attachment_policy_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
