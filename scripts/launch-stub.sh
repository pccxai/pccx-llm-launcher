#!/usr/bin/env bash
# scripts/launch-stub.sh — dry-run preview of the *intended* launcher
# sequence. This script does NOT run inference, does NOT open a model,
# and does NOT talk to a target device. It only describes what the
# launcher will eventually do, in order, so contributors can see the
# planned shape before any of it is wired up.
#
# Hardware readiness (KV260 / Gemma 3N E4B) is gated on
# pccxai/pccx-FPGA-NPU-LLM-kv260 publishing verified bring-up
# evidence. Until that lands, this stub stays as a description.
#
# Always exits 0 (preview-only).

set -u

INFO()  { printf '[INFO]  %s\n' "$*"; }
NOTE()  { printf '[NOTE]  %s\n' "$*"; }
HEAD()  { printf '\n=== %s ===\n' "$*"; }

HEAD "host"
INFO "uname -s : $(uname -s)"
INFO "uname -m : $(uname -m)"
if [ -r /etc/os-release ]; then
    INFO "$(grep -E '^(NAME|VERSION)=' /etc/os-release | tr '\n' ' ')"
fi

HEAD "tooling availability"
for cmd in bash python3 cmake g++ git curl; do
    if command -v "$cmd" >/dev/null 2>&1; then
        INFO "$cmd : $(command -v "$cmd")"
    else
        NOTE "$cmd : not installed (the eventual launcher may need this)"
    fi
done

HEAD "target / device hint"
INFO "target platform (planned) : Xilinx Kria KV260"
INFO "target model (planned)    : Gemma 3N E4B"
if [ -r /proc/device-tree/model ]; then
    MODEL="$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || true)"
    INFO "device-tree model        : ${MODEL:-unknown}"
else
    NOTE "device-tree model        : not readable on this host"
fi

HEAD "planned launch sequence (preview only)"
cat <<'STEPS'
The launcher, once a real engine is wired up, is intended to perform:

  1. Verify host / device prerequisites.
  2. Bind to the target device (via the verified bring-up path supplied
     by pccxai/pccx-FPGA-NPU-LLM-kv260, after that work lands).
  3. Pick a target model (initially Gemma 3N E4B) and a precision mode.
  4. Hand control to a launch backend that drives the actual inference.
  5. Surface logs and diagnostics via pccx-lab integration so device /
     kernel state is visible from the launcher UI.

None of these steps are executed by this script.
STEPS

HEAD "gating dependencies"
NOTE "Step 2 (device binding)    requires pccx-FPGA bring-up evidence."
NOTE "Step 4 (launch backend)    requires that bring-up plus a launcher engine."
NOTE "Step 5 (diagnostics)       requires pccx-lab CLI / core boundary integration."

HEAD "summary"
INFO "preview complete; no inference was started, no device was contacted"
exit 0
