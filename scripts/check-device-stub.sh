#!/usr/bin/env bash
# scripts/check-device-stub.sh — narrowly-scoped device probe.
#
# A focused complement to scripts/check.sh: this stub only inspects what
# is reachable from the host and prints which target-device facts would
# matter once the launcher engine is wired up. It does NOT contact a
# remote device, does NOT flash anything, and does NOT claim that any
# device path is functional.
#
# KV260 / Kria detection is best-effort; on x86_64 hosts the device-tree
# model file is usually missing and that is expected.
#
# Always exits 0 (probe-only).

set -u

INFO()  { printf '[INFO]  %s\n' "$*"; }
NOTE()  { printf '[NOTE]  %s\n' "$*"; }
HEAD()  { printf '\n=== %s ===\n' "$*"; }

HEAD "device-tree probe"
if [ -r /proc/device-tree/model ]; then
    MODEL="$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || true)"
    INFO "model           : ${MODEL:-unknown}"
    case "$MODEL" in
        *KV260*|*Kria*)
            INFO "platform class  : Kria-class (matches the planned target)"
            ;;
        *)
            NOTE "platform class  : not a Kria-class device"
            ;;
    esac
else
    NOTE "model           : /proc/device-tree/model not readable (expected on most x86_64 hosts)"
fi

HEAD "FPGA / accel hints"
for path in /dev/xdma0 /dev/xdma /dev/zynqmp /sys/class/fpga_manager; do
    if [ -e "$path" ]; then
        INFO "$path : present"
    else
        NOTE "$path : absent (expected on a non-target host)"
    fi
done

HEAD "summary"
NOTE "this script is a probe; it does not configure or contact any device"
NOTE "KV260 bring-up evidence comes from pccxai/pccx-FPGA-NPU-LLM-kv260"
exit 0
