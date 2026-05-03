#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# Render a read-only standalone chat surface preview from the checked contract.

set -eu

ERROR() { printf '[ERROR] %s\n' "$*" >&2; }

usage() {
    cat <<'EOF'
Usage: bash scripts/chat-surface-preview.sh [--model gemma3n-e4b] [--target kv260]

Render the local standalone chat surface preview from the data-only
chat/session contract. This does not capture prompts, execute a model,
touch hardware, call providers, invoke pccx-lab, or write artifacts.
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
CHAT_SESSION_STUB="$ROOT_DIR/scripts/chat-session-stub.sh"

if [ ! -f "$CHAT_SESSION_STUB" ]; then
    ERROR "chat/session stub not found: $CHAT_SESSION_STUB"
    exit 1
fi

if ! CHAT_SESSION_JSON="$(bash "$CHAT_SESSION_STUB" --model "$MODEL" --target "$TARGET" 2>&1)"; then
    ERROR "chat/session stub failed"
    printf '%s\n' "$CHAT_SESSION_JSON" >&2
    exit 1
fi

printf '%s\n' "$CHAT_SESSION_JSON" | python3 -c '
import json
import sys

data = json.load(sys.stdin)
flags = data["safetyFlags"]
forbidden_true_flags = [
    "writesArtifacts",
    "promptContentIncluded",
    "responseContentIncluded",
    "transcriptPersistence",
    "touchesHardware",
    "kv260Access",
    "opensSerialPort",
    "networkCalls",
    "networkScan",
    "runtimeExecution",
    "modelLoaded",
    "modelExecution",
    "providerCalls",
    "cloudCalls",
    "telemetry",
    "automaticUpload",
    "writeBack",
    "executesPccxLab",
    "executesSystemverilogIde",
]

unexpected = [name for name in forbidden_true_flags if flags.get(name)]
if unexpected:
    raise SystemExit("unsafe chat preview flags: {}".format(", ".join(unexpected)))

controls = data["sessionControls"]
blocked = data["blockedReasons"]

print("=== standalone chat surface preview ===")
print("[INFO]  boundary   : read-only local preview; no prompt/model/provider/hardware/lab/IDE execution")
print("[INFO]  session    : {}".format(data["sessionId"]))
print("[INFO]  target     : {}".format(data["targetDevice"]))
print("[INFO]  model      : {}".format(data["targetModel"]))
print("[INFO]  surface    : {}".format(data["surfaceState"]))
print("[INFO]  chat       : {}".format(data["chatState"]))
print("[INFO]  input      : {}".format(data["inputState"]))
print("[INFO]  send       : {}".format(data["sendState"]))
print("[INFO]  model load : {}".format(data["modelStatus"]))
print("[INFO]  transcript : {} / {}".format(
    data["transcriptPolicy"]["state"],
    data["transcriptPolicy"]["persistence"],
))
print("[INFO]  response   : {}".format(data["messageEnvelope"]["responseState"]))
print("")
print("[CHAT]  system     : local chat is blocked until readiness and session evidence exist")
print("[CHAT]  input      : ready for future explicit input; no content is captured here")
print("[CHAT]  assistant  : unavailable")
print("")
print("[INFO]  controls")
for control in controls:
    enabled = "enabled" if control["enabled"] else "disabled"
    print("[INFO]    {} : {} ({})".format(
        control["controlId"],
        control["state"],
        enabled,
    ))
print("")
print("[INFO]  blocked reasons")
for reason in blocked:
    print("[INFO]    {} -> {}".format(
        reason["reasonId"],
        reason["requiredBefore"],
    ))
print("")
print("[INFO]  safety     : readOnly=true dataOnly=true runtimeExecution=false modelExecution=false kv260Access=false providerCalls=false")
'
