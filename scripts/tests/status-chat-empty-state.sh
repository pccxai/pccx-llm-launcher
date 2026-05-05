#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-empty-state.sh - status empty-state tests.
#
# Usage: bash scripts/tests/status-chat-empty-state.sh [path/to/status-stub.sh]

set -eu

PASS() { printf '[PASS]  %s\n' "$*"; }
FAIL() { printf '[FAIL]  %s\n' "$*" >&2; }
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

HEAD "1: status can include chat empty state"
OUTPUT="$("$STUB" --include-chat-empty-state)"
require_contains "$OUTPUT" "=== chat empty state ==="
require_contains "$OUTPUT" "source     : scripts/chat-empty-state-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/response/transcript/session-store/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "empty      : available_as_data"
require_contains "$OUTPUT" "surface    : placeholder"
require_contains "$OUTPUT" "session    : inactive"
require_contains "$OUTPUT" "modelstate : not_loaded"
require_contains "$OUTPUT" "readiness  : blocked"
require_contains "$OUTPUT" "prompt     : empty_not_captured"
require_contains "$OUTPUT" "transcript : empty_not_captured"
require_contains "$OUTPUT" "actions    : disabled"
require_contains "$OUTPUT" "runtime    : not_started"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat empty-state section is present and conservative"

HEAD "2: slots and hints stay display-only"
require_contains "$OUTPUT" "empty-policy : available_as_data renderMode=future_local_chat_empty_state sideEffectPolicy=local_render_only"
require_contains "$OUTPUT" "slots      : target_banner=target_selected:true"
require_contains "$OUTPUT" "empty_transcript_notice=empty_not_captured:true"
require_contains "$OUTPUT" "readiness_notice=blocked:true"
require_contains "$OUTPUT" "composer_disabled_notice=disabled:true"
require_contains "$OUTPUT" "local_only_notice=summary_only:true"
require_contains "$OUTPUT" "hints      : start_new_session_hint=disabled:false"
require_contains "$OUTPUT" "select_model_hint=blocked:false"
require_contains "$OUTPUT" "review_readiness_hint=available_as_data:false"
require_contains "$OUTPUT" "focus_composer_hint=disabled:false"
require_contains "$OUTPUT" "blocked    : runtime_evidence_absent=blocked"
require_contains "$OUTPUT" "model_asset_boundary_absent=not_configured"
require_contains "$OUTPUT" "session_store_not_configured=not_configured"
require_contains "$OUTPUT" "prompt_capture_blocked=empty_not_captured"
require_contains "$OUTPUT" "action_execution_disabled=disabled"
PASS "empty-state metadata is summarized without actions or content"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "emptyStateDisplayOnly=true"
require_contains "$OUTPUT" "emptyStateTextOnly=true"
require_contains "$OUTPUT" "localRenderOnly=true"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptRead=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "inputAccepted=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "messageContentIncluded=false"
require_contains "$OUTPUT" "sessionTitleIncluded=false"
require_contains "$OUTPUT" "summaryIncluded=false"
require_contains "$OUTPUT" "readsSessionStore=false"
require_contains "$OUTPUT" "writesSessionStore=false"
require_contains "$OUTPUT" "actionExecution=false"
require_contains "$OUTPUT" "commandDispatch=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "empty-state execution, persistence, and content flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-empty-state)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat empty-state output changed between runs"
    exit 1
fi
PASS "status chat empty-state output is deterministic"

HEAD "5: empty-state option does not combine with pccx-lab backend"
if "$STUB" --include-chat-empty-state --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-empty-state/backend mode to fail"
    exit 1
fi
PASS "chat empty state remains separate from backend execution"

HEAD "6: output avoids known overclaims and chat content"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
require_not_contains "$OUTPUT" "hello"
require_not_contains "$OUTPUT" "assistant response:"
require_not_contains "$OUTPUT" "session title:"
PASS "no empty-state overclaim or chat content in status output"

printf '\n[DONE]  all status-chat-empty-state tests passed\n'
