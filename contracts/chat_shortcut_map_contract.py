#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat shortcut-map contract for the planned launcher UI.

The contract describes disabled keyboard shortcuts for the standalone chat
surface. It does not install keyboard listeners, capture key events, dispatch
commands, focus controls, read prompts, read responses, read transcripts, read
session stores, copy clipboard data, attach files, start runtime code, load
models, touch KV260 hardware, call providers, invoke pccx-lab, or persist
anything.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatShortcutMap.v0"

CHAT_SHORTCUT_MAP_FIELDS = (
    "schemaVersion",
    "shortcutMapId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "shortcutMapState",
    "focusState",
    "keyboardCaptureState",
    "commandDispatchState",
    "actionExecutionState",
    "chatSessionRef",
    "chatComposerRef",
    "chatMessageListRef",
    "chatActionBarRef",
    "shortcutPolicy",
    "shortcutScopes",
    "shortcutBindings",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

SHORTCUT_POLICY_FIELDS = (
    "state",
    "renderMode",
    "sourcePolicy",
    "contentPolicy",
    "keyboardPolicy",
    "dispatchPolicy",
    "sideEffectPolicy",
    "persistencePolicy",
)

SHORTCUT_SCOPE_FIELDS = (
    "scopeId",
    "label",
    "state",
    "visible",
    "enabled",
    "summary",
)

SHORTCUT_BINDING_FIELDS = (
    "shortcutId",
    "label",
    "scopeId",
    "keyChord",
    "state",
    "visible",
    "enabled",
    "requiresExplicitUserAction",
    "sourceRef",
    "resultState",
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

CHAT_SHORTCUT_MAP_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "inactive",
    "not_configured",
    "not_generated",
    "not_installed",
    "not_invoked",
    "not_started",
    "planned",
    "read_only",
    "summary_only",
    "unavailable",
)

_CHAT_SHORTCUT_MAP = {
    "schemaVersion": SCHEMA_VERSION,
    "shortcutMapId": "chat_shortcut_map_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-shortcut-map.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_shortcut_map_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "shortcutMapState": "blocked",
    "focusState": "inactive",
    "keyboardCaptureState": "not_installed",
    "commandDispatchState": "blocked",
    "actionExecutionState": "not_invoked",
    "chatSessionRef": "chat_session_gemma3n_e4b_kv260_placeholder",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatMessageListRef": "chat_message_list_gemma3n_e4b_kv260_placeholder",
    "chatActionBarRef": "chat_action_bar_gemma3n_e4b_kv260_placeholder",
    "shortcutPolicy": {
        "state": "planned",
        "renderMode": "future_local_chat_shortcut_map",
        "sourcePolicy": "checked fixture only; no keyboard listener, session store, transcript, prompt, response, clipboard, file, or model path is read",
        "contentPolicy": "shortcut metadata only; no key-event stream, prompt text, response text, message body, transcript text, or session title is included",
        "keyboardPolicy": "all key chords are display metadata until a reviewed UI input boundary exists",
        "dispatchPolicy": "no command dispatch, focus change, send attempt, retry, stop signal, copy, attach, session creation, clear, or export action is performed",
        "sideEffectPolicy": "local_render_only",
        "persistencePolicy": "no shortcut settings, key events, prompts, responses, transcripts, clipboard data, attachments, or artifacts are read or written",
    },
    "shortcutScopes": [
        {
            "scopeId": "global_chat_shell",
            "label": "global chat shell",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "summary": "Global chat-shell shortcuts remain disabled until the standalone surface has a reviewed input boundary.",
        },
        {
            "scopeId": "composer_focus",
            "label": "composer focus",
            "state": "inactive",
            "visible": True,
            "enabled": False,
            "summary": "Composer focus shortcuts remain inactive because prompt capture is disabled.",
        },
        {
            "scopeId": "message_list",
            "label": "message list",
            "state": "empty_not_captured",
            "visible": True,
            "enabled": False,
            "summary": "Message navigation shortcuts remain disabled because no messages are present.",
        },
        {
            "scopeId": "action_bar",
            "label": "action bar",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "summary": "Action-bar shortcuts mirror disabled conversation controls.",
        },
    ],
    "shortcutBindings": [
        {
            "shortcutId": "focus_composer",
            "label": "focus composer",
            "scopeId": "composer_focus",
            "keyChord": "Ctrl+L",
            "state": "inactive",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_composer",
            "resultState": "not_invoked",
            "sideEffectPolicy": "no_focus_change",
            "blockedReasonRef": "keyboard_listener_not_installed",
        },
        {
            "shortcutId": "submit_message",
            "label": "submit message",
            "scopeId": "composer_focus",
            "keyChord": "Ctrl+Enter",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_send_result",
            "resultState": "not_invoked",
            "sideEffectPolicy": "no_send_attempt",
            "blockedReasonRef": "send_boundary_blocked",
        },
        {
            "shortcutId": "stop_response",
            "label": "stop response",
            "scopeId": "action_bar",
            "keyChord": "Esc",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_action_bar",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_stop_signal",
            "blockedReasonRef": "response_stream_not_started",
        },
        {
            "shortcutId": "copy_response",
            "label": "copy response",
            "scopeId": "message_list",
            "keyChord": "Ctrl+Shift+C",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_message_list",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_clipboard_write",
            "blockedReasonRef": "message_content_absent",
        },
        {
            "shortcutId": "new_chat",
            "label": "new chat",
            "scopeId": "global_chat_shell",
            "keyChord": "Ctrl+N",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_session_lifecycle",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_session_create",
            "blockedReasonRef": "session_lifecycle_not_enabled",
        },
        {
            "shortcutId": "clear_conversation",
            "label": "clear conversation",
            "scopeId": "action_bar",
            "keyChord": "Ctrl+Shift+Backspace",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_transcript_policy",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_transcript_delete",
            "blockedReasonRef": "transcript_store_not_configured",
        },
        {
            "shortcutId": "export_transcript",
            "label": "export transcript",
            "scopeId": "action_bar",
            "keyChord": "Ctrl+Shift+E",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_transcript_policy",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_transcript_export",
            "blockedReasonRef": "transcript_export_not_reviewed",
        },
        {
            "shortcutId": "attach_context",
            "label": "attach context",
            "scopeId": "action_bar",
            "keyChord": "Ctrl+Shift+A",
            "state": "planned",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_action_bar",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_file_or_artifact_read",
            "blockedReasonRef": "attachment_boundary_absent",
        },
        {
            "shortcutId": "next_message",
            "label": "next message",
            "scopeId": "message_list",
            "keyChord": "Alt+Down",
            "state": "empty_not_captured",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_message_list",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_message_selection",
            "blockedReasonRef": "message_list_empty",
        },
        {
            "shortcutId": "previous_message",
            "label": "previous message",
            "scopeId": "message_list",
            "keyChord": "Alt+Up",
            "state": "empty_not_captured",
            "visible": True,
            "enabled": False,
            "requiresExplicitUserAction": True,
            "sourceRef": "chat_message_list",
            "resultState": "unavailable",
            "sideEffectPolicy": "no_message_selection",
            "blockedReasonRef": "message_list_empty",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "keyboard_listener_not_installed",
            "state": "not_installed",
            "summary": "No keyboard listener or focus manager exists in this boundary.",
            "requiredBefore": "keyboard_shortcuts_enabled",
        },
        {
            "reasonId": "send_boundary_blocked",
            "state": "blocked",
            "summary": "The send-result boundary remains blocked and no prompt can be accepted.",
            "requiredBefore": "submit_message_enabled",
        },
        {
            "reasonId": "response_stream_not_started",
            "state": "not_started",
            "summary": "No local response stream exists, so stop controls have no target.",
            "requiredBefore": "stop_response_enabled",
        },
        {
            "reasonId": "message_content_absent",
            "state": "empty_not_captured",
            "summary": "The message-list boundary contains no message bodies or response content.",
            "requiredBefore": "message_shortcuts_enabled",
        },
        {
            "reasonId": "session_lifecycle_not_enabled",
            "state": "blocked",
            "summary": "Session create/restore/clear operations remain disabled.",
            "requiredBefore": "session_shortcuts_enabled",
        },
        {
            "reasonId": "transcript_store_not_configured",
            "state": "not_configured",
            "summary": "No reviewed local transcript store exists.",
            "requiredBefore": "clear_conversation_enabled",
        },
        {
            "reasonId": "transcript_export_not_reviewed",
            "state": "not_configured",
            "summary": "Transcript export requires a separate reviewed storage and redaction boundary.",
            "requiredBefore": "export_transcript_enabled",
        },
        {
            "reasonId": "attachment_boundary_absent",
            "state": "planned",
            "summary": "Attachment shortcuts require a separate reviewed file/artifact input boundary.",
            "requiredBefore": "attach_context_enabled",
        },
        {
            "reasonId": "message_list_empty",
            "state": "empty_not_captured",
            "summary": "Message navigation has no message rows to select.",
            "requiredBefore": "message_navigation_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_session",
            "schemaVersion": "pccx.chatSession.v0",
            "fixturePath": "contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Blocked standalone chat/session state.",
        },
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Disabled composer and prompt-capture boundary.",
        },
        {
            "refId": "chat_message_list",
            "schemaVersion": "pccx.chatMessageList.v0",
            "fixturePath": "contracts/fixtures/chat-message-list.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Empty message-list display boundary.",
        },
        {
            "refId": "chat_action_bar",
            "schemaVersion": "pccx.chatActionBar.v0",
            "fixturePath": "contracts/fixtures/chat-action-bar.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Disabled conversation action-bar boundary.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Transcript retention/export policy boundary.",
        },
    ],
    "safetyFlags": {
        "readOnly": True,
        "dataOnly": True,
        "deterministic": True,
        "shortcutMapDisplayOnly": True,
        "shortcutMetadataOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "keyboardListenerInstalled": False,
        "keyboardCaptureEnabled": False,
        "commandDispatchEnabled": False,
        "shortcutExecuted": False,
        "shortcutPersistence": False,
        "focusChanged": False,
        "readsSessionStore": False,
        "readsTranscript": False,
        "readsMessages": False,
        "readsPrompt": False,
        "writesPrompt": False,
        "promptCapture": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "promptPersistence": False,
        "inputAccepted": False,
        "sendAttempted": False,
        "retryAttempted": False,
        "stopSignalSent": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "messageBodiesIncluded": False,
        "transcriptExport": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
        "conversationCreated": False,
        "conversationCleared": False,
        "attachmentReads": False,
        "fileUpload": False,
        "clipboardRead": False,
        "clipboardWrite": False,
        "modelAssetRead": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "runtimeExecution": False,
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
        "runtimeLogsIncluded": False,
        "telemetry": False,
        "automaticUpload": False,
        "writeBack": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "mcpServerImplemented": False,
        "lspImplemented": False,
        "stableApiAbiClaim": False,
        "marketplaceClaim": False,
    },
    "limitations": [
        "Data-only chat shortcut-map fixture; no keyboard listener, focus manager, prompt, response, transcript, message body, session title, model path, runtime log, file, or clipboard content is read or written.",
        "Shortcut bindings remain disabled, blocked, inactive, unavailable, or planned until reviewed UI input and command-dispatch boundaries exist.",
        "No focus change, send attempt, retry, stop signal, session creation, conversation clear, transcript export, clipboard write, attachment read, or file upload is performed.",
        "No model load, runtime execution, provider call, network call, pccx-lab call, editor call, KV260 hardware access, telemetry, artifact read, or artifact write is performed.",
        "This is not a release, tag, compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, or runtime implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_shortcut_map() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat shortcut-map fixture."""
    return copy.deepcopy(_CHAT_SHORTCUT_MAP)


def chat_shortcut_map_json(shortcut_map: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        shortcut_map
        if shortcut_map is not None
        else create_gemma3n_e4b_kv260_chat_shortcut_map(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat shortcut-map JSON.",
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
    sys.stdout.write(chat_shortcut_map_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
