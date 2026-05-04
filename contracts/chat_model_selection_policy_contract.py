#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat model-selection policy contract for the planned launcher UI.

The contract describes the disabled model picker and catalog boundary for the
standalone chat surface. It does not read configuration, environment values,
model catalogs, model paths, model assets, prompts, responses, transcripts,
runtime logs, private paths, or artifacts; it does not persist a selection,
load a model, start a runtime, call providers, invoke pccx-lab, or touch
KV260 hardware.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatModelSelectionPolicy.v0"

CHAT_MODEL_SELECTION_POLICY_FIELDS = (
    "schemaVersion",
    "selectionPolicyId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "selectionState",
    "catalogState",
    "pickerState",
    "selectedModelState",
    "descriptorState",
    "assetDiscoveryState",
    "assetPathState",
    "providerFallbackState",
    "loadRequestState",
    "privacyState",
    "chatModelStatusRef",
    "chatModelLoadRequestRef",
    "chatLocalOnlyPolicyRef",
    "chatReadinessRef",
    "selectionPolicy",
    "modelOptions",
    "selectionControls",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

SELECTION_POLICY_FIELDS = (
    "state",
    "mode",
    "sourcePolicy",
    "staticOptionCount",
    "dynamicCatalogConfigured",
    "localCatalogRead",
    "assetDiscoveryEnabled",
    "selectionEnabled",
    "selectionPersistenceEnabled",
    "providerFallbackEnabled",
    "loadRequestEnabled",
    "sideEffectPolicy",
    "contentPolicy",
)

MODEL_OPTION_FIELDS = (
    "optionId",
    "label",
    "state",
    "selected",
    "enabled",
    "modelFamily",
    "targetDevice",
    "descriptorRef",
    "assetPolicy",
    "runtimePolicy",
    "contentPolicy",
)

SELECTION_CONTROL_FIELDS = (
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

CHAT_MODEL_SELECTION_POLICY_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "external_not_configured",
    "inactive",
    "not_configured",
    "not_loaded",
    "not_started",
    "not_used",
    "placeholder",
    "planned",
    "requires_evidence",
    "static_placeholder",
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_MODEL_SELECTION_POLICY = {
    "schemaVersion": SCHEMA_VERSION,
    "selectionPolicyId": "chat_model_selection_policy_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-model-selection-policy.gemma3n-e4b-kv260.2026-05-05",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_model_selection_policy_boundary_2026-05-05",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "selectionState": "blocked",
    "catalogState": "static_placeholder",
    "pickerState": "disabled",
    "selectedModelState": "target_selected",
    "descriptorState": "available_as_data",
    "assetDiscoveryState": "blocked",
    "assetPathState": "not_configured",
    "providerFallbackState": "disabled",
    "loadRequestState": "blocked",
    "privacyState": "summary_only",
    "chatModelStatusRef": "chat_model_status_gemma3n_e4b_kv260_placeholder",
    "chatModelLoadRequestRef": "chat_model_load_request_gemma3n_e4b_kv260_placeholder",
    "chatLocalOnlyPolicyRef": "chat_local_only_policy_gemma3n_e4b_kv260_placeholder",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "selectionPolicy": {
        "state": "blocked",
        "mode": "disabled_until_reviewed_model_catalog_and_selection_boundary_exists",
        "sourcePolicy": "checked fixture only; no config, environment, model catalog, model path, asset path, weight file, tokenizer file, prompt, response, transcript, artifact, or runtime log is read",
        "staticOptionCount": 1,
        "dynamicCatalogConfigured": False,
        "localCatalogRead": False,
        "assetDiscoveryEnabled": False,
        "selectionEnabled": False,
        "selectionPersistenceEnabled": False,
        "providerFallbackEnabled": False,
        "loadRequestEnabled": False,
        "sideEffectPolicy": "local_render_only",
        "contentPolicy": "model selection metadata only; no model path, asset path, catalog body, file name, checksum value, prompt text, response text, transcript text, runtime log, or private path is included",
    },
    "modelOptions": [
        {
            "optionId": "gemma3n_e4b_kv260_placeholder",
            "label": "Gemma 3N E4B on KV260 target",
            "state": "target_selected",
            "selected": True,
            "enabled": False,
            "modelFamily": "gemma3n",
            "targetDevice": "kv260",
            "descriptorRef": "model_runtime_descriptor_gemma3n_e4b_kv260_placeholder",
            "assetPolicy": "placeholder_descriptor_only_no_asset_path",
            "runtimePolicy": "not_loaded_no_runtime_started",
            "contentPolicy": "target label, family, and descriptor reference only",
        }
    ],
    "selectionControls": [
        {
            "controlId": "review_static_target",
            "label": "review static target",
            "state": "available_as_data",
            "enabled": False,
            "userAction": "Review the checked target model label in the future chat UI.",
            "launcherAction": "Render static descriptor metadata from checked fixtures only.",
            "sideEffectPolicy": "local_render_only",
            "blockedReasonRef": "selection_executor_absent",
        },
        {
            "controlId": "open_model_catalog",
            "label": "open model catalog",
            "state": "blocked",
            "enabled": False,
            "userAction": "Open a local catalog only after catalog source and redaction rules are reviewed.",
            "launcherAction": "Keep catalog discovery disabled and do not read files, paths, config, or manifests.",
            "sideEffectPolicy": "no_catalog_or_config_read",
            "blockedReasonRef": "dynamic_catalog_boundary_absent",
        },
        {
            "controlId": "select_model_option",
            "label": "select model option",
            "state": "disabled",
            "enabled": False,
            "userAction": "Select a model only after the reviewed picker boundary exists.",
            "launcherAction": "Keep selection disabled and do not persist choices.",
            "sideEffectPolicy": "no_selection_persistence",
            "blockedReasonRef": "selection_executor_absent",
        },
        {
            "controlId": "discover_local_assets",
            "label": "discover local assets",
            "state": "blocked",
            "enabled": False,
            "userAction": "Discover assets only after a reviewed local asset boundary exists.",
            "launcherAction": "Do not scan directories, read model paths, or inspect model files.",
            "sideEffectPolicy": "no_model_asset_read",
            "blockedReasonRef": "model_asset_discovery_blocked",
        },
        {
            "controlId": "configure_provider_fallback",
            "label": "configure provider fallback",
            "state": "disabled",
            "enabled": False,
            "userAction": "Provider fallback is out of scope for core local chat behavior.",
            "launcherAction": "Keep provider and cloud fallback disabled.",
            "sideEffectPolicy": "no_provider_or_network_call",
            "blockedReasonRef": "provider_fallback_disabled",
        },
        {
            "controlId": "handoff_to_load_request",
            "label": "handoff to load request",
            "state": "blocked",
            "enabled": False,
            "userAction": "Create a load request only after model assets and runtime evidence are reviewed.",
            "launcherAction": "Render blocked handoff metadata only.",
            "sideEffectPolicy": "no_model_load",
            "blockedReasonRef": "load_request_blocked",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "dynamic_catalog_boundary_absent",
            "state": "not_configured",
            "summary": "No reviewed local model catalog source or redaction boundary exists.",
            "requiredBefore": "dynamic_catalog_enabled",
        },
        {
            "reasonId": "selection_executor_absent",
            "state": "disabled",
            "summary": "No reviewed picker executor or selection persistence boundary exists.",
            "requiredBefore": "model_picker_enabled",
        },
        {
            "reasonId": "model_asset_discovery_blocked",
            "state": "blocked",
            "summary": "Model asset discovery is blocked until asset path and manifest handling are reviewed.",
            "requiredBefore": "asset_discovery_enabled",
        },
        {
            "reasonId": "provider_fallback_disabled",
            "state": "disabled",
            "summary": "Provider and cloud fallback are disabled by the local-only policy.",
            "requiredBefore": "fallback_policy_reviewed",
        },
        {
            "reasonId": "load_request_blocked",
            "state": "blocked",
            "summary": "The downstream model-load request boundary remains blocked and data-only.",
            "requiredBefore": "load_request_enabled",
        },
        {
            "reasonId": "runtime_evidence_absent",
            "state": "requires_evidence",
            "summary": "Runtime readiness evidence is absent.",
            "requiredBefore": "runtime_dependent_selection_enabled",
        },
        {
            "reasonId": "hardware_evidence_absent",
            "state": "requires_evidence",
            "summary": "No KV260 runtime or model execution evidence is available in this repository.",
            "requiredBefore": "hardware_target_selection_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "fixturePath": "contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Model status display keeps model loading blocked and disabled.",
        },
        {
            "refId": "chat_model_load_request",
            "schemaVersion": "pccx.chatModelLoadRequest.v0",
            "fixturePath": "contracts/fixtures/chat-model-load-request.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Model-load request remains disabled and does not read assets or start runtime.",
        },
        {
            "refId": "chat_local_only_policy",
            "schemaVersion": "pccx.chatLocalOnlyPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-local-only-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Local-only policy keeps provider, cloud, and fallback paths blocked.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Chat readiness keeps send and recovery actions blocked.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "selectionPolicyDisplayOnly": True,
        "staticOptionOnly": True,
        "dynamicCatalogConfigured": False,
        "modelCatalogRead": False,
        "dynamicCatalogDiscovery": False,
        "modelSelectionPersisted": False,
        "modelSelectionAcceptedFromUser": False,
        "modelOptionsFromConfig": False,
        "modelAssetPathsIncluded": False,
        "modelWeightPathsIncluded": False,
        "modelAssetPathRead": False,
        "modelAssetRead": False,
        "modelWeightRead": False,
        "tokenizerRead": False,
        "checksumManifestRead": False,
        "checksumValuesIncluded": False,
        "configRead": False,
        "configWrite": False,
        "environmentRead": False,
        "providerConfigRead": False,
        "providerCalls": False,
        "cloudCalls": False,
        "networkCalls": False,
        "promptContentIncluded": False,
        "promptCapture": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "transcriptContentIncluded": False,
        "transcriptPersistence": False,
        "sessionPersistence": False,
        "runtimePreflightExecuted": False,
        "runtimeStarted": False,
        "runtimeExecution": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "kv260Access": False,
        "hardwareAccess": False,
        "readsArtifacts": False,
        "writesArtifacts": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
        "telemetry": False,
        "automaticUpload": False,
        "writeBack": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "mcpServerImplemented": False,
        "lspImplemented": False,
        "compatibilityClaim": False,
    },
    "limitations": [
        "Data-only chat model-selection policy fixture; the selected target is static placeholder metadata.",
        "No model catalog, configuration file, environment value, model path, asset path, model weight, tokenizer, checksum manifest, prompt, response, transcript, runtime log, private path, secret, or token is read.",
        "No user model selection is accepted, persisted, or handed to a runtime.",
        "No model asset discovery, provider fallback, network call, runtime preflight, model load, model execution, telemetry, upload, or artifact write is performed.",
        "No KV260 hardware access, pccx-lab invocation, or systemverilog-ide invocation is performed.",
        "This is not a release, tag, compatibility commitment, marketplace flow, provider integration, storage layer, runtime, model-loader, or hardware implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_model_selection_policy() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 model-selection fixture."""
    return copy.deepcopy(_CHAT_MODEL_SELECTION_POLICY)


def chat_model_selection_policy_json(policy: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        policy
        if policy is not None
        else create_gemma3n_e4b_kv260_chat_model_selection_policy(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat model-selection policy JSON.",
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
    sys.stdout.write(chat_model_selection_policy_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
