#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-message-list.sh - status message-list tests.
#
# Usage: bash scripts/tests/status-chat-message-list.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat message list"
OUTPUT="$("$STUB" --include-chat-message-list)"
require_contains "$OUTPUT" "=== chat message list ==="
require_contains "$OUTPUT" "source     : scripts/chat-message-list-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no message bodies/transcript/session-store/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "list       : empty_not_captured"
require_contains "$OUTPUT" "viewport   : placeholder"
require_contains "$OUTPUT" "transcript : not_started"
require_contains "$OUTPUT" "content    : empty_not_captured"
require_contains "$OUTPUT" "empty      : available_as_data"
require_contains "$OUTPUT" "selection  : disabled"
require_contains "$OUTPUT" "scroll     : disabled"
PASS "chat message-list section is present and conservative"

HEAD "2: collection and slots stay empty"
require_contains "$OUTPUT" "collection : empty itemCount=0 promptMessagesIncluded=false assistantMessagesIncluded=false systemNoticesIncluded=false messageBodiesIncluded=false transcriptReadEnabled=false"
require_contains "$OUTPUT" "slots      : empty_conversation_notice=available_as_data"
require_contains "$OUTPUT" "assistant_response_placeholder=blocked"
require_contains "$OUTPUT" "send_feedback_placeholder=blocked"
require_contains "$OUTPUT" "transcript_policy_notice=disabled"
require_contains "$OUTPUT" "blocked    : session_inactive=inactive"
require_contains "$OUTPUT" "transcript_source_not_configured=not_configured"
require_contains "$OUTPUT" "send_result_blocked=blocked"
require_contains "$OUTPUT" "response_stream_blocked=blocked"
require_contains "$OUTPUT" "message_content_policy_disabled=disabled"
PASS "empty message-list metadata is summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "messageListDisplayOnly=true"
require_contains "$OUTPUT" "messageMetadataOnly=true"
require_contains "$OUTPUT" "readsSessionStore=false"
require_contains "$OUTPUT" "readsTranscript=false"
require_contains "$OUTPUT" "messageBodiesIncluded=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "sendAttempted=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-message-list)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat message-list output changed between runs"
    exit 1
fi
PASS "status chat message-list output is deterministic"

HEAD "5: chat message-list option does not combine with pccx-lab backend"
if "$STUB" --include-chat-message-list --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-message-list/backend mode to fail"
    exit 1
fi
PASS "chat message-list remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat message-list or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-message-list tests passed\n'
