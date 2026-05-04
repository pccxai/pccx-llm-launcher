#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-preferences.sh - status chat preferences tests.
#
# Usage: bash scripts/tests/status-chat-preferences.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat preferences"
OUTPUT="$("$STUB" --include-chat-preferences)"
require_contains "$OUTPUT" "=== chat preferences ==="
require_contains "$OUTPUT" "source     : scripts/chat-preferences-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no config/provider/session-store/model path/runtime execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "preferences: available_as_data"
require_contains "$OUTPUT" "storage    : not_configured"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat preferences section is present and conservative"

HEAD "2: panels and controls stay display-only or disabled"
require_contains "$OUTPUT" "panels     : model_target_preferences=display_only"
require_contains "$OUTPUT" "privacy_preferences=summary_only"
require_contains "$OUTPUT" "local_only_preferences=available_as_data"
require_contains "$OUTPUT" "transcript_preferences=planned"
require_contains "$OUTPUT" "session_preferences=not_configured"
require_contains "$OUTPUT" "controls   : target_model_display=display_only"
require_contains "$OUTPUT" "target_device_display=display_only"
require_contains "$OUTPUT" "model_asset_picker=disabled"
require_contains "$OUTPUT" "local_only_mode=available_as_data"
require_contains "$OUTPUT" "cloud_fallback=disabled"
require_contains "$OUTPUT" "transcript_retention=disabled"
require_contains "$OUTPUT" "transcript_export=disabled"
require_contains "$OUTPUT" "session_store_location=unavailable"
require_contains "$OUTPUT" "diagnostics_verbosity=summary_only"
PASS "preferences panels and controls are bounded metadata"

HEAD "3: blocked reasons require reviewed write and path boundaries"
require_contains "$OUTPUT" "blocked    : preferences_persistence_not_reviewed=blocked"
require_contains "$OUTPUT" "model_asset_picker_not_reviewed=disabled"
require_contains "$OUTPUT" "session_store_not_configured=not_configured"
require_contains "$OUTPUT" "provider_and_network_paths_blocked=disabled"
PASS "preference persistence, model path, session store, and external paths stay blocked"

HEAD "4: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "preferencesDisplayOnly=true"
require_contains "$OUTPUT" "preferencePersistence=false"
require_contains "$OUTPUT" "preferenceWrite=false"
require_contains "$OUTPUT" "configRead=false"
require_contains "$OUTPUT" "environmentRead=false"
require_contains "$OUTPUT" "secretsRead=false"
require_contains "$OUTPUT" "tokensRead=false"
require_contains "$OUTPUT" "providerConfigRead=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelPathIncluded=false"
require_contains "$OUTPUT" "sessionStoreRead=false"
require_contains "$OUTPUT" "sessionStoreWrite=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "transcriptContentIncluded=false"
require_contains "$OUTPUT" "transcriptPersistence=false"
require_contains "$OUTPUT" "transcriptExport=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "executesPccxLab=false"
require_contains "$OUTPUT" "executesSystemverilogIde=false"
PASS "chat preferences execution, provider, persistence, and content flags remain false"

HEAD "5: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-preferences)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat preferences output changed between runs"
    exit 1
fi
PASS "status chat preferences output is deterministic"

HEAD "6: preferences option does not combine with pccx-lab backend"
if "$STUB" --include-chat-preferences --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined preferences/backend mode to fail"
    exit 1
fi
PASS "chat preferences remain separate from backend execution"

HEAD "7: output avoids known overclaims and chat content"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
require_not_contains "$OUTPUT" "hello"
require_not_contains "$OUTPUT" "assistant response:"
require_not_contains "$OUTPUT" "session title:"
require_not_contains "$OUTPUT" "api_key"
require_not_contains "$OUTPUT" "authorization:"
PASS "no preferences overclaim, credential, or chat content in status output"

printf '\n[DONE]  all status-chat-preferences tests passed\n'
