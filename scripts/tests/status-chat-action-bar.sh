#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-action-bar.sh - status action-bar tests.
#
# Usage: bash scripts/tests/status-chat-action-bar.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat action bar"
OUTPUT="$("$STUB" --include-chat-action-bar)"
require_contains "$OUTPUT" "=== chat action bar ==="
require_contains "$OUTPUT" "source     : scripts/chat-action-bar-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no action execution/session-store/transcript/clipboard/file/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "actions    : blocked"
require_contains "$OUTPUT" "conversation: inactive"
require_contains "$OUTPUT" "selection  : disabled"
require_contains "$OUTPUT" "transcript : not_started"
require_contains "$OUTPUT" "response   : not_generated"
require_contains "$OUTPUT" "attachment : disabled"
require_contains "$OUTPUT" "clipboard  : disabled"
require_contains "$OUTPUT" "export     : disabled"
require_contains "$OUTPUT" "stop       : disabled"
PASS "chat action-bar section is present and conservative"

HEAD "2: groups and controls stay disabled"
require_contains "$OUTPUT" "groups     : conversation_actions=blocked"
require_contains "$OUTPUT" "message_actions=disabled"
require_contains "$OUTPUT" "transcript_actions=not_configured"
require_contains "$OUTPUT" "runtime_actions=not_started"
require_contains "$OUTPUT" "attachment_actions=planned"
require_contains "$OUTPUT" "controls   : new_chat=blocked:false"
require_contains "$OUTPUT" "clear_conversation=disabled:false"
require_contains "$OUTPUT" "export_transcript=disabled:false"
require_contains "$OUTPUT" "retry_response=blocked:false"
require_contains "$OUTPUT" "copy_response=disabled:false"
require_contains "$OUTPUT" "stop_response=disabled:false"
require_contains "$OUTPUT" "attach_context=disabled:false"
require_contains "$OUTPUT" "blocked    : session_lifecycle_not_enabled=blocked"
require_contains "$OUTPUT" "transcript_store_not_configured=not_configured"
require_contains "$OUTPUT" "transcript_export_not_reviewed=not_configured"
require_contains "$OUTPUT" "message_content_absent=empty_not_captured"
require_contains "$OUTPUT" "response_stream_blocked=blocked"
require_contains "$OUTPUT" "runtime_stream_not_started=not_started"
require_contains "$OUTPUT" "attachment_boundary_absent=planned"
PASS "disabled action-bar metadata is summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "actionBarDisplayOnly=true"
require_contains "$OUTPUT" "actionMetadataOnly=true"
require_contains "$OUTPUT" "readsSessionStore=false"
require_contains "$OUTPUT" "readsTranscript=false"
require_contains "$OUTPUT" "transcriptExport=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "sessionStoreWrite=false"
require_contains "$OUTPUT" "conversationCreated=false"
require_contains "$OUTPUT" "conversationCleared=false"
require_contains "$OUTPUT" "attachmentReads=false"
require_contains "$OUTPUT" "fileUpload=false"
require_contains "$OUTPUT" "clipboardWrite=false"
require_contains "$OUTPUT" "sendAttempted=false"
require_contains "$OUTPUT" "retryAttempted=false"
require_contains "$OUTPUT" "stopSignalSent=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-action-bar)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat action-bar output changed between runs"
    exit 1
fi
PASS "status chat action-bar output is deterministic"

HEAD "5: chat action-bar option does not combine with pccx-lab backend"
if "$STUB" --include-chat-action-bar --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-action-bar/backend mode to fail"
    exit 1
fi
PASS "chat action-bar remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat action-bar or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-action-bar tests passed\n'
