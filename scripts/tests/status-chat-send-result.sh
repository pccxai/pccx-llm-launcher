#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-send-result.sh - status chat send-result tests.
#
# Usage: bash scripts/tests/status-chat-send-result.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat send result"
OUTPUT="$("$STUB" --include-chat-send-result)"
require_contains "$OUTPUT" "=== chat send result ==="
require_contains "$OUTPUT" "source     : scripts/chat-send-result-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/response/model/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "result     : blocked"
require_contains "$OUTPUT" "attempt    : disabled"
require_contains "$OUTPUT" "prompt     : empty_not_captured"
require_contains "$OUTPUT" "response   : not_generated"
require_contains "$OUTPUT" "runtime    : not_started"
require_contains "$OUTPUT" "model load : not_loaded"
require_contains "$OUTPUT" "session    : inactive"
PASS "chat send-result section is present and conservative"

HEAD "2: result envelope and blocked reasons stay non-executing"
require_contains "$OUTPUT" "envelope   : blocked"
require_contains "$OUTPUT" "inputAccepted=false"
require_contains "$OUTPUT" "sendAttempted=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "blocked    : composer_send_disabled=disabled"
require_contains "$OUTPUT" "readiness_blocked=blocked"
require_contains "$OUTPUT" "runtime_not_started=not_started"
require_contains "$OUTPUT" "model_not_loaded=not_loaded"
require_contains "$OUTPUT" "session_store_not_configured=not_configured"
require_contains "$OUTPUT" "messages   : send_disabled=disabled"
require_contains "$OUTPUT" "response_unavailable=not_generated"
PASS "send result metadata is summarized without response content"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "sendResultDisplayOnly=true"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "attachmentReads=false"
require_contains "$OUTPUT" "fileUpload=false"
require_contains "$OUTPUT" "clipboardRead=false"
require_contains "$OUTPUT" "clipboardWrite=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptEchoed=false"
require_contains "$OUTPUT" "promptPersistence=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelLoaded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-send-result)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat send-result output changed between runs"
    exit 1
fi
PASS "status chat send-result output is deterministic"

HEAD "5: chat send-result option does not combine with pccx-lab backend"
if "$STUB" --include-chat-send-result --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-send-result/backend mode to fail"
    exit 1
fi
PASS "chat send result remains separate from backend execution"

HEAD "6: output avoids known overclaims and prompt echo"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
require_not_contains "$OUTPUT" "hello"
PASS "no chat send-result overclaim or prompt echo in status output"

printf '\n[DONE]  all status-chat-send-result tests passed\n'
