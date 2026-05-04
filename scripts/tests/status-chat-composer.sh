#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-composer.sh - status chat composer summary tests.
#
# Usage: bash scripts/tests/status-chat-composer.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat composer"
OUTPUT="$("$STUB" --include-chat-composer)"
require_contains "$OUTPUT" "=== chat composer ==="
require_contains "$OUTPUT" "source     : scripts/chat-composer-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/provider/model/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "composer   : blocked"
require_contains "$OUTPUT" "input      : empty_not_captured"
require_contains "$OUTPUT" "send       : disabled"
require_contains "$OUTPUT" "attachment : disabled"
require_contains "$OUTPUT" "privacy    : available_as_data"
require_contains "$OUTPUT" "validation : blocked"
PASS "chat composer section is present and conservative"

HEAD "2: composer controls and validation rules stay non-executing"
require_contains "$OUTPUT" "controls   : focus_input=placeholder"
require_contains "$OUTPUT" "attach_context=disabled"
require_contains "$OUTPUT" "send_message=disabled"
require_contains "$OUTPUT" "clear_draft=inactive"
require_contains "$OUTPUT" "rules      : no_prompt_content_in_fixture=available_as_data"
require_contains "$OUTPUT" "runtime_readiness_required=blocked"
require_contains "$OUTPUT" "model_load_required=not_loaded"
require_contains "$OUTPUT" "session_store_required=not_configured"
require_contains "$OUTPUT" "attachment_boundary_required=planned"
require_contains "$OUTPUT" "provider_mode_disabled=not_used"
require_contains "$OUTPUT" "blocked    : send_readiness_blocked=blocked"
require_contains "$OUTPUT" "draft_capture_not_reviewed=not_configured"
require_contains "$OUTPUT" "attachment_boundary_absent=planned"
require_contains "$OUTPUT" "runtime_not_started=not_started"
PASS "composer controls, validation rules, and blocked reasons are summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "composerDisplayOnly=true"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "attachmentReads=false"
require_contains "$OUTPUT" "fileUpload=false"
require_contains "$OUTPUT" "clipboardRead=false"
require_contains "$OUTPUT" "clipboardWrite=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "promptEchoed=false"
require_contains "$OUTPUT" "promptPersistence=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelLoaded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-composer)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat composer output changed between runs"
    exit 1
fi
PASS "status chat composer output is deterministic"

HEAD "5: chat composer option does not combine with pccx-lab backend"
if "$STUB" --include-chat-composer --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-composer/backend mode to fail"
    exit 1
fi
PASS "chat composer remains separate from backend execution"

HEAD "6: output avoids known overclaims and prompt echo"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
require_not_contains "$OUTPUT" "hello"
PASS "no chat composer overclaim or prompt echo in status output"

printf '\n[DONE]  all status-chat-composer tests passed\n'
