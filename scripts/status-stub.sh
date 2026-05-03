#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# scripts/status-stub.sh — launcher state summary
# Default mode: local scaffold output, no external calls, always exits 0.
#
# Runtime readiness summary (explicit opt-in, read-only local data):
#   --include-runtime-readiness
#
# Device/session status panel (explicit opt-in, read-only local data):
#   --include-device-session
#
# Chat/session status (explicit opt-in, read-only local data):
#   --include-chat-session
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
INCLUDE_RUNTIME_READINESS="0"
INCLUDE_DEVICE_SESSION="0"
INCLUDE_CHAT_SESSION="0"

print_chat_session_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    CHAT_SESSION_STUB="$ROOT_DIR/scripts/chat-session-stub.sh"

    if [ ! -f "$CHAT_SESSION_STUB" ]; then
        ERROR "chat/session stub not found: $CHAT_SESSION_STUB"
        return 1
    fi

    if ! CHAT_SESSION_JSON="$(bash "$CHAT_SESSION_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "chat/session stub failed"
        printf '%s\n' "$CHAT_SESSION_JSON" >&2
        return 1
    fi

    if ! CHAT_SESSION_SUMMARY="$(
        printf '%s\n' "$CHAT_SESSION_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
controls = " ".join(
    "{}={}".format(control["controlId"], control["state"])
    for control in data["sessionControls"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/chat-session-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no prompt/model/provider/hardware/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  surface    : {}".format(data["surfaceState"]))
print("[INFO]  chat       : {}".format(data["chatState"]))
print("[INFO]  input      : {}".format(data["inputState"]))
print("[INFO]  send       : {}".format(data["sendState"]))
print("[INFO]  model load : {}".format(data["modelStatus"]))
print("[INFO]  transcript : {}".format(data["transcriptPolicy"]["state"]))
print("[INFO]  response   : {}".format(data["messageEnvelope"]["responseState"]))
print("[INFO]  controls   : {}".format(controls))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "runtimeExecution={} modelLoaded={} modelExecution={} kv260Access={} "
    "providerCalls={} cloudCalls={} networkCalls={} transcriptPersistence={} "
    "promptContentIncluded={} responseContentIncluded={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["runtimeExecution"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["kv260Access"]),
        b(flags["providerCalls"]),
        b(flags["cloudCalls"]),
        b(flags["networkCalls"]),
        b(flags["transcriptPersistence"]),
        b(flags["promptContentIncluded"]),
        b(flags["responseContentIncluded"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "chat/session JSON could not be summarized"
        return 1
    fi

    HEAD "chat/session status"
    printf '%s\n' "$CHAT_SESSION_SUMMARY"
}

print_device_session_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    DEVICE_SESSION_STUB="$ROOT_DIR/scripts/device-session-status-stub.sh"

    if [ ! -f "$DEVICE_SESSION_STUB" ]; then
        ERROR "device/session status stub not found: $DEVICE_SESSION_STUB"
        return 1
    fi

    if ! DEVICE_SESSION_JSON="$(bash "$DEVICE_SESSION_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "device/session status stub failed"
        printf '%s\n' "$DEVICE_SESSION_JSON" >&2
        return 1
    fi

    if ! DEVICE_SESSION_SUMMARY="$(
        printf '%s\n' "$DEVICE_SESSION_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
rows = " ".join(
    "{}={}".format(row["rowId"], row["state"])
    for row in data["statusPanel"]
)

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/device-session-status-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no hardware/model/provider/lab/IDE execution")
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  connection : {}".format(data["connectionState"]))
print("[INFO]  discovery  : {}".format(data["discoveryState"]))
print("[INFO]  auth       : {}".format(data["authenticationState"]))
print("[INFO]  runtime    : {}".format(data["runtimeState"]))
print("[INFO]  model load : {}".format(data["modelLoadState"]))
print("[INFO]  session    : {}".format(data["sessionState"]))
print("[INFO]  logs       : {}".format(data["logStreamState"]))
print("[INFO]  diagnostic : {}".format(data["diagnosticsState"]))
print("[INFO]  readiness  : {}".format(data["readinessState"]))
print("[INFO]  panel      : {}".format(rows))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "runtimeExecution={} modelLoaded={} modelExecution={} kv260Access={} "
    "opensSerialPort={} networkCalls={} networkScan={} sshExecution={} "
    "authenticationAttempt={} executesPccxLab={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["runtimeExecution"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["kv260Access"]),
        b(flags["opensSerialPort"]),
        b(flags["networkCalls"]),
        b(flags["networkScan"]),
        b(flags["sshExecution"]),
        b(flags["authenticationAttempt"]),
        b(flags["executesPccxLab"]),
    )
)
'
    )"; then
        ERROR "device/session status JSON could not be summarized"
        return 1
    fi

    HEAD "device/session status"
    printf '%s\n' "$DEVICE_SESSION_SUMMARY"
}

