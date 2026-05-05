#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only chat context-policy contract for the planned launcher UI.

The contract describes the disabled context-window and context-assembly
boundary for the standalone chat surface. It does not read prompts,
responses, transcripts, summaries, stores, model paths, tokenizer files,
configuration, environment values, runtime logs, private paths, or
artifacts; it does not count tokens, truncate context, summarize content,
load a model, start a runtime, call providers, invoke pccx-lab, or touch
KV260 hardware.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.chatContextPolicy.v0"

CHAT_CONTEXT_POLICY_FIELDS = (
    "schemaVersion",
    "contextPolicyId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "contextPolicyState",
    "contextWindowState",
    "budgetState",
    "tokenizationState",
    "promptContentState",
    "transcriptState",
    "summaryState",
    "truncationState",
    "contextAssemblyState",
    "runtimeHandoffState",
    "privacyState",
    "chatComposerRef",
    "chatTranscriptPolicyRef",
    "chatMessageListRef",
    "chatModelStatusRef",
    "contextPolicy",
    "contextSlots",
    "contextControls",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

CONTEXT_POLICY_FIELDS = (
    "state",
    "mode",
    "contextWindowConfigured",
    "tokenBudgetConfigured",
    "tokenizerConfigured",
    "tokenCountingEnabled",
    "promptReadEnabled",
    "transcriptReadEnabled",
    "summaryReadEnabled",
    "truncationEnabled",
    "contextAssemblyEnabled",
    "runtimeHandoffEnabled",
    "sideEffectPolicy",
    "contentPolicy",
)

CONTEXT_SLOT_FIELDS = (
    "slotId",
    "label",
    "state",
    "enabled",
    "sourcePolicy",
    "contentPolicy",
    "blockedReasonRef",
)

CONTEXT_CONTROL_FIELDS = (
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

CHAT_CONTEXT_POLICY_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "empty_not_captured",
    "external_not_configured",
    "inactive",
    "not_configured",
    "not_generated",
    "not_loaded",
    "not_measured",
    "not_started",
    "not_used",
    "planned",
    "requires_evidence",
    "summary_only",
    "target_selected",
    "unavailable",
)


_CHAT_CONTEXT_POLICY = {
    "schemaVersion": SCHEMA_VERSION,
    "contextPolicyId": "chat_context_policy_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "chat-context-policy.gemma3n-e4b-kv260.2026-05-05",
    "lastUpdatedSource": "pccx_launcher_issue_9_chat_context_policy_boundary_2026-05-05",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "contextPolicyState": "blocked",
    "contextWindowState": "not_configured",
    "budgetState": "not_configured",
    "tokenizationState": "blocked",
    "promptContentState": "empty_not_captured",
    "transcriptState": "not_configured",
    "summaryState": "not_generated",
    "truncationState": "disabled",
    "contextAssemblyState": "blocked",
    "runtimeHandoffState": "blocked",
    "privacyState": "summary_only",
    "chatComposerRef": "chat_composer_gemma3n_e4b_kv260_placeholder",
    "chatTranscriptPolicyRef": "chat_transcript_policy_gemma3n_e4b_kv260_placeholder",
    "chatMessageListRef": "chat_message_list_gemma3n_e4b_kv260_placeholder",
    "chatModelStatusRef": "chat_model_status_gemma3n_e4b_kv260_placeholder",
    "contextPolicy": {
        "state": "blocked",
        "mode": "disabled_until_reviewed_context_window_tokenization_and_runtime_boundary_exists",
        "contextWindowConfigured": False,
        "tokenBudgetConfigured": False,
        "tokenizerConfigured": False,
        "tokenCountingEnabled": False,
        "promptReadEnabled": False,
        "transcriptReadEnabled": False,
        "summaryReadEnabled": False,
        "truncationEnabled": False,
        "contextAssemblyEnabled": False,
        "runtimeHandoffEnabled": False,
        "sideEffectPolicy": "local_render_only",
        "contentPolicy": "context metadata only; no prompt, response, transcript, summary, token text, token count, model path, tokenizer path, runtime log, or private path is included",
    },
    "contextSlots": [
        {
            "slotId": "model_context_window",
            "label": "model context window",
            "state": "not_configured",
            "enabled": False,
            "sourcePolicy": "checked target label only; no model descriptor, runtime, config, model path, tokenizer, or asset file is read",
            "contentPolicy": "no context size, token budget, path, or runtime evidence value is included",
            "blockedReasonRef": "context_window_evidence_absent",
        },
        {
            "slotId": "prompt_draft",
            "label": "prompt draft",
            "state": "empty_not_captured",
            "enabled": False,
            "sourcePolicy": "composer boundary remains disabled and does not capture prompt text",
            "contentPolicy": "no prompt content, prompt length, token text, token count, or derived summary is included",
            "blockedReasonRef": "prompt_capture_blocked",
        },
        {
            "slotId": "transcript_history",
            "label": "transcript history",
            "state": "not_configured",
            "enabled": False,
            "sourcePolicy": "transcript and session-store reads are disabled",
            "contentPolicy": "no transcript message bodies, summaries, token counts, or history metadata are included",
            "blockedReasonRef": "transcript_store_blocked",
        },
        {
            "slotId": "generated_summary",
            "label": "generated summary",
            "state": "not_generated",
            "enabled": False,
            "sourcePolicy": "summary generation and summary reads are unavailable",
            "contentPolicy": "no summary text, transcript-derived metadata, or generated content is included",
            "blockedReasonRef": "summarization_boundary_absent",
        },
        {
            "slotId": "assembled_context",
            "label": "assembled runtime context",
            "state": "blocked",
            "enabled": False,
            "sourcePolicy": "context assembly is blocked until prompt, transcript, tokenizer, and runtime handoff boundaries are reviewed",
            "contentPolicy": "no assembled prompt, serialized context, tokenized context, or runtime payload is included",
            "blockedReasonRef": "runtime_handoff_blocked",
        },
    ],
    "contextControls": [
        {
            "controlId": "review_context_policy",
            "label": "review context policy",
            "state": "available_as_data",
            "enabled": False,
            "userAction": "Review checked context-policy metadata in the future chat UI.",
            "launcherAction": "Render deterministic metadata from checked fixtures only.",
            "sideEffectPolicy": "local_render_only",
            "blockedReasonRef": "context_window_evidence_absent",
        },
        {
            "controlId": "measure_prompt_tokens",
            "label": "measure prompt tokens",
            "state": "blocked",
            "enabled": False,
            "userAction": "Measure prompt tokens only after tokenizer and prompt-read boundaries are reviewed.",
            "launcherAction": "Do not read prompts or invoke a tokenizer.",
            "sideEffectPolicy": "no_prompt_read_or_token_count",
            "blockedReasonRef": "tokenizer_boundary_absent",
        },
        {
            "controlId": "read_transcript_context",
            "label": "read transcript context",
            "state": "blocked",
            "enabled": False,
            "userAction": "Use transcript history only after a reviewed session-store and transcript boundary exists.",
            "launcherAction": "Do not read transcript, message, summary, or session-store data.",
            "sideEffectPolicy": "no_transcript_or_store_read",
            "blockedReasonRef": "transcript_store_blocked",
        },
        {
            "controlId": "truncate_context",
            "label": "truncate context",
            "state": "disabled",
            "enabled": False,
            "userAction": "Apply truncation only after context-budget and redaction rules are reviewed.",
            "launcherAction": "Do not truncate, mutate, or persist context data.",
            "sideEffectPolicy": "no_context_mutation",
            "blockedReasonRef": "context_window_evidence_absent",
        },
        {
            "controlId": "generate_context_summary",
            "label": "generate context summary",
            "state": "blocked",
            "enabled": False,
            "userAction": "Generate summaries only after explicit summary and storage boundaries are reviewed.",
            "launcherAction": "Do not generate or read summaries.",
            "sideEffectPolicy": "no_summary_generation",
            "blockedReasonRef": "summarization_boundary_absent",
        },
        {
            "controlId": "handoff_runtime_context",
            "label": "handoff runtime context",
            "state": "blocked",
            "enabled": False,
            "userAction": "Send context to a runtime only after model-load and runtime evidence are reviewed.",
            "launcherAction": "Keep runtime handoff blocked and do not start model execution.",
            "sideEffectPolicy": "no_runtime_handoff",
            "blockedReasonRef": "runtime_handoff_blocked",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "context_window_evidence_absent",
            "state": "requires_evidence",
            "summary": "No reviewed context-window size, budget source, or runtime evidence exists.",
            "requiredBefore": "context_budget_display_enabled",
        },
        {
            "reasonId": "tokenizer_boundary_absent",
            "state": "blocked",
            "summary": "No reviewed tokenizer, token counter, or token redaction boundary exists.",
            "requiredBefore": "token_counting_enabled",
        },
        {
            "reasonId": "prompt_capture_blocked",
            "state": "empty_not_captured",
            "summary": "Prompt capture remains disabled by the composer and send-result boundaries.",
            "requiredBefore": "prompt_context_enabled",
        },
        {
            "reasonId": "transcript_store_blocked",
            "state": "not_configured",
            "summary": "No reviewed transcript/session-store read boundary exists.",
            "requiredBefore": "transcript_context_enabled",
        },
        {
            "reasonId": "summarization_boundary_absent",
            "state": "not_generated",
            "summary": "No reviewed summary generation, summary read, or summary storage boundary exists.",
            "requiredBefore": "summary_context_enabled",
        },
        {
            "reasonId": "runtime_handoff_blocked",
            "state": "blocked",
            "summary": "Runtime context handoff is blocked until model-load and runtime execution evidence exist.",
            "requiredBefore": "runtime_context_handoff_enabled",
        },
    ],
    "handoffRefs": [
        {
            "refId": "chat_composer",
            "schemaVersion": "pccx.chatComposer.v0",
            "fixturePath": "contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Composer metadata keeps prompt capture and send controls blocked.",
        },
        {
            "refId": "chat_transcript_policy",
            "schemaVersion": "pccx.chatTranscriptPolicy.v0",
            "fixturePath": "contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Transcript policy keeps retention, export, and content access disabled.",
        },
        {
            "refId": "chat_message_list",
            "schemaVersion": "pccx.chatMessageList.v0",
            "fixturePath": "contracts/fixtures/chat-message-list.gemma3n-e4b-kv260-placeholder.json",
            "state": "empty_not_captured",
            "summary": "Message-list metadata keeps the viewport empty and message bodies absent.",
        },
        {
            "refId": "chat_model_status",
            "schemaVersion": "pccx.chatModelStatus.v0",
            "fixturePath": "contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json",
            "state": "blocked",
            "summary": "Model status keeps runtime, context, and response rows blocked.",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "contextPolicyDisplayOnly": True,
        "contextMetadataOnly": True,
        "contextWindowConfigured": False,
        "contextWindowSizeIncluded": False,
        "tokenBudgetConfigured": False,
        "tokenBudgetIncluded": False,
        "tokenizerConfigured": False,
        "tokenCountingEnabled": False,
        "tokenCountMeasured": False,
        "tokenContentIncluded": False,
        "tokensIncluded": False,
        "promptCapture": False,
        "promptRead": False,
        "promptContentIncluded": False,
        "promptEchoed": False,
        "responseContentIncluded": False,
        "responseGenerated": False,
        "transcriptContentIncluded": False,
        "readsTranscript": False,
        "transcriptPersistence": False,
        "summaryIncluded": False,
        "summaryGenerated": False,
        "sessionStoreRead": False,
        "contextAssemblyAttempted": False,
        "contextTruncationAttempted": False,
        "modelContextUpdated": False,
        "runtimeHandoffAttempted": False,
        "modelLoadAttempted": False,
        "modelLoaded": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "runtimeStarted": False,
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
        "Data-only chat context-policy fixture; context windows, budgets, tokenization, summaries, and runtime handoff remain disabled.",
        "No prompt, response, transcript, message body, summary, session store, configuration file, environment value, model path, tokenizer path, runtime log, private path, secret, or token is read.",
        "No token count, context-window size, token budget, transcript history, summary text, or runtime payload is included.",
        "No prompt capture, transcript read, token counting, context truncation, context assembly, summary generation, model load, model execution, runtime handoff, telemetry, upload, or artifact write is performed.",
        "No KV260 hardware access, pccx-lab invocation, or systemverilog-ide invocation is performed.",
        "This is not a release, tag, compatibility commitment, marketplace flow, storage layer, tokenizer implementation, context manager, runtime, model-loader, or hardware implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#9",
    ],
}


def create_gemma3n_e4b_kv260_chat_context_policy() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 context-policy fixture."""
    return copy.deepcopy(_CHAT_CONTEXT_POLICY)


def chat_context_policy_json(policy: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        policy if policy is not None else create_gemma3n_e4b_kv260_chat_context_policy(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only chat context-policy JSON.",
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
    sys.stdout.write(chat_context_policy_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
