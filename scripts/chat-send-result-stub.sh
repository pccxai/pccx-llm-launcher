#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/chat-send-result-stub.sh - print data-only chat send-result JSON.
#
# This script does not read, accept, or echo prompts, generate responses,
# persist transcripts, read attachments, load models, start runtime code, touch
# KV260 hardware, call providers, read/write artifacts, or invoke pccx-lab.

set -eu

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"

MODEL="gemma3n-e4b"
TARGET="kv260"

while [ $# -gt 0 ]; do
    case "$1" in
        --model)
            MODEL="${2:-}"
            if [ -z "$MODEL" ]; then
                printf '[ERROR] --model requires an argument\n' >&2
                exit 2
            fi
            shift 2
            ;;
        --target)
            TARGET="${2:-}"
            if [ -z "$TARGET" ]; then
                printf '[ERROR] --target requires an argument\n' >&2
                exit 2
            fi
            shift 2
            ;;
        *)
            printf '[ERROR] unknown option: %s\n' "$1" >&2
            exit 2
            ;;
    esac
done

exec python3 "$ROOT_DIR/contracts/chat_send_result_contract.py" \
    --model "$MODEL" \
    --target "$TARGET"
