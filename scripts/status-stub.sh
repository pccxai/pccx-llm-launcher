#!/usr/bin/env bash
# scripts/status-stub.sh — launcher state summary
# Default mode: local scaffold output, no external calls, always exits 0.
#
# pccx-lab backend (explicit opt-in):
#   --backend pccx-lab        call pccx-lab status --format json
#   PCCX_LAB_BIN              override path to pccx-lab binary (takes priority over PATH)
#
# No silent fallback: if --backend pccx-lab is requested and the binary
# cannot be found or fails, the script exits non-zero with a clear error.

set -u

INFO()  { printf '[INFO]  %s\n' "$*"; }
NOTE()  { printf '[NOTE]  %s\n' "$*"; }
ERROR() { printf '[ERROR] %s\n' "$*" >&2; }
HEAD()  { printf '\n=== %s ===\n' "$*"; }

BACKEND=""

while [ $# -gt 0 ]; do
    case "$1" in
        --backend)
            BACKEND="${2:-}"
            if [ -z "$BACKEND" ]; then
                ERROR "--backend requires an argument"
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

# ── Default mode ──────────────────────────────────────────────────────────────
if [ -z "$BACKEND" ]; then
    HEAD "launcher state"
    NOTE "chat-stub      : available (dry-run only; see scripts/chat-stub.sh)"
    NOTE "launch-stub    : available (dry-run only; --dry-run flag required)"
    NOTE "inference path : not active"
    NOTE "KV260 path     : gated on pccxai/pccx-FPGA-NPU-LLM-kv260 bring-up"
    NOTE "pccx-lab diag  : deferred (analyze handoff not yet wired into launcher)"
    NOTE "pccx-lab status: opt-in via --backend pccx-lab (host-dry-run scaffold)"
    NOTE "editor bridge  : planned (VS Code / other IDEs)"

    HEAD "summary"
    INFO "no inference engine is wired up; all paths are planned or deferred"
    exit 0
fi

if [ "$BACKEND" != "pccx-lab" ]; then
    ERROR "unknown backend: $BACKEND (supported: pccx-lab)"
    exit 1
fi

# ── pccx-lab backend ─────────────────────────────────────────────────────────
# Resolution order: PCCX_LAB_BIN env var (if non-empty), then pccx-lab on PATH.
_PCCX_LAB_BIN="${PCCX_LAB_BIN:-}"
if [ -n "$_PCCX_LAB_BIN" ]; then
    if [ ! -x "$_PCCX_LAB_BIN" ]; then
        ERROR "PCCX_LAB_BIN=$_PCCX_LAB_BIN is not executable or does not exist."
        ERROR "No silent fallback: --backend pccx-lab was explicitly requested."
        exit 1
    fi
    LAB_BIN="$_PCCX_LAB_BIN"
elif command -v pccx-lab >/dev/null 2>&1; then
    LAB_BIN="$(command -v pccx-lab)"
else
    ERROR "pccx-lab binary not found."
    ERROR "Set PCCX_LAB_BIN=/path/to/pccx-lab or ensure pccx-lab is on PATH."
    ERROR "No silent fallback: --backend pccx-lab was explicitly requested."
    exit 1
fi

HEAD "pccx-lab status handoff"
INFO "backend   : pccx-lab"
INFO "binary    : $LAB_BIN"
INFO "boundary  : run-status envelope (host-dry-run / early scaffold)"
INFO "note      : no real KV260 device probing; no inference executed"

if ! OUTPUT="$("$LAB_BIN" status --format json 2>&1)"; then
    ERROR "pccx-lab exited with error"
    printf '%s\n' "$OUTPUT" >&2
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    ERROR "pccx-lab status produced no output"
    exit 1
fi

# Lightweight JSON shape check — output must begin with '{'.
STRIPPED="$(printf '%s' "$OUTPUT" | tr -d '[:space:]')"
FIRST_CHAR="${STRIPPED:0:1}"
if [ "$FIRST_CHAR" != "{" ]; then
    ERROR "pccx-lab output does not look like a JSON object (first char: '$FIRST_CHAR')"
    printf '%s\n' "$OUTPUT" >&2
    exit 1
fi

HEAD "run-status envelope"
printf '%s\n' "$OUTPUT"

HEAD "summary"
INFO "pccx-lab status handoff complete (host-dry-run; no KV260 probing; no inference)"
exit 0
