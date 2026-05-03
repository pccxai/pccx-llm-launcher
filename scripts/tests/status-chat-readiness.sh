#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-readiness.sh - status chat readiness summary tests.
#
# Usage: bash scripts/tests/status-chat-readiness.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat readiness"
OUTPUT="$("$STUB" --include-chat-readiness)"
require_contains "$OUTPUT" "=== chat readiness ==="
require_contains "$OUTPUT" "source     : scripts/chat-readiness-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/model/provider/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "overall    : blocked"
require_contains "$OUTPUT" "input      : available_as_data"
require_contains "$OUTPUT" "send       : disabled"
require_contains "$OUTPUT" "recovery   : requires_evidence"
require_contains "$OUTPUT" "evidence   : blocked"
PASS "chat readiness section is present and conservative"

HEAD "2: readiness checks and recovery actions stay non-executing"
require_contains "$OUTPUT" "checks     : chat_surface_fixture=available_as_data"
require_contains "$OUTPUT" "model_target=target_selected"
require_contains "$OUTPUT" "model_assets=external_not_configured"
require_contains "$OUTPUT" "runtime_readiness=blocked"
require_contains "$OUTPUT" "device_session=inactive"
require_contains "$OUTPUT" "chat_runtime=not_started"
require_contains "$OUTPUT" "session_store=not_configured"
require_contains "$OUTPUT" "provider_mode=not_used"
require_contains "$OUTPUT" "errors     : runtime_not_ready=blocked"
require_contains "$OUTPUT" "model_assets_missing=external_not_configured"
require_contains "$OUTPUT" "device_session_absent=inactive"
require_contains "$OUTPUT" "chat_runtime_absent=not_started"
require_contains "$OUTPUT" "session_store_absent=not_configured"
require_contains "$OUTPUT" "actions    : review_runtime_readiness=available_as_data"
require_contains "$OUTPUT" "configure_model_assets_future=blocked"
require_contains "$OUTPUT" "review_device_session_status=available_as_data"
require_contains "$OUTPUT" "wait_for_runtime_boundary=requires_evidence"
require_contains "$OUTPUT" "review_session_store_policy=planned"
PASS "readiness checks, errors, and actions are summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "readinessDisplayOnly=true"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "sessionPersistence=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelLoaded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "opensSerialPort=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "sshExecution=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-readiness)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat readiness output changed between runs"
    exit 1
fi
PASS "status chat readiness output is deterministic"

HEAD "5: chat readiness option does not combine with pccx-lab backend"
if "$STUB" --include-chat-readiness --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-readiness/backend mode to fail"
    exit 1
fi
PASS "chat readiness remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat readiness or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-readiness tests passed\n'
