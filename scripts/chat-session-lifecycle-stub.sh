#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# Print the data-only chat session lifecycle fixture.

set -eu

ERROR() { printf '[ERROR] %s\n' "$*" >&2; }

usage() {
    cat <<'EOF'
Usage: bash scripts/chat-session-lifecycle-stub.sh [--model gemma3n-e4b] [--target kv260]

Print the checked chat session lifecycle fixture. This does not create,
restore, clear, close, or export a session; it does not capture prompts,
execute a model, touch hardware, call providers, invoke pccx-lab, or write
artifacts.
EOF
}

MODEL="gemma3n-e4b"
TARGET="kv260"

while [ $# -gt 0 ]; do
    case "$1" in
        --model)
            if [ -z "${2:-}" ]; then
                ERROR "--model requires an argument"
                exit 1
            fi
            MODEL="$2"
            shift 2
            ;;
        --target)
            if [ -z "${2:-}" ]; then
                ERROR "--target requires an argument"
                exit 1
            fi
            TARGET="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            ERROR "unknown option: $1"
            usage >&2
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"

python3 "$ROOT_DIR/contracts/chat_session_lifecycle_contract.py" \
    --model "$MODEL" \
    --target "$TARGET"
