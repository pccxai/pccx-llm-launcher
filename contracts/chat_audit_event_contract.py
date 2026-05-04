#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat audit-event contract for the planned launcher UI.

The contract describes a conservative audit-event metadata shape for future
blocked chat UI events. It does not read, accept, echo, store, persist, or log
prompt, response, transcript, model, runtime, or artifact content. It also does
not load models, start runtime code, touch KV260 hardware, call providers,
invoke pccx-lab, or read/write artifacts.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatAuditEvent.v0"
AUDIT_EVENT_ENVELOPE_SCHEMA_VERSION = "pccx.chatAuditEventEnvelope.v0"

CHAT_AUDIT_EVENT_FIELDS = (
    "schemaVersion",
    "auditEventId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "auditState",
    "eventState",
    "loggingState",
    "eventKind",
    "eventOutcome",
    "contentState",
    "persistenceState",
    "storageState",
    "privacyState",
    "parentChatSessionRef",
    "chatReadinessRef",
    "chatComposerRef",
    "chatSendResultRef",
    "chatTranscriptPolicyRef",
    "eventEnvelope",
    "redactionPolicy",
    "auditFields",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

EVENT_ENVELOPE_FIELDS = (
    "schemaVersion",
    "envelopeId",
    "state",
    "eventKind",
    "eventOutcome",
    "sequenceState",
    "timestampState",
    "targetIncluded",
    "sessionRefIncluded",
    "actorIdentifierIncluded",
    "promptContentIncluded",
    "responseContentIncluded",
    "transcriptContentIncluded",
    "modelPathIncluded",
    "runtimeStarted",
    "modelLoaded",
    "writeAttempted",
    "contentPolicy",
    "sideEffectPolicy",
    "summary",
)

REDACTION_POLICY_FIELDS = (
    "state",
    "summaryLevel",
    "promptContentIncluded",
    "responseContentIncluded",
    "transcriptContentIncluded",
    "privatePathsIncluded",
    "secretsIncluded",
    "tokensIncluded",
    "rawLogsIncluded",
    "hardwareDumpsIncluded",
    "generatedBlobsIncluded",
    "actorIdentifiersIncluded",
    "modelPathsIncluded",
    "summary",
)

AUDIT_FIELD_FIELDS = (
    "fieldId",
    "valueKind",
    "state",
    "included",
    "summary",
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

CHAT_AUDIT_EVENT_STATE_VALUES = (
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
    "redacted",
    "requires_evidence",
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_AUDIT_EVENT = {
    "schemaVersion": SCHEMA_VERSION,
    "auditEventId": "chat_audit_event_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-audit-event.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_audit_event_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "auditState": "available_as_data",
    "eventState": "blocked",
    "loggingState": "not_configured",
    "eventKind": "blocked_chat_send",
    "eventOutcome": "blocked",
    "contentState": "empty_not_captured",
    "persistenceState": "disabled",
    "storageState": "not_configured",
    "privacyState": "summary_only",
    "parentChatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatSendResultRef": "chat_send_result_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "eventEnvelope": {
        "schemaVersion": AUDIT_EVENT_ENVELOPE_SCHEMA_VERSION,
        "envelopeId": "blocked_chat_send_audit_event_gemma3n_e4b_kv260_placeholder",
        "state": "blocked",
        "eventKind": "blocked_chat_send",
        "eventOutcome": "blocked",
        "sequenceState": "placeholder",
        "timestampState": "not_generated",
        "targetIncluded": True,
        "sessionRefIncluded": True,
        "actorIdentifierIncluded": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptContentIncluded": False,
        "modelPathIncluded": False,
        "runtimeStarted": False,
        "modelLoaded": False,
        "writeAttempted": False,
        "contentPolicy": "fixture carries audit metadata only; no prompt, response, or transcript content is stored",
        "sideEffectPolicy": "no_runtime_execution_no_write",
        "summary": "Blocked chat send can be represented as local audit metadata without creating a log entry.",
    },
    "redactionPolicy": {
        "state": "summary_only",
        "summaryLevel": "metadata_only",
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptContentIncluded": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
        "rawLogsIncluded": False,
        "hardwareDumpsIncluded": False,
        "generatedBlobsIncluded": False,
        "actorIdentifiersIncluded": False,
        "modelPathsIncluded": False,
        "summary": "Audit summaries stay limited to event ids, states, blocked reasons, and fixture references.",
    },
    "auditFields": [
        {
            "fieldId": "audit_event_id",
            "valueKind": "deterministic_fixture_identifier",
            "state": "placeholder",
            "included": True,
            "summary": "A deterministic fixture identifier is available.",
            "contentPolicy": "metadata_only",
        },
        {
            "fieldId": "event_kind",
            "valueKind": "enumerated_state",
            "state": "available_as_data",
            "included": True,
            "summary": "The blocked chat send event kind is represented as local data.",
            "contentPolicy": "metadata_only",
        },
        {
            "fieldId": "target_identity",
            "valueKind": "target_descriptor",
            "state": "target_selected",
            "included": True,
            "summary": "The planned Gemma 3N E4B plus KV260 target identity is included.",
            "contentPolicy": "target_metadata_only",
        },
        {
            "fieldId": "chat_session_ref",
            "valueKind": "fixture_reference",
            "state": "available_as_data",
            "included": True,
            "summary": "The parent chat/session fixture id is referenced without session content.",
            "contentPolicy": "reference_only",
        },
        {
            "fieldId": "blocked_reason_ids",
            "valueKind": "reason_identifier_list",
            "state": "blocked",
            "included": True,
            "summary": "Blocked reason identifiers are included without prompt or response bodies.",
            "contentPolicy": "metadata_only",
        },
        {
            "fieldId": "prompt_content",
            "valueKind": "message_body",
            "state": "empty_not_captured",
            "included": False,
            "summary": "Prompt text is not captured or included.",
            "contentPolicy": "content_absent",
        },
        {
            "fieldId": "response_content",
            "valueKind": "message_body",
            "state": "not_generated",
            "included": False,
            "summary": "No assistant response exists in this fixture.",
            "contentPolicy": "content_absent",
        },
        {
            "fieldId": "transcript_content",
            "valueKind": "transcript_body",
            "state": "disabled",
            "included": False,
            "summary": "Transcript bodies are disabled for this boundary.",
            "contentPolicy": "content_absent",
        },
        {
            "fieldId": "actor_identifier",
            "valueKind": "user_or_account_identifier",
            "state": "redacted",
            "included": False,
            "summary": "User or account identifiers are not included.",
            "contentPolicy": "identity_absent",
        },
        {
            "fieldId": "runtime_trace",
            "valueKind": "runtime_log_reference",
            "state": "not_started",
            "included": False,
            "summary": "No runtime has started, so no runtime trace exists.",
            "contentPolicy": "log_absent",
        },
        {
            "fieldId": "artifact_path",
            "valueKind": "filesystem_path",
            "state": "not_configured",
            "included": False,
            "summary": "No artifact path is configured, read, or emitted.",
            "contentPolicy": "path_absent",
        },
        {
            "fieldId": "event_timestamp",
            "valueKind": "clock_value",
            "state": "not_generated",
            "included": False,
            "summary": "No wall-clock timestamp is emitted by this fixture.",
            "contentPolicy": "timestamp_absent",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "audit_logger_not_configured",
            "state": "not_configured",
            "summary": "No reviewed audit logger or local audit store exists.",
            "requiredBefore": "audit_event_persistence_enabled",
        },
        {
            "reasonId": "prompt_capture_disabled",
            "state": "disabled",
            "summary": "Prompt capture, echo, and persistence remain disabled.",
            "requiredBefore": "prompt_content_can_be_logged",
        },
        {
            "reasonId": "response_generation_absent",
            "state": "not_generated",
            "summary": "No response text is emitted by the launcher fixture.",
            "requiredBefore": "response_event_can_exist",
        },
        {
            "reasonId": "transcript_persistence_disabled",
            "state": "disabled",
            "summary": "Transcript persistence remains disabled.",
            "requiredBefore": "transcript_event_can_be_persisted",
        },
        {
            "reasonId": "runtime_not_started",
            "state": "not_started",
            "summary": "No local chat runtime has been implemented or started.",
            "requiredBefore": "runtime_execution_events_can_exist",
        },
        {
            "reasonId": "local_store_not_configured",
            "state": "not_configured",
            "summary": "No local audit history store or retention policy is configured.",
            "requiredBefore": "audit_history_enabled",
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
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Chat readiness keeps message send unavailable.",
        },
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Composer send controls remain disabled.",
        },
        {
            "refId": "chat_send_result",
            "schemaVersion": "pccx.chatSendResult.v0",
            "fixturePath": "contracts/fixtures/chat-send-result.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Send result contains no prompt or response content.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Transcript retention, export, and persistence remain disabled.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "auditEventDisplayOnly": True,
        "auditLoggerImplemented": False,
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
        "inputAccepted": False,
        "sendAttempted": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "transcriptContentIncluded": False,
        "transcriptPersistence": False,
        "transcriptExport": False,
        "messageBodiesIncluded": False,
        "summaryGenerated": False,
        "auditEventPersisted": False,
        "localStoreConfigured": False,
        "eventTimestampRecorded": False,
        "actorIdentifierIncluded": False,
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
        "rawLogsIncluded": False,
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
        "Data-only chat audit-event fixture; no prompt, response, message, transcript, summary, or actor content is read, generated, logged, stored, or persisted.",
        "No reviewed audit logger, local audit history store, retention period, redaction rule, or audit export path exists in this boundary.",
        "No model path, generated artifact, private path, secret, token, raw log, runtime trace, or hardware dump is read or written.",
        "No KV260 hardware access, serial access, SSH execution, network call, provider call, telemetry, upload, or write-back is performed.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_audit_event() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat audit-event fixture."""
    return copy.deepcopy(_CHAT_AUDIT_EVENT)


def chat_audit_event_json(event: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        event if event is not None else create_gemma3n_e4b_kv260_chat_audit_event(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat audit-event JSON.",
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
    sys.stdout.write(chat_audit_event_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
