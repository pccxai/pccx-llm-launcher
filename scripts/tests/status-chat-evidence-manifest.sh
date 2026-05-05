#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-evidence-manifest.sh - status chat evidence manifest tests.
#
# Usage: bash scripts/tests/status-chat-evidence-manifest.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat evidence manifest"
OUTPUT="$("$STUB" --include-chat-evidence-manifest)"
require_contains "$OUTPUT" "=== chat evidence manifest ==="
require_contains "$OUTPUT" "source     : scripts/chat-evidence-manifest-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/session-store/artifact/model/runtime/provider/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "manifest  : available_as_data"
require_contains "$OUTPUT" "review    : not_approved"
require_contains "$OUTPUT" "gap       : blocked"
require_contains "$OUTPUT" "evidence  : requires_evidence"
require_contains "$OUTPUT" "artifact  : unavailable"
PASS "chat evidence-manifest section is present and conservative"

HEAD "2: references, review links, and actions are summarized"
require_contains "$OUTPUT" "refs       : runtime_readiness=requires_evidence"
require_contains "$OUTPUT" "device_session_status=requires_evidence"
require_contains "$OUTPUT" "chat_review_packet=not_approved"
require_contains "$OUTPUT" "chat_gap_matrix=blocked"
require_contains "$OUTPUT" "chat_status_summary=summary_only"
require_contains "$OUTPUT" "chat_redaction_policy=summary_only"
require_contains "$OUTPUT" "chat_clipboard_policy=requires_review"
require_contains "$OUTPUT" "chat_accessibility=requires_review"
require_contains "$OUTPUT" "links      : review_packet_gate=not_approved"
require_contains "$OUTPUT" "gap_matrix_gate=blocked"
require_contains "$OUTPUT" "runtime_evidence_gate=requires_evidence"
require_contains "$OUTPUT" "accessibility_review_gate=requires_review"
require_contains "$OUTPUT" "clipboard_policy_gate=requires_review"
require_contains "$OUTPUT" "blocked    : runtime_evidence_absent=requires_evidence"
require_contains "$OUTPUT" "review_not_approved=not_approved"
require_contains "$OUTPUT" "artifact_evidence_not_read=unavailable"
require_contains "$OUTPUT" "standalone_chat_still_blocked=blocked"
require_contains "$OUTPUT" "accessibility_review_pending=requires_review"
require_contains "$OUTPUT" "clipboard_review_pending=requires_review"
require_contains "$OUTPUT" "actions    : collect_runtime_evidence=disabled:false"
require_contains "$OUTPUT" "review_manifest_refs=requires_review:false"
require_contains "$OUTPUT" "keep_chat_blocked=blocked:false"
require_contains "$OUTPUT" "review_accessibility_metadata=requires_review:false"
require_contains "$OUTPUT" "review_clipboard_policy=requires_review:false"
PASS "evidence manifest references and blocked actions are summarized"

HEAD "3: safety flags stay data-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "evidenceManifestOnly=true"
require_contains "$OUTPUT" "referencesCheckedFixturesOnly=true"
require_contains "$OUTPUT" "reviewPacketReferencedOnly=true"
require_contains "$OUTPUT" "gapMatrixReferencedOnly=true"
require_contains "$OUTPUT" "statusSummaryReferencedOnly=true"
require_contains "$OUTPUT" "evidenceAccepted=false"
require_contains "$OUTPUT" "gapClosed=false"
require_contains "$OUTPUT" "approvalGranted=false"
require_contains "$OUTPUT" "artifactRead=false"
require_contains "$OUTPUT" "artifactWrite=false"
require_contains "$OUTPUT" "rawLogRead=false"
require_contains "$OUTPUT" "hardwareDumpRead=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptRead=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "messageBodiesIncluded=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "sendEnabled=false"
require_contains "$OUTPUT" "clipboardRead=false"
require_contains "$OUTPUT" "attachmentReads=false"
require_contains "$OUTPUT" "fileMetadataRead=false"
require_contains "$OUTPUT" "fileContentRead=false"
require_contains "$OUTPUT" "directoryScan=false"
require_contains "$OUTPUT" "redactionRulesLoaded=false"
require_contains "$OUTPUT" "contentScan=false"
require_contains "$OUTPUT" "redactionApplied=false"
require_contains "$OUTPUT" "auditLogWritten=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
require_contains "$OUTPUT" "executesSystemverilogIde=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-evidence-manifest)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat evidence-manifest output changed between runs"
    exit 1
fi
PASS "status chat evidence-manifest output is deterministic"

HEAD "5: chat evidence-manifest option does not combine with pccx-lab backend"
if "$STUB" --include-chat-evidence-manifest --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-evidence-manifest/backend mode to fail"
    exit 1
fi
PASS "chat evidence manifest remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat evidence-manifest or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-evidence-manifest tests passed\n'
