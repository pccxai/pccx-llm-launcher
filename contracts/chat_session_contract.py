#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only standalone chat/session contract for the planned launcher UI.

The contract describes local chat session state, disabled send controls,
message envelope shape, model status, and readiness references without
persisting prompts, contacting providers, loading model assets, touching KV260
hardware, invoking pccx-lab, or starting runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatSession.v0"
MESSAGE_SCHEMA_VERSION = "pccx.chatMessage.v0"

CHAT_SESSION_FIELDS = (
    "schemaVersion",
    "sessionId",
    "fixtureVersion",
    "lastUpdatedSource",
    "surfaceState",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "modelStatus",
    "runtimeReadinessRef",
    "deviceSessionStatusRef",
    "chatState",
    "inputState",
    "sendState",
    "transcriptPolicy",
    "sessionControls",
    "messageEnvelope",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

CONTROL_FIELDS = (
    "controlId",
    "label",
    "state",
    "enabled",
    "userAction",
    "launcherAction",
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

CHAT_SESSION_STATE_VALUES = (
    "target",
    "planned",
    "placeholder",
    "blocked",
    "inactive",
    "disabled",
    "ready_for_inputs",
    "not_configured",
    "not_loaded",
    "not_started",
    "unavailable",
    "available_as_data",
)

_CHAT_SESSION_STATUS = {
    "schemaVersion": SCHEMA_VERSION,
    "sessionId": "chat_session_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-session.gemma3n-e4b-kv260.2026-05-03",
    "lastUpdatedSource": "pccx_launcher_issue_9_boundary_2026-05-03",
    "surfaceState": "blocked",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "modelStatus": "not_loaded",
    "runtimeReadinessRef": "runtime_readiness_gemma3n_e4b_kv260",
    "deviceSessionStatusRef": "device_session_status_gemma3n_e4b_kv260_placeholder",
    "chatState": "inactive",
    "inputState": "ready_for_inputs",
    "sendState": "disabled",
    "transcriptPolicy": {
        "state": "not_started",
        "persistence": "not_configured",
        "promptCapture": "disabled",
        "responseCapture": "disabled",
        "summary": "This fixture stores no user prompts, responses, transcripts, or generated content.",
    },
    "sessionControls": [
        {
            "controlId": "new_session",
            "label": "new session",
            "state": "placeholder",
            "enabled": False,
            "userAction": "Open the chat surface when the launcher UI exists.",
            "launcherAction": "Render deterministic placeholder session state.",
            "sideEffectPolicy": "local_render_only",
        },
        {
            "controlId": "model_status",
            "label": "model status",
            "state": "not_loaded",
            "enabled": False,
            "userAction": "Review model readiness before chat controls are enabled.",
            "launcherAction": "Show the target descriptor and blocked model-load state.",
            "sideEffectPolicy": "data_only",
        },
        {
            "controlId": "send_message",
            "label": "send message",
            "state": "disabled",
            "enabled": False,
            "userAction": "Draft input only after a reviewed local session boundary exists.",
            "launcherAction": "Keep send disabled while runtime readiness is blocked.",
            "sideEffectPolicy": "no_runtime_execution",
        },
        {
            "controlId": "clear_session",
            "label": "clear session",
            "state": "inactive",
            "enabled": False,
            "userAction": "Clear only a future local transcript owned by the launcher.",
            "launcherAction": "No-op because no transcript exists in this fixture.",
            "sideEffectPolicy": "no_write",
        },
        {
            "controlId": "export_summary",
            "label": "export summary",
            "state": "blocked",
            "enabled": False,
            "userAction": "Export only bounded summaries after an explicit export boundary exists.",
            "launcherAction": "Refuse export because no chat session exists.",
            "sideEffectPolicy": "no_artifact_write",
        },
    ],
    "messageEnvelope": {
        "schemaVersion": MESSAGE_SCHEMA_VERSION,
        "state": "available_as_data",
        "roleVocabulary": [
            "system_notice",
            "user",
            "assistant",
        ],
        "messageIdPolicy": "local_session_scoped_future_id",
        "contentPolicy": "fixture carries field shape only; no prompt or response content is stored",
        "orderingPolicy": "future session-local monotonic order",
        "redactionPolicy": "prompt and response bodies stay outside checked fixtures",
        "responseState": "unavailable",
    },
    "blockedReasons": [
        {
            "reasonId": "runtime_readiness_blocked",
            "state": "blocked",
            "summary": "Runtime readiness remains blocked for the Gemma 3N E4B plus KV260 target.",
            "requiredBefore": "send_message_enabled",
        },
        {
            "reasonId": "model_assets_not_configured",
            "state": "not_configured",
            "summary": "Model assets are external and are not configured by this fixture.",
            "requiredBefore": "model_load_enabled",
        },
        {
            "reasonId": "chat_runtime_not_implemented",
            "state": "planned",
            "summary": "The local chat runtime boundary has not been implemented in this repository.",
            "requiredBefore": "session_start_enabled",
        },
        {
            "reasonId": "kv260_session_absent",
            "state": "inactive",
            "summary": "No target device session exists and no log stream has started.",
            "requiredBefore": "assistant_response_available",
        },
    ],
    "handoffRefs": [
        {
            "refId": "runtime_readiness",
            "schemaVersion": "pccx.runtimeReadiness.v0",
            "fixturePath": "contracts/fixtures/runtime-readiness.gemma3n-e4b-kv260.json",
            "state": "blocked",
            "summary": "Runtime readiness is consumed as local data only.",
        },
        {
            "refId": "device_session_status",
            "schemaVersion": "pccx.deviceSessionStatus.v0",
            "fixturePath": "contracts/fixtures/device-session-status.gemma3n-e4b-kv260.json",
            "state": "available_as_data",
            "summary": "Device/session status is consumed as local data only.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "writesArtifacts": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptPersistence": False,
        "touchesHardware": False,
        "kv260Access": False,
        "opensSerialPort": False,
        "networkCalls": False,
        "networkScan": False,
        "runtimeExecution": False,
        "modelLoaded": False,
        "modelExecution": False,
        "modelWeightPathsIncluded": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
        "generatedBlobsIncluded": False,
        "hardwareDumpsIncluded": False,
        "providerCalls": False,
        "cloudCalls": False,
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
        "Data-only standalone chat/session fixture; no model response is generated.",
        "No prompts, responses, transcripts, model paths, generated artifacts, private paths, secrets, or tokens are stored.",
        "No KV260 hardware access, serial access, network call, provider call, telemetry, upload, or write-back is performed.",
        "Send controls remain disabled until runtime readiness and model/session evidence are available.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_session() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat/session fixture."""
    return copy.deepcopy(_CHAT_SESSION_STATUS)


def chat_session_json(status: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        status if status is not None else create_gemma3n_e4b_kv260_chat_session(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat/session status JSON.",
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
    sys.stdout.write(chat_session_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
