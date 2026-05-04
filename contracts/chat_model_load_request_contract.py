#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat model-load request contract for the planned launcher UI.

The contract describes the disabled local model-load request boundary for the
standalone chat surface. It does not read configuration, environment values,
model asset paths, model weights, tokenizer files, checksum manifests, prompts,
responses, transcripts, private paths, or runtime logs; it does not validate,
load, unload, warm up, execute, touch KV260 hardware, call providers, invoke
pccx-lab, or write artifacts.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatModelLoadRequest.v0"

CHAT_MODEL_LOAD_REQUEST_FIELDS = (
    "schemaVersion",
    "loadRequestId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "loadRequestState",
    "selectedModelState",
    "descriptorState",
    "assetInputState",
    "assetPathState",
    "checksumState",
    "loadPlanState",
    "runtimePreflightState",
    "deviceSessionState",
    "warmupState",
    "unloadState",
    "privacyState",
    "chatModelStatusRef",
    "runtimeReadinessRef",
    "deviceSessionStatusRef",
    "chatReadinessRef",
    "chatLocalOnlyPolicyRef",
    "loadRequestPolicy",
    "loadInputs",
    "loadControls",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

LOAD_REQUEST_POLICY_FIELDS = (
    "state",
    "mode",
    "sourcePolicy",
    "descriptorSelected",
    "modelAssetsConfigured",
    "assetPathsConfigured",
    "checksumsAvailable",
    "runtimeReady",
    "deviceSessionReady",
    "loadEnabled",
    "warmupEnabled",
    "unloadEnabled",
    "sideEffectPolicy",
    "contentPolicy",
)

LOAD_INPUT_FIELDS = (
    "inputId",
    "label",
    "state",
    "enabled",
    "summary",
    "sideEffectPolicy",
    "contentPolicy",
)

LOAD_CONTROL_FIELDS = (
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

CHAT_MODEL_LOAD_REQUEST_STATE_VALUES = (
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
    "summary_only",
    "target_selected",
    "unavailable",
)

_CHAT_MODEL_LOAD_REQUEST = {
    "schemaVersion": SCHEMA_VERSION,
    "loadRequestId": "chat_model_load_request_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-model-load-request.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_model_load_request_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "loadRequestState": "blocked",
    "selectedModelState": "target_selected",
    "descriptorState": "available_as_data",
    "assetInputState": "blocked",
    "assetPathState": "not_configured",
    "checksumState": "not_configured",
    "loadPlanState": "blocked",
    "runtimePreflightState": "blocked",
    "deviceSessionState": "inactive",
    "warmupState": "disabled",
    "unloadState": "disabled",
    "privacyState": "summary_only",
    "chatModelStatusRef": "chat_model_status_gemma3n_e4b_kv260_placeholder",
    "runtimeReadinessRef": "runtime_readiness_gemma3n_e4b_kv260",
    "deviceSessionStatusRef": "device_session_status_gemma3n_e4b_kv260",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "chatLocalOnlyPolicyRef": "chat_local_only_policy_gemma3n_e4b_kv260_placeholder",
    "loadRequestPolicy": {
        "state": "blocked",
        "mode": "disabled_until_reviewed_model_load_boundary_exists",
        "sourcePolicy": "checked fixture only; no config, environment, model path, asset path, weight file, tokenizer file, checksum manifest, prompt, response, transcript, artifact, or runtime log is read",
        "descriptorSelected": True,
        "modelAssetsConfigured": False,
        "assetPathsConfigured": False,
        "checksumsAvailable": False,
        "runtimeReady": False,
        "deviceSessionReady": False,
        "loadEnabled": False,
        "warmupEnabled": False,
        "unloadEnabled": False,
        "sideEffectPolicy": "local_render_only",
        "contentPolicy": "model-load request metadata only; no model path, asset path, file name, checksum value, manifest body, prompt text, response text, transcript text, runtime log, or private path is included",
    },
    "loadInputs": [
        {
            "inputId": "model_descriptor",
            "label": "model descriptor",
            "state": "available_as_data",
            "enabled": False,
            "summary": "Gemma 3N E4B is represented by the checked descriptor fixture only.",
            "sideEffectPolicy": "fixture_metadata_only",
            "contentPolicy": "descriptor_id_and_target_label_only",
        },
        {
            "inputId": "local_asset_path",
            "label": "local asset path",
            "state": "not_configured",
            "enabled": False,
            "summary": "No reviewed local model asset path is configured, resolved, read, or emitted.",
            "sideEffectPolicy": "no_config_or_path_read",
            "contentPolicy": "no_model_asset_path_or_private_path",
        },
        {
            "inputId": "model_weight_file",
            "label": "model weight file",
            "state": "blocked",
            "enabled": False,
            "summary": "Model weight files are not discovered, opened, validated, or loaded.",
            "sideEffectPolicy": "no_model_asset_read",
            "contentPolicy": "no_weight_filename_path_or_bytes",
        },
        {
            "inputId": "tokenizer_asset",
            "label": "tokenizer asset",
            "state": "blocked",
            "enabled": False,
            "summary": "Tokenizer assets are not discovered, opened, validated, or loaded.",
            "sideEffectPolicy": "no_tokenizer_read",
            "contentPolicy": "no_tokenizer_filename_path_or_bytes",
        },
        {
            "inputId": "checksum_manifest",
            "label": "checksum manifest",
            "state": "not_configured",
            "enabled": False,
            "summary": "No checksum manifest schema or local integrity evidence is configured.",
            "sideEffectPolicy": "no_manifest_read",
            "contentPolicy": "no_checksum_values_or_manifest_body",
        },
        {
            "inputId": "runtime_profile",
            "label": "runtime profile",
            "state": "blocked",
            "enabled": False,
            "summary": "Runtime profile selection is blocked until runtime readiness is evidence-backed.",
            "sideEffectPolicy": "no_runtime_preflight",
            "contentPolicy": "profile_metadata_only",
        },
        {
            "inputId": "device_session",
            "label": "device session",
            "state": "inactive",
            "enabled": False,
            "summary": "No target device session exists and no board runtime state is measured.",
            "sideEffectPolicy": "no_hardware_probe",
            "contentPolicy": "inactive_status_only",
        },
    ],
    "loadControls": [
        {
            "controlId": "select_model_descriptor",
            "label": "select model descriptor",
            "state": "target_selected",
            "enabled": False,
            "userAction": "Review the target model descriptor in the future chat UI.",
            "launcherAction": "Render descriptor metadata from checked fixtures only.",
            "sideEffectPolicy": "local_render_only",
            "blockedReasonRef": "model_load_executor_absent",
        },
        {
            "controlId": "configure_asset_path",
            "label": "configure asset path",
            "state": "blocked",
            "enabled": False,
            "userAction": "Configure local assets only after a reviewed model-asset input boundary exists.",
            "launcherAction": "Keep asset path configuration disabled and do not read config or paths.",
            "sideEffectPolicy": "no_config_or_path_read",
            "blockedReasonRef": "model_asset_input_boundary_absent",
        },
        {
            "controlId": "validate_assets",
            "label": "validate assets",
            "state": "blocked",
            "enabled": False,
            "userAction": "Validate assets only after integrity and redaction rules are reviewed.",
            "launcherAction": "Refuse asset validation and do not open model files or manifests.",
            "sideEffectPolicy": "no_model_asset_read",
            "blockedReasonRef": "model_integrity_evidence_absent",
        },
        {
            "controlId": "build_load_plan",
            "label": "build load plan",
            "state": "blocked",
            "enabled": False,
            "userAction": "Build a load plan only after asset, runtime, and target-session evidence exists.",
            "launcherAction": "Render blocked load-plan metadata only.",
            "sideEffectPolicy": "no_runtime_preflight",
            "blockedReasonRef": "runtime_readiness_blocked",
        },
        {
            "controlId": "start_runtime",
            "label": "start runtime",
            "state": "disabled",
            "enabled": False,
            "userAction": "Start runtime only after evidence-backed runtime and target-session readiness.",
            "launcherAction": "Keep runtime start disabled.",
            "sideEffectPolicy": "no_runtime_execution",
            "blockedReasonRef": "runtime_readiness_blocked",
        },
        {
            "controlId": "load_model",
            "label": "load model",
            "state": "disabled",
            "enabled": False,
            "userAction": "Load model only after assets, integrity, runtime, and device evidence are reviewed.",
            "launcherAction": "Refuse model load and do not touch model assets or hardware.",
            "sideEffectPolicy": "no_model_load",
            "blockedReasonRef": "model_load_executor_absent",
        },
        {
            "controlId": "warmup_model",
            "label": "warm up model",
            "state": "disabled",
            "enabled": False,
            "userAction": "Warm up only after a model is loaded by a reviewed runtime path.",
            "launcherAction": "Keep warmup disabled and do not execute inference.",
            "sideEffectPolicy": "no_model_execution",
            "blockedReasonRef": "model_load_executor_absent",
        },
        {
            "controlId": "unload_model",
            "label": "unload model",
            "state": "disabled",
            "enabled": False,
            "userAction": "Unload only after a reviewed runtime lifecycle exists.",
            "launcherAction": "Keep unload disabled because no model is loaded.",
            "sideEffectPolicy": "no_runtime_execution",
            "blockedReasonRef": "unload_policy_absent",
        },
        {
            "controlId": "persist_load_request",
            "label": "persist load request",
            "state": "disabled",
            "enabled": False,
            "userAction": "Persist load requests only after local configuration storage is reviewed.",
            "launcherAction": "Do not write policy, request, preference, or config files.",
            "sideEffectPolicy": "no_policy_write",
            "blockedReasonRef": "model_asset_path_boundary_absent",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "model_asset_input_boundary_absent",
            "state": "blocked",
            "summary": "No reviewed local model asset input boundary exists.",
            "requiredBefore": "configure_asset_path_enabled",
        },
        {
            "reasonId": "model_asset_path_boundary_absent",
            "state": "not_configured",
            "summary": "No reviewed config/path boundary exists for model asset locations.",
            "requiredBefore": "asset_paths_available",
        },
        {
            "reasonId": "model_integrity_evidence_absent",
            "state": "requires_evidence",
            "summary": "Checksum, size, format, and provenance evidence are absent.",
            "requiredBefore": "validate_assets_enabled",
        },
        {
            "reasonId": "runtime_readiness_blocked",
            "state": "blocked",
            "summary": "Runtime readiness remains blocked and not evidence-backed.",
            "requiredBefore": "runtime_preflight_enabled",
        },
        {
            "reasonId": "device_session_inactive",
            "state": "inactive",
            "summary": "No KV260 target session exists for model load handoff.",
            "requiredBefore": "load_model_enabled",
        },
        {
            "reasonId": "model_load_executor_absent",
            "state": "disabled",
            "summary": "No reviewed model-load executor or runtime lifecycle exists.",
            "requiredBefore": "load_model_enabled",
        },
        {
            "reasonId": "unload_policy_absent",
            "state": "planned",
            "summary": "Unload, cleanup, and rollback policy needs a reviewed runtime lifecycle.",
            "requiredBefore": "unload_model_enabled",
        },
        {
            "reasonId": "local_only_policy_required",
            "state": "planned",
            "summary": "Local-only policy must continue blocking provider and cloud fallback paths.",
            "requiredBefore": "load_request_review_complete",
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
            "refId": "runtime_readiness",
            "schemaVersion": "pccx.runtimeReadiness.v0",
            "fixturePath": "contracts/fixtures/runtime-readiness.gemma3n-e4b-kv260.json",
            "state": "blocked",
            "summary": "Runtime readiness remains blocked and local-data only.",
        },
        {
            "refId": "device_session_status",
            "schemaVersion": "pccx.deviceSessionStatus.v0",
            "fixturePath": "contracts/fixtures/device-session-status.gemma3n-e4b-kv260.json",
            "state": "inactive",
            "summary": "Device/session status reports no active target session.",
        },
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Chat readiness keeps send and recovery actions blocked.",
        },
        {
            "refId": "chat_local_only_policy",
            "schemaVersion": "pccx.chatLocalOnlyPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-local-only-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Local-only policy keeps provider, cloud, and fallback paths blocked.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "loadRequestDisplayOnly": True,
        "modelDescriptorMetadataOnly": True,
        "modelAssetsConfigured": False,
        "modelAssetPathsConfigured": False,
        "modelAssetPathsIncluded": False,
        "modelWeightPathsIncluded": False,
        "modelAssetRead": False,
        "modelWeightRead": False,
        "tokenizerRead": False,
        "checksumManifestRead": False,
        "checksumValuesIncluded": False,
        "modelIntegrityChecked": False,
        "configRead": False,
        "configWrite": False,
        "environmentRead": False,
        "promptContentIncluded": False,
        "promptCapture": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "transcriptPersistence": False,
        "sessionPersistence": False,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "artifactWrites": False,
        "artifactReads": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
        "runtimePreflightExecuted": False,
        "runtimeStarted": False,
        "runtimeExecution": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelUnloadAttempted": False,
        "modelExecution": False,
        "warmupAttempted": False,
        "touchesHardware": False,
        "hardwareAccess": False,
        "kv260Access": False,
        "opensSerialPort": False,
        "networkCalls": False,
        "networkScan": False,
        "sshExecution": False,
        "providerCalls": False,
        "cloudCalls": False,
        "runtimeLogsIncluded": False,
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
        "Data-only chat model-load request fixture; no model asset path is configured, read, resolved, or emitted.",
        "No model weights, tokenizer files, checksum manifests, configuration files, environment values, prompts, responses, transcripts, runtime logs, private paths, secrets, or tokens are read.",
        "No model asset validation, checksum computation, runtime preflight, model load, model unload, model warmup, response generation, persistence, import, export, upload, telemetry, or artifact write is performed.",
        "No KV260 hardware access, serial access, network call, provider call, pccx-lab invocation, or systemverilog-ide invocation is performed.",
        "This is not a release, tag, compatibility commitment, MCP, LSP, IDE, marketplace, telemetry, runtime, model-loader, provider, storage, or hardware implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_model_load_request() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 model-load request fixture."""
    return copy.deepcopy(_CHAT_MODEL_LOAD_REQUEST)


def chat_model_load_request_json(request: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        request
        if request is not None
        else create_gemma3n_e4b_kv260_chat_model_load_request(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat model-load request JSON.",
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
    sys.stdout.write(chat_model_load_request_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
