#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-local-only-policy.sh - status local-only policy tests.
#
# Usage: bash scripts/tests/status-chat-local-only-policy.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat local-only policy"
OUTPUT="$("$STUB" --include-chat-local-only-policy)"
require_contains "$OUTPUT" "=== chat local-only policy ==="
require_contains "$OUTPUT" "source     : scripts/chat-local-only-policy-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no cloud/provider/network/model/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "policy     : enforced_as_metadata"
require_contains "$OUTPUT" "local      : blocked"
require_contains "$OUTPUT" "cloud      : no_external_dependency"
require_contains "$OUTPUT" "provider   : not_used"
require_contains "$OUTPUT" "network    : not_used"
require_contains "$OUTPUT" "offline    : available_as_data"
require_contains "$OUTPUT" "fallback   : disabled"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat local-only policy section is present and conservative"

HEAD "2: controls and dependency checks block external fallback"
require_contains "$OUTPUT" "controls   : local_only_mode_indicator=available_as_data"
require_contains "$OUTPUT" "cloud_provider_selector=disabled"
require_contains "$OUTPUT" "cloud_fallback_control=disabled"
require_contains "$OUTPUT" "offline_policy_banner=summary_only"
require_contains "$OUTPUT" "checks     : core_chat_requires_cloud=no_external_dependency"
require_contains "$OUTPUT" "provider_configuration_present=not_used"
require_contains "$OUTPUT" "network_access_required=not_used"
require_contains "$OUTPUT" "cloud_fallback_enabled=disabled"
require_contains "$OUTPUT" "local_runtime_evidence=blocked"
require_contains "$OUTPUT" "local_model_loaded=not_loaded"
require_contains "$OUTPUT" "blocked    : local_runtime_not_started=not_started"
require_contains "$OUTPUT" "model_not_loaded=not_loaded"
require_contains "$OUTPUT" "provider_calls_blocked=disabled"
require_contains "$OUTPUT" "network_calls_blocked=disabled"
require_contains "$OUTPUT" "cloud_fallback_blocked=disabled"
PASS "local-only policy metadata blocks provider, network, and fallback paths"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "localOnlyPolicyDisplayOnly=true"
require_contains "$OUTPUT" "cloudDependency=false"
require_contains "$OUTPUT" "cloudFallbackEnabled=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerConfigRead=false"
require_contains "$OUTPUT" "environmentRead=false"
require_contains "$OUTPUT" "secretsRead=false"
require_contains "$OUTPUT" "tokensRead=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "executesPccxLab=false"
require_contains "$OUTPUT" "executesSystemverilogIde=false"
PASS "local-only policy execution, provider, persistence, and content flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-local-only-policy)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat local-only policy output changed between runs"
    exit 1
fi
PASS "status chat local-only policy output is deterministic"

HEAD "5: local-only policy option does not combine with pccx-lab backend"
if "$STUB" --include-chat-local-only-policy --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined local-only/backend mode to fail"
    exit 1
fi
PASS "chat local-only policy remains separate from backend execution"

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
require_not_contains "$OUTPUT" "api_key"
require_not_contains "$OUTPUT" "authorization:"
PASS "no local-only policy overclaim, credential, or chat content in status output"

printf '\n[DONE]  all status-chat-local-only-policy tests passed\n'
