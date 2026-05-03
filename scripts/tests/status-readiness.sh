#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-readiness.sh — status runtime-readiness summary tests.
#
# Usage: bash scripts/tests/status-readiness.sh [path/to/status-stub.sh]

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

HEAD "1: status can include runtime readiness"
OUTPUT="$("$STUB" --include-runtime-readiness)"
require_contains "$OUTPUT" "=== runtime readiness ==="
require_contains "$OUTPUT" "source     : scripts/runtime-readiness-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no hardware/model/provider/lab/IDE execution"
require_contains "$OUTPUT" "status     : blocked_not_yet_evidence_backed"
require_contains "$OUTPUT" "readiness  : blocked"
require_contains "$OUTPUT" "evidence   : blocked"
require_contains "$OUTPUT" "descriptor : evidence_present"
require_contains "$OUTPUT" "xsim       : evidence_present"
require_contains "$OUTPUT" "synth      : evidence_present"
require_contains "$OUTPUT" "timing     : blocked"
require_contains "$OUTPUT" "impl       : blocked"
require_contains "$OUTPUT" "bitstream  : blocked"
require_contains "$OUTPUT" "smoke      : blocked"
require_contains "$OUTPUT" "runtime    : blocked"
require_contains "$OUTPUT" "throughput : target-only; 20 tok/s unmeasured"
PASS "runtime readiness section is present and conservative"

HEAD "2: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "modelLoaded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "providerCalls=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "executesPccxLab=false"
require_contains "$OUTPUT" "executesSystemverilogIde=false"
PASS "execution-related flags remain false"

HEAD "3: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-runtime-readiness)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status readiness output changed between runs"
    exit 1
fi
PASS "status readiness output is deterministic"

HEAD "4: readiness option does not combine with pccx-lab backend"
if "$STUB" --include-runtime-readiness --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined readiness/backend mode to fail"
    exit 1
fi
PASS "runtime readiness status remains separate from backend execution"

HEAD "5: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no readiness or throughput overclaim in status output"

printf '\n[DONE]  all status-readiness tests passed\n'
