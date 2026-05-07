#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only preferences contract for the planned standalone chat UI.

The contract describes settings panels and disabled preference controls for
the local chat surface. It does not read or write configuration files, provider
settings, environment variables, secrets, tokens, model assets, session stores,
prompts, responses, transcripts, logs, or artifacts; it does not start runtime
code, load models, touch KV260 hardware, call providers, invoke pccx-lab, or
persist preferences.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pccx_launcher.errors import TraceError


SCHEMA_VERSION = "pccx.chatPreferences.v0"

CHAT_PREFERENCES_FIELDS = (
    "schemaVersion",
    "preferencesId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "preferencesState",
    "storageState",
    "privacyState",
    "localOnlyPolicyRef",
    "sessionIndexRef",
    "modelStatusRef",
    "readinessRef",
    "preferencePanels",
    "preferenceControls",
    "blockedReasons",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

PREFERENCE_PANEL_FIELDS = (
    "panelId",
    "label",
    "state",
    "visible",
    "enabled",
    "sourcePolicy",
    "contentPolicy",
)

PREFERENCE_CONTROL_FIELDS = (
    "controlId",
    "panelId",
    "label",
    "state",
    "valueKind",
    "defaultValue",
    "currentValue",
    "userAction",
    "launcherAction",
    "sideEffectPolicy",
    "contentPolicy",
)

BLOCKED_REASON_FIELDS = (
    "reasonId",
    "state",
    "summary",
    "requiredBefore",
)

CHAT_PREFERENCES_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "display_only",
    "local_data_only",
    "not_configured",
    "not_loaded",
    "not_read",
    "not_started",
    "not_used",
    "placeholder",
    "planned",
    "read_only",
    "requires_review",
    "summary_only",
    "unavailable",
)

