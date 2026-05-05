#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-accessibility.sh - status accessibility tests.
#
# Usage: bash scripts/tests/status-chat-accessibility.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat accessibility"
OUTPUT="$("$STUB" --include-chat-accessibility)"
require_contains "$OUTPUT" "=== chat accessibility ==="
require_contains "$OUTPUT" "source     : scripts/chat-accessibility-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no prompt/response/transcript/session-store/focus-change/keyboard-capture/model/runtime/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "access     : available_as_data"
require_contains "$OUTPUT" "surface    : placeholder"
require_contains "$OUTPUT" "semantic   : planned"
require_contains "$OUTPUT" "announce   : disabled"
require_contains "$OUTPUT" "focus      : inactive"
require_contains "$OUTPUT" "contrast   : requires_review"
require_contains "$OUTPUT" "motion     : requires_review"
require_contains "$OUTPUT" "input      : disabled"
require_contains "$OUTPUT" "runtime    : not_started"
PASS "chat accessibility section is present and conservative"

HEAD "2: landmarks, labels, and review gates stay metadata-only"
require_contains "$OUTPUT" "access-policy : planned renderMode=future_local_chat_accessibility_metadata sideEffectPolicy=local_render_only"
require_contains "$OUTPUT" "landmarks  : chat_shell=placeholder:false"
require_contains "$OUTPUT" "model_status_header=blocked:false"
require_contains "$OUTPUT" "conversation_region=empty_not_captured:false"
require_contains "$OUTPUT" "composer_region=disabled:false"
require_contains "$OUTPUT" "bindings   : surface_landmark_label=available_as_data:false"
require_contains "$OUTPUT" "readiness_status_label=blocked:false"
require_contains "$OUTPUT" "transcript_region_label=empty_not_captured:false"
require_contains "$OUTPUT" "composer_disabled_label=disabled:false"
require_contains "$OUTPUT" "focus-order: status_header_order=blocked:false:1"
require_contains "$OUTPUT" "conversation_region_order=empty_not_captured:false:3"
require_contains "$OUTPUT" "action_bar_order=disabled:false:5"
require_contains "$OUTPUT" "gates      : semantic_labels_reviewed=requires_review:false"
require_contains "$OUTPUT" "contrast_tokens_reviewed=requires_review:false"
require_contains "$OUTPUT" "live_region_behavior_reviewed=disabled:false"
require_contains "$OUTPUT" "keyboard_path_reviewed=blocked:false"
require_contains "$OUTPUT" "blocked    : focus_manager_not_installed=not_installed"
require_contains "$OUTPUT" "live_regions_disabled=disabled"
require_contains "$OUTPUT" "contrast_review_missing=requires_review"
require_contains "$OUTPUT" "content_boundaries_blocked=blocked"
PASS "accessibility metadata is summarized without UI execution"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "accessibilityMetadataOnly=true"
require_contains "$OUTPUT" "semanticLabelsOnly=true"
require_contains "$OUTPUT" "localRenderOnly=true"
require_contains "$OUTPUT" "promptCapture=false"
require_contains "$OUTPUT" "promptRead=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "messageContentIncluded=false"
require_contains "$OUTPUT" "readsSessionStore=false"
require_contains "$OUTPUT" "keyboardListenerInstalled=false"
require_contains "$OUTPUT" "keyboardCapture=false"
require_contains "$OUTPUT" "commandDispatch=false"
require_contains "$OUTPUT" "focusChanged=false"
require_contains "$OUTPUT" "liveRegionUpdated=false"
require_contains "$OUTPUT" "screenReaderEventEmitted=false"
require_contains "$OUTPUT" "contrastMeasured=false"
require_contains "$OUTPUT" "motionPreferenceRead=false"
require_contains "$OUTPUT" "themeRead=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "accessibility execution, input, and runtime flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-accessibility)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat accessibility output changed between runs"
    exit 1
fi
PASS "status chat accessibility output is deterministic"

HEAD "5: accessibility option does not combine with pccx-lab backend"
if "$STUB" --include-chat-accessibility --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-accessibility/backend mode to fail"
    exit 1
fi
PASS "chat accessibility remains separate from backend execution"

HEAD "6: output avoids known overclaims and chat content"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
require_not_contains "$OUTPUT" "hello"
require_not_contains "$OUTPUT" "assistant response:"
require_not_contains "$OUTPUT" "session title:"
PASS "no accessibility overclaim or chat content in status output"

printf '\n[DONE]  all status-chat-accessibility tests passed\n'
