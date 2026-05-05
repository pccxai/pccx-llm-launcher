#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat empty-state contract for the planned launcher UI.

The contract describes the static empty-state surface for the standalone
chat shell while keeping prompts, responses, transcripts, session stores,
model assets, runtime handoff, providers, target hardware, pccx-lab, IDE
integration, and artifact paths disabled or absent.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatEmptyState.v0"

CHAT_EMPTY_STATE_FIELDS = (
    "schemaVersion",
    "emptyStateId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "emptyStateState",
    "surfaceState",
    "sessionState",
    "modelState",
    "readinessState",
    "promptState",
    "transcriptState",
    "actionState",
    "runtimeState",
    "privacyState",
    "chatSurfaceLayoutRef",
    "chatSessionIndexRef",
    "chatReadinessRef",
    "chatComposerRef",
    "chatModelStatusRef",
    "chatActionBarRef",
    "emptyStatePolicy",
    "displaySlots",
    "affordanceHints",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

EMPTY_STATE_POLICY_FIELDS = (
    "state",
    "renderMode",
    "messagePolicy",
    "hintPolicy",
    "contentPolicy",
    "sideEffectPolicy",
    "externalDependencyPolicy",
)

DISPLAY_SLOT_FIELDS = (
    "slotId",
    "label",
    "state",
    "visible",
    "enabled",
    "sourceRef",
    "displayRole",
    "contentPolicy",
)

AFFORDANCE_HINT_FIELDS = (
    "hintId",
    "label",
    "state",
    "visible",
    "enabled",
    "sourceRef",
    "blockedReasonRef",
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

CHAT_EMPTY_STATE_VALUES = (
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
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_EMPTY_STATE = {
    "schemaVersion": SCHEMA_VERSION,
    "emptyStateId": "chat_empty_state_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-empty-state.gemma3n-e4b-kv260.2026-05-05",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_empty_state_boundary_2026-05-05",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "emptyStateState": "available_as_data",
    "surfaceState": "placeholder",
    "sessionState": "inactive",
    "modelState": "not_loaded",
    "readinessState": "blocked",
    "promptState": "empty_not_captured",
    "transcriptState": "empty_not_captured",
    "actionState": "disabled",
    "runtimeState": "not_started",
    "privacyState": "summary_only",
    "chatSurfaceLayoutRef": "chat_surface_layout_gemma3n_e4b_kv260_placeholder",
    "chatSessionIndexRef": "chat_session_index_gemma3n_e4b_kv260_placeholder",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatModelStatusRef": "chat_model_status_gemma3n_e4b_kv260_placeholder",
    "chatActionBarRef": "chat_action_bar_gemma3n_e4b_kv260_placeholder",
    "emptyStatePolicy": {
        "state": "available_as_data",
        "renderMode": "future_local_chat_empty_state",
        "messagePolicy": "static placeholder text only; no prompt, response, transcript, session title, summary, or generated content is read",
        "hintPolicy": "disabled affordance hints only; no command ids, command dispatch, or action execution is included",
        "contentPolicy": "empty-state metadata only; no message body, transcript text, prompt text, response text, file path, model path, runtime log, or private path is included",
        "sideEffectPolicy": "local_render_only",
        "externalDependencyPolicy": "no provider, network, hardware, pccx-lab, IDE, model asset, session store, or artifact dependency is used",
    },
    "displaySlots": [
        {
            "slotId": "target_banner",
            "label": "target banner",
            "state": "target_selected",
            "visible": True,
            "enabled": True,
            "sourceRef": "chat_model_status",
            "displayRole": "status",
            "contentPolicy": "target labels only; no model asset, model path, tokenizer, runtime, or hardware evidence is included",
        },
        {
            "slotId": "empty_transcript_notice",
            "label": "empty transcript notice",
            "state": "empty_not_captured",
            "visible": True,
            "enabled": True,
            "sourceRef": "chat_message_list",
            "displayRole": "primary",
            "contentPolicy": "no prompt, response, message body, transcript text, session title, or summary is included",
        },
        {
            "slotId": "readiness_notice",
            "label": "readiness notice",
            "state": "blocked",
            "visible": True,
            "enabled": True,
            "sourceRef": "chat_readiness",
            "displayRole": "readiness",
            "contentPolicy": "readiness labels only; no log, runtime output, hardware probe, or provider state is included",
        },
        {
            "slotId": "composer_disabled_notice",
            "label": "composer disabled notice",
            "state": "disabled",
            "visible": True,
            "enabled": True,
            "sourceRef": "chat_composer",
            "displayRole": "input",
            "contentPolicy": "input affordance metadata only; no prompt capture, echo, validation, or persistence is included",
        },
        {
            "slotId": "local_only_notice",
            "label": "local-only notice",
            "state": "summary_only",
            "visible": True,
            "enabled": True,
            "sourceRef": "chat_local_only_policy",
            "displayRole": "policy",
            "contentPolicy": "local-only policy labels only; no provider configuration, network state, or fallback path is included",
        },
    ],
    "affordanceHints": [
        {
            "hintId": "start_new_session_hint",
            "label": "start new session hint",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_session_lifecycle",
            "blockedReasonRef": "session_store_not_configured",
            "contentPolicy": "display label only; no session creation, title generation, store read, store write, or command dispatch",
        },
        {
            "hintId": "select_model_hint",
            "label": "select model hint",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_model_selection_policy",
            "blockedReasonRef": "model_asset_boundary_absent",
            "contentPolicy": "display label only; no catalog read, model path read, asset validation, or model selection persistence",
        },
        {
            "hintId": "review_readiness_hint",
            "label": "review readiness hint",
            "state": "available_as_data",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_readiness",
            "blockedReasonRef": "runtime_evidence_absent",
            "contentPolicy": "display label only; no runtime check, log read, hardware probe, or provider call",
        },
        {
            "hintId": "focus_composer_hint",
            "label": "focus composer hint",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_composer",
            "blockedReasonRef": "prompt_capture_blocked",
            "contentPolicy": "display label only; no focus change, prompt read, prompt capture, or key event capture",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "runtime_evidence_absent",
            "state": "blocked",
            "summary": "No reviewed local chat runtime evidence exists for enabling conversation output.",
            "requiredBefore": "assistant_response_display_enabled",
        },
        {
            "reasonId": "model_asset_boundary_absent",
            "state": "not_configured",
            "summary": "No reviewed model asset input, validation, or load boundary exists.",
            "requiredBefore": "model_picker_enabled",
        },
        {
            "reasonId": "session_store_not_configured",
            "state": "not_configured",
            "summary": "No reviewed session store, retention, or title boundary is enabled.",
            "requiredBefore": "session_creation_enabled",
        },
        {
            "reasonId": "prompt_capture_blocked",
            "state": "empty_not_captured",
            "summary": "Prompt capture remains disabled by the composer and send-result boundaries.",
            "requiredBefore": "composer_focus_or_send_enabled",
        },
        {
            "reasonId": "transcript_content_absent",
            "state": "empty_not_captured",
            "summary": "No prompt, response, message body, transcript, session title, or summary content exists in this fixture.",
            "requiredBefore": "message_list_rendered_from_store",
        },
        {
            "reasonId": "action_execution_disabled",
            "state": "disabled",
            "summary": "Empty-state hints are display-only and do not dispatch commands.",
            "requiredBefore": "empty_state_affordances_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_surface_layout",
            "schemaVersion": "pccx.chatSurfaceLayout.v0",
            "fixturePath": "contracts/fixtures/chat-surface-layout.gemma3n-e4b-kv260-placeholder.json",
            "state": "placeholder",
            "summary": "Surface layout defines the planned shell regions for the empty state.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Readiness metadata keeps model, runtime, and target checks blocked.",
        },
        {
            "refId": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "fixturePath": "contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Model status keeps descriptor, load, runtime, context, and response rows blocked.",
        },
        {
            "refId": "chat_session_index",
            "schemaVersion": "pccx.chatSessionIndex.v0",
            "fixturePath": "contracts/fixtures/chat-session-index.gemma3n-e4b-kv260-placeholder.json",
            "state": "empty_not_captured",
            "summary": "Session index remains empty and does not read titles, summaries, or stores.",
        },
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Composer metadata keeps prompt capture and send disabled.",
        },
        {
            "refId": "chat_message_list",
            "schemaVersion": "pccx.chatMessageList.v0",
            "fixturePath": "contracts/fixtures/chat-message-list.gemma3n-e4b-kv260-placeholder.json",
            "state": "empty_not_captured",
            "summary": "Message list remains empty without message bodies or transcript content.",
        },
        {
            "refId": "chat_action_bar",
            "schemaVersion": "pccx.chatActionBar.v0",
            "fixturePath": "contracts/fixtures/chat-action-bar.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Action-bar metadata keeps conversation controls disabled.",
        },
        {
            "refId": "chat_local_only_policy",
            "schemaVersion": "pccx.chatLocalOnlyPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-local-only-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "summary_only",
            "summary": "Local-only policy keeps provider, cloud, and fallback paths unavailable.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "emptyStateDisplayOnly": True,
        "emptyStateTextOnly": True,
        "localRenderOnly": True,
        "promptCapture": False,
        "promptRead": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "inputAccepted": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "transcriptContentIncluded": False,
        "messageContentIncluded": False,
        "sessionTitleIncluded": False,
        "summaryIncluded": False,
        "readsSessionStore": False,
        "writesSessionStore": False,
        "actionExecution": False,
        "commandDispatch": False,
        "focusChanged": False,
        "keyboardCapture": False,
        "clipboardRead": False,
        "clipboardWrite": False,
        "attachmentReads": False,
        "filePickerOpened": False,
        "modelAssetRead": False,
        "modelPathIncluded": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "runtimeStarted": False,
        "runtimeExecution": False,
        "runtimeOutputIncluded": False,
        "kv260Access": False,
        "hardwareAccess": False,
        "providerCalls": False,
        "cloudCalls": False,
        "networkCalls": False,
        "configRead": False,
        "environmentRead": False,
        "providerConfigRead": False,
        "readsArtifacts": False,
        "writesArtifacts": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "telemetry": False,
        "upload": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "mcpServerImplemented": False,
        "lspImplemented": False,
        "compatibilityClaim": False,
    },
    "limitations": [
        "Data-only chat empty-state fixture; all displayed values are checked metadata for the planned local chat shell.",
        "No prompt, response, transcript, message body, summary, session title, session store, configuration file, environment value, model path, tokenizer path, runtime log, private path, secret, or token is read.",
        "No prompt capture, input acceptance, response generation, model asset read, model load, runtime start, target access, provider call, command dispatch, focus change, clipboard access, attachment read, telemetry, upload, or artifact write is performed.",
        "No pccx-lab invocation, systemverilog-ide invocation, MCP server, LSP, compatibility promise, storage layer, runtime, model-loader, or hardware implementation is included.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_empty_state() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 empty-state fixture."""
    return copy.deepcopy(_CHAT_EMPTY_STATE)


def chat_empty_state_json(state: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        state if state is not None else create_gemma3n_e4b_kv260_chat_empty_state(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat empty-state JSON.",
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
    sys.stdout.write(chat_empty_state_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
