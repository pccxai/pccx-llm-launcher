#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-session-title-policy.sh - status title-policy tests.
#
# Usage: bash scripts/tests/status-chat-session-title-policy.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat session title policy"
OUTPUT="$("$STUB" --include-chat-session-title-policy)"
require_contains "$OUTPUT" "=== chat session title policy ==="
require_contains "$OUTPUT" "source     : scripts/chat-session-title-policy-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no session-store/title/transcript/prompt/model/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "title      : available_as_data"
require_contains "$OUTPUT" "source     : not_configured"
require_contains "$OUTPUT" "display    : placeholder"
require_contains "$OUTPUT" "generation : blocked"
require_contains "$OUTPUT" "rename     : disabled"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat session title policy section is present and conservative"

HEAD "2: policy and controls stay display-only"
require_contains "$OUTPUT" "title-policy : available_as_data displayMode=placeholder_only titleReadEnabled=false titleGenerationEnabled=false titleRenameEnabled=false titlePersistenceEnabled=false summaryReadEnabled=false"
require_contains "$OUTPUT" "placeholder : placeholder displayKind=static_placeholder_label contentIncluded=false"
require_contains "$OUTPUT" "controls   : render_placeholder_title=available_as_data"
require_contains "$OUTPUT" "read_stored_title=blocked"
require_contains "$OUTPUT" "generate_title=blocked"
require_contains "$OUTPUT" "rename_title=disabled"
require_contains "$OUTPUT" "persist_title=disabled"
require_contains "$OUTPUT" "blocked    : session_store_not_configured=not_configured"
require_contains "$OUTPUT" "session_title_read_boundary_absent=planned"
require_contains "$OUTPUT" "title_generation_not_reviewed=blocked"
require_contains "$OUTPUT" "rename_write_boundary_absent=requires_evidence"
PASS "title policy metadata is summarized without title, store, or transcript reads"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "sessionTitlePolicyDisplayOnly=true"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "readsSessionManifest=false"
require_contains "$OUTPUT" "readsSessionTitle=false"
require_contains "$OUTPUT" "readsTranscript=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "titleContentIncluded=false"
require_contains "$OUTPUT" "sessionTitleIncluded=false"
require_contains "$OUTPUT" "sessionTitleGenerated=false"
require_contains "$OUTPUT" "titleRenameImplemented=false"
require_contains "$OUTPUT" "titlePersistence=false"
require_contains "$OUTPUT" "summaryIncluded=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "title-policy execution, persistence, and content flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-session-title-policy)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat session title policy output changed between runs"
    exit 1
fi
PASS "status chat session title policy output is deterministic"

HEAD "5: title-policy option does not combine with pccx-lab backend"
if "$STUB" --include-chat-session-title-policy --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined title-policy/backend mode to fail"
    exit 1
fi
PASS "chat session title policy remains separate from backend execution"

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
PASS "no title-policy overclaim or chat content in status output"

printf '\n[DONE]  all status-chat-session-title-policy tests passed\n'