_CHAT_PREFERENCES = {
    "schemaVersion": SCHEMA_VERSION,
    "preferencesId": "chat_preferences_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-preferences.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_preferences_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "preferencesState": "available_as_data",
    "storageState": "not_configured",
    "privacyState": "summary_only",
    "localOnlyPolicyRef": "chat_local_only_policy_gemma3n_e4b_kv260_placeholder",
    "sessionIndexRef": "chat_session_index_gemma3n_e4b_kv260_placeholder",
    "modelStatusRef": "chat_model_status_gemma3n_e4b_kv260_placeholder",
    "readinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "preferencePanels": [
        {
            "panelId": "model_target_preferences",
            "label": "model and target preferences",
            "state": "display_only",
            "visible": True,
            "enabled": False,
            "sourcePolicy": "checked_fixture_values_only",
            "contentPolicy": "no_model_asset_path_or_private_path_content",
        },
        {
            "panelId": "privacy_preferences",
            "label": "privacy preferences",
            "state": "summary_only",
            "visible": True,
            "enabled": False,
            "sourcePolicy": "local_metadata_only",
            "contentPolicy": "no_prompt_response_transcript_or_identifier_content",
        },
        {
            "panelId": "local_only_preferences",
            "label": "local-only preferences",
            "state": "available_as_data",
            "visible": True,
            "enabled": False,
            "sourcePolicy": "chat_local_only_policy_reference",
            "contentPolicy": "no_provider_configuration_or_network_content",
        },
        {
            "panelId": "transcript_preferences",
            "label": "transcript preferences",
            "state": "planned",
            "visible": True,
            "enabled": False,
            "sourcePolicy": "policy_metadata_only",
            "contentPolicy": "no_transcript_message_or_summary_content",
        },
        {
            "panelId": "session_preferences",
            "label": "session preferences",
            "state": "not_configured",
            "visible": True,
            "enabled": False,
            "sourcePolicy": "session_index_reference",
            "contentPolicy": "no_session_store_title_manifest_or_path_content",
        },
    ],
    "preferenceControls": [
        {
            "controlId": "target_model_display",
            "panelId": "model_target_preferences",
            "label": "target model display",
            "state": "display_only",
            "valueKind": "enum",
            "defaultValue": "gemma3n-e4b",
            "currentValue": "gemma3n-e4b",
            "userAction": "none",
            "launcherAction": "render_metadata_only",
            "sideEffectPolicy": "no_model_asset_read",
            "contentPolicy": "target_model_name_only",
        },
        {
            "controlId": "target_device_display",
            "panelId": "model_target_preferences",
            "label": "target device display",
            "state": "display_only",
            "valueKind": "enum",
            "defaultValue": "kv260",
            "currentValue": "kv260",
            "userAction": "none",
            "launcherAction": "render_metadata_only",
            "sideEffectPolicy": "no_hardware_probe",
            "contentPolicy": "target_device_name_only",
        },
        {
            "controlId": "model_asset_picker",
            "panelId": "model_target_preferences",
            "label": "model asset picker",
            "state": "disabled",
            "valueKind": "path",
            "defaultValue": "unavailable",
            "currentValue": "unavailable",
            "userAction": "unavailable",
            "launcherAction": "blocked",
            "sideEffectPolicy": "no_file_picker_no_model_path_read",
            "contentPolicy": "no_model_path_or_weight_content",
        },
        {
            "controlId": "local_only_mode",
            "panelId": "local_only_preferences",
            "label": "local-only mode",
            "state": "available_as_data",
            "valueKind": "boolean",
            "defaultValue": True,
            "currentValue": True,
            "userAction": "none",
            "launcherAction": "render_metadata_only",
            "sideEffectPolicy": "no_provider_or_network_call",
            "contentPolicy": "policy_summary_only",
        },
        {
            "controlId": "cloud_fallback",
            "panelId": "local_only_preferences",
            "label": "cloud fallback",
            "state": "disabled",
            "valueKind": "boolean",
            "defaultValue": False,
            "currentValue": False,
            "userAction": "unavailable",
            "launcherAction": "blocked",
            "sideEffectPolicy": "no_provider_or_network_call",
            "contentPolicy": "no_provider_configuration_or_prompt_content",
        },
        {
            "controlId": "transcript_retention",
            "panelId": "transcript_preferences",
            "label": "transcript retention",
            "state": "disabled",
            "valueKind": "enum",
            "defaultValue": "not_configured",
            "currentValue": "not_configured",
            "userAction": "unavailable",
            "launcherAction": "blocked",
            "sideEffectPolicy": "no_transcript_store_read_or_write",
            "contentPolicy": "no_transcript_message_or_summary_content",
        },
        {
            "controlId": "transcript_export",
            "panelId": "transcript_preferences",
            "label": "transcript export",
            "state": "disabled",
            "valueKind": "boolean",
            "defaultValue": False,
            "currentValue": False,
            "userAction": "unavailable",
            "launcherAction": "blocked",
            "sideEffectPolicy": "no_artifact_write_or_export",
            "contentPolicy": "no_transcript_content",
        },
        {
            "controlId": "session_store_location",
            "panelId": "session_preferences",
            "label": "session store location",
            "state": "unavailable",
            "valueKind": "path",
            "defaultValue": "unavailable",
            "currentValue": "unavailable",
            "userAction": "unavailable",
            "launcherAction": "blocked",
            "sideEffectPolicy": "no_session_store_path_read",
            "contentPolicy": "no_private_path_or_session_title_content",
        },
        {
            "controlId": "diagnostics_verbosity",
            "panelId": "privacy_preferences",
            "label": "diagnostics verbosity",
            "state": "summary_only",
            "valueKind": "enum",
            "defaultValue": "summary",
            "currentValue": "summary",
            "userAction": "none",
            "launcherAction": "render_metadata_only",
            "sideEffectPolicy": "no_log_read_or_telemetry_upload",
            "contentPolicy": "summary_labels_only",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "preferences_persistence_not_reviewed",
            "state": "blocked",
            "summary": "preference writes require a reviewed local storage boundary",
            "requiredBefore": "enable preference save actions",
        },
        {
            "reasonId": "model_asset_picker_not_reviewed",
            "state": "disabled",
            "summary": "model path selection is outside this metadata boundary",
            "requiredBefore": "read or display model asset paths",
        },
        {
            "reasonId": "session_store_not_configured",
            "state": "not_configured",
            "summary": "no reviewed local session store exists",
            "requiredBefore": "enable session or transcript preferences",
        },
        {
            "reasonId": "provider_and_network_paths_blocked",
            "state": "disabled",
            "summary": "provider, cloud, and network fallback paths remain outside core chat",
            "requiredBefore": "enable any non-local preference",
        },
    ],
    "safetyFlags": {
        "readOnly": True,
        "dataOnly": True,
        "deterministic": True,
        "preferencesDisplayOnly": True,
        "preferencePersistence": False,
        "preferenceWrite": False,
        "configRead": False,
        "environmentRead": False,
        "secretsRead": False,
        "tokensRead": False,
        "providerConfigRead": False,
        "providerCalls": False,
        "cloudCalls": False,
        "networkCalls": False,
        "modelAssetRead": False,
        "modelPathIncluded": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "kv260Access": False,
        "hardwareAccess": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
        "sessionTitleIncluded": False,
        "summaryIncluded": False,
        "promptCapture": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "promptPersistence": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "transcriptContentIncluded": False,
        "transcriptPersistence": False,
        "transcriptExport": False,
        "readsArtifacts": False,
        "writesArtifacts": False,
        "privatePathIncluded": False,
        "rawLogIncluded": False,
        "telemetry": False,
        "upload": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "compatibilityClaim": False,
    },
    "limitations": [
        "preferences are deterministic fixture data only",
        "preference persistence is not configured or implemented",
        "provider configuration, environment secrets, tokens, and network paths are not read",
        "model asset paths, session-store paths, transcripts, prompts, responses, and summaries are not read",
        "no preference save, import, export, runtime launch, model load, or hardware access is performed",
        "no compatibility promise is made",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def _iter_state_values(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            if (
                key == "state"
                or key.endswith("State")
                or key.endswith("Status")
            ) and isinstance(nested, str):
                yield nested
            yield from _iter_state_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _iter_state_values(nested)


def _validate_preferences(preferences: dict) -> None:
    if tuple(preferences.keys()) != CHAT_PREFERENCES_FIELDS:
        raise TraceError("chat preferences fields changed")
    if preferences["schemaVersion"] != SCHEMA_VERSION:
        raise TraceError("unexpected chat preferences schema version")

    allowed = set(CHAT_PREFERENCES_STATE_VALUES)
    for state in _iter_state_values(preferences):
        if state not in allowed:
            raise TraceError(f"unexpected chat preferences state: {state}")

    for panel in preferences["preferencePanels"]:
        if tuple(panel.keys()) != PREFERENCE_PANEL_FIELDS:
            raise TraceError("preference panel fields changed")
    for control in preferences["preferenceControls"]:
        if tuple(control.keys()) != PREFERENCE_CONTROL_FIELDS:
            raise TraceError("preference control fields changed")
    for reason in preferences["blockedReasons"]:
        if tuple(reason.keys()) != BLOCKED_REASON_FIELDS:
            raise TraceError("blocked reason fields changed")


def create_gemma3n_e4b_kv260_chat_preferences() -> dict:
    preferences = copy.deepcopy(_CHAT_PREFERENCES)
    _validate_preferences(preferences)
    return preferences


def chat_preferences_json(preferences: dict | None = None) -> str:
    if preferences is None:
        preferences = create_gemma3n_e4b_kv260_chat_preferences()
    _validate_preferences(preferences)
    return json.dumps(preferences, indent=2, sort_keys=False) + "\n"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print the data-only launcher chat preferences fixture."
    )
    parser.add_argument("--model", default="gemma3n-e4b")
    parser.add_argument("--target", default="kv260")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    if args.model != "gemma3n-e4b" or args.target != "kv260":
        print(
            "only --model gemma3n-e4b --target kv260 is available in this fixture",
            file=sys.stderr,
        )
        return 2
    sys.stdout.write(chat_preferences_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
