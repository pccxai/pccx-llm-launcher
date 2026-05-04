#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only local-only policy contract for the planned launcher chat UI.

The contract describes how the standalone chat surface records the current
local-only policy and cloud/provider disablement while keeping every runtime,
model, hardware, network, prompt, response, transcript, and artifact path
disabled or blocked. It does not read provider configuration, environment
secrets, model assets, prompts, responses, transcripts, session stores,
private paths, or logs; it does not write artifacts, load models, touch KV260
hardware, call providers, invoke pccx-lab, or start runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatLocalOnlyPolicy.v0"

CHAT_LOCAL_ONLY_POLICY_FIELDS = (
    "schemaVersion",
    "policyId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "policyState",
    "localExecutionState",
    "cloudDependencyState",
    "providerState",
    "networkState",
    "offlineModeState",
    "fallbackState",
    "privacyState",
    "chatReadinessRef",
    "chatModelStatusRef",
    "runtimeReadinessRef",
    "policyControls",
    "dependencyChecks",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

POLICY_CONTROL_FIELDS = (
    "controlId",
    "label",
    "state",
    "visible",
    "enabled",
    "userAction",
    "launcherAction",
    "sideEffectPolicy",
    "contentPolicy",
)

DEPENDENCY_CHECK_FIELDS = (
    "checkId",
    "state",
    "requiredForSend",
    "externalDependency",
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

CHAT_LOCAL_ONLY_POLICY_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "enforced_as_metadata",
    "inactive",
    "local_only",
    "no_external_dependency",
    "not_configured",
    "not_loaded",
    "not_started",
    "not_used",
    "placeholder",
    "planned",
    "requires_evidence",
    "summary_only",
    "unavailable",
)

_CHAT_LOCAL_ONLY_POLICY = {
    "schemaVersion": SCHEMA_VERSION,
    "policyId": "chat_local_only_policy_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-local-only-policy.gemma3n-e4b-kv260.2026-05-04",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_local_only_policy_boundary_2026-05-04",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "policyState": "enforced_as_metadata",
    "localExecutionState": "blocked",
    "cloudDependencyState": "no_external_dependency",
    "providerState": "not_used",
    "networkState": "not_used",
    "offlineModeState": "available_as_data",
    "fallbackState": "disabled",
    "privacyState": "summary_only",
    "chatReadinessRef": "chat_readiness_gemma3n_e4b_kv260_placeholder",
    "chatModelStatusRef": "chat_model_status_gemma3n_e4b_kv260_placeholder",
    "runtimeReadinessRef": "runtime_readiness_gemma3n_e4b_kv260",
    "policyControls": [
        {
            "controlId": "local_only_mode_indicator",
            "label": "local-only mode indicator",
            "state": "available_as_data",
            "visible": True,
            "enabled": False,
            "userAction": "none",
            "launcherAction": "render_metadata_only",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "no_prompt_response_transcript_or_model_path_content",
        },
        {
            "controlId": "cloud_provider_selector",
            "label": "cloud provider selector",
            "state": "disabled",
            "visible": False,
            "enabled": False,
            "userAction": "unavailable",
            "launcherAction": "blocked",
            "sideEffectPolicy": "no_provider_or_network_call",
            "contentPolicy": "no_provider_configuration_or_secret_content",
        },
        {
            "controlId": "cloud_fallback_control",
            "label": "cloud fallback control",
            "state": "disabled",
            "visible": False,
            "enabled": False,
            "userAction": "unavailable",
            "launcherAction": "blocked",
            "sideEffectPolicy": "no_provider_or_network_call",
            "contentPolicy": "no_prompt_or_response_content",
        },
        {
            "controlId": "offline_policy_banner",
            "label": "offline policy banner",
            "state": "summary_only",
            "visible": True,
            "enabled": False,
            "userAction": "none",
            "launcherAction": "render_metadata_only",
            "sideEffectPolicy": "local_render_only",
            "contentPolicy": "policy_summary_only",
        },
    ],
    "dependencyChecks": [
        {
            "checkId": "core_chat_requires_cloud",
            "state": "no_external_dependency",
            "requiredForSend": False,
            "externalDependency": False,
            "summary": "core chat target is recorded as local-only metadata",
        },
        {
            "checkId": "provider_configuration_present",
            "state": "not_used",
            "requiredForSend": False,
            "externalDependency": True,
            "summary": "provider configuration is not read or required",
        },
        {
            "checkId": "network_access_required",
            "state": "not_used",
            "requiredForSend": False,
            "externalDependency": True,
            "summary": "network access is not required by this fixture",
        },
        {
            "checkId": "cloud_fallback_enabled",
            "state": "disabled",
            "requiredForSend": False,
            "externalDependency": True,
            "summary": "cloud fallback is disabled and not implemented",
        },
        {
            "checkId": "local_runtime_evidence",
            "state": "blocked",
            "requiredForSend": True,
            "externalDependency": False,
            "summary": "local runtime evidence is required before send enablement",
        },
        {
            "checkId": "local_model_loaded",
            "state": "not_loaded",
            "requiredForSend": True,
            "externalDependency": False,
            "summary": "model assets are not loaded by this fixture",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "local_runtime_not_started",
            "state": "not_started",
            "summary": "no local runtime session exists",
            "requiredBefore": "enable chat send controls",
        },
        {
            "reasonId": "model_not_loaded",
            "state": "not_loaded",
            "summary": "no model assets are loaded",
            "requiredBefore": "enable chat send controls",
        },
        {
            "reasonId": "provider_calls_blocked",
            "state": "disabled",
            "summary": "provider calls are outside this local-only boundary",
            "requiredBefore": "keep disabled unless separately reviewed",
        },
        {
            "reasonId": "network_calls_blocked",
            "state": "disabled",
            "summary": "network calls are outside this local-only boundary",
            "requiredBefore": "keep disabled unless separately reviewed",
        },
        {
            "reasonId": "cloud_fallback_blocked",
            "state": "disabled",
            "summary": "cloud fallback is not part of the core local chat path",
            "requiredBefore": "keep disabled unless separately reviewed",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_readiness",
            "schemaVersion": "pccx.chatReadiness.v0",
            "fixturePath": "contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "readiness checks include no-provider and local runtime gates",
        },
        {
            "refId": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "fixturePath": "contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json",
            "state": "available_as_data",
            "summary": "model display remains local descriptor metadata only",
        },
        {
            "refId": "runtime_readiness",
            "schemaVersion": "pccx.runtimeReadiness.v0",
            "fixturePath": "contracts/fixtures/runtime-readiness.gemma3n-e4b-kv260.json",
            "state": "blocked",
            "summary": "runtime readiness remains evidence-gated",
        },
    ],
    "safetyFlags": {
        "readOnly": True,
        "dataOnly": True,
        "deterministic": True,
        "localOnlyPolicyDisplayOnly": True,
        "cloudDependency": False,
        "cloudFallbackEnabled": False,
        "providerCalls": False,
        "cloudCalls": False,
        "networkCalls": False,
        "providerConfigRead": False,
        "environmentRead": False,
        "secretsRead": False,
        "tokensRead": False,
        "promptCapture": False,
        "promptContentIncluded": False,
        "responseContentIncluded": False,
        "transcriptContentIncluded": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "kv260Access": False,
        "writesArtifacts": False,
        "readsArtifacts": False,
        "telemetry": False,
        "upload": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
    },
    "limitations": [
        "policy is a deterministic fixture only",
        "local runtime evidence is not present in this repository",
        "model assets are not loaded or inspected",
        "provider configuration, environment secrets, tokens, and network paths are not read",
        "cloud fallback is disabled and not implemented",
        "send controls remain disabled until separate reviewed boundaries exist",
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


def _validate_policy(policy: dict) -> None:
    if tuple(policy.keys()) != CHAT_LOCAL_ONLY_POLICY_FIELDS:
        raise ValueError("chat local-only policy fields changed")
    if policy["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected chat local-only policy schema version")

    allowed = set(CHAT_LOCAL_ONLY_POLICY_STATE_VALUES)
    for state in _iter_state_values(policy):
        if state not in allowed:
            raise ValueError(f"unexpected chat local-only policy state: {state}")

    for control in policy["policyControls"]:
        if tuple(control.keys()) != POLICY_CONTROL_FIELDS:
            raise ValueError("policy control fields changed")
    for check in policy["dependencyChecks"]:
        if tuple(check.keys()) != DEPENDENCY_CHECK_FIELDS:
            raise ValueError("dependency check fields changed")
    for reason in policy["blockedReasons"]:
        if tuple(reason.keys()) != BLOCKED_REASON_FIELDS:
            raise ValueError("blocked reason fields changed")
    for ref in policy["handoffRefs"]:
        if tuple(ref.keys()) != HANDOFF_REF_FIELDS:
            raise ValueError("handoff ref fields changed")


def create_gemma3n_e4b_kv260_chat_local_only_policy() -> dict:
    policy = copy.deepcopy(_CHAT_LOCAL_ONLY_POLICY)
    _validate_policy(policy)
    return policy


def chat_local_only_policy_json(policy: dict | None = None) -> str:
    if policy is None:
        policy = create_gemma3n_e4b_kv260_chat_local_only_policy()
    _validate_policy(policy)
    return json.dumps(policy, indent=2, sort_keys=False) + "\n"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print the data-only launcher chat local-only policy fixture."
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
    sys.stdout.write(chat_local_only_policy_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
