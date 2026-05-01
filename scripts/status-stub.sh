#!/usr/bin/env bash
# scripts/status-stub.sh — launcher state summary
# Reports what is and is not wired up in this planning skeleton.
# Does not probe hardware. Does not start inference. Always exits 0.

set -u

INFO() { printf '[INFO]  %s\n' "$*"; }
NOTE() { printf '[NOTE]  %s\n' "$*"; }
HEAD() { printf '\n=== %s ===\n' "$*"; }

HEAD "launcher state"
NOTE "chat-stub      : available (dry-run only; see scripts/chat-stub.sh)"
NOTE "launch-stub    : available (dry-run only; --dry-run flag required)"
NOTE "inference path : not active"
NOTE "KV260 path     : gated on pccxai/pccx-FPGA-NPU-LLM-kv260 bring-up"
NOTE "pccx-lab diag  : deferred (depends on pccx-lab CLI/core boundary)"
NOTE "editor bridge  : planned (VS Code / other IDEs)"

HEAD "summary"
INFO "no inference engine is wired up; all paths are planned or deferred"
exit 0
