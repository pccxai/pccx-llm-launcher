#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat send-result contract for the planned launcher UI.

The contract describes the conservative result shown when a future chat send
action remains blocked. It does not read, accept, echo, store, or persist
prompt content. It also does not generate responses, load models, start runtime
code, touch KV260 hardware, call providers, invoke pccx-lab, or read/write
artifacts.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatSendResult.v0"
RESULT_ENVELOPE_SCHEMA_VERSION = "pccx.chatSendResultEnvelope.v0"

CHAT_SEND_RESULT_FIELDS = (
    "schemaVersion",
    "sendResultId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "resultState",
    "sendAttemptState",
    "promptHandlingState",
    "responseState",
    "runtimeState",
    "modelState",
    "sessionState",
    "errorState",
    "userVisibleState",
    "chatComposerRef",
    "chatReadinessRef",
    "parentChatSessionRef",
    "resultEnvelope",
    "blockedReasons",
    "displayMessages",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

RESULT_ENVELOPE_FIELDS = (
    "schemaVersion",
    "envelopeId",
    "state",
    "sendAttempted",
    "inputAccepted",
    "promptContentIncluded",
    "promptEchoed",
    "responseGenerated",
    "responseContentIncluded",
    "exitCode",
    "contentPolicy",
    "sideEffectPolicy",
    "summary",
)

BLOCKED_REASON_FIELDS = (
    "reasonId",
    "state",
    "summary",
    "requiredBefore",
)

DISPLAY_MESSAGE_FIELDS = (
    "messageId",
    "state",
    "severity",
    "userMessage",
    "diagnosticHint",
    "contentPolicy",
)

HANDOFF_REF_FIELDS = (
    "refId",
    "schemaVersion",
    "fixturePath",
    "state",
    "summary",
)

CHAT_SEND_RESULT_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "external_not_configured",
    "inactive",
    "not_configured",
    "not_generated",
    "not_loaded",
    "not_started",
    "not_used",
    "placeholder",
    "planned",
    "requires_evidence",
    "target_selected",
    "unavailable",
)

_CHAT_SEND_RESULT = {
    "schemaVersion": SCHEMA_VERSION,
    "sendResultId": "chat_send_result_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-send-result.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_send_result_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "resultState": "blocked",
    "sendAttemptState": "disabled",
    "promptHandlingState": "empty_not_captured",
    "responseState": "not_generated",
    "runtimeState": "not_started",
    "modelState": "not_loaded",
    "sessionState": "inactive",
    "errorState": "blocked",
    "userVisibleState": "available_as_data",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "parentChatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "resultEnvelope": {
        "schemaVersion": RESULT_ENVELOPE_SCHEMA_VERSION,
        "envelopeId": "blocked_send_result_gemma3n_e4b_kv260_placeholder",
        "state": "blocked",
        "sendAttempted": False,
        "inputAccepted": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "responseGenerated": False,
        "responseContentIncluded": False,
        "exitCode": None,
        "contentPolicy": "fixture carries blocked result metadata only; no prompt or response body is stored",
        "sideEffectPolicy": "no_runtime_execution_no_write",
        "summary": "Send is disabled because readiness, runtime, model, and session evidence are missing.",
    },
    "blockedReasons": [
        {
            "reasonId": "composer_send_disabled",
            "state": "disabled",
            "summary": "The composer send control remains disabled.",
            "requiredBefore": "send_attempt_recorded",
        },
        {
            "reasonId": "readiness_blocked",
            "state": "blocked",
            "summary": "Chat readiness has not advanced beyond the blocked checklist state.",
            "requiredBefore": "send_message_enabled",
        },
        {
            "reasonId": "runtime_not_started",
            "state": "not_started",
            "summary": "No local chat runtime has been implemented or started.",
            "requiredBefore": "assistant_response_available",
        },
        {
            "reasonId": "model_not_loaded",
            "state": "not_loaded",
            "summary": "Model assets are not configured or loaded by this fixture.",
            "requiredBefore": "model_execution_enabled",
        },
        {
            "reasonId": "session_store_not_configured",
            "state": "not_configured",
            "summary": "No reviewed local session store or retention rule exists.",
            "requiredBefore": "result_or_transcript_persistence_enabled",
        },
    ],
    "displayMessages": [
        {
            "messageId": "send_disabled",
            "state": "disabled",
            "severity": "blocked",
            "userMessage": "Send is disabled until local chat readiness evidence exists.",
            "diagnosticHint": "Review the chat readiness and composer fixtures before enabling send.",
            "contentPolicy": "no_prompt_response_or_transcript_content",
        },
        {
            "messageId": "response_unavailable",
            "state": "not_generated",
            "severity": "info",
            "userMessage": "Assistant response output is unavailable in this fixture.",
            "diagnosticHint": "A future reviewed runtime boundary is required before responses can exist.",
            "contentPolicy": "no_generated_response_content",
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
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Composer send controls remain disabled.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Chat readiness keeps message send unavailable.",
        },
        {
            "refId": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "fixturePath": "contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Model status display is consumed as local data only.",
        },
        {
            "refId": "chat_session_lifecycle",
            "schemaVersion": "pccx.chatSessionLifecycle.v0",
            "fixturePath": "contracts/fixtures/chat-session-lifecycle.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Session lifecycle operations remain disabled or blocked.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "sendResultDisplayOnly": True,
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
        "transcriptPersistence": False,
        "sessionPersistence": False,
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
        "Data-only blocked chat send-result fixture; no prompt text is read, accepted, echoed, stored, or persisted.",
        "No assistant response, transcript, summary, model path, generated artifact, private path, secret, or token is read or written.",
        "No KV260 hardware access, serial access, SSH execution, network call, provider call, telemetry, upload, or write-back is performed.",
        "The send result remains blocked until chat readiness, runtime, model-load, device-session, and local session evidence are available.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_send_result() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat send-result fixture."""
    return copy.deepcopy(_CHAT_SEND_RESULT)


def chat_send_result_json(result: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        result if result is not None else create_gemma3n_e4b_kv260_chat_send_result(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat send-result JSON.",
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
    sys.stdout.write(chat_send_result_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
