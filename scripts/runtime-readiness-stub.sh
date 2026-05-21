#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/runtime-readiness-stub.sh — deterministic readiness JSON stub.
#
# This script prints the checked Gemma 3N E4B plus KV260 readiness fixture.
# It does not touch hardware, load a model, call providers, upload telemetry,
# write artifacts, or invoke pccx-lab or editor tooling.

set -eu

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
PCCX_LAUNCHER_ROOT="$ROOT_DIR"
# shellcheck source=scripts/lib/errors.sh
. "$ROOT_DIR/scripts/lib/errors.sh"

MODEL=""
TARGET=""

usage() {
    printf 'Usage: bash scripts/runtime-readiness-stub.sh --model gemma3n-e4b --target kv260\n'
}

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
        --help|-h)
            usage
            exit 0
            ;;
        *)
            TRACE_ERROR "unknown option: $1"
            usage >&2
            exit 1
            ;;
    esac
done

if [ "$MODEL" != "gemma3n-e4b" ]; then
    GEMMA_ERROR "--model must be gemma3n-e4b"
    exit 1
fi

if [ "$TARGET" != "kv260" ]; then
    KV260_ERROR "--target must be kv260"
    exit 1
fi

python3 "$ROOT_DIR/contracts/runtime_readiness_contract.py" \
    --model "$MODEL" \
    --target "$TARGET"
