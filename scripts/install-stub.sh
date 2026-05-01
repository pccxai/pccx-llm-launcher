#!/usr/bin/env bash
# scripts/install-stub.sh — preview of the *intended* install flow.
#
# This script does NOT install anything. It only describes which package
# / runtime / device pieces the eventual launcher install path will need
# and reports which of them are already available on the current host.
#
# Real installation is gated on KV260 bring-up evidence from
# pccxai/pccx-FPGA-NPU-LLM-kv260. Until that lands, we keep the install
# path honest as a preview.
#
# Always exits 0 (preview-only).

set -u

INFO()  { printf '[INFO]  %s\n' "$*"; }
NOTE()  { printf '[NOTE]  %s\n' "$*"; }
HEAD()  { printf '\n=== %s ===\n' "$*"; }

HEAD "host runtime requirements (planned)"
have_count=0
miss_count=0
for cmd in bash python3 git curl tar; do
    if command -v "$cmd" >/dev/null 2>&1; then
        INFO "$cmd : present ($(command -v "$cmd"))"
        have_count=$((have_count + 1))
    else
        NOTE "$cmd : missing — install via the host package manager before launcher work"
        miss_count=$((miss_count + 1))
    fi
done

HEAD "device-side requirements (target / future)"
NOTE "KV260 bitstream / overlay : provided later by pccxai/pccx-FPGA-NPU-LLM-kv260"
NOTE "kernel / driver           : provided later by pccxai/pccx-FPGA-NPU-LLM-kv260"
NOTE "model artifact            : Gemma 3N E4B is a target, not bundled here"

HEAD "pccx-lab integration (target / future)"
NOTE "diagnostics integration   : depends on pccx-lab CLI / core boundary"
NOTE "trace surfacing           : same dependency"

HEAD "summary"
INFO "host runtime present : ${have_count}"
INFO "host runtime missing : ${miss_count}"
NOTE "this script is a preview; it has not installed anything"
exit 0
