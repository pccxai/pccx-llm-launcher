#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-session-index.sh - status session-index tests.
#
# Usage: bash scripts/tests/status-chat-session-index.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat session index"
OUTPUT="$("$STUB" --include-chat-session-index)"
require_contains "$OUTPUT" "=== chat session index ==="
require_contains "$OUTPUT" "source     : scripts/chat-session-index-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no session-store/transcript/prompt/model/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "index      : not_configured"
require_contains "$OUTPUT" "store      : not_configured"
require_contains "$OUTPUT" "manifest   : unavailable"
require_contains "$OUTPUT" "selection  : disabled"
require_contains "$OUTPUT" "restore    : unavailable"
require_contains "$OUTPUT" "content    : empty_not_captured"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat session index section is present and conservative"

HEAD "2: policy and controls stay local-render only"
require_contains "$OUTPUT" "index-policy : not_configured localStoreConfigured=false manifestReadEnabled=false transcriptReadEnabled=false"
require_contains "$OUTPUT" "empty      : placeholder itemCount=0 displayKind=no_sessions_available"
require_contains "$OUTPUT" "controls   : open_session_index=available_as_data"
require_contains "$OUTPUT" "refresh_session_index=blocked"
require_contains "$OUTPUT" "select_session=disabled"
require_contains "$OUTPUT" "restore_selected_session=unavailable"
require_contains "$OUTPUT" "rename_session=disabled"
require_contains "$OUTPUT" "delete_session=inactive"
require_contains "$OUTPUT" "blocked    : session_store_not_configured=not_configured"
require_contains "$OUTPUT" "session_manifest_boundary_absent=planned"
require_contains "$OUTPUT" "session_titles_not_captured=empty_not_captured"
require_contains "$OUTPUT" "artifact_read_boundary_absent=requires_evidence"
PASS "session index metadata is summarized without store or transcript reads"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "sessionIndexDisplayOnly=true"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "readsSessionManifest=false"
require_contains "$OUTPUT" "readsTranscript=false"
require_contains "$OUTPUT" "sessionPersistence=false"
require_contains "$OUTPUT" "transcriptPersistence=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "messageBodiesIncluded=false"
require_contains "$OUTPUT" "summaryIncluded=false"
require_contains "$OUTPUT" "sessionTitleIncluded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "session-index execution, persistence, and content flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-session-index)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat session index output changed between runs"
    exit 1
fi
PASS "status chat session index output is deterministic"

HEAD "5: session-index option does not combine with pccx-lab backend"
if "$STUB" --include-chat-session-index --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined session-index/backend mode to fail"
    exit 1
fi
PASS "chat session index remains separate from backend execution"

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
PASS "no session-index overclaim or chat content in status output"

printf '\n[DONE]  all status-chat-session-index tests passed\n'
