#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-attachment-policy.sh - status attachment-policy tests.
#
# Usage: bash scripts/tests/status-chat-attachment-policy.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat attachment policy"
OUTPUT="$("$STUB" --include-chat-attachment-policy)"
require_contains "$OUTPUT" "=== chat attachment policy ==="
require_contains "$OUTPUT" "source     : scripts/chat-attachment-policy-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no file picker/file metadata/file content/upload/import/clipboard/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "policy     : blocked"
require_contains "$OUTPUT" "attachment : disabled"
require_contains "$OUTPUT" "file picker: disabled"
require_contains "$OUTPUT" "file read  : blocked"
require_contains "$OUTPUT" "upload     : disabled"
require_contains "$OUTPUT" "import     : disabled"
require_contains "$OUTPUT" "preview    : disabled"
require_contains "$OUTPUT" "persistence: disabled"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat attachment-policy section is present and conservative"

HEAD "2: policy, inputs, and controls stay disabled"
require_contains "$OUTPUT" "attachment-policy : blocked mode=disabled_until_reviewed_local_input_boundary_exists"
require_contains "$OUTPUT" "maxAttachmentCount=0"
require_contains "$OUTPUT" "filePickerEnabled=false"
require_contains "$OUTPUT" "fileMetadataReadEnabled=false"
require_contains "$OUTPUT" "fileContentReadEnabled=false"
require_contains "$OUTPUT" "uploadEnabled=false"
require_contains "$OUTPUT" "importEnabled=false"
require_contains "$OUTPUT" "previewEnabled=false"
require_contains "$OUTPUT" "persistenceEnabled=false"
require_contains "$OUTPUT" "inputs     : local_file=blocked:false"
require_contains "$OUTPUT" "local_directory=blocked:false"
require_contains "$OUTPUT" "clipboard_payload=disabled:false"
require_contains "$OUTPUT" "generated_artifact=blocked:false"
require_contains "$OUTPUT" "transcript_export=disabled:false"
require_contains "$OUTPUT" "controls   : open_file_picker=disabled:false"
require_contains "$OUTPUT" "read_file_metadata=blocked:false"
require_contains "$OUTPUT" "read_file_content=blocked:false"
require_contains "$OUTPUT" "import_attachment=disabled:false"
require_contains "$OUTPUT" "upload_attachment=disabled:false"
require_contains "$OUTPUT" "preview_attachment=disabled:false"
require_contains "$OUTPUT" "persist_attachment=disabled:false"
PASS "attachment policy metadata is summarized without file reads"

HEAD "3: blocked reasons stay explicit"
require_contains "$OUTPUT" "blocked    : attachment_runtime_not_reviewed=blocked"
require_contains "$OUTPUT" "file_picker_boundary_absent=planned"
require_contains "$OUTPUT" "metadata_read_boundary_absent=planned"
require_contains "$OUTPUT" "file_content_read_boundary_absent=planned"
require_contains "$OUTPUT" "import_export_boundary_absent=not_configured"
require_contains "$OUTPUT" "attachment_persistence_boundary_absent=requires_evidence"
require_contains "$OUTPUT" "local_only_upload_block=disabled"
require_contains "$OUTPUT" "clipboard_boundary_absent=not_configured"
PASS "attachment blockers remain visible"

HEAD "4: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "attachmentPolicyDisplayOnly=true"
require_contains "$OUTPUT" "attachmentMetadataOnly=true"
require_contains "$OUTPUT" "attachmentsEnabled=false"
require_contains "$OUTPUT" "filePickerOpened=false"
require_contains "$OUTPUT" "fileMetadataRead=false"
require_contains "$OUTPUT" "fileContentRead=false"
require_contains "$OUTPUT" "fileNameIncluded=false"
require_contains "$OUTPUT" "filePathIncluded=false"
require_contains "$OUTPUT" "fileBytesIncluded=false"
require_contains "$OUTPUT" "directoryScan=false"
require_contains "$OUTPUT" "attachmentReads=false"
require_contains "$OUTPUT" "attachmentPersistence=false"
require_contains "$OUTPUT" "fileUpload=false"
require_contains "$OUTPUT" "fileImport=false"
require_contains "$OUTPUT" "filePreview=false"
require_contains "$OUTPUT" "clipboardRead=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "readsTranscript=false"
require_contains "$OUTPUT" "transcriptExport=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution, read, upload, and persistence flags remain false"

HEAD "5: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-attachment-policy)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat attachment-policy output changed between runs"
    exit 1
fi
PASS "status chat attachment-policy output is deterministic"

HEAD "6: chat attachment-policy option does not combine with pccx-lab backend"
if "$STUB" --include-chat-attachment-policy --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-attachment-policy/backend mode to fail"
    exit 1
fi
PASS "chat attachment policy remains separate from backend execution"

HEAD "7: output avoids known overclaims and content"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
require_not_contains "$OUTPUT" "hello"
require_not_contains "$OUTPUT" "assistant response:"
require_not_contains "$OUTPUT" "attachment:"
PASS "no attachment-policy overclaim or content in status output"

printf '\n[DONE]  all status-chat-attachment-policy tests passed\n'
