#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/chat-readiness-stub.sh - print data-only chat readiness JSON.
#
# This script does not read prompts, load model assets, start runtime code,
# touch KV260 hardware, call providers, read/write artifacts, or invoke
# pccx-lab.

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
                exit 2
            fi
            shift 2
            ;;
        --target)
            TARGET="${2:-}"
            if [ -z "$TARGET" ]; then
                TRACE_ERROR "--target requires an argument"
                exit 2
            fi
            shift 2
            ;;
        *)
            TRACE_ERROR "unknown option: $1"
            exit 2
            ;;
    esac
done

exec python3 "$ROOT_DIR/contracts/chat_readiness_contract.py" \
    --model "$MODEL" \
    --target "$TARGET"
