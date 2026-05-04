#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-error-taxonomy.sh - status error taxonomy tests.
#
# Usage: bash scripts/tests/status-chat-error-taxonomy.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat error taxonomy"
OUTPUT="$("$STUB" --include-chat-error-taxonomy)"
require_contains "$OUTPUT" "=== chat error taxonomy ==="
require_contains "$OUTPUT" "source     : scripts/chat-error-taxonomy-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/provider/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "taxonomy   : available_as_data"
require_contains "$OUTPUT" "display    : summary_only"
require_contains "$OUTPUT" "input      : unavailable"
require_contains "$OUTPUT" "runtime    : not_started"
PASS "chat error taxonomy section is present and conservative"

HEAD "2: groups, items, and actions stay display-only"
require_contains "$OUTPUT" "groups     : readiness_blockers=blocked"
require_contains "$OUTPUT" "model_and_runtime_blockers=requires_evidence"
require_contains "$OUTPUT" "session_and_policy_blockers=not_configured"
require_contains "$OUTPUT" "items      : send_disabled_by_readiness=blocked"
require_contains "$OUTPUT" "model_assets_not_configured=external_not_configured"
require_contains "$OUTPUT" "runtime_not_started=not_started"
require_contains "$OUTPUT" "session_store_not_configured=not_configured"
require_contains "$OUTPUT" "provider_paths_not_used=not_used"
require_contains "$OUTPUT" "actions    : review_chat_readiness=available_as_data"
require_contains "$OUTPUT" "wait_for_asset_boundary=requires_evidence"
require_contains "$OUTPUT" "wait_for_runtime_boundary=requires_evidence"
require_contains "$OUTPUT" "review_session_policy=planned"
require_contains "$OUTPUT" "review_local_only_policy=available_as_data"
PASS "error groups, items, and actions are summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "taxonomyDisplayOnly=true"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "configRead=false"
require_contains "$OUTPUT" "providerConfigRead=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-error-taxonomy)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat error taxonomy output changed between runs"
    exit 1
fi
PASS "status chat error taxonomy output is deterministic"

HEAD "5: chat error taxonomy option does not combine with pccx-lab backend"
if "$STUB" --include-chat-error-taxonomy --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-error-taxonomy/backend mode to fail"
    exit 1
fi
PASS "chat error taxonomy remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat error taxonomy or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-error-taxonomy tests passed\n'
