#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/device-session-status-stub.sh - data-only device/session JSON.

set -eu

MODEL="gemma3n-e4b"
TARGET="kv260"

ERROR() { printf '[ERROR] %s\n' "$*" >&2; }

while [ $# -gt 0 ]; do
    case "$1" in
        --model)
            MODEL="${2:-}"
            if [ -z "$MODEL" ]; then
                ERROR "--model requires an argument"
                exit 1
            fi
            shift 2
            ;;
        --target)
            TARGET="${2:-}"
            if [ -z "$TARGET" ]; then
                ERROR "--target requires an argument"
                exit 1
            fi
            shift 2
            ;;
        *)
            ERROR "unknown option: $1"
            exit 1
            ;;
    esac
done

if [ "$MODEL" != "gemma3n-e4b" ]; then
    ERROR "unsupported model: $MODEL (supported: gemma3n-e4b)"
    exit 1
fi

if [ "$TARGET" != "kv260" ]; then
    ERROR "unsupported target: $TARGET (supported: kv260)"
    exit 1
fi

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"

python3 "$ROOT_DIR/contracts/device_session_status_contract.py" \
    --model "$MODEL" \
    --target "$TARGET"
