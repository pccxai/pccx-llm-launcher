#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-gap-matrix.sh - status chat gap-matrix tests.
#
# Usage: bash scripts/tests/status-chat-gap-matrix.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat gap matrix"
OUTPUT="$("$STUB" --include-chat-gap-matrix)"
require_contains "$OUTPUT" "=== chat gap matrix ==="
require_contains "$OUTPUT" "source     : scripts/chat-gap-matrix-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/session-store/model/runtime/provider/hardware/lab/IDE/artifact execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "matrix     : available_as_data"
require_contains "$OUTPUT" "standalone : blocked"
require_contains "$OUTPUT" "review    : not_approved"
require_contains "$OUTPUT" "evidence  : requires_evidence"
require_contains "$OUTPUT" "readiness : blocked"
PASS "chat gap-matrix section is present and conservative"

HEAD "2: gaps, dependencies, and exit criteria are summarized"
require_contains "$OUTPUT" "gaps       : runtime_device_evidence=requires_evidence:blocker"
require_contains "$OUTPUT" "model_asset_boundary=not_loaded:blocker"
require_contains "$OUTPUT" "prompt_input_boundary=disabled:blocker"
require_contains "$OUTPUT" "response_generation_boundary=disabled:blocker"
require_contains "$OUTPUT" "session_store_boundary=not_configured:blocker"
require_contains "$OUTPUT" "transcript_export_boundary=disabled:blocker"
require_contains "$OUTPUT" "privacy_content_policy=requires_review:blocker"
require_contains "$OUTPUT" "attachment_clipboard_boundary=disabled:blocker"
require_contains "$OUTPUT" "audit_persistence_boundary=not_configured:blocker"
require_contains "$OUTPUT" "ui_enablement_boundary=blocked:blocker"
require_contains "$OUTPUT" "refs       : chat_review_packet=not_approved"
require_contains "$OUTPUT" "chat_status_summary=summary_only"
require_contains "$OUTPUT" "chat_readiness=blocked"
require_contains "$OUTPUT" "chat_model_load_request=blocked"
require_contains "$OUTPUT" "chat_session_store_policy=not_configured"
require_contains "$OUTPUT" "chat_redaction_policy=summary_only"
require_contains "$OUTPUT" "criteria   : runtime_and_device_evidence_accepted=requires_evidence:false"
require_contains "$OUTPUT" "model_and_session_boundaries_reviewed=not_approved:false"
require_contains "$OUTPUT" "content_privacy_boundaries_reviewed=requires_review:false"
require_contains "$OUTPUT" "blocked    : standalone_chat_not_enabled=blocked"
require_contains "$OUTPUT" "review_packet_not_approved=not_approved"
require_contains "$OUTPUT" "runtime_evidence_absent=requires_evidence"
require_contains "$OUTPUT" "content_paths_disabled=disabled"
PASS "gap matrix blockers and references are summarized"

HEAD "3: safety flags stay data-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "gapMatrixOnly=true"
require_contains "$OUTPUT" "referencesCheckedFixturesOnly=true"
require_contains "$OUTPUT" "reviewPacketReferencedOnly=true"
require_contains "$OUTPUT" "statusSummaryReferencedOnly=true"
require_contains "$OUTPUT" "gapClosed=false"
require_contains "$OUTPUT" "approvalGranted=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptRead=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "promptEchoed=false"
require_contains "$OUTPUT" "inputAccepted=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "responseGenerated=false"
require_contains "$OUTPUT" "responseChunksEmitted=false"
require_contains "$OUTPUT" "tokenCountMeasured=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "messageBodiesIncluded=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "sessionStoreWrite=false"
require_contains "$OUTPUT" "sessionPersistence=false"
require_contains "$OUTPUT" "summaryGenerated=false"
require_contains "$OUTPUT" "transcriptExported=false"
require_contains "$OUTPUT" "clipboardRead=false"
require_contains "$OUTPUT" "clipboardWrite=false"
require_contains "$OUTPUT" "attachmentReads=false"
require_contains "$OUTPUT" "fileMetadataRead=false"
require_contains "$OUTPUT" "fileContentRead=false"
require_contains "$OUTPUT" "directoryScan=false"
require_contains "$OUTPUT" "redactionRulesLoaded=false"
require_contains "$OUTPUT" "contentScan=false"
require_contains "$OUTPUT" "redactionApplied=false"
require_contains "$OUTPUT" "auditLogWritten=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "sendEnabled=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
require_contains "$OUTPUT" "executesSystemverilogIde=false"
require_contains "$OUTPUT" "commandDispatch=false"
require_contains "$OUTPUT" "actionExecution=false"
require_contains "$OUTPUT" "focusChanged=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-gap-matrix)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat gap-matrix output changed between runs"
    exit 1
fi
PASS "status chat gap-matrix output is deterministic"

HEAD "5: chat gap-matrix option does not combine with pccx-lab backend"
if "$STUB" --include-chat-gap-matrix --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-gap-matrix/backend mode to fail"
    exit 1
fi
PASS "chat gap-matrix remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat gap-matrix or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-gap-matrix tests passed\n'
