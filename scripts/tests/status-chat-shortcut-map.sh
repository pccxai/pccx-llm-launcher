#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-shortcut-map.sh - status shortcut-map tests.
#
# Usage: bash scripts/tests/status-chat-shortcut-map.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat shortcut map"
OUTPUT="$("$STUB" --include-chat-shortcut-map)"
require_contains "$OUTPUT" "=== chat shortcut map ==="
require_contains "$OUTPUT" "source     : scripts/chat-shortcut-map-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no keyboard listener/command dispatch/session-store/transcript/clipboard/file/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "shortcuts  : blocked"
require_contains "$OUTPUT" "focus      : inactive"
require_contains "$OUTPUT" "keyboard   : not_installed"
require_contains "$OUTPUT" "dispatch   : blocked"
require_contains "$OUTPUT" "execution  : not_invoked"
PASS "chat shortcut-map section is present and conservative"

HEAD "2: scopes and bindings stay disabled"
require_contains "$OUTPUT" "scopes     : global_chat_shell=blocked"
require_contains "$OUTPUT" "composer_focus=inactive"
require_contains "$OUTPUT" "message_list=empty_not_captured"
require_contains "$OUTPUT" "action_bar=disabled"
require_contains "$OUTPUT" "bindings   : focus_composer=inactive:false"
require_contains "$OUTPUT" "submit_message=blocked:false"
require_contains "$OUTPUT" "stop_response=disabled:false"
require_contains "$OUTPUT" "copy_response=disabled:false"
require_contains "$OUTPUT" "new_chat=blocked:false"
require_contains "$OUTPUT" "clear_conversation=disabled:false"
require_contains "$OUTPUT" "export_transcript=disabled:false"
require_contains "$OUTPUT" "attach_context=planned:false"
require_contains "$OUTPUT" "next_message=empty_not_captured:false"
require_contains "$OUTPUT" "previous_message=empty_not_captured:false"
require_contains "$OUTPUT" "blocked    : keyboard_listener_not_installed=not_installed"
require_contains "$OUTPUT" "send_boundary_blocked=blocked"
require_contains "$OUTPUT" "message_list_empty=empty_not_captured"
PASS "disabled shortcut metadata is summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "shortcutMapDisplayOnly=true"
require_contains "$OUTPUT" "shortcutMetadataOnly=true"
require_contains "$OUTPUT" "keyboardListenerInstalled=false"
require_contains "$OUTPUT" "keyboardCaptureEnabled=false"
require_contains "$OUTPUT" "commandDispatchEnabled=false"
require_contains "$OUTPUT" "shortcutExecuted=false"
require_contains "$OUTPUT" "focusChanged=false"
require_contains "$OUTPUT" "readsSessionStore=false"
require_contains "$OUTPUT" "readsTranscript=false"
require_contains "$OUTPUT" "readsMessages=false"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "sendAttempted=false"
require_contains "$OUTPUT" "stopSignalSent=false"
require_contains "$OUTPUT" "clipboardWrite=false"
require_contains "$OUTPUT" "attachmentReads=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-shortcut-map)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat shortcut-map output changed between runs"
    exit 1
fi
PASS "status chat shortcut-map output is deterministic"

HEAD "5: chat shortcut-map option does not combine with pccx-lab backend"
if "$STUB" --include-chat-shortcut-map --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-shortcut-map/backend mode to fail"
    exit 1
fi
PASS "chat shortcut map remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no chat shortcut-map or throughput overclaim in status output"

printf '\n[DONE]  all status-chat-shortcut-map tests passed\n'
