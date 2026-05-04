#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-chat-model-load-request.sh - status model-load request tests.
#
# Usage: bash scripts/tests/status-chat-model-load-request.sh [path/to/status-stub.sh]

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

HEAD "1: status can include chat model-load request"
OUTPUT="$("$STUB" --include-chat-model-load-request)"
require_contains "$OUTPUT" "=== chat model load request ==="
require_contains "$OUTPUT" "source     : scripts/chat-model-load-request-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no model asset path/read/load/runtime/provider/hardware/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "request    : blocked"
require_contains "$OUTPUT" "selected   : target_selected"
require_contains "$OUTPUT" "descriptor : available_as_data"
require_contains "$OUTPUT" "assets     : blocked"
require_contains "$OUTPUT" "paths      : not_configured"
require_contains "$OUTPUT" "checksums  : not_configured"
require_contains "$OUTPUT" "plan       : blocked"
require_contains "$OUTPUT" "preflight  : blocked"
require_contains "$OUTPUT" "device     : inactive"
require_contains "$OUTPUT" "warmup     : disabled"
require_contains "$OUTPUT" "unload     : disabled"
require_contains "$OUTPUT" "privacy    : summary_only"
PASS "chat model-load request section is present and conservative"

HEAD "2: policy, inputs, and controls stay disabled"
require_contains "$OUTPUT" "model-load-request : blocked mode=disabled_until_reviewed_model_load_boundary_exists"
require_contains "$OUTPUT" "descriptorSelected=true"
require_contains "$OUTPUT" "modelAssetsConfigured=false"
require_contains "$OUTPUT" "assetPathsConfigured=false"
require_contains "$OUTPUT" "checksumsAvailable=false"
require_contains "$OUTPUT" "runtimeReady=false"
require_contains "$OUTPUT" "deviceSessionReady=false"
require_contains "$OUTPUT" "loadEnabled=false"
require_contains "$OUTPUT" "warmupEnabled=false"
require_contains "$OUTPUT" "unloadEnabled=false"
require_contains "$OUTPUT" "inputs     : model_descriptor=available_as_data:false"
require_contains "$OUTPUT" "local_asset_path=not_configured:false"
require_contains "$OUTPUT" "model_weight_file=blocked:false"
require_contains "$OUTPUT" "tokenizer_asset=blocked:false"
require_contains "$OUTPUT" "checksum_manifest=not_configured:false"
require_contains "$OUTPUT" "runtime_profile=blocked:false"
require_contains "$OUTPUT" "device_session=inactive:false"
require_contains "$OUTPUT" "controls   : select_model_descriptor=target_selected:false"
require_contains "$OUTPUT" "configure_asset_path=blocked:false"
require_contains "$OUTPUT" "validate_assets=blocked:false"
require_contains "$OUTPUT" "build_load_plan=blocked:false"
require_contains "$OUTPUT" "start_runtime=disabled:false"
require_contains "$OUTPUT" "load_model=disabled:false"
require_contains "$OUTPUT" "warmup_model=disabled:false"
require_contains "$OUTPUT" "unload_model=disabled:false"
require_contains "$OUTPUT" "persist_load_request=disabled:false"
PASS "model-load request metadata is summarized without asset reads"

HEAD "3: blocked reasons stay explicit"
require_contains "$OUTPUT" "blocked    : model_asset_input_boundary_absent=blocked"
require_contains "$OUTPUT" "model_asset_path_boundary_absent=not_configured"
require_contains "$OUTPUT" "model_integrity_evidence_absent=requires_evidence"
require_contains "$OUTPUT" "runtime_readiness_blocked=blocked"
require_contains "$OUTPUT" "device_session_inactive=inactive"
require_contains "$OUTPUT" "model_load_executor_absent=disabled"
require_contains "$OUTPUT" "unload_policy_absent=planned"
require_contains "$OUTPUT" "local_only_policy_required=planned"
PASS "model-load blockers remain visible"

HEAD "4: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "loadRequestDisplayOnly=true"
require_contains "$OUTPUT" "modelDescriptorMetadataOnly=true"
require_contains "$OUTPUT" "modelAssetsConfigured=false"
require_contains "$OUTPUT" "modelAssetPathsConfigured=false"
require_contains "$OUTPUT" "modelAssetPathsIncluded=false"
require_contains "$OUTPUT" "modelWeightPathsIncluded=false"
require_contains "$OUTPUT" "modelAssetRead=false"
require_contains "$OUTPUT" "modelWeightRead=false"
require_contains "$OUTPUT" "tokenizerRead=false"
require_contains "$OUTPUT" "checksumManifestRead=false"
require_contains "$OUTPUT" "checksumValuesIncluded=false"
require_contains "$OUTPUT" "modelIntegrityChecked=false"
require_contains "$OUTPUT" "configRead=false"
require_contains "$OUTPUT" "configWrite=false"
require_contains "$OUTPUT" "environmentRead=false"
require_contains "$OUTPUT" "promptContentIncluded=false"
require_contains "$OUTPUT" "responseContentIncluded=false"
require_contains "$OUTPUT" "runtimePreflightExecuted=false"
require_contains "$OUTPUT" "runtimeStarted=false"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "modelLoadAttempted=false"
require_contains "$OUTPUT" "modelLoaded=false"
require_contains "$OUTPUT" "modelUnloadAttempted=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "warmupAttempted=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "hardwareAccess=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "cloudCalls=false"
require_contains "$OUTPUT" "writesArtifacts=false"
require_contains "$OUTPUT" "readsArtifacts=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution, asset read, and persistence flags remain false"

HEAD "5: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-chat-model-load-request)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status chat model-load request output changed between runs"
    exit 1
fi
PASS "status chat model-load request output is deterministic"

HEAD "6: chat model-load request option does not combine with pccx-lab backend"
if "$STUB" --include-chat-model-load-request --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined chat-model-load-request/backend mode to fail"
    exit 1
fi
PASS "chat model-load request remains separate from backend execution"

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
PASS "no model-load overclaim or asset/content leakage in status output"

printf '\n[DONE]  all status-chat-model-load-request tests passed\n'
