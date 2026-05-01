#!/usr/bin/env bash
# scripts/chat-stub.sh — dry-run chat stub
# Requires --dry-run. No model is executed. No network call is made.
# Accepts a prompt via --prompt "..." or stdin.

set -u

INFO() { printf '[INFO]  %s\n' "$*"; }
NOTE() { printf '[NOTE]  %s\n' "$*"; }
HEAD() { printf '\n=== %s ===\n' "$*"; }

DRY_RUN=0
PROMPT=""

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        *)
            printf '[ERROR] unknown option: %s\n' "$1" >&2
            exit 1
            ;;
    esac
done

if [ "$DRY_RUN" -eq 0 ]; then
    printf '[ERROR] --dry-run is required. No model is available for execution.\n' >&2
    printf '        Real chat requires pccx-FPGA verified bring-up.\n' >&2
    exit 1
fi

if [ -z "$PROMPT" ] && [ -t 0 ]; then
    printf '[ERROR] provide --prompt "..." or pipe input via stdin.\n' >&2
    exit 1
fi

if [ -z "$PROMPT" ]; then
    PROMPT="$(cat)"
fi

HEAD "pccx-launcher chat-stub | dry-run"
INFO "prompt   : ${PROMPT}"
NOTE "no model executed"
NOTE "no network call made"
NOTE "response : [placeholder — real inference requires pccx-FPGA bring-up evidence]"
exit 0
