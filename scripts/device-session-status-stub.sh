#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/device-session-status-stub.sh - data-only device/session JSON.

set -eu

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
PCCX_LAUNCHER_ROOT="$ROOT_DIR"
# shellcheck source=scripts/lib/errors.sh
. "$ROOT_DIR/scripts/lib/errors.sh"

MODEL="gemma3n-e4b"
TARGET="kv260"

while [ $# -gt 0 ]; do
    case "$1" in
        --model)
            MODEL="${2:-}"
            if [ -z "$MODEL" ]; then
                TRACE_ERROR "--model requires an argument"
                exit 1
            fi
            shift 2
            ;;
        --target)
            TARGET="${2:-}"
            if [ -z "$TARGET" ]; then
                TRACE_ERROR "--target requires an argument"
                exit 1
            fi
            shift 2
            ;;
        *)
            TRACE_ERROR "unknown option: $1"
            exit 1
            ;;
    esac
done

if [ "$MODEL" != "gemma3n-e4b" ]; then
    GEMMA_ERROR "unsupported model: $MODEL (supported: gemma3n-e4b)"
    exit 1
fi

if [ "$TARGET" != "kv260" ]; then
    KV260_ERROR "unsupported target: $TARGET (supported: kv260)"
    exit 1
fi

python3 "$ROOT_DIR/contracts/device_session_status_contract.py" \
    --model "$MODEL" \
    --target "$TARGET"
