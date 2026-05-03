#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/tests/status-device-session.sh - status device/session summary tests.
#
# Usage: bash scripts/tests/status-device-session.sh [path/to/status-stub.sh]

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

HEAD "1: status can include device/session panel"
OUTPUT="$("$STUB" --include-device-session)"
require_contains "$OUTPUT" "=== device/session status ==="
require_contains "$OUTPUT" "source     : scripts/device-session-status-stub.sh --model gemma3n-e4b --target kv260"
require_contains "$OUTPUT" "boundary   : read-only data; no hardware/model/provider/lab/IDE execution"
require_contains "$OUTPUT" "target     : kv260"
require_contains "$OUTPUT" "model      : gemma3n-e4b"
require_contains "$OUTPUT" "connection : not_configured"
require_contains "$OUTPUT" "discovery  : not_started"
require_contains "$OUTPUT" "auth       : not_configured"
require_contains "$OUTPUT" "model load : not_loaded"
require_contains "$OUTPUT" "session    : inactive"
require_contains "$OUTPUT" "logs       : not_started"
require_contains "$OUTPUT" "diagnostic : available_as_placeholder"
require_contains "$OUTPUT" "readiness  : blocked"
PASS "device/session section is present and conservative"

HEAD "2: status panel rows cover device, model, session, diagnostics, readiness"
require_contains "$OUTPUT" "panel      : device_connection=not_configured"
require_contains "$OUTPUT" "model_load=not_loaded"
require_contains "$OUTPUT" "session_activity=inactive"
require_contains "$OUTPUT" "pccx_lab_diagnostics=available_as_placeholder"
require_contains "$OUTPUT" "runtime_readiness=blocked"
PASS "status panel rows are summarized"

HEAD "3: safety flags stay read-only and non-executing"
require_contains "$OUTPUT" "readOnly=true"
require_contains "$OUTPUT" "dataOnly=true"
require_contains "$OUTPUT" "deterministic=true"
require_contains "$OUTPUT" "runtimeExecution=false"
require_contains "$OUTPUT" "modelLoaded=false"
require_contains "$OUTPUT" "modelExecution=false"
require_contains "$OUTPUT" "kv260Access=false"
require_contains "$OUTPUT" "opensSerialPort=false"
require_contains "$OUTPUT" "networkCalls=false"
require_contains "$OUTPUT" "networkScan=false"
require_contains "$OUTPUT" "sshExecution=false"
require_contains "$OUTPUT" "authenticationAttempt=false"
require_contains "$OUTPUT" "executesPccxLab=false"
PASS "execution-related flags remain false"

HEAD "4: output is deterministic"
OUTPUT_AGAIN="$("$STUB" --include-device-session)"
if [ "$OUTPUT" != "$OUTPUT_AGAIN" ]; then
    FAIL "status device/session output changed between runs"
    exit 1
fi
PASS "status device/session output is deterministic"

HEAD "5: device/session option does not combine with pccx-lab backend"
if "$STUB" --include-device-session --backend pccx-lab >/dev/null 2>&1; then
    FAIL "expected combined device-session/backend mode to fail"
    exit 1
fi
PASS "device/session status remains separate from backend execution"

HEAD "6: output avoids known overclaims"
FORBIDDEN_PREFIX="KV260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
require_not_contains "$OUTPUT" "$FORBIDDEN_CLAIM"
THROUGHPUT_PREFIX="20 tok/s"
THROUGHPUT_CLAIM="${THROUGHPUT_PREFIX} achieved"
require_not_contains "$OUTPUT" "$THROUGHPUT_CLAIM"
PASS "no device/session or throughput overclaim in status output"

printf '\n[DONE]  all status-device-session tests passed\n'
