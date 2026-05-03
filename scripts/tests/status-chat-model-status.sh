#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-model-status.sh - status chat model summary tests.
#
# Usage: bash scripts/tests/status-chat-model-status.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat model status"
OUTPUT="$("$STUB" --include-chat-model-status)"
require_contains "$OUTPUT" "=== chat model status ==="
require_contains "$OUTPUT" "source     : scripts/chat-model-status-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no model load/provider/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "display    : blocked"
require_contains "$OUTPUT" "descriptor : available_as_data"
require_contains "$OUTPUT" "assets     : external_not_configured"
require_contains "$OUTPUT" "load       : blocked"
require_contains "$OUTPUT" "runtime    : not_started"
require_contains "$OUTPUT" "context    : unavailable"
require_contains "$OUTPUT" "response   : unavailable"
require_contains "$OUTPUT" "provider   : not_used"
PASS "chat model status section is present and conservative"

HEAD "2: rows and actions stay blocked or non-executing"
require_contains "$OUTPUT" "rows       : model_descriptor=available_as_data"
require_contains "$OUTPUT" "model_assets=external_not_configured"
require_contains "$OUTPUT" "runtime_readiness=blocked"
require_contains "$OUTPUT" "device_session=inactive"
require_contains "$OUTPUT" "load_operation=disabled"
require_contains "$OUTPUT" "chat_context=unavailable"
require_contains "$OUTPUT" "assistant_response=unavailable"
require_contains "$OUTPUT" "actions    : select_model_target=target_selected"
require_contains "$OUTPUT" "configure_model_assets=blocked"
require_contains "$OUTPUT" "load_model=disabled"
require_contains "$OUTPUT" "refresh_status=available_as_data"
PASS "model-status rows and actions are summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "statusDisplayOnly=true"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelLoaded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "modelAssetPathsIncluded=false"
require_contains "$OUTPUT" "modelWeightPathsIncluded=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-model-status)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat model output changed between runs"
    exit 1
fi
PASS "status chat model output is deterministic"

HEAD "5: chat model option does not combine with pccx-lab backend"
if "$STUB" --include-chat-model-status --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-model/backend mode to fail"
    exit 1
fi
PASS "chat model status remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat model or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-model-status tests passed\n'
