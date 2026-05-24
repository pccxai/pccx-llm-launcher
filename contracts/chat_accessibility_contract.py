#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat accessibility contract for the planned launcher UI.

The contract describes accessibility metadata for the future standalone chat
surface while keeping UI execution, focus changes, keyboard capture, prompt
content, transcripts, session stores, model assets, runtime paths, providers,
target hardware, pccx-lab, IDE integration, and artifact paths disabled or
absent.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatAccessibility.v0"

CHAT_ACCESSIBILITY_FIELDS = (
    "schemaVersion",
    "accessibilityId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "accessibilityState",
    "surfaceState",
    "semanticState",
    "announcementState",
    "focusOrderState",
    "contrastState",
    "motionState",
    "inputState",
    "runtimeState",
    "privacyState",
    "chatSurfaceLayoutRef",
    "chatMessageListRef",
    "chatComposerRef",
    "chatActionBarRef",
    "chatReadinessRef",
    "accessibilityPolicy",
    "landmarkRegions",
    "ariaBindings",
    "focusOrderItems",
    "reviewGates",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

ACCESSIBILITY_POLICY_FIELDS = (
    "state",
    "renderMode",
    "semanticPolicy",
    "announcementPolicy",
    "focusPolicy",
    "contentPolicy",
    "sideEffectPolicy",
    "externalDependencyPolicy",
)

LANDMARK_REGION_FIELDS = (
    "regionId",
    "label",
    "state",
    "visible",
    "enabled",
    "sourceRef",
    "role",
    "descriptionPolicy",
    "contentPolicy",
)

ARIA_BINDING_FIELDS = (
    "bindingId",
    "label",
    "state",
    "visible",
    "enabled",
    "sourceRef",
    "ariaRole",
    "ariaLabelPolicy",
    "liveRegionPolicy",
    "contentPolicy",
)

FOCUS_ORDER_ITEM_FIELDS = (
    "orderId",
    "label",
    "state",
    "visible",
    "enabled",
    "sourceRef",
    "tabStop",
    "orderIndex",
    "sideEffectPolicy",
    "blockedReasonRef",
)

REVIEW_GATE_FIELDS = (
    "gateId",
    "label",
    "state",
    "enabled",
    "requiredBefore",
    "summary",
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

CHAT_ACCESSIBILITY_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "inactive",
    "not_configured",
    "not_installed",
    "not_started",
    "placeholder",
    "planned",
    "requires_review",
    "summary_only",
    "unavailable",
)

_CHAT_ACCESSIBILITY = {
    "schemaVersion": SCHEMA_VERSION,
    "accessibilityId": "chat_accessibility_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-accessibility.gemma3n-e4b-kv260.2026-05-05",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_accessibility_boundary_2026-05-05",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "accessibilityState": "available_as_data",
    "surfaceState": "placeholder",
    "semanticState": "planned",
    "announcementState": "disabled",
    "focusOrderState": "inactive",
    "contrastState": "requires_review",
    "motionState": "requires_review",
    "inputState": "disabled",
    "runtimeState": "not_started",
    "privacyState": "summary_only",
    "chatSurfaceLayoutRef": "chat_surface_layout_gemma3n_e4b_kv260_placeholder",
    "chatMessageListRef": "chat_message_list_gemma3n_e4b_kv260_placeholder",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatActionBarRef": "chat_action_bar_gemma3n_e4b_kv260_placeholder",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "accessibilityPolicy": {
        "state": "planned",
        "renderMode": "future_local_chat_accessibility_metadata",
        "semanticPolicy": "checked landmark and label metadata only; no app shell implementation is started",
        "announcementPolicy": "live-region metadata remains disabled until content and runtime boundaries are reviewed",
        "focusPolicy": "focus-order metadata only; no focus changes, keyboard listeners, or event capture are installed",
        "contentPolicy": "no prompt, response, transcript, message body, session title, summary, path, runtime log, private path, or artifact content is included",
        "sideEffectPolicy": "local_render_only",
        "externalDependencyPolicy": "no provider, network, hardware, pccx-lab, IDE, model asset, session store, or artifact dependency is used",
    },
    "landmarkRegions": [
        {
            "regionId": "chat_shell",
            "label": "chat shell",
            "state": "placeholder",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_surface_layout",
            "role": "application_region",
            "descriptionPolicy": "static shell label metadata only",
            "contentPolicy": "no_prompt_response_transcript_or_session_title_content",
        },
        {
            "regionId": "model_status_header",
            "label": "model status header",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_model_status",
            "role": "status_region",
            "descriptionPolicy": "target descriptor label metadata only",
            "contentPolicy": "no_model_path_runtime_log_or_hardware_state_content",
        },
        {
            "regionId": "readiness_banner",
            "label": "readiness banner",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_readiness",
            "role": "status_region",
            "descriptionPolicy": "blocked readiness label metadata only",
            "contentPolicy": "no_runtime_check_log_provider_or_device_probe_content",
        },
        {
            "regionId": "conversation_region",
            "label": "conversation region",
            "state": "empty_not_captured",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_message_list",
            "role": "main_region",
            "descriptionPolicy": "empty conversation label metadata only",
            "contentPolicy": "no_message_body_prompt_response_or_transcript_content",
        },
        {
            "regionId": "composer_region",
            "label": "composer region",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_composer",
            "role": "input_region",
            "descriptionPolicy": "disabled composer label metadata only",
            "contentPolicy": "no_prompt_capture_echo_validation_or_persistence",
        },
        {
            "regionId": "action_bar_region",
            "label": "action bar region",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_action_bar",
            "role": "toolbar_region",
            "descriptionPolicy": "disabled control group label metadata only",
            "contentPolicy": "no_command_ids_transcript_export_clipboard_or_file_content",
        },
    ],
    "ariaBindings": [
        {
            "bindingId": "surface_landmark_label",
            "label": "surface landmark label",
            "state": "available_as_data",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_surface_layout",
            "ariaRole": "region",
            "ariaLabelPolicy": "static label metadata only",
            "liveRegionPolicy": "not_configured",
            "contentPolicy": "no_prompt_response_transcript_or_session_title_content",
        },
        {
            "bindingId": "model_status_label",
            "label": "model status label",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_model_status",
            "ariaRole": "status",
            "ariaLabelPolicy": "target label metadata only",
            "liveRegionPolicy": "disabled",
            "contentPolicy": "descriptor_metadata_only_no_model_paths",
        },
        {
            "bindingId": "readiness_status_label",
            "label": "readiness status label",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_readiness",
            "ariaRole": "status",
            "ariaLabelPolicy": "blocked readiness metadata only",
            "liveRegionPolicy": "disabled",
            "contentPolicy": "readiness_metadata_only_no_logs_or_device_state",
        },
        {
            "bindingId": "transcript_region_label",
            "label": "transcript region label",
            "state": "empty_not_captured",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_message_list",
            "ariaRole": "log",
            "ariaLabelPolicy": "empty conversation metadata only",
            "liveRegionPolicy": "disabled",
            "contentPolicy": "no_message_body_prompt_response_or_transcript_content",
        },
        {
            "bindingId": "composer_disabled_label",
            "label": "composer disabled label",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_composer",
            "ariaRole": "textbox",
            "ariaLabelPolicy": "disabled input metadata only",
            "liveRegionPolicy": "not_configured",
            "contentPolicy": "no_prompt_capture_echo_or_persistence",
        },
        {
            "bindingId": "actions_disabled_label",
            "label": "actions disabled label",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_action_bar",
            "ariaRole": "toolbar",
            "ariaLabelPolicy": "disabled action metadata only",
            "liveRegionPolicy": "not_configured",
            "contentPolicy": "no_action_execution_clipboard_export_or_attachment_content",
        },
    ],
    "focusOrderItems": [
        {
            "orderId": "status_header_order",
            "label": "status header order",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_model_status",
            "tabStop": False,
            "orderIndex": 1,
            "sideEffectPolicy": "no_focus_change",
            "blockedReasonRef": "focus_manager_not_installed",
        },
        {
            "orderId": "readiness_banner_order",
            "label": "readiness banner order",
            "state": "blocked",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_readiness",
            "tabStop": False,
            "orderIndex": 2,
            "sideEffectPolicy": "no_focus_change",
            "blockedReasonRef": "live_regions_disabled",
        },
        {
            "orderId": "conversation_region_order",
            "label": "conversation region order",
            "state": "empty_not_captured",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_message_list",
            "tabStop": False,
            "orderIndex": 3,
            "sideEffectPolicy": "no_focus_change",
            "blockedReasonRef": "content_boundaries_blocked",
        },
        {
            "orderId": "composer_region_order",
            "label": "composer region order",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_composer",
            "tabStop": False,
            "orderIndex": 4,
            "sideEffectPolicy": "no_focus_change",
            "blockedReasonRef": "content_boundaries_blocked",
        },
        {
            "orderId": "action_bar_order",
            "label": "action bar order",
            "state": "disabled",
            "visible": True,
            "enabled": False,
            "sourceRef": "chat_action_bar",
            "tabStop": False,
            "orderIndex": 5,
            "sideEffectPolicy": "no_focus_change",
            "blockedReasonRef": "content_boundaries_blocked",
        },
    ],
    "reviewGates": [
        {
            "gateId": "semantic_labels_reviewed",
            "label": "semantic labels reviewed",
            "state": "requires_review",
            "enabled": False,
            "requiredBefore": "accessibility_labels_enabled",
            "summary": "Landmark and label metadata needs UI review before it can be treated as implemented.",
        },
        {
            "gateId": "contrast_tokens_reviewed",
            "label": "contrast tokens reviewed",
            "state": "requires_review",
            "enabled": False,
            "requiredBefore": "visual_theme_enabled",
            "summary": "Contrast expectations are recorded as a review gate only; no theme tokens are read.",
        },
        {
            "gateId": "reduced_motion_reviewed",
            "label": "reduced motion reviewed",
            "state": "requires_review",
            "enabled": False,
            "requiredBefore": "animation_or_streaming_ui_enabled",
            "summary": "Motion preferences remain review metadata and no system preference is read.",
        },
        {
            "gateId": "live_region_behavior_reviewed",
            "label": "live region behavior reviewed",
            "state": "disabled",
            "enabled": False,
            "requiredBefore": "runtime_status_announcements_enabled",
            "summary": "Live status announcements remain disabled until runtime status content exists.",
        },
        {
            "gateId": "keyboard_path_reviewed",
            "label": "keyboard path reviewed",
            "state": "blocked",
            "enabled": False,
            "requiredBefore": "keyboard_navigation_enabled",
            "summary": "Keyboard path review is blocked because no focus manager or input boundary is installed.",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "focus_manager_not_installed",
            "state": "not_installed",
            "summary": "No focus manager, keyboard listener, or input event boundary exists in this contract.",
            "requiredBefore": "keyboard_navigation_enabled",
        },
        {
            "reasonId": "live_regions_disabled",
            "state": "disabled",
            "summary": "Live-region updates remain disabled because no runtime status or message content is emitted.",
            "requiredBefore": "runtime_status_announcements_enabled",
        },
        {
            "reasonId": "contrast_review_missing",
            "state": "requires_review",
            "summary": "Visual contrast expectations require UI review and are not measured by this fixture.",
            "requiredBefore": "visual_theme_enabled",
        },
        {
            "reasonId": "reduced_motion_review_missing",
            "state": "requires_review",
            "summary": "Reduced-motion behavior requires UI review and no system preference is read.",
            "requiredBefore": "animation_or_streaming_ui_enabled",
        },
        {
            "reasonId": "content_boundaries_blocked",
            "state": "blocked",
            "summary": "Prompt, response, transcript, message, session-store, runtime, and action boundaries remain blocked.",
            "requiredBefore": "chat_content_accessibility_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_surface_layout",
            "schemaVersion": "pccx.chatSurfaceLayout.v0",
            "fixturePath": "contracts/fixtures/chat-surface-layout.gemma3n-e4b-kv260-placeholder.json",
            "state": "placeholder",
            "summary": "Surface layout defines the planned regions that need accessibility review.",
        },
        {
            "refId": "chat_message_list",
            "schemaVersion": "pccx.chatMessageList.v0",
            "fixturePath": "contracts/fixtures/chat-message-list.gemma3n-e4b-kv260-placeholder.json",
            "state": "empty_not_captured",
            "summary": "Message list remains empty and provides no prompt or response content.",
        },
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Composer metadata keeps prompt capture and focus actions disabled.",
        },
        {
            "refId": "chat_action_bar",
            "schemaVersion": "pccx.chatActionBar.v0",
            "fixturePath": "contracts/fixtures/chat-action-bar.gemma3n-e4b-kv260-placeholder.json",
            "state": "disabled",
            "summary": "Action-bar metadata keeps command execution, clipboard, export, and attachment controls disabled.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Readiness metadata remains blocked and does not emit runtime announcements.",
        },
        {
            "refId": "chat_shortcut_map",
            "schemaVersion": "pccx.chatShortcutMap.v0",
            "fixturePath": "contracts/fixtures/chat-shortcut-map.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Shortcut metadata remains display-only with no listener, dispatch, or focus change.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "accessibilityMetadataOnly": True,
        "semanticLabelsOnly": True,
        "localRenderOnly": True,
        "promptCapture": False,
        "promptRead": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptContentIncluded": False,
        "messageContentIncluded": False,
        "sessionTitleIncluded": False,
        "summaryIncluded": False,
        "readsSessionStore": False,
        "writesSessionStore": False,
        "keyboardListenerInstalled": False,
        "keyboardCapture": False,
        "commandDispatch": False,
        "focusChanged": False,
        "liveRegionUpdated": False,
        "screenReaderEventEmitted": False,
        "contrastMeasured": False,
        "motionPreferenceRead": False,
        "themeRead": False,
        "configRead": False,
        "environmentRead": False,
        "modelAssetRead": False,
        "modelLoadAttempted": False,
        "modelExecution": False,
        "runtimeStarted": False,
        "runtimeExecution": False,
        "kv260Access": False,
        "hardwareAccess": False,
        "providerCalls": False,
        "cloudCalls": False,
        "networkCalls": False,
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
        "Data-only chat accessibility fixture; all displayed values are checked metadata for the planned local chat shell.",
        "No prompt, response, transcript, message body, summary, session title, session store, configuration file, environment value, model path, tokenizer path, runtime log, private path, secret, or token is read.",
        "No UI shell, focus manager, keyboard listener, input event capture, live-region update, contrast measurement, motion preference read, prompt capture, response generation, model load, runtime start, target access, provider call, telemetry, upload, or artifact write is performed.",
        "No pccx-lab invocation, systemverilog-ide invocation, MCP server, LSP, compatibility promise, storage layer, runtime, model-loader, or hardware implementation is included.",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_accessibility() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 accessibility fixture."""
    return copy.deepcopy(_CHAT_ACCESSIBILITY)


def chat_accessibility_json(state: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        state if state is not None else create_gemma3n_e4b_kv260_chat_accessibility(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat accessibility JSON.",
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
    sys.stdout.write(chat_accessibility_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
