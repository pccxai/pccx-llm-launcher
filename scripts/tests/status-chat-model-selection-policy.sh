#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-model-selection-policy.sh - status model-selection tests.
#
# Usage: bash scripts/tests/status-chat-model-selection-policy.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat model-selection policy"
OUTPUT="$("$STUB" --include-chat-model-selection-policy)"
require_contains "$OUTPUT" "=== chat model selection policy ==="
require_contains "$OUTPUT" "source     : scripts/chat-model-selection-policy-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no catalog/config/model asset path/read/load/runtime/provider/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "selection  : blocked"
require_contains "$OUTPUT" "catalog    : static_placeholder"
require_contains "$OUTPUT" "picker     : disabled"
require_contains "$OUTPUT" "selected   : target_selected"
require_contains "$OUTPUT" "descriptor : available_as_data"
require_contains "$OUTPUT" "asset disc : blocked"
require_contains "$OUTPUT" "asset paths: not_configured"
require_contains "$OUTPUT" "fallback   : disabled"
require_contains "$OUTPUT" "load req   : blocked"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat model-selection section is present and conservative"

HEAD "2: policy, options, and controls stay disabled"
require_contains "$OUTPUT" "model-selection : blocked mode=disabled_until_reviewed_model_catalog_and_selection_boundary_exists"
require_contains "$OUTPUT" "staticOptionCount=1"
require_contains "$OUTPUT" "dynamicCatalogConfigured=false"
require_contains "$OUTPUT" "localCatalogRead=false"
require_contains "$OUTPUT" "assetDiscoveryEnabled=false"
require_contains "$OUTPUT" "selectionEnabled=false"
require_contains "$OUTPUT" "selectionPersistenceEnabled=false"
require_contains "$OUTPUT" "providerFallbackEnabled=false"
require_contains "$OUTPUT" "loadRequestEnabled=false"
require_contains "$OUTPUT" "options    : gemma3n_e4b_kv260_placeholder=target_selected:true:false"
require_contains "$OUTPUT" "controls   : review_static_target=available_as_data:false"
require_contains "$OUTPUT" "open_model_catalog=blocked:false"
require_contains "$OUTPUT" "select_model_option=disabled:false"
require_contains "$OUTPUT" "discover_local_assets=blocked:false"
require_contains "$OUTPUT" "configure_provider_fallback=disabled:false"
require_contains "$OUTPUT" "handoff_to_load_request=blocked:false"
PASS "model-selection metadata is summarized without catalog or asset reads"

HEAD "3: blocked reasons stay explicit"
require_contains "$OUTPUT" "blocked    : dynamic_catalog_boundary_absent=not_configured"
require_contains "$OUTPUT" "selection_executor_absent=disabled"
require_contains "$OUTPUT" "model_asset_discovery_blocked=blocked"
require_contains "$OUTPUT" "provider_fallback_disabled=disabled"
require_contains "$OUTPUT" "load_request_blocked=blocked"
require_contains "$OUTPUT" "runtime_evidence_absent=requires_evidence"
require_contains "$OUTPUT" "hardware_evidence_absent=requires_evidence"
PASS "model-selection blockers remain visible"

HEAD "4: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "selectionPolicyDisplayOnly=true"
require_contains "$OUTPUT" "staticOptionOnly=true"
require_contains "$OUTPUT" "dynamicCatalogConfigured=false"
require_contains "$OUTPUT" "modelCatalogRead=false"
require_contains "$OUTPUT" "dynamicCatalogDiscovery=false"
require_contains "$OUTPUT" "modelSelectionPersisted=false"
require_contains "$OUTPUT" "modelSelectionAcceptedFromUser=false"
require_contains "$OUTPUT" "modelOptionsFromConfig=false"
require_contains "$OUTPUT" "modelAssetPathsIncluded=false"
require_contains "$OUTPUT" "modelAssetPathRead=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "configRead=false"
require_contains "$OUTPUT" "environmentRead=false"
require_contains "$OUTPUT" "providerConfigRead=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelLoaded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "catalog, selection, runtime, and asset flags remain disabled"

HEAD "5: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-model-selection-policy)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat model-selection output changed between runs"
    exit 1
fi
PASS "status chat model-selection output is deterministic"

HEAD "6: chat model-selection option does not combine with pccx-lab backend"
if "$STUB" --include-chat-model-selection-policy --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-model-selection/backend mode to fail"
    exit 1
fi
PASS "chat model-selection remains separate from backend execution"

HEAD "7: output avoids known overclaims and content"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
GGUF_EXT=".g""guf"
SAFETENSORS_EXT=".safe""tensors"
require_not_contains "$OUTPUT" "$GGUF_EXT"
require_not_contains "$OUTPUT" "$SAFETENSORS_EXT"
require_not_contains "$OUTPUT" "assistant response:"
require_not_contains "$OUTPUT" "hello"
PASS "no model-selection overclaim or asset/content leakage in status output"

printf '\n[DONE]  all status-chat-model-selection-policy tests passed\n'
