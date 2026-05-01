#!/usr/bin/env bash
# scripts/check.sh — minimal environment / target-device check for
# pccx-llm-launcher. This is intentionally a lightweight, honest probe:
# it reports what is present, but it does NOT claim that any particular
# inference path is wired up. The launcher engine itself is not yet
# imported into this repository.
#
# Exit code 0 always (probe-only). Output is informational.

set -u

INFO()  { printf '[INFO]  %s\n' "$*"; }
NOTE()  { printf '[NOTE]  %s\n' "$*"; }
WARN()  { printf '[WARN]  %s\n' "$*" >&2; }
HEAD()  { printf '\n=== %s ===\n' "$*"; }

HEAD "host"
INFO "uname -s : $(uname -s)"
INFO "uname -m : $(uname -m)"
if [ -r /etc/os-release ]; then
    INFO "$(grep -E '^(NAME|VERSION)=' /etc/os-release | tr '\n' ' ')"
fi

HEAD "tooling"
for cmd in bash python3 cmake g++ shellcheck; do
    if command -v "$cmd" >/dev/null 2>&1; then
        INFO "$cmd     : $(command -v "$cmd")"
    else
        NOTE "$cmd     : not installed"
    fi
done

HEAD "edge-device hints"
if [ -r /proc/device-tree/model ]; then
    MODEL="$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || true)"
    INFO "device-tree model : ${MODEL:-unknown}"
    case "$MODEL" in
        *KV260*|*Kria*) INFO "Kria-class device detected (target platform)" ;;
        *raspberry*|*Raspberry*) INFO "Raspberry Pi class device detected" ;;
    esac
else
    NOTE "device-tree model : not readable on this host (expected on most x86_64 desktops)"
fi

HEAD "launcher status"
NOTE "pccx-llm-launcher does not yet ship a working inference path."
NOTE "KV260 / Gemma 3N E4B support is a target, not a current claim."
NOTE "Hardware readiness depends on pccxai/pccx-FPGA-NPU-LLM-kv260 bring-up."

exit 0
