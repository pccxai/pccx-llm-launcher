#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-redaction-policy.sh - status redaction-policy tests.
#
# Usage: bash scripts/tests/status-chat-redaction-policy.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat redaction policy"
OUTPUT="$("$STUB" --include-chat-redaction-policy)"
require_contains "$OUTPUT" "=== chat redaction policy ==="
require_contains "$OUTPUT" "source     : scripts/chat-redaction-policy-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no redaction rule load/content scan/PII detection/secret detection/prompt/message/transcript/clipboard/file/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "policy     : blocked"
require_contains "$OUTPUT" "scan       : disabled"
require_contains "$OUTPUT" "prompt    : disabled"
require_contains "$OUTPUT" "response  : disabled"
require_contains "$OUTPUT" "transcript: not_configured"
require_contains "$OUTPUT" "message   : empty_not_captured"
require_contains "$OUTPUT" "attachment: blocked"
require_contains "$OUTPUT" "clipboard : disabled"
require_contains "$OUTPUT" "audit     : blocked"
require_contains "$OUTPUT" "pii       : disabled"
require_contains "$OUTPUT" "secrets   : disabled"
require_contains "$OUTPUT" "persistence: disabled"
require_contains "$OUTPUT" "privacy   : summary_only"
PASS "chat redaction-policy section is present and conservative"

HEAD "2: surfaces and controls stay disabled"
require_contains "$OUTPUT" "redaction-policy : blocked mode=disabled_until_reviewed_redaction_rules_and_content_boundaries_exist"
require_contains "$OUTPUT" "scannerEnabled=false"
require_contains "$OUTPUT" "promptRedactionEnabled=false"
require_contains "$OUTPUT" "responseRedactionEnabled=false"
require_contains "$OUTPUT" "transcriptRedactionEnabled=false"
require_contains "$OUTPUT" "messageRedactionEnabled=false"
require_contains "$OUTPUT" "attachmentRedactionEnabled=false"
require_contains "$OUTPUT" "clipboardRedactionEnabled=false"
require_contains "$OUTPUT" "auditRedactionEnabled=false"
require_contains "$OUTPUT" "piiDetectionEnabled=false"
require_contains "$OUTPUT" "secretDetectionEnabled=false"
require_contains "$OUTPUT" "persistenceEnabled=false"
require_contains "$OUTPUT" "surfaces   : composer_prompt=blocked:false"
require_contains "$OUTPUT" "assistant_response=disabled:false"
require_contains "$OUTPUT" "message_list=empty_not_captured:false"
require_contains "$OUTPUT" "transcript_export=not_configured:false"
require_contains "$OUTPUT" "attachment_payload=blocked:false"
require_contains "$OUTPUT" "clipboard_payload=disabled:false"
require_contains "$OUTPUT" "audit_event=blocked:false"
require_contains "$OUTPUT" "controls   : review_redaction_rules=not_configured:false"
require_contains "$OUTPUT" "scan_prompt_content=disabled:false"
require_contains "$OUTPUT" "scan_response_content=disabled:false"
require_contains "$OUTPUT" "scan_transcript_content=not_configured:false"
require_contains "$OUTPUT" "detect_sensitive_content=disabled:false"
require_contains "$OUTPUT" "redact_attachment_payload=blocked:false"
require_contains "$OUTPUT" "redact_clipboard_payload=disabled:false"
require_contains "$OUTPUT" "persist_redaction_result=disabled:false"
require_contains "$OUTPUT" "blocked    : redaction_rules_absent=not_configured"
require_contains "$OUTPUT" "content_boundary_absent=blocked"
require_contains "$OUTPUT" "transcript_policy_not_reviewed=not_configured"
require_contains "$OUTPUT" "scanner_not_reviewed=requires_review"
require_contains "$OUTPUT" "persistence_not_configured=disabled"
PASS "disabled redaction metadata is summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "redactionPolicyDisplayOnly=true"
require_contains "$OUTPUT" "redactionMetadataOnly=true"
require_contains "$OUTPUT" "redactionRulesLoaded=false"
require_contains "$OUTPUT" "redactionRulesPersisted=false"
require_contains "$OUTPUT" "contentScan=false"
require_contains "$OUTPUT" "piiDetection=false"
require_contains "$OUTPUT" "secretDetection=false"
require_contains "$OUTPUT" "identifierDetection=false"
require_contains "$OUTPUT" "promptRedaction=false"
require_contains "$OUTPUT" "responseRedaction=false"
require_contains "$OUTPUT" "transcriptRedaction=false"
require_contains "$OUTPUT" "messageRedaction=false"
require_contains "$OUTPUT" "attachmentRedaction=false"
require_contains "$OUTPUT" "clipboardRedaction=false"
require_contains "$OUTPUT" "auditRedaction=false"
require_contains "$OUTPUT" "redactionApplied=false"
require_contains "$OUTPUT" "redactionResultPersisted=false"
require_contains "$OUTPUT" "redactionReportGenerated=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptRead=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "messageBodiesIncluded=false"
require_contains "$OUTPUT" "readsTranscript=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "clipboardRead=false"
require_contains "$OUTPUT" "clipboardWrite=false"
require_contains "$OUTPUT" "attachmentReads=false"
require_contains "$OUTPUT" "fileMetadataRead=false"
require_contains "$OUTPUT" "fileContentRead=false"
require_contains "$OUTPUT" "directoryScan=false"
require_contains "$OUTPUT" "fileImport=false"
require_contains "$OUTPUT" "fileUpload=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
require_contains "$OUTPUT" "executesSystemverilogIde=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-redaction-policy)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat redaction-policy output changed between runs"
    exit 1
fi
PASS "status chat redaction-policy output is deterministic"

HEAD "5: chat redaction-policy option does not combine with pccx-lab backend"
if "$STUB" --include-chat-redaction-policy --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-redaction-policy/backend mode to fail"
    exit 1
fi
PASS "chat redaction-policy remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat redaction-policy or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-redaction-policy tests passed\n'
