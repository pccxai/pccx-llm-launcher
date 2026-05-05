#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-review-packet.sh - status chat review-packet tests.
#
# Usage: bash scripts/tests/status-chat-review-packet.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat review packet"
OUTPUT="$("$STUB" --include-chat-review-packet)"
require_contains "$OUTPUT" "=== chat review packet ==="
require_contains "$OUTPUT" "source     : scripts/chat-review-packet-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/session-store/config/model/runtime/hardware/provider/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "review    : blocked"
require_contains "$OUTPUT" "approval  : not_approved"
require_contains "$OUTPUT" "execution : not_started"
require_contains "$OUTPUT" "content   : empty_not_captured"
require_contains "$OUTPUT" "privacy   : requires_review"
require_contains "$OUTPUT" "evidence  : requires_evidence"
PASS "chat review-packet section is present and conservative"

HEAD "2: review sections, required reviews, and blockers are summarized"
require_contains "$OUTPUT" "sections   : surface_and_controls=available_as_data"
require_contains "$OUTPUT" "session_management=blocked"
require_contains "$OUTPUT" "model_runtime_and_device=requires_evidence"
require_contains "$OUTPUT" "content_flow=disabled"
require_contains "$OUTPUT" "privacy_and_local_only_policy=requires_review"
require_contains "$OUTPUT" "aggregate_status=summary_only"
require_contains "$OUTPUT" "reviews    : runtime_evidence_review=requires_evidence:false"
require_contains "$OUTPUT" "model_asset_review=not_approved:false"
require_contains "$OUTPUT" "session_store_review=not_approved:false"
require_contains "$OUTPUT" "content_privacy_review=requires_review:false"
require_contains "$OUTPUT" "send_enablement_review=blocked:false"
require_contains "$OUTPUT" "blocked    : review_packet_not_approved=not_approved"
require_contains "$OUTPUT" "runtime_and_device_evidence_absent=requires_evidence"
require_contains "$OUTPUT" "model_asset_boundary_absent=not_loaded"
require_contains "$OUTPUT" "session_store_boundary_absent=not_configured"
require_contains "$OUTPUT" "content_privacy_boundary_absent=requires_review"
require_contains "$OUTPUT" "refs       : chat_status_summary=summary_only"
require_contains "$OUTPUT" "chat_local_only_policy=blocked"
require_contains "$OUTPUT" "chat_redaction_policy=summary_only"
require_contains "$OUTPUT" "chat_session_store_policy=not_configured"
require_contains "$OUTPUT" "chat_model_load_request=blocked"
require_contains "$OUTPUT" "chat_readiness=blocked"
PASS "review packet gates and references are summarized"

HEAD "3: safety flags stay review-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "reviewPacketOnly=true"
require_contains "$OUTPUT" "aggregatesCheckedFixturesOnly=true"
require_contains "$OUTPUT" "statusSummaryReferencedOnly=true"
require_contains "$OUTPUT" "approvalGranted=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptRead=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "messageBodiesIncluded=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
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
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-review-packet)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat review-packet output changed between runs"
    exit 1
fi
PASS "status chat review-packet output is deterministic"

HEAD "5: chat review-packet option does not combine with pccx-lab backend"
if "$STUB" --include-chat-review-packet --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-review-packet/backend mode to fail"
    exit 1
fi
PASS "chat review-packet remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat review-packet or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-review-packet tests passed\n'
