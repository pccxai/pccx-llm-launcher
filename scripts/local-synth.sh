#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai

set -euo pipefail

usage() {
    cat <<'USAGE'
Usage:
  scripts/local-synth.sh --detect-only [--vendor auto|vivado|quartus]
  scripts/local-synth.sh --script <file.tcl> [--vendor auto|vivado|quartus] [--work-dir <dir>] [--dry-run|--run]

Runs a user-supplied local synthesis script through the user's installed EDA
toolchain. Dry-run is the default. No network access, downloads, or uploads are
performed by this wrapper.
USAGE
}

VENDOR="auto"
SCRIPT_FILE=""
WORK_DIR=""
MODE="dry-run"
DETECT_ONLY=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --vendor)
            VENDOR="${2:-}"
            shift 2
            ;;
        --script)
            SCRIPT_FILE="${2:-}"
            shift 2
            ;;
        --work-dir)
            WORK_DIR="${2:-}"
            shift 2
            ;;
        --dry-run)
            MODE="dry-run"
            shift
            ;;
        --run)
            MODE="run"
            shift
            ;;
        --detect-only)
            DETECT_ONLY=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            printf '[ERROR] unknown argument: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

case "$VENDOR" in
    auto|vivado|quartus) ;;
    *)
        printf '[ERROR] unsupported vendor: %s\n' "$VENDOR" >&2
        exit 2
        ;;
esac

find_executable() {
    local env_name="$1"
    local command_name="$2"
    local override="${!env_name:-}"

    if [ -n "$override" ]; then
        if [ -x "$override" ]; then
            printf '%s\n' "$override"
            return 0
        fi
        return 1
    fi

    command -v "$command_name" 2>/dev/null || return 1
}

detect_vendor() {
    local requested="$1"
    local tool=""

    if [ "$requested" = "vivado" ] || [ "$requested" = "auto" ]; then
        if tool="$(find_executable PCCX_VIVADO_BIN vivado)"; then
            printf 'vivado\t%s\n' "$tool"
            return 0
        fi
    fi

    if [ "$requested" = "quartus" ] || [ "$requested" = "auto" ]; then
        if tool="$(find_executable PCCX_QUARTUS_SH_BIN quartus_sh)"; then
            printf 'quartus\t%s\n' "$tool"
            return 0
        fi
    fi

    return 1
}

absolute_path() {
    local path="$1"
    local dir=""
    local base=""

    case "$path" in
        /*)
            printf '%s\n' "$path"
            ;;
        *)
            dir="$(dirname "$path")"
            base="$(basename "$path")"
            (
                cd "$dir"
                printf '%s/%s\n' "$(pwd -P)" "$base"
            )
            ;;
    esac
}

DETECTED="$(detect_vendor "$VENDOR" || true)"
if [ -n "$DETECTED" ]; then
    TOOL_VENDOR="${DETECTED%%	*}"
    TOOL_PATH="${DETECTED#*	}"
else
    TOOL_VENDOR="$VENDOR"
    [ "$TOOL_VENDOR" = "auto" ] && TOOL_VENDOR="not_found"
    TOOL_PATH="not_found"
fi

printf '=== local synthesis wrapper ===\n'
printf 'mode       : %s\n' "$MODE"
printf 'vendor     : %s\n' "$TOOL_VENDOR"
printf 'tool       : %s\n' "$TOOL_PATH"
printf 'offline    : supported; this wrapper performs no network operation\n'

if [ "$DETECT_ONLY" = "1" ]; then
    exit 0
fi

if [ -z "$SCRIPT_FILE" ]; then
    printf '[ERROR] --script is required unless --detect-only is used\n' >&2
    exit 2
fi

if [ ! -f "$SCRIPT_FILE" ]; then
    printf '[ERROR] synthesis script not found: %s\n' "$SCRIPT_FILE" >&2
    exit 2
fi

SCRIPT_ABS="$(absolute_path "$SCRIPT_FILE")"
if [ -n "$WORK_DIR" ]; then
    if [ ! -d "$WORK_DIR" ]; then
        printf '[ERROR] work directory not found: %s\n' "$WORK_DIR" >&2
        exit 2
    fi
    WORK_DIR_ABS="$(absolute_path "$WORK_DIR")"
else
    WORK_DIR_ABS="$(pwd -P)"
fi

printf 'script     : %s\n' "$SCRIPT_ABS"
printf 'work-dir   : %s\n' "$WORK_DIR_ABS"

if [ "$TOOL_PATH" = "not_found" ]; then
    printf 'command    : unavailable; install or point PCCX_VIVADO_BIN/PCCX_QUARTUS_SH_BIN to a local tool\n'
    [ "$MODE" = "run" ] && exit 2
    exit 0
fi

if [ "$TOOL_VENDOR" = "vivado" ]; then
    COMMAND=("$TOOL_PATH" -mode batch -source "$SCRIPT_ABS")
elif [ "$TOOL_VENDOR" = "quartus" ]; then
    COMMAND=("$TOOL_PATH" -t "$SCRIPT_ABS")
else
    printf '[ERROR] no supported local synthesis tool detected\n' >&2
    exit 2
fi

printf 'command    :'
printf ' %q' "${COMMAND[@]}"
printf '\n'

if [ "$MODE" = "dry-run" ]; then
    exit 0
fi

(
    cd "$WORK_DIR_ABS"
    "${COMMAND[@]}"
)
