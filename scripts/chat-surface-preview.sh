#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# Render a read-only standalone chat surface preview from the checked contract.

set -eu

ERROR() { printf '[ERROR] %s\n' "$*" >&2; }

usage() {
    cat <<'EOF'
Usage: bash scripts/chat-surface-preview.sh [--model gemma3n-e4b] [--target kv260] [--html]

Render the local standalone chat surface preview from the data-only
chat/session contract. This does not capture prompts, execute a model,
touch hardware, call providers, invoke pccx-lab, or write artifacts.

Options:
  --html    Render a read-only branded app-shell preview to stdout.
EOF
}

MODEL="gemma3n-e4b"
TARGET="kv260"
FORMAT="terminal"

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
        --html)
            FORMAT="html"
            shift
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

CHAT_SESSION_JSON="$CHAT_SESSION_JSON" PCCX_PREVIEW_FORMAT="$FORMAT" python3 - <<'PY'
import html
import json
import os

data = json.loads(os.environ["CHAT_SESSION_JSON"])
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
preview_format = os.environ["PCCX_PREVIEW_FORMAT"]

if preview_format == "html":
    def esc(value):
        return html.escape(str(value), quote=True)

    def pill_class(state):
        if state in ("blocked", "disabled", "unavailable"):
            return "danger"
        if state in ("not_loaded", "inactive", "placeholder"):
            return "muted"
        return "info"

    print("""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>pccx-llm-launcher surface preview</title>
  <link rel="icon" href="assets/icon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="assets/pccx-ui/launcher.css">
</head>
<body>
  <main class="launcher-window" aria-label="pccx-llm-launcher read-only surface preview">
    <header class="titlebar">
      <div class="traffic" aria-hidden="true">
        <span class="light close"></span>
        <span class="light min"></span>
        <span class="light max"></span>
      </div>
      <div class="brand-lockup">
        <img class="brand-mark" src="assets/pccx-ui/logo-mark.svg" alt="pccx">
        <div class="brand-copy">
          <div class="app-title">pccx-llm-launcher</div>
          <div class="tagline">parallel compute core executor</div>
        </div>
      </div>
      <div class="tb-spacer"></div>
      <div class="tb-target">
        <span class="label">Target</span>
        <span class="pill muted"><span class="dot"></span>""" + esc(data["targetDevice"]) + """</span>
      </div>
      <button class="tb-btn" type="button" disabled>Launch disabled</button>
    </header>
    <section class="launcher-body">
      <nav class="sidebar" aria-label="Launcher sections">
        <div class="nav-item active"><span class="ic">[]</span><span>Chat Surface</span></div>
        <div class="nav-item"><span class="ic">[]</span><span>Model Status</span></div>
        <div class="nav-item"><span class="ic">[]</span><span>Readiness</span></div>
        <div class="nav-item"><span class="ic">[]</span><span>About</span></div>
      </nav>
      <section class="content">
        <div class="grid-2">
          <section class="panel">
            <div class="h"><h3>Chat Surface</h3></div>
            <div class="b">
              <div class="kv">
                <div class="k">Session</div><div class="v mono">""" + esc(data["sessionId"]) + """</div>
                <div class="k">Model</div><div class="v mono">""" + esc(data["targetModel"]) + """</div>
                <div class="k">Surface</div><div class="v"><span class="pill """ + pill_class(data["surfaceState"]) + """"><span class="dot"></span>""" + esc(data["surfaceState"]) + """</span></div>
                <div class="k">Chat</div><div class="v"><span class="pill """ + pill_class(data["chatState"]) + """"><span class="dot"></span>""" + esc(data["chatState"]) + """</span></div>
                <div class="k">Input</div><div class="v mono">""" + esc(data["inputState"]) + """</div>
                <div class="k">Send</div><div class="v"><span class="pill danger"><span class="dot"></span>""" + esc(data["sendState"]) + """</span></div>
              </div>
              <div class="empty">
                <div class="title">No prompt, response, transcript, or session content is rendered.</div>
                <div class="desc">The checked contract keeps this surface read-only while readiness and implementation evidence are incomplete.</div>
              </div>
            </div>
          </section>
          <section class="panel about-panel">
            <div class="h"><h3>About</h3></div>
            <div class="b">
              <img src="assets/pccx-ui/logo-mark.svg" alt="pccx logo" width="48" height="48">
              <p class="surface-note">pccx-UI theme tokens and logo assets are applied to this visual app-shell preview only.</p>
              <div class="safe-note">No model is loaded, no runtime path is executed, no provider is called, and no KV260 access is attempted.</div>
            </div>
          </section>
        </div>
        <section class="panel" style="margin-top:20px">
          <div class="h"><h3>Controls</h3></div>
          <div class="b">
            <div class="sessions">
              <table>
                <thead><tr><th>Control</th><th>State</th><th>Enabled</th></tr></thead>
                <tbody>""")
    for control in controls:
        print("                  <tr><td class=\"mono\">{}</td><td>{}</td><td>{}</td></tr>".format(
            esc(control["controlId"]),
            esc(control["state"]),
            "yes" if control["enabled"] else "no",
        ))
    print("""                </tbody>
              </table>
            </div>
          </div>
        </section>
        <section class="panel" style="margin-top:20px">
          <div class="h"><h3>Blocked Reasons</h3></div>
          <div class="b">
            <div class="console">""")
    for reason in blocked:
        print("[blocked] {} -> {}".format(esc(reason["reasonId"]), esc(reason["requiredBefore"])))
    print("""            </div>
          </div>
        </section>
      </section>
    </section>
  </main>
</body>
</html>""")
    raise SystemExit(0)

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
PY
