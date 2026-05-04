#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-response-stream.sh - status response stream tests.
#
# Usage: bash scripts/tests/status-chat-response-stream.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat response stream"
OUTPUT="$("$STUB" --include-chat-response-stream)"
require_contains "$OUTPUT" "=== chat response stream ==="
require_contains "$OUTPUT" "source     : scripts/chat-response-stream-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/response stream/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "stream     : blocked"
require_contains "$OUTPUT" "response   : not_generated"
require_contains "$OUTPUT" "transport  : not_started"
require_contains "$OUTPUT" "tokens     : unavailable"
require_contains "$OUTPUT" "progress   : disabled"
require_contains "$OUTPUT" "cancel     : disabled"
PASS "chat response stream section is present and conservative"

HEAD "2: envelope and display slots stay blocked"
require_contains "$OUTPUT" "envelope   : blocked streamStarted=false transportOpened=false chunksEmitted=false tokenContentIncluded=false responseContentIncluded=false tokenCount=none stopSignalSent=false"
require_contains "$OUTPUT" "phases     : wait_for_send_result=blocked"
require_contains "$OUTPUT" "open_stream_transport=not_started"
require_contains "$OUTPUT" "emit_response_chunks=not_generated"
require_contains "$OUTPUT" "complete_stream=unavailable"
require_contains "$OUTPUT" "slots      : assistant_response_placeholder=available_as_data"
require_contains "$OUTPUT" "stream_progress_indicator=disabled"
require_contains "$OUTPUT" "token_counter=unavailable"
require_contains "$OUTPUT" "stop_generation_control=disabled"
require_contains "$OUTPUT" "blocked    : send_result_blocked=blocked"
require_contains "$OUTPUT" "runtime_not_started=not_started"
require_contains "$OUTPUT" "model_not_loaded=not_loaded"
require_contains "$OUTPUT" "session_inactive=inactive"
require_contains "$OUTPUT" "transcript_policy_disabled=disabled"
PASS "response stream display metadata is summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "responseStreamDisplayOnly=true"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "responseChunksEmitted=false"
require_contains "$OUTPUT" "tokenContentIncluded=false"
require_contains "$OUTPUT" "tokenCountMeasured=false"
require_contains "$OUTPUT" "streamStarted=false"
require_contains "$OUTPUT" "streamTransportOpened=false"
require_contains "$OUTPUT" "streamCancellationAttempted=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-response-stream)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat response stream output changed between runs"
    exit 1
fi
PASS "status chat response stream output is deterministic"

HEAD "5: chat response stream option does not combine with pccx-lab backend"
if "$STUB" --include-chat-response-stream --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-response-stream/backend mode to fail"
    exit 1
fi
PASS "chat response stream remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat response stream or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-response-stream tests passed\n'
