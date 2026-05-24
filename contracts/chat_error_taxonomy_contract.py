#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat error taxonomy contract for the planned launcher UI.

The contract describes grouped, user-visible blocked error categories for the
local chat surface. It does not read prompts, responses, transcripts, config,
provider settings, environment variables, secrets, tokens, model assets,
session stores, logs, or artifacts; it does not start runtime code, load
models, touch KV260 hardware, call providers, invoke pccx-lab, or persist
anything.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatErrorTaxonomy.v0"

CHAT_ERROR_TAXONOMY_FIELDS = (
    "schemaVersion",
    "taxonomyId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "taxonomyState",
    "displayState",
    "inputContentState",
    "runtimeState",
    "chatReadinessRef",
    "chatSendResultRef",
    "chatComposerRef",
    "chatAuditEventRef",
    "chatLocalOnlyPolicyRef",
    "errorGroups",
    "errorItems",
    "actionRefs",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

ERROR_GROUP_FIELDS = (
    "groupId",
    "label",
    "state",
    "severity",
    "sourceRefs",
    "displayPolicy",
    "contentPolicy",
)

ERROR_ITEM_FIELDS = (
    "itemId",
    "groupId",
    "state",
    "severity",
    "userMessage",
    "diagnosticHint",
    "primaryActionRef",
    "sourceErrorRefs",
    "contentPolicy",
)

ACTION_REF_FIELDS = (
    "actionId",
    "label",
    "state",
    "enabled",
    "sourceRef",
    "sideEffectPolicy",
)

HANDOFF_REF_FIELDS = (
    "refId",
    "schemaVersion",
    "fixturePath",
    "state",
    "summary",
)

CHAT_ERROR_TAXONOMY_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "external_not_configured",
    "inactive",
    "not_configured",
    "not_loaded",
    "not_started",
    "not_used",
    "planned",
    "requires_evidence",
    "summary_only",
    "unavailable",
)

