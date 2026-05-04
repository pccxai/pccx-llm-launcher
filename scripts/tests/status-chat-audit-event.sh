#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-audit-event.sh - status audit-event tests.
#
# Usage: bash scripts/tests/status-chat-audit-event.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat audit-event"
OUTPUT="$("$STUB" --include-chat-audit-event)"
require_contains "$OUTPUT" "=== chat audit event ==="
require_contains "$OUTPUT" "source     : scripts/chat-audit-event-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/response/transcript content/model/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "audit      : available_as_data"
require_contains "$OUTPUT" "event      : blocked"
require_contains "$OUTPUT" "logging    : not_configured"
require_contains "$OUTPUT" "kind       : blocked_chat_send"
require_contains "$OUTPUT" "outcome    : blocked"
require_contains "$OUTPUT" "content    : empty_not_captured"
require_contains "$OUTPUT" "persistence: disabled"
require_contains "$OUTPUT" "storage    : not_configured"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat audit-event section is present and conservative"

HEAD "2: event envelope and redaction stay content-free"
require_contains "$OUTPUT" "envelope   : blocked targetIncluded=true sessionRefIncluded=true actorIdentifierIncluded=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "runtimeStarted=false"
require_contains "$OUTPUT" "modelLoaded=false"
require_contains "$OUTPUT" "writeAttempted=false"
require_contains "$OUTPUT" "redaction  : summary_only"
require_contains "$OUTPUT" "actorIdentifiersIncluded=false"
require_contains "$OUTPUT" "privatePathsIncluded=false"
require_contains "$OUTPUT" "secretsIncluded=false"
require_contains "$OUTPUT" "tokensIncluded=false"
require_contains "$OUTPUT" "rawLogsIncluded=false"
require_contains "$OUTPUT" "hardwareDumpsIncluded=false"
require_contains "$OUTPUT" "generatedBlobsIncluded=false"
require_contains "$OUTPUT" "modelPathsIncluded=false"
PASS "audit-event metadata is summarized without prompt/response/transcript content"

HEAD "3: audit fields and blocked reasons remain metadata only"
require_contains "$OUTPUT" "fields     : audit_event_id=placeholder"
require_contains "$OUTPUT" "event_kind=available_as_data"
require_contains "$OUTPUT" "target_identity=target_selected"
require_contains "$OUTPUT" "prompt_content=empty_not_captured"
require_contains "$OUTPUT" "response_content=not_generated"
require_contains "$OUTPUT" "transcript_content=disabled"
require_contains "$OUTPUT" "actor_identifier=redacted"
require_contains "$OUTPUT" "runtime_trace=not_started"
require_contains "$OUTPUT" "artifact_path=not_configured"
require_contains "$OUTPUT" "blocked    : audit_logger_not_configured=not_configured"
require_contains "$OUTPUT" "prompt_capture_disabled=disabled"
require_contains "$OUTPUT" "response_generation_absent=not_generated"
require_contains "$OUTPUT" "transcript_persistence_disabled=disabled"
require_contains "$OUTPUT" "runtime_not_started=not_started"
require_contains "$OUTPUT" "local_store_not_configured=not_configured"
PASS "audit-event field and blocked reason summaries are bounded"

HEAD "4: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "auditEventDisplayOnly=true"
require_contains "$OUTPUT" "auditLoggerImplemented=false"
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
require_contains "$OUTPUT" "inputAccepted=false"
require_contains "$OUTPUT" "sendAttempted=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "transcriptPersistence=false"
require_contains "$OUTPUT" "transcriptExport=false"
require_contains "$OUTPUT" "messageBodiesIncluded=false"
require_contains "$OUTPUT" "summaryGenerated=false"
require_contains "$OUTPUT" "auditEventPersisted=false"
require_contains "$OUTPUT" "localStoreConfigured=false"
require_contains "$OUTPUT" "eventTimestampRecorded=false"
require_contains "$OUTPUT" "actorIdentifierIncluded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution, logging, and persistence flags remain false"

HEAD "5: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-audit-event)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat audit-event output changed between runs"
    exit 1
fi
PASS "status chat audit-event output is deterministic"

HEAD "6: audit-event option does not combine with pccx-lab backend"
if "$STUB" --include-chat-audit-event --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined audit-event/backend mode to fail"
    exit 1
fi
PASS "chat audit-event remains separate from backend execution"

HEAD "7: output avoids known overclaims and prompt/response content"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
require_not_contains "$OUTPUT" "hello"
require_not_contains "$OUTPUT" "assistant response:"
PASS "no audit-event overclaim or chat content in status output"

printf '\n[DONE]  all status-chat-audit-event tests passed\n'
