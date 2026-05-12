#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat response stream contract for the planned launcher UI.

The contract describes the disabled assistant response streaming/progress
display for the local chat surface. It does not read prompts, accept input,
generate response chunks, count produced tokens, start runtime code, load
models, touch KV260 hardware, call providers, invoke pccx-lab, read stores,
or persist anything.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatResponseStream.v0"
STREAM_ENVELOPE_SCHEMA_VERSION = "pccx.chatResponseStreamEnvelope.v0"

CHAT_RESPONSE_STREAM_FIELDS = (
    "schemaVersion",
    "streamId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "streamState",
    "responseState",
    "streamTransportState",
    "tokenState",
    "progressState",
    "cancelState",
    "runtimeState",
    "modelState",
    "sessionState",
    "chatSendResultRef",
    "chatReadinessRef",
    "chatModelStatusRef",
    "chatTranscriptPolicyRef",
    "streamEnvelope",
    "streamPhases",
    "displaySlots",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

STREAM_ENVELOPE_FIELDS = (
    "schemaVersion",
    "envelopeId",
    "state",
    "streamStarted",
    "transportOpened",
    "chunksEmitted",
    "tokenContentIncluded",
    "responseContentIncluded",
    "tokenCount",
    "stopSignalSent",
    "contentPolicy",
    "sideEffectPolicy",
    "summary",
)

STREAM_PHASE_FIELDS = (
    "phaseId",
    "label",
    "state",
    "visible",
    "enabled",
    "summary",
    "requiredBefore",
    "contentPolicy",
)

DISPLAY_SLOT_FIELDS = (
    "slotId",
    "label",
    "state",
    "visible",
    "enabled",
    "sourceRef",
    "displayPolicy",
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

CHAT_RESPONSE_STREAM_STATE_VALUES = (
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

_CHAT_RESPONSE_STREAM = {
    "schemaVersion": SCHEMA_VERSION,
    "streamId": "chat_response_stream_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-response-stream.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_response_stream_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "streamState": "blocked",
    "responseState": "not_generated",
    "streamTransportState": "not_started",
    "tokenState": "unavailable",
    "progressState": "disabled",
    "cancelState": "disabled",
    "runtimeState": "not_started",
    "modelState": "not_loaded",
    "sessionState": "inactive",
    "chatSendResultRef": "chat_send_result_gemma3n_e4b_kv260_placeholder",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "chatModelStatusRef": "chat_model_status_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "streamEnvelope": {
        "schemaVersion": STREAM_ENVELOPE_SCHEMA_VERSION,
        "envelopeId": "blocked_response_stream_gemma3n_e4b_kv260_placeholder",
        "state": "blocked",
        "streamStarted": False,
        "transportOpened": False,
        "chunksEmitted": False,
        "tokenContentIncluded": False,
        "responseContentIncluded": False,
        "tokenCount": None,
        "stopSignalSent": False,
        "contentPolicy": "fixture carries response stream metadata only; no prompt, token, or response body is stored",
        "sideEffectPolicy": "no_runtime_execution_no_stream_transport_no_write",
        "summary": "Assistant response streaming is blocked because send, runtime, model, and session evidence are missing.",
    },
    "streamPhases": [
        {
            "phaseId": "wait_for_send_result",
            "label": "wait for send result",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "summary": "No send attempt exists, so no response stream can start.",
            "requiredBefore": "stream_transport_opened",
            "contentPolicy": "no_prompt_or_response_content",
        },
        {
            "phaseId": "open_stream_transport",
            "label": "open stream transport",
            "state": "not_started",
            "visible": True,
            "enabled": False,
            "summary": "No local runtime transport is implemented or opened.",
            "requiredBefore": "response_chunks_emitted",
            "contentPolicy": "no_runtime_log_or_transport_payload_content",
        },
        {
            "phaseId": "emit_response_chunks",
            "label": "emit response chunks",
            "state": "not_generated",
            "visible": True,
            "enabled": False,
            "summary": "No assistant response chunks are produced in this fixture.",
            "requiredBefore": "assistant_message_available",
            "contentPolicy": "no_generated_response_content",
        },
        {
            "phaseId": "complete_stream",
            "label": "complete stream",
            "state": "unavailable",
            "visible": True,
            "enabled": False,
            "summary": "No stream completion event exists because no stream starts.",
            "requiredBefore": "transcript_append_enabled",
            "contentPolicy": "no_transcript_or_summary_content",
        },
    ],
    "displaySlots": [
        {
            "slotId": "assistant_response_placeholder",
            "label": "assistant response placeholder",
            "state": "available_as_data",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_send_result",
            "displayPolicy": "show unavailable response state only",
            "contentPolicy": "no_response_content",
        },
        {
            "slotId": "stream_progress_indicator",
            "label": "stream progress indicator",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_readiness",
            "displayPolicy": "show disabled progress state without runtime activity",
            "contentPolicy": "metadata_only",
        },
        {
            "slotId": "token_counter",
            "label": "token counter",
            "state": "unavailable",
            "visible": False,
            "enabled": False,
            "sourceRef": "chat_model_status",
            "displayPolicy": "hide until a reviewed runtime boundary exposes counts",
            "contentPolicy": "no_token_counts_or_token_text",
        },
        {
            "slotId": "stop_generation_control",
            "label": "stop generation control",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_response_stream",
            "displayPolicy": "show disabled stop control only",
            "contentPolicy": "no_runtime_signal_payload",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "send_result_blocked",
            "state": "blocked",
            "summary": "The checked send-result boundary reports no send attempt.",
            "requiredBefore": "response_stream_started",
        },
        {
            "reasonId": "runtime_not_started",
            "state": "not_started",
            "summary": "No local chat runtime has been implemented or started.",
            "requiredBefore": "stream_transport_opened",
        },
        {
            "reasonId": "model_not_loaded",
            "state": "not_loaded",
            "summary": "Model assets are not configured or loaded by this fixture.",
            "requiredBefore": "response_chunks_emitted",
        },
        {
            "reasonId": "session_inactive",
            "state": "inactive",
            "summary": "No launcher-owned chat session exists for streamed output.",
            "requiredBefore": "response_display_appended",
        },
        {
            "reasonId": "transcript_policy_disabled",
            "state": "disabled",
            "summary": "Transcript persistence and export remain disabled.",
            "requiredBefore": "stream_result_persisted",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_send_result",
            "schemaVersion": "pccx.chatSendResult.v0",
            "fixturePath": "contracts/fixtures/chat-send-result.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Blocked send-result data is consumed before stream display state.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Readiness data keeps response streaming disabled.",
        },
        {
            "refId": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "fixturePath": "contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Model status is consumed as descriptor metadata only.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Transcript persistence remains unavailable for streamed output.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "responseStreamDisplayOnly": True,
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
        "responseChunkContentIncluded": False,
        "responseChunksEmitted": False,
        "tokenContentIncluded": False,
        "tokenCountMeasured": False,
        "streamStarted": False,
        "streamTransportOpened": False,
        "streamCancellationAttempted": False,
        "transcriptPersistence": False,
        "sessionPersistence": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
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
        "Data-only blocked chat response-stream fixture; no prompt, token, response, transcript, summary, or runtime log content is read or written.",
        "No stream transport is opened, no response chunks are generated, no token counts are measured, and no stop signal is sent.",
        "No model assets, model paths, private paths, secrets, tokens, stores, logs, or artifacts are read.",
        "No KV260 hardware access, serial access, SSH execution, network call, provider call, telemetry, upload, or write-back is performed.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_response_stream() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat response stream fixture."""
    return copy.deepcopy(_CHAT_RESPONSE_STREAM)


def chat_response_stream_json(stream: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        stream if stream is not None else create_gemma3n_e4b_kv260_chat_response_stream(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat response stream JSON.",
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
    sys.stdout.write(chat_response_stream_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
