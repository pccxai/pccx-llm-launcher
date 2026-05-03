#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-session.sh - status chat/session summary tests.
#
# Usage: bash scripts/tests/status-chat-session.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat/session state"
OUTPUT="$("$STUB" --include-chat-session)"
require_contains "$OUTPUT" "=== chat/session status ==="
require_contains "$OUTPUT" "source     : scripts/chat-session-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/model/provider/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "surface    : blocked"
require_contains "$OUTPUT" "chat       : inactive"
require_contains "$OUTPUT" "input      : ready_for_inputs"
require_contains "$OUTPUT" "send       : disabled"
require_contains "$OUTPUT" "model load : not_loaded"
require_contains "$OUTPUT" "transcript : not_started"
require_contains "$OUTPUT" "response   : unavailable"
PASS "chat/session section is present and conservative"

HEAD "2: controls stay disabled or non-executing"
require_contains "$OUTPUT" "controls   : new_session=placeholder"
require_contains "$OUTPUT" "model_status=not_loaded"
require_contains "$OUTPUT" "send_message=disabled"
require_contains "$OUTPUT" "clear_session=inactive"
require_contains "$OUTPUT" "export_summary=blocked"
PASS "chat/session controls are summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "modelLoaded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "transcriptPersistence=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-session)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat/session output changed between runs"
    exit 1
fi
PASS "status chat/session output is deterministic"

HEAD "5: chat/session option does not combine with pccx-lab backend"
if "$STUB" --include-chat-session --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-session/backend mode to fail"
    exit 1
fi
PASS "chat/session status remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat/session or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-session tests passed\n'