_CHAT_ERROR_TAXONOMY = {
    "schemaVersion": SCHEMA_VERSION,
    "taxonomyId": "chat_error_taxonomy_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-error-taxonomy.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_error_taxonomy_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "taxonomyState": "available_as_data",
    "displayState": "summary_only",
    "inputContentState": "unavailable",
    "runtimeState": "not_started",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "chatSendResultRef": "chat_send_result_gemma3n_e4b_kv260_placeholder",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatAuditEventRef": "chat_audit_event_gemma3n_e4b_kv260_placeholder",
    "chatLocalOnlyPolicyRef": "chat_local_only_policy_gemma3n_e4b_kv260_placeholder",
    "errorGroups": [
        {
            "groupId": "readiness_blockers",
            "label": "readiness blockers",
            "state": "blocked",
            "severity": "blocked",
            "sourceRefs": [
                "chat_readiness",
                "runtime_readiness",
                "device_session_status",
            ],
            "displayPolicy": "show concise blocked status rows only",
            "contentPolicy": "no_prompt_response_transcript_or_log_content",
        },
        {
            "groupId": "model_and_runtime_blockers",
            "label": "model and runtime blockers",
            "state": "requires_evidence",
            "severity": "blocked",
            "sourceRefs": [
                "chat_model_status",
                "runtime_readiness",
            ],
            "displayPolicy": "show evidence requirements without model paths",
            "contentPolicy": "no_model_path_weight_or_runtime_log_content",
        },
        {
            "groupId": "session_and_policy_blockers",
            "label": "session and policy blockers",
            "state": "not_configured",
            "severity": "blocked",
            "sourceRefs": [
                "chat_session_index",
                "chat_transcript_policy",
                "chat_local_only_policy",
            ],
            "displayPolicy": "show policy summaries without reading stores",
            "contentPolicy": "no_session_store_title_summary_or_path_content",
        },
    ],
    "errorItems": [
        {
            "itemId": "send_disabled_by_readiness",
            "groupId": "readiness_blockers",
            "state": "blocked",
            "severity": "blocked",
            "userMessage": "Send stays disabled until local chat readiness evidence exists.",
            "diagnosticHint": "Review the chat readiness and blocked send-result fixtures.",
            "primaryActionRef": "review_chat_readiness",
            "sourceErrorRefs": [
                "runtime_not_ready",
                "readiness_blocked",
            ],
            "contentPolicy": "no_prompt_response_or_transcript_content",
        },
        {
            "itemId": "model_assets_not_configured",
            "groupId": "model_and_runtime_blockers",
            "state": "external_not_configured",
            "severity": "blocked",
            "userMessage": "Model assets are not configured by this fixture.",
            "diagnosticHint": "A future reviewed asset input boundary must redact local paths.",
            "primaryActionRef": "wait_for_asset_boundary",
            "sourceErrorRefs": [
                "model_assets_missing",
                "model_not_loaded",
            ],
            "contentPolicy": "no_model_paths_or_weight_names",
        },
        {
            "itemId": "runtime_not_started",
            "groupId": "model_and_runtime_blockers",
            "state": "not_started",
            "severity": "blocked",
            "userMessage": "No local chat runtime is available for responses.",
            "diagnosticHint": "Runtime execution requires a separate reviewed implementation boundary.",
            "primaryActionRef": "wait_for_runtime_boundary",
            "sourceErrorRefs": [
                "chat_runtime_absent",
                "runtime_not_started",
            ],
            "contentPolicy": "no_generated_response_content",
        },
        {
            "itemId": "session_store_not_configured",
            "groupId": "session_and_policy_blockers",
            "state": "not_configured",
            "severity": "blocked",
            "userMessage": "Session restore, transcript retention, and export are unavailable.",
            "diagnosticHint": "A future local session store must define retention and redaction rules.",
            "primaryActionRef": "review_session_policy",
            "sourceErrorRefs": [
                "session_store_absent",
                "session_store_not_configured",
            ],
            "contentPolicy": "no_manifest_transcript_summary_or_path_content",
        },
        {
            "itemId": "provider_paths_not_used",
            "groupId": "session_and_policy_blockers",
            "state": "not_used",
            "severity": "info",
            "userMessage": "External provider paths are not used for core local chat.",
            "diagnosticHint": "Local-only policy remains display data and does not read provider configuration.",
            "primaryActionRef": "review_local_only_policy",
            "sourceErrorRefs": [
                "provider_mode",
                "provider_and_network_paths_blocked",
            ],
            "contentPolicy": "no_provider_configuration_or_prompt_content",
        },
    ],
    "actionRefs": [
        {
            "actionId": "review_chat_readiness",
            "label": "review chat readiness",
            "state": "available_as_data",
            "enabled": False,
            "sourceRef": "chat_readiness",
            "sideEffectPolicy": "read_only_data",
        },
        {
            "actionId": "wait_for_asset_boundary",
            "label": "wait for asset boundary",
            "state": "requires_evidence",
            "enabled": False,
            "sourceRef": "chat_model_status",
            "sideEffectPolicy": "no_model_asset_read",
        },
        {
            "actionId": "wait_for_runtime_boundary",
            "label": "wait for runtime boundary",
            "state": "requires_evidence",
            "enabled": False,
            "sourceRef": "runtime_readiness",
            "sideEffectPolicy": "no_runtime_execution",
        },
        {
            "actionId": "review_session_policy",
            "label": "review session policy",
            "state": "planned",
            "enabled": False,
            "sourceRef": "chat_transcript_policy",
            "sideEffectPolicy": "no_artifact_read_no_write",
        },
        {
            "actionId": "review_local_only_policy",
            "label": "review local-only policy",
            "state": "available_as_data",
            "enabled": False,
            "sourceRef": "chat_local_only_policy",
            "sideEffectPolicy": "no_provider_or_network_call",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Readiness checks and recovery actions remain local data only.",
        },
        {
            "refId": "chat_send_result",
            "schemaVersion": "pccx.chatSendResult.v0",
            "fixturePath": "contracts/fixtures/chat-send-result.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Send result stays blocked with no accepted input.",
        },
        {
            "refId": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "fixturePath": "contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Model status display is consumed without model paths.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Transcript retention and export remain disabled.",
        },
        {
            "refId": "chat_local_only_policy",
            "schemaVersion": "pccx.chatLocalOnlyPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-local-only-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "Local-only policy is consumed as summary data only.",
        },
    ],
    "safetyFlags": {
        "readOnly": True,
        "dataOnly": True,
        "deterministic": True,
        "taxonomyDisplayOnly": True,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "promptCapture": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "promptPersistence": False,
        "inputAccepted": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "transcriptContentIncluded": False,
        "transcriptPersistence": False,
        "sessionStoreRead": False,
        "sessionStoreWrite": False,
        "sessionTitleIncluded": False,
        "summaryIncluded": False,
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
        "modelWeightPathsIncluded": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "kv260Access": False,
        "hardwareAccess": False,
        "opensSerialPort": False,
        "networkScan": False,
        "sshExecution": False,
        "privatePathIncluded": False,
        "rawLogIncluded": False,
        "hardwareDumpsIncluded": False,
        "generatedBlobsIncluded": False,
        "telemetry": False,
        "upload": False,
        "writeBack": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "compatibilityClaim": False,
    },
    "limitations": [
        "error taxonomy is deterministic fixture data only",
        "error groups summarize blocked local chat states without reading prompts, responses, transcripts, logs, paths, or artifacts",
        "model assets, provider configuration, environment secrets, tokens, and network paths are not read",
        "no recovery action, runtime launch, model load, provider call, hardware probe, preference write, or artifact read/write is performed",
        "no compatibility promise is made",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_error_taxonomy() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 chat error taxonomy fixture."""
    return copy.deepcopy(_CHAT_ERROR_TAXONOMY)


def chat_error_taxonomy_json(taxonomy: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        taxonomy
        if taxonomy is not None
        else create_gemma3n_e4b_kv260_chat_error_taxonomy(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat error taxonomy JSON.",
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
    sys.stdout.write(chat_error_taxonomy_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
