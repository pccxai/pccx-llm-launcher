#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat composer contract for the planned launcher UI.

The contract describes composer controls, input validation state, and send
gating for the standalone chat surface without reading, echoing, storing, or
persisting prompt content. It does not load models, start runtime code, touch
KV260 hardware, call providers, invoke pccx-lab, or read/write artifacts.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatComposer.v0"

CHAT_COMPOSER_FIELDS = (
    "schemaVersion",
    "composerId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "composerState",
    "inputBufferState",
    "sendControlState",
    "attachmentState",
    "privacyState",
    "validationState",
    "chatReadinessRef",
    "parentChatSessionRef",
    "inputPolicy",
    "composerControls",
    "validationRules",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

INPUT_POLICY_FIELDS = (
    "state",
    "promptCapture",
    "promptEcho",
    "promptPersistence",
    "contentIncluded",
    "maxDraftChars",
    "draftStorage",
    "redactionPolicy",
    "summary",
)

COMPOSER_CONTROL_FIELDS = (
    "controlId",
    "label",
    "state",
    "enabled",
    "userAction",
    "launcherAction",
    "sideEffectPolicy",
)

VALIDATION_RULE_FIELDS = (
    "ruleId",
    "state",
    "severity",
    "summary",
    "requiredBefore",
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

CHAT_COMPOSER_STATE_VALUES = (
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
    "target_selected",
    "unavailable",
)

_CHAT_COMPOSER = {
    "schemaVersion": SCHEMA_VERSION,
    "composerId": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-composer.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_composer_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "composerState": "blocked",
    "inputBufferState": "empty_not_captured",
    "sendControlState": "disabled",
    "attachmentState": "disabled",
    "privacyState": "available_as_data",
    "validationState": "blocked",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "parentChatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "inputPolicy": {
        "state": "planned",
        "promptCapture": "disabled",
        "promptEcho": "disabled",
        "promptPersistence": "disabled",
        "contentIncluded": False,
        "maxDraftChars": 0,
        "draftStorage": "not_configured",
        "redactionPolicy": "prompt text stays outside checked fixtures and status summaries",
        "summary": "Composer fixture carries input control state only; no draft text is stored.",
    },
    "composerControls": [
        {
            "controlId": "focus_input",
            "label": "focus input",
            "state": "placeholder",
            "enabled": False,
            "userAction": "Focus the composer only after a reviewed local chat UI exists.",
            "launcherAction": "Render placeholder input state without reading text.",
            "sideEffectPolicy": "local_render_only",
        },
        {
            "controlId": "attach_context",
            "label": "attach context",
            "state": "disabled",
            "enabled": False,
            "userAction": "Attach local context only after an explicit artifact input boundary exists.",
            "launcherAction": "Keep attachments disabled and do not read files.",
            "sideEffectPolicy": "no_artifact_read",
        },
        {
            "controlId": "send_message",
            "label": "send message",
            "state": "disabled",
            "enabled": False,
            "userAction": "Send only after runtime, model, session, and retention evidence exists.",
            "launcherAction": "Keep send disabled while readiness is blocked.",
            "sideEffectPolicy": "no_runtime_execution",
        },
        {
            "controlId": "clear_draft",
            "label": "clear draft",
            "state": "inactive",
            "enabled": False,
            "userAction": "Clear only future in-memory draft text owned by the launcher UI.",
            "launcherAction": "No-op because no draft is captured by this fixture.",
            "sideEffectPolicy": "no_write",
        },
    ],
    "validationRules": [
        {
            "ruleId": "no_prompt_content_in_fixture",
            "state": "available_as_data",
            "severity": "info",
            "summary": "Composer fixtures and status summaries must not include prompt text.",
            "requiredBefore": "composer_fixture_checked",
        },
        {
            "ruleId": "runtime_readiness_required",
            "state": "blocked",
            "severity": "blocked",
            "summary": "Runtime readiness remains blocked and not yet evidence-backed.",
            "requiredBefore": "send_message_enabled",
        },
        {
            "ruleId": "model_load_required",
            "state": "not_loaded",
            "severity": "blocked",
            "summary": "Model assets are not configured or loaded by this fixture.",
            "requiredBefore": "send_message_enabled",
        },
        {
            "ruleId": "session_store_required",
            "state": "not_configured",
            "severity": "blocked",
            "summary": "No reviewed local session store or retention rule exists.",
            "requiredBefore": "draft_or_transcript_persistence_enabled",
        },
        {
            "ruleId": "attachment_boundary_required",
            "state": "planned",
            "severity": "blocked",
            "summary": "Attachments require a separate reviewed local artifact input boundary.",
            "requiredBefore": "attach_context_enabled",
        },
        {
            "ruleId": "provider_mode_disabled",
            "state": "not_used",
            "severity": "info",
            "summary": "External provider state is not used by this local launcher boundary.",
            "requiredBefore": "core_chat_available",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "send_readiness_blocked",
            "state": "blocked",
            "summary": "Chat readiness keeps send controls disabled.",
            "requiredBefore": "send_message_enabled",
        },
        {
            "reasonId": "draft_capture_not_reviewed",
            "state": "not_configured",
            "summary": "No prompt capture, echo, persistence, or retention policy exists.",
            "requiredBefore": "input_capture_enabled",
        },
        {
            "reasonId": "attachment_boundary_absent",
            "state": "planned",
            "summary": "No reviewed local artifact input boundary exists for composer attachments.",
            "requiredBefore": "attach_context_enabled",
        },
        {
            "reasonId": "runtime_not_started",
            "state": "not_started",
            "summary": "No local chat runtime has been implemented or started.",
            "requiredBefore": "assistant_response_available",
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
            "summary": "Chat readiness keeps send controls disabled.",
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
            "summary": "Session lifecycle remains disabled or blocked.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "composerDisplayOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "attachmentReads": False,
        "fileUpload": False,
        "clipboardRead": False,
        "clipboardWrite": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "promptPersistence": False,
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
        "Data-only chat composer fixture; no prompt text is read, echoed, stored, or persisted.",
        "No attachments, manifests, transcripts, summaries, model paths, generated artifacts, private paths, secrets, or tokens are read or written.",
        "No KV260 hardware access, serial access, SSH execution, network call, provider call, telemetry, upload, or write-back is performed.",
        "Composer send controls remain disabled until chat readiness, runtime, model-load, device-session, and local session evidence are available.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_composer() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat composer fixture."""
    return copy.deepcopy(_CHAT_COMPOSER)


def chat_composer_json(composer: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        composer if composer is not None else create_gemma3n_e4b_kv260_chat_composer(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat composer JSON.",
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
    sys.stdout.write(chat_composer_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
