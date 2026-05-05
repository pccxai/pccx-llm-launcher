#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-clipboard-policy.sh - status clipboard-policy tests.
#
# Usage: bash scripts/tests/status-chat-clipboard-policy.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat clipboard policy"
OUTPUT="$("$STUB" --include-chat-clipboard-policy)"
require_contains "$OUTPUT" "=== chat clipboard policy ==="
require_contains "$OUTPUT" "source     : scripts/chat-clipboard-policy-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no clipboard read/write/paste/copy/import/export/session-store/transcript/message/file/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "policy     : blocked"
require_contains "$OUTPUT" "read       : disabled"
require_contains "$OUTPUT" "write      : disabled"
require_contains "$OUTPUT" "copy       : disabled"
require_contains "$OUTPUT" "paste      : disabled"
require_contains "$OUTPUT" "import     : disabled"
require_contains "$OUTPUT" "export     : disabled"
require_contains "$OUTPUT" "selection  : empty_not_captured"
require_contains "$OUTPUT" "message    : empty_not_captured"
require_contains "$OUTPUT" "transcript : not_started"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat clipboard-policy section is present and conservative"

HEAD "2: surfaces and controls stay disabled"
require_contains "$OUTPUT" "clipboard-policy : blocked mode=disabled_until_reviewed_clipboard_boundary_exists"
require_contains "$OUTPUT" "readEnabled=false"
require_contains "$OUTPUT" "writeEnabled=false"
require_contains "$OUTPUT" "copyEnabled=false"
require_contains "$OUTPUT" "pasteEnabled=false"
require_contains "$OUTPUT" "importEnabled=false"
require_contains "$OUTPUT" "exportEnabled=false"
require_contains "$OUTPUT" "userConsentRequired=true"
require_contains "$OUTPUT" "surfaces   : message_actions=disabled:false"
require_contains "$OUTPUT" "composer_input=blocked:false"
require_contains "$OUTPUT" "attachment_input=disabled:false"
require_contains "$OUTPUT" "transcript_export=not_configured:false"
require_contains "$OUTPUT" "controls   : copy_message=disabled:false"
require_contains "$OUTPUT" "copy_transcript=disabled:false"
require_contains "$OUTPUT" "paste_prompt=disabled:false"
require_contains "$OUTPUT" "paste_attachment=disabled:false"
require_contains "$OUTPUT" "import_clipboard_payload=disabled:false"
require_contains "$OUTPUT" "export_to_clipboard=disabled:false"
require_contains "$OUTPUT" "blocked    : clipboard_api_boundary_absent=blocked"
require_contains "$OUTPUT" "message_content_absent=empty_not_captured"
require_contains "$OUTPUT" "transcript_export_not_reviewed=not_configured"
require_contains "$OUTPUT" "attachment_clipboard_boundary_absent=disabled"
require_contains "$OUTPUT" "privacy_redaction_not_reviewed=not_configured"
PASS "disabled clipboard metadata is summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "clipboardPolicyDisplayOnly=true"
require_contains "$OUTPUT" "clipboardMetadataOnly=true"
require_contains "$OUTPUT" "clipboardRead=false"
require_contains "$OUTPUT" "clipboardWrite=false"
require_contains "$OUTPUT" "clipboardCopy=false"
require_contains "$OUTPUT" "clipboardPaste=false"
require_contains "$OUTPUT" "clipboardImport=false"
require_contains "$OUTPUT" "clipboardExport=false"
require_contains "$OUTPUT" "clipboardAttachmentRead=false"
require_contains "$OUTPUT" "clipboardEventListenerInstalled=false"
require_contains "$OUTPUT" "selectionRead=false"
require_contains "$OUTPUT" "messageBodiesIncluded=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptRead=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "readsTranscript=false"
require_contains "$OUTPUT" "transcriptExport=false"
require_contains "$OUTPUT" "readsSessionStore=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "sessionStoreWrite=false"
require_contains "$OUTPUT" "attachmentReads=false"
require_contains "$OUTPUT" "fileUpload=false"
require_contains "$OUTPUT" "fileImport=false"
require_contains "$OUTPUT" "filePreview=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-clipboard-policy)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat clipboard-policy output changed between runs"
    exit 1
fi
PASS "status chat clipboard-policy output is deterministic"

HEAD "5: chat clipboard-policy option does not combine with pccx-lab backend"
if "$STUB" --include-chat-clipboard-policy --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-clipboard-policy/backend mode to fail"
    exit 1
fi
PASS "chat clipboard-policy remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat clipboard-policy or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-clipboard-policy tests passed\n'
