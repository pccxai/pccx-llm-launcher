#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-context-policy.sh - status context-policy tests.
#
# Usage: bash scripts/tests/status-chat-context-policy.sh [path/to/status-stub.sh]

set -eu

PASS() { printf '[PASS]  %s\n' "$*"; }
FAIL() { printf '[FAIL] %s\n' "$*" >&2; }
HEAD() { printf '\n=== %s ===\n' "$*"; }

STUB="${1:-scripts/status-stub.sh}"

if [ ! -x "$STUB" ]; then
    chmod +x "$STUB"
fi

contains() {
    case "$1" in
        *"$2"*) return 0 ;;
        *) return 1 ;;
    esac
}

require_contains() {
    local output="$1"
    local expected="$2"
    if ! contains "$output" "$expected"; then
        FAIL "expected output to contain: $expected"
        printf '%s\n' "$output" >&2
        exit 1
    fi
}

require_not_contains() {
    local output="$1"
    local forbidden="$2"
    if contains "$output" "$forbidden"; then
        FAIL "output contained forbidden text: $forbidden"
        printf '%s\n' "$output" >&2
        exit 1
    fi
}

HEAD "1: status can include chat context policy"
OUTPUT="$("$STUB" --include-chat-context-policy)"
require_contains "$OUTPUT" "=== chat context policy ==="
require_contains "$OUTPUT" "source     : scripts/chat-context-policy-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/transcript/tokenizer/runtime/model/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "context   : blocked"
require_contains "$OUTPUT" "window    : not_configured"
require_contains "$OUTPUT" "budget    : not_configured"
require_contains "$OUTPUT" "tokens    : blocked"
require_contains "$OUTPUT" "prompt    : empty_not_captured"
require_contains "$OUTPUT" "transcript: not_configured"
require_contains "$OUTPUT" "summary   : not_generated"
require_contains "$OUTPUT" "truncate  : disabled"
require_contains "$OUTPUT" "assembly  : blocked"
require_contains "$OUTPUT" "handoff   : blocked"
PASS "chat context-policy section is present and conservative"

HEAD "2: slots and controls stay disabled"
require_contains "$OUTPUT" "context-policy : blocked mode=disabled_until_reviewed_context_window_tokenization_and_runtime_boundary_exists"
require_contains "$OUTPUT" "contextWindowConfigured=false"
require_contains "$OUTPUT" "tokenBudgetConfigured=false"
require_contains "$OUTPUT" "tokenizerConfigured=false"
require_contains "$OUTPUT" "tokenCountingEnabled=false"
require_contains "$OUTPUT" "promptReadEnabled=false"
require_contains "$OUTPUT" "transcriptReadEnabled=false"
require_contains "$OUTPUT" "summaryReadEnabled=false"
require_contains "$OUTPUT" "truncationEnabled=false"
require_contains "$OUTPUT" "contextAssemblyEnabled=false"
require_contains "$OUTPUT" "runtimeHandoffEnabled=false"
require_contains "$OUTPUT" "slots      : model_context_window=not_configured:false"
require_contains "$OUTPUT" "prompt_draft=empty_not_captured:false"
require_contains "$OUTPUT" "transcript_history=not_configured:false"
require_contains "$OUTPUT" "generated_summary=not_generated:false"
require_contains "$OUTPUT" "assembled_context=blocked:false"
require_contains "$OUTPUT" "controls   : review_context_policy=available_as_data:false"
require_contains "$OUTPUT" "measure_prompt_tokens=blocked:false"
require_contains "$OUTPUT" "read_transcript_context=blocked:false"
require_contains "$OUTPUT" "truncate_context=disabled:false"
require_contains "$OUTPUT" "generate_context_summary=blocked:false"
require_contains "$OUTPUT" "handoff_runtime_context=blocked:false"
require_contains "$OUTPUT" "blocked    : context_window_evidence_absent=requires_evidence"
require_contains "$OUTPUT" "tokenizer_boundary_absent=blocked"
require_contains "$OUTPUT" "prompt_capture_blocked=empty_not_captured"
require_contains "$OUTPUT" "runtime_handoff_blocked=blocked"
PASS "disabled context metadata is summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "contextPolicyDisplayOnly=true"
require_contains "$OUTPUT" "contextMetadataOnly=true"
require_contains "$OUTPUT" "contextWindowConfigured=false"
require_contains "$OUTPUT" "contextWindowSizeIncluded=false"
require_contains "$OUTPUT" "tokenBudgetConfigured=false"
require_contains "$OUTPUT" "tokenBudgetIncluded=false"
require_contains "$OUTPUT" "tokenizerConfigured=false"
require_contains "$OUTPUT" "tokenCountingEnabled=false"
require_contains "$OUTPUT" "tokenCountMeasured=false"
require_contains "$OUTPUT" "tokenContentIncluded=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptRead=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "readsTranscript=false"
require_contains "$OUTPUT" "summaryGenerated=false"
require_contains "$OUTPUT" "contextAssemblyAttempted=false"
require_contains "$OUTPUT" "contextTruncationAttempted=false"
require_contains "$OUTPUT" "runtimeHandoffAttempted=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-context-policy)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat context-policy output changed between runs"
    exit 1
fi
PASS "status chat context-policy output is deterministic"

HEAD "5: chat context-policy option does not combine with pccx-lab backend"
if "$STUB" --include-chat-context-policy --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-context-policy/backend mode to fail"
    exit 1
fi
PASS "chat context policy remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat context-policy or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-context-policy tests passed\n'
