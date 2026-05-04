#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-transcript-policy.sh - status transcript tests.
#
# Usage: bash scripts/tests/status-chat-transcript-policy.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat transcript policy"
OUTPUT="$("$STUB" --include-chat-transcript-policy)"
require_contains "$OUTPUT" "=== chat transcript policy ==="
require_contains "$OUTPUT" "source     : scripts/chat-transcript-policy-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/response/transcript content/model/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "transcript : disabled"
require_contains "$OUTPUT" "message    : empty_not_captured"
require_contains "$OUTPUT" "retention  : not_configured"
require_contains "$OUTPUT" "export     : disabled"
require_contains "$OUTPUT" "storage    : not_configured"
require_contains "$OUTPUT" "privacy    : available_as_data"
PASS "chat transcript policy section is present and conservative"

HEAD "2: retention, export, and blocked reasons stay non-persistent"
require_contains "$OUTPUT" "retention-policy : not_configured localStoreConfigured=false sessionPersistence=false transcriptPersistence=false retentionDays=none"
require_contains "$OUTPUT" "content-policy   : empty_not_captured contentIncluded=false promptContentIncluded=false responseContentIncluded=false messageBodiesIncluded=false summaryIncluded=false"
require_contains "$OUTPUT" "export-policy    : disabled exportEnabled=false summaryExportState=blocked contentExportState=unavailable formats=none"
require_contains "$OUTPUT" "blocked    : session_store_not_configured=not_configured"
require_contains "$OUTPUT" "prompt_capture_disabled=disabled"
require_contains "$OUTPUT" "response_generation_absent=not_generated"
require_contains "$OUTPUT" "redaction_export_rule_missing=planned"
PASS "transcript policy metadata is summarized without message content"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "transcriptPolicyDisplayOnly=true"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "attachmentReads=false"
require_contains "$OUTPUT" "fileUpload=false"
require_contains "$OUTPUT" "clipboardRead=false"
require_contains "$OUTPUT" "clipboardWrite=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "promptEchoed=false"
require_contains "$OUTPUT" "promptPersistence=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "messageBodiesIncluded=false"
require_contains "$OUTPUT" "summaryGenerated=false"
require_contains "$OUTPUT" "transcriptPersistence=false"
require_contains "$OUTPUT" "transcriptExport=false"
require_contains "$OUTPUT" "localStoreConfigured=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution and persistence flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-transcript-policy)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat transcript policy output changed between runs"
    exit 1
fi
PASS "status chat transcript policy output is deterministic"

HEAD "5: transcript policy option does not combine with pccx-lab backend"
if "$STUB" --include-chat-transcript-policy --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined transcript-policy/backend mode to fail"
    exit 1
fi
PASS "chat transcript policy remains separate from backend execution"

HEAD "6: output avoids known overclaims and prompt/response content"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
require_not_contains "$OUTPUT" "hello"
require_not_contains "$OUTPUT" "assistant response:"
PASS "no transcript policy overclaim or chat content in status output"

printf '\n[DONE]  all status-chat-transcript-policy tests passed\n'
