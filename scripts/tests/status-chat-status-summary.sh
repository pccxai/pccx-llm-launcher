#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-status-summary.sh - status chat summary tests.
#
# Usage: bash scripts/tests/status-chat-status-summary.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat status summary"
OUTPUT="$("$STUB" --include-chat-status-summary)"
require_contains "$OUTPUT" "=== chat status summary ==="
require_contains "$OUTPUT" "source     : scripts/chat-status-summary-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/session-store/config/model/runtime/hardware/provider/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "overall   : blocked"
require_contains "$OUTPUT" "surface   : available_as_data"
require_contains "$OUTPUT" "session   : inactive"
require_contains "$OUTPUT" "modelState: blocked"
require_contains "$OUTPUT" "runtime   : blocked"
require_contains "$OUTPUT" "send      : disabled"
require_contains "$OUTPUT" "content   : empty_not_captured"
require_contains "$OUTPUT" "privacy   : summary_only"
PASS "chat status-summary section is present and conservative"

HEAD "2: aggregate cards and blockers are summarized"
require_contains "$OUTPUT" "cards      : surface_layout=available_as_data:info"
require_contains "$OUTPUT" "session_state=inactive:blocked"
require_contains "$OUTPUT" "model_status=blocked:blocked"
require_contains "$OUTPUT" "readiness=blocked:blocked"
require_contains "$OUTPUT" "composer=available_as_data:info"
require_contains "$OUTPUT" "send_result=disabled:blocked"
require_contains "$OUTPUT" "message_list=empty_not_captured:info"
require_contains "$OUTPUT" "response_stream=disabled:blocked"
require_contains "$OUTPUT" "privacy_controls=summary_only:blocked"
require_contains "$OUTPUT" "blocked    : runtime_evidence_absent=blocked"
require_contains "$OUTPUT" "model_load_absent=blocked"
require_contains "$OUTPUT" "device_session_absent=inactive"
require_contains "$OUTPUT" "session_store_absent=not_configured"
require_contains "$OUTPUT" "content_boundary_absent=requires_review"
require_contains "$OUTPUT" "actions    : review_readiness_data=available_as_data:false"
require_contains "$OUTPUT" "keep_send_disabled=blocked:false"
require_contains "$OUTPUT" "wait_for_runtime_boundary=requires_evidence:false"
PASS "status cards, blockers, and actions are summarized"

HEAD "3: safety flags stay summary-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "statusSummaryOnly=true"
require_contains "$OUTPUT" "aggregatesCheckedFixturesOnly=true"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptRead=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "messageBodiesIncluded=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "configRead=false"
require_contains "$OUTPUT" "environmentRead=false"
require_contains "$OUTPUT" "providerConfigRead=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "sendEnabled=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
require_contains "$OUTPUT" "executesSystemverilogIde=false"
require_contains "$OUTPUT" "releaseOrTagAction=false"
require_contains "$OUTPUT" "settingsChange=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-status-summary)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat status-summary output changed between runs"
    exit 1
fi
PASS "status chat status-summary output is deterministic"

HEAD "5: chat status-summary option does not combine with pccx-lab backend"
if "$STUB" --include-chat-status-summary --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-status-summary/backend mode to fail"
    exit 1
fi
PASS "chat status-summary remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat status-summary or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-status-summary tests passed\n'
