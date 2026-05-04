#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-session-store-policy.sh - status session-store policy tests.
#
# Usage: bash scripts/tests/status-chat-session-store-policy.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat session-store policy"
OUTPUT="$("$STUB" --include-chat-session-store-policy)"
require_contains "$OUTPUT" "=== chat session store policy ==="
require_contains "$OUTPUT" "source     : scripts/chat-session-store-policy-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no config/path/manifest/session-store/transcript/title/prompt/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "policy     : blocked"
require_contains "$OUTPUT" "store      : not_configured"
require_contains "$OUTPUT" "path       : not_configured"
require_contains "$OUTPUT" "manifest   : not_configured"
require_contains "$OUTPUT" "read       : blocked"
require_contains "$OUTPUT" "write      : disabled"
require_contains "$OUTPUT" "delete     : disabled"
require_contains "$OUTPUT" "retention  : not_configured"
require_contains "$OUTPUT" "migration  : disabled"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat session-store policy section is present and conservative"

HEAD "2: policy, surfaces, and controls stay disabled"
require_contains "$OUTPUT" "session-store-policy : blocked mode=disabled_until_reviewed_local_session_store_boundary_exists"
require_contains "$OUTPUT" "storeConfigured=false"
require_contains "$OUTPUT" "storePathConfigured=false"
require_contains "$OUTPUT" "manifestSchemaConfigured=false"
require_contains "$OUTPUT" "readEnabled=false"
require_contains "$OUTPUT" "writeEnabled=false"
require_contains "$OUTPUT" "deleteEnabled=false"
require_contains "$OUTPUT" "retentionEnabled=false"
require_contains "$OUTPUT" "migrationEnabled=false"
require_contains "$OUTPUT" "surfaces   : local_store_path=not_configured:false"
require_contains "$OUTPUT" "session_manifest=not_configured:false"
require_contains "$OUTPUT" "session_record=blocked:false"
require_contains "$OUTPUT" "title_record=blocked:false"
require_contains "$OUTPUT" "transcript_record=disabled:false"
require_contains "$OUTPUT" "retention_rule=not_configured:false"
require_contains "$OUTPUT" "controls   : configure_store=disabled:false"
require_contains "$OUTPUT" "read_store_path=blocked:false"
require_contains "$OUTPUT" "read_manifest=blocked:false"
require_contains "$OUTPUT" "read_session_record=blocked:false"
require_contains "$OUTPUT" "write_session_record=disabled:false"
require_contains "$OUTPUT" "delete_session_record=disabled:false"
require_contains "$OUTPUT" "migrate_store=disabled:false"
require_contains "$OUTPUT" "persist_store_policy=disabled:false"
PASS "session-store policy metadata is summarized without store reads"

HEAD "3: blocked reasons stay explicit"
require_contains "$OUTPUT" "blocked    : store_not_configured=not_configured"
require_contains "$OUTPUT" "store_path_boundary_absent=planned"
require_contains "$OUTPUT" "manifest_schema_absent=not_configured"
require_contains "$OUTPUT" "session_store_read_boundary_absent=blocked"
require_contains "$OUTPUT" "session_store_write_boundary_absent=disabled"
require_contains "$OUTPUT" "deletion_retention_policy_absent=requires_evidence"
require_contains "$OUTPUT" "migration_policy_absent=not_configured"
require_contains "$OUTPUT" "redaction_policy_absent=planned"
PASS "session-store blockers remain visible"

HEAD "4: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "sessionStorePolicyDisplayOnly=true"
require_contains "$OUTPUT" "storeMetadataOnly=true"
require_contains "$OUTPUT" "storeConfigured=false"
require_contains "$OUTPUT" "storePathConfigured=false"
require_contains "$OUTPUT" "storePathIncluded=false"
require_contains "$OUTPUT" "configRead=false"
require_contains "$OUTPUT" "configWrite=false"
require_contains "$OUTPUT" "readsSessionStore=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "sessionStoreWrite=false"
require_contains "$OUTPUT" "readsSessionManifest=false"
require_contains "$OUTPUT" "manifestContentIncluded=false"
require_contains "$OUTPUT" "sessionRecordIncluded=false"
require_contains "$OUTPUT" "sessionPersistence=false"
require_contains "$OUTPUT" "sessionDeletion=false"
require_contains "$OUTPUT" "retentionPolicyActive=false"
require_contains "$OUTPUT" "migrationAttempted=false"
require_contains "$OUTPUT" "readsSessionTitle=false"
require_contains "$OUTPUT" "sessionTitleIncluded=false"
require_contains "$OUTPUT" "readsTranscript=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution, store read/write, and persistence flags remain false"

HEAD "5: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-session-store-policy)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat session-store policy output changed between runs"
    exit 1
fi
PASS "status chat session-store policy output is deterministic"

HEAD "6: chat session-store policy option does not combine with pccx-lab backend"
if "$STUB" --include-chat-session-store-policy --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-session-store-policy/backend mode to fail"
    exit 1
fi
PASS "chat session-store policy remains separate from backend execution"

HEAD "7: output avoids known overclaims and content"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
require_not_contains "$OUTPUT" "hello"
require_not_contains "$OUTPUT" "assistant response:"
require_not_contains "$OUTPUT" "session title:"
PASS "no session-store policy overclaim or content in status output"

printf '\n[DONE]  all status-chat-session-store-policy tests passed\n'
