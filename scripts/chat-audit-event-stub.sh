#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/chat-audit-event-stub.sh - print chat audit-event JSON.
#
# This script does not read, accept, echo, store, persist, log, summarize, or
# export prompts, responses, message bodies, transcripts, artifacts, actor
# identifiers, or runtime traces. It does not load models, start runtime code,
# touch KV260 hardware, call providers, or invoke pccx-lab.

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

exec python3 "$ROOT_DIR/contracts/chat_audit_event_contract.py" \
    --model "$MODEL" \
    --target "$TARGET"