print_runtime_readiness_summary() {
    SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
    ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"
    READINESS_STUB="$ROOT_DIR/scripts/runtime-readiness-stub.sh"

    if [ ! -f "$READINESS_STUB" ]; then
        ERROR "runtime readiness stub not found: $READINESS_STUB"
        return 1
    fi

    if ! READINESS_JSON="$(bash "$READINESS_STUB" --model gemma3n-e4b --target kv260 2>&1)"; then
        ERROR "runtime readiness stub failed"
        printf '%s\n' "$READINESS_JSON" >&2
        return 1
    fi

    if ! READINESS_SUMMARY="$(
        printf '%s\n' "$READINESS_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
performance = data["performanceTargets"][0]
flags = data["safetyFlags"]

def b(value):
    return "true" if value else "false"

print("[INFO]  source     : scripts/runtime-readiness-stub.sh --model gemma3n-e4b --target kv260")
print("[INFO]  boundary   : read-only data; no hardware/model/provider/lab/IDE execution")
print("[INFO]  model      : {} {}".format(data["modelFamily"], data["modelVariant"]))
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  status     : {}".format(data["statusAnswer"]))
print("[INFO]  readiness  : {}".format(data["readinessState"]))
print("[INFO]  evidence   : {}".format(data["evidenceState"]))
print("[INFO]  descriptor : {}".format(data["descriptorState"]))
print("[INFO]  xsim       : {}".format(data["simulationEvidenceState"]))
print("[INFO]  synth      : {}".format(data["vivadoSynthState"]))
print("[INFO]  timing     : {}".format(data["timingEvidenceState"]))
print("[INFO]  impl       : {}".format(data["implementationState"]))
print("[INFO]  bitstream  : {}".format(data["bitstreamState"]))
print("[INFO]  smoke      : {}".format(data["kv260SmokeState"]))
print("[INFO]  runtime    : {}".format(data["runtimeEvidenceState"]))
print("[INFO]  throughput : target-only; {} unmeasured".format(performance["target"]))
print(
    "[INFO]  flags      : readOnly={} dataOnly={} deterministic={} "
    "runtimeExecution={} modelLoaded={} modelExecution={} kv260Access={} "
    "providerCalls={} networkCalls={} executesPccxLab={} executesSystemverilogIde={}".format(
        b(flags["readOnly"]),
        b(flags["dataOnly"]),
        b(flags["deterministic"]),
        b(flags["runtimeExecution"]),
        b(flags["modelLoaded"]),
        b(flags["modelExecution"]),
        b(flags["kv260Access"]),
        b(flags["providerCalls"]),
        b(flags["networkCalls"]),
        b(flags["executesPccxLab"]),
        b(flags["executesSystemverilogIde"]),
    )
)
'
    )"; then
        ERROR "runtime readiness JSON could not be summarized"
        return 1
    fi

    HEAD "runtime readiness"
    printf '%s\n' "$READINESS_SUMMARY"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --include-runtime-readiness)
            INCLUDE_RUNTIME_READINESS="1"
            shift
            ;;
        --include-device-session)
            INCLUDE_DEVICE_SESSION="1"
            shift
            ;;
        --include-chat-session)
            INCLUDE_CHAT_SESSION="1"
            shift
            ;;
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

if [ -n "$BACKEND" ] && { [ "$INCLUDE_RUNTIME_READINESS" = "1" ] || [ "$INCLUDE_DEVICE_SESSION" = "1" ] || [ "$INCLUDE_CHAT_SESSION" = "1" ]; }; then
    ERROR "--include-runtime-readiness, --include-device-session, and --include-chat-session are only supported in local scaffold mode"
    exit 1
fi

# ── Default mode ──────────────────────────────────────────────────────────────
if [ -z "$BACKEND" ]; then
    HEAD "launcher state"
    NOTE "chat-stub      : available (dry-run only; see scripts/chat-stub.sh)"
    NOTE "launch-stub    : available (dry-run only; --dry-run flag required)"
    NOTE "inference path : not active"
    NOTE "KV260 path     : gated on pccxai/pccx-FPGA-NPU-LLM-kv260 bring-up"
    NOTE "pccx-lab diag  : deferred (analyze handoff not yet wired into launcher)"
    NOTE "pccx-lab status: opt-in via --backend pccx-lab (host-dry-run scaffold)"
    NOTE "runtime ready  : opt-in via --include-runtime-readiness (read-only data)"
    NOTE "device/session: opt-in via --include-device-session (read-only panel data)"
    NOTE "chat/session  : opt-in via --include-chat-session (read-only blocked chat data)"
    NOTE "editor bridge  : planned (VS Code / other IDEs)"

    if [ "$INCLUDE_CHAT_SESSION" = "1" ]; then
        if ! print_chat_session_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_DEVICE_SESSION" = "1" ]; then
        if ! print_device_session_summary; then
            exit 1
        fi
    fi

    if [ "$INCLUDE_RUNTIME_READINESS" = "1" ]; then
        if ! print_runtime_readiness_summary; then
            exit 1
        fi
    fi

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
