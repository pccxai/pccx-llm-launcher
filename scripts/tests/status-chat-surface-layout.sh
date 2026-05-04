#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-surface-layout.sh - status surface-layout tests.
#
# Usage: bash scripts/tests/status-chat-surface-layout.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat surface layout"
OUTPUT="$("$STUB" --include-chat-surface-layout)"
require_contains "$OUTPUT" "=== chat surface layout ==="
require_contains "$OUTPUT" "source     : scripts/chat-surface-layout-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/response/transcript/session-store/model/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "layout     : blocked"
require_contains "$OUTPUT" "shell      : placeholder"
require_contains "$OUTPUT" "navigation : available_as_data"
require_contains "$OUTPUT" "primary    : empty_not_captured"
require_contains "$OUTPUT" "side       : placeholder"
require_contains "$OUTPUT" "footer     : available_as_data"
require_contains "$OUTPUT" "content    : empty_not_captured"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat surface layout section is present and conservative"

HEAD "2: regions and navigation stay local metadata"
require_contains "$OUTPUT" "layout-policy : placeholder renderMode=future_local_shell_layout sideEffectPolicy=local_render_only"
require_contains "$OUTPUT" "regions    : session_index_sidebar=placeholder"
require_contains "$OUTPUT" "model_status_header=blocked"
require_contains "$OUTPUT" "transcript_region=empty_not_captured"
require_contains "$OUTPUT" "composer_bar=disabled"
require_contains "$OUTPUT" "audit_footer=summary_only"
require_contains "$OUTPUT" "nav        : open_chat_surface=available_as_data"
require_contains "$OUTPUT" "open_session_index=available_as_data"
require_contains "$OUTPUT" "open_model_status=blocked"
require_contains "$OUTPUT" "focus_composer=disabled"
require_contains "$OUTPUT" "blocked    : runtime_readiness_blocked=blocked"
require_contains "$OUTPUT" "chat_runtime_not_started=not_started"
require_contains "$OUTPUT" "composer_send_disabled=disabled"
require_contains "$OUTPUT" "transcript_content_absent=empty_not_captured"
PASS "surface layout metadata is summarized without content or runtime actions"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "surfaceLayoutDisplayOnly=true"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "sessionTitleIncluded=false"
require_contains "$OUTPUT" "summaryIncluded=false"
require_contains "$OUTPUT" "inputAccepted=false"
require_contains "$OUTPUT" "sendAttempted=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "surface-layout execution, persistence, and content flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-surface-layout)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat surface layout output changed between runs"
    exit 1
fi
PASS "status chat surface layout output is deterministic"

HEAD "5: surface-layout option does not combine with pccx-lab backend"
if "$STUB" --include-chat-surface-layout --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined surface-layout/backend mode to fail"
    exit 1
fi
PASS "chat surface layout remains separate from backend execution"

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
PASS "no surface-layout overclaim or chat content in status output"

printf '\n[DONE]  all status-chat-surface-layout tests passed\n'
