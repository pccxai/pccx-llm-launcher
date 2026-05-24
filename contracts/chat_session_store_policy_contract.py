#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat session-store policy contract for the planned launcher UI.

The contract describes disabled local session-store configuration, read,
write, delete, retention, and migration gates for the standalone chat
surface. It does not read configuration files, paths, manifests, session
records, transcripts, titles, prompts, responses, summaries, model assets,
private paths, or logs; it does not write, delete, migrate, persist, load
models, touch KV260 hardware, call providers, invoke pccx-lab, or start
runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatSessionStorePolicy.v0"

CHAT_SESSION_STORE_POLICY_FIELDS = (
    "schemaVersion",
    "sessionStorePolicyId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "sessionStorePolicyState",
    "storeState",
    "storePathState",
    "manifestState",
    "readState",
    "writeState",
    "deleteState",
    "retentionState",
    "migrationState",
    "privacyState",
    "chatSessionRef",
    "chatSessionIndexRef",
    "chatSessionLifecycleRef",
    "chatSessionTitlePolicyRef",
    "chatTranscriptPolicyRef",
    "chatPreferencesRef",
    "sessionStorePolicy",
    "storeSurfaces",
    "storeControls",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

SESSION_STORE_POLICY_FIELDS = (
    "state",
    "mode",
    "sourcePolicy",
    "storeConfigured",
    "storePathConfigured",
    "manifestSchemaConfigured",
    "readEnabled",
    "writeEnabled",
    "deleteEnabled",
    "retentionEnabled",
    "migrationEnabled",
    "sideEffectPolicy",
    "contentPolicy",
)

STORE_SURFACE_FIELDS = (
    "surfaceId",
    "label",
    "state",
    "enabled",
    "summary",
    "sideEffectPolicy",
    "contentPolicy",
)

STORE_CONTROL_FIELDS = (
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

CHAT_SESSION_STORE_POLICY_STATE_VALUES = (
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

_CHAT_SESSION_STORE_POLICY = {
    "schemaVersion": SCHEMA_VERSION,
    "sessionStorePolicyId": "chat_session_store_policy_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-session-store-policy.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_session_store_policy_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "sessionStorePolicyState": "blocked",
    "storeState": "not_configured",
    "storePathState": "not_configured",
    "manifestState": "not_configured",
    "readState": "blocked",
    "writeState": "disabled",
    "deleteState": "disabled",
    "retentionState": "not_configured",
    "migrationState": "disabled",
    "privacyState": "summary_only",
    "chatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "chatSessionIndexRef": "chat_session_index_gemma3n_e4b_kv260_placeholder",
    "chatSessionLifecycleRef": "chat_session_lifecycle_gemma3n_e4b_kv260_placeholder",
    "chatSessionTitlePolicyRef": "chat_session_title_policy_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "chatPreferencesRef": "chat_preferences_gemma3n_e4b_kv260_placeholder",
    "sessionStorePolicy": {
        "state": "blocked",
        "mode": "disabled_until_reviewed_local_session_store_boundary_exists",
        "sourcePolicy": "checked fixture only; no config, environment, path, manifest, transcript, title, prompt, response, summary, artifact, model path, or runtime log is read",
        "storeConfigured": False,
        "storePathConfigured": False,
        "manifestSchemaConfigured": False,
        "readEnabled": False,
        "writeEnabled": False,
        "deleteEnabled": False,
        "retentionEnabled": False,
        "migrationEnabled": False,
        "sideEffectPolicy": "local_render_only",
        "contentPolicy": "session-store policy metadata only; no store path, manifest body, session record, transcript text, title text, prompt text, response text, summary text, or model path is included",
    },
    "storeSurfaces": [
        {
            "surfaceId": "local_store_path",
            "label": "local store path",
            "state": "not_configured",
            "enabled": False,
            "summary": "No local session-store path is configured, read, resolved, or emitted.",
            "sideEffectPolicy": "no_config_or_path_read",
            "contentPolicy": "no_store_path_or_private_path",
        },
        {
            "surfaceId": "session_manifest",
            "label": "session manifest",
            "state": "not_configured",
            "enabled": False,
            "summary": "No manifest schema is configured and no manifest is read.",
            "sideEffectPolicy": "no_manifest_read",
            "contentPolicy": "no_manifest_body_or_session_ids",
        },
        {
            "surfaceId": "session_record",
            "label": "session record",
            "state": "blocked",
            "enabled": False,
            "summary": "Session records stay unavailable until a reviewed read/write boundary exists.",
            "sideEffectPolicy": "no_session_store_read",
            "contentPolicy": "no_session_record_or_message_content",
        },
        {
            "surfaceId": "title_record",
            "label": "title record",
            "state": "blocked",
            "enabled": False,
            "summary": "Stored titles remain unavailable because no title-read boundary exists.",
            "sideEffectPolicy": "no_session_title_read",
            "contentPolicy": "no_session_title_content",
        },
        {
            "surfaceId": "transcript_record",
            "label": "transcript record",
            "state": "disabled",
            "enabled": False,
            "summary": "Transcript records are not retained or read.",
            "sideEffectPolicy": "no_transcript_read_or_persistence",
            "contentPolicy": "no_transcript_content",
        },
        {
            "surfaceId": "retention_rule",
            "label": "retention rule",
            "state": "not_configured",
            "enabled": False,
            "summary": "No retention period, deletion rule, or migration rule is configured.",
            "sideEffectPolicy": "no_retention_write",
            "contentPolicy": "retention_metadata_only",
        },
    ],
    "storeControls": [
        {
            "controlId": "configure_store",
            "label": "configure store",
            "state": "disabled",
            "enabled": False,
            "userAction": "Configure a local store only after explicit storage, path, and privacy review.",
            "launcherAction": "Keep store configuration disabled and do not read or write config.",
            "sideEffectPolicy": "no_config_read_or_write",
            "blockedReasonRef": "store_path_boundary_absent",
        },
        {
            "controlId": "read_store_path",
            "label": "read store path",
            "state": "blocked",
            "enabled": False,
            "userAction": "Read a configured store path only after explicit local path review.",
            "launcherAction": "Refuse path reads because no config/path boundary exists.",
            "sideEffectPolicy": "no_config_or_path_read",
            "blockedReasonRef": "store_path_boundary_absent",
        },
        {
            "controlId": "read_manifest",
            "label": "read manifest",
            "state": "blocked",
            "enabled": False,
            "userAction": "Read a manifest only after schema, redaction, and migration rules are reviewed.",
            "launcherAction": "Refuse manifest reads because no session-store boundary exists.",
            "sideEffectPolicy": "no_manifest_read",
            "blockedReasonRef": "manifest_schema_absent",
        },
        {
            "controlId": "read_session_record",
            "label": "read session record",
            "state": "blocked",
            "enabled": False,
            "userAction": "Read session records only after local store and content redaction review.",
            "launcherAction": "Refuse session-record reads.",
            "sideEffectPolicy": "no_session_store_read",
            "blockedReasonRef": "session_store_read_boundary_absent",
        },
        {
            "controlId": "write_session_record",
            "label": "write session record",
            "state": "disabled",
            "enabled": False,
            "userAction": "Persist sessions only after a reviewed write, retention, and rollback policy exists.",
            "launcherAction": "Refuse session writes and do not create store files.",
            "sideEffectPolicy": "no_session_store_write",
            "blockedReasonRef": "session_store_write_boundary_absent",
        },
        {
            "controlId": "delete_session_record",
            "label": "delete session record",
            "state": "disabled",
            "enabled": False,
            "userAction": "Delete records only after retention, confirmation, and rollback rules exist.",
            "launcherAction": "Keep deletion disabled and do not mutate a store.",
            "sideEffectPolicy": "no_delete_no_write",
            "blockedReasonRef": "deletion_retention_policy_absent",
        },
        {
            "controlId": "migrate_store",
            "label": "migrate store",
            "state": "disabled",
            "enabled": False,
            "userAction": "Migrate a store only after versioned schema and rollback review.",
            "launcherAction": "Keep migration disabled and do not inspect or rewrite store files.",
            "sideEffectPolicy": "no_migration_no_store_read",
            "blockedReasonRef": "migration_policy_absent",
        },
        {
            "controlId": "persist_store_policy",
            "label": "persist store policy",
            "state": "disabled",
            "enabled": False,
            "userAction": "Persist policy only after configuration storage is reviewed.",
            "launcherAction": "Do not write policy, preference, or config files.",
            "sideEffectPolicy": "no_policy_write",
            "blockedReasonRef": "session_store_write_boundary_absent",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "store_not_configured",
            "state": "not_configured",
            "summary": "No reviewed local chat session store is configured.",
            "requiredBefore": "session_store_available",
        },
        {
            "reasonId": "store_path_boundary_absent",
            "state": "planned",
            "summary": "No reviewed config/path boundary exists for locating a local store.",
            "requiredBefore": "store_path_available",
        },
        {
            "reasonId": "manifest_schema_absent",
            "state": "not_configured",
            "summary": "No reviewed manifest schema, version, or migration policy exists.",
            "requiredBefore": "manifest_read_enabled",
        },
        {
            "reasonId": "session_store_read_boundary_absent",
            "state": "blocked",
            "summary": "Session reads require reviewed manifest, redaction, and content policy.",
            "requiredBefore": "read_session_record_enabled",
        },
        {
            "reasonId": "session_store_write_boundary_absent",
            "state": "disabled",
            "summary": "Session writes require explicit local persistence and rollback policy.",
            "requiredBefore": "write_session_record_enabled",
        },
        {
            "reasonId": "deletion_retention_policy_absent",
            "state": "requires_evidence",
            "summary": "Deletion needs retention, confirmation, and recovery rules.",
            "requiredBefore": "delete_session_record_enabled",
        },
        {
            "reasonId": "migration_policy_absent",
            "state": "not_configured",
            "summary": "No versioned schema migration or rollback policy exists.",
            "requiredBefore": "migrate_store_enabled",
        },
        {
            "reasonId": "redaction_policy_absent",
            "state": "planned",
            "summary": "Stored content would require prompt, response, transcript, title, and summary redaction rules.",
            "requiredBefore": "stored_content_allowed",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_session",
            "schemaVersion": "pccx.chatSession.v0",
            "fixturePath": "contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json",
            "state": "inactive",
            "summary": "Base chat session remains inactive and does not persist state.",
        },
        {
            "refId": "chat_session_index",
            "schemaVersion": "pccx.chatSessionIndex.v0",
            "fixturePath": "contracts/fixtures/chat-session-index.gemma3n-e4b-kv260-placeholder.json",
            "state": "not_configured",
            "summary": "Session index remains empty and does not read a store.",
        },
        {
            "refId": "chat_session_lifecycle",
            "schemaVersion": "pccx.chatSessionLifecycle.v0",
            "fixturePath": "contracts/fixtures/chat-session-lifecycle.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Lifecycle create, restore, clear, close, and export actions remain disabled or blocked.",
        },
        {
            "refId": "chat_session_title_policy",
            "schemaVersion": "pccx.chatSessionTitlePolicy.v0",
            "fixturePath": "contracts/fixtures/chat-session-title-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Stored title reads, generation, rename, and persistence remain disabled or blocked.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Transcript persistence and export remain disabled.",
        },
        {
            "refId": "chat_preferences",
            "schemaVersion": "pccx.chatPreferences.v0",
            "fixturePath": "contracts/fixtures/chat-preferences.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Preferences do not read or write store paths.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "sessionStorePolicyDisplayOnly": True,
        "storeMetadataOnly": True,
        "storeConfigured": False,
        "storePathConfigured": False,
        "storePathIncluded": False,
        "configRead": False,
        "configWrite": False,
        "environmentRead": False,
        "readsSessionStore": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
        "readsSessionManifest": False,
        "manifestContentIncluded": False,
        "sessionRecordIncluded": False,
        "sessionPersistence": False,
        "sessionDeletion": False,
        "retentionPolicyActive": False,
        "migrationAttempted": False,
        "rollbackAttempted": False,
        "readsSessionTitle": False,
        "sessionTitleIncluded": False,
        "titleContentIncluded": False,
        "titlePersistence": False,
        "readsTranscript": False,
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
        "clipboardRead": False,
        "clipboardWrite": False,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "artifactWrites": False,
        "artifactReads": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
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
        "runtimeLogsIncluded": False,
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
        "Data-only chat session-store policy fixture; no real local session store is configured or read.",
        "No store path, private path, manifest body, session record, stored title, transcript, prompt, response, summary, model path, runtime log, secret, or token content is included.",
        "No configuration file, environment value, session store, manifest, transcript, title, prompt, response, summary, attachment, artifact, model asset, private path, raw log, or hardware dump is read.",
        "No session, transcript, title, policy, config, preference, artifact, or store file is written, deleted, migrated, persisted, imported, exported, compacted, or rolled back.",
        "No model load, runtime execution, provider call, network call, pccx-lab invocation, systemverilog-ide invocation, or KV260 hardware access is performed.",
        "This is not a release, tag, compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, runtime, model, session-store, migration, or storage implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_session_store_policy() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 session-store policy fixture."""
    return copy.deepcopy(_CHAT_SESSION_STORE_POLICY)


def chat_session_store_policy_json(policy: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        policy
        if policy is not None
        else create_gemma3n_e4b_kv260_chat_session_store_policy(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat session-store policy JSON.",
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
    sys.stdout.write(chat_session_store_policy_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
