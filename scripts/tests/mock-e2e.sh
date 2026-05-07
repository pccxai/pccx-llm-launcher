#!/usr/bin/env bash
# scripts/tests/mock-e2e.sh - clean-room mock smoke path for the launcher.
#
# Requires no hardware, no model downloads, no provider calls, and no network
# after the repository has been cloned.

set -eu

HEAD() { printf '\n=== %s ===\n' "$*"; }

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$ROOT"

run() {
    HEAD "$*"
    "$@"
}

run bash scripts/check.sh
run bash scripts/check-device-stub.sh
run bash scripts/install-stub.sh
run bash scripts/status-stub.sh
run bash scripts/status-stub.sh --include-device-session
run bash scripts/status-stub.sh --include-runtime-readiness
run bash scripts/launch-stub.sh --dry-run
run bash scripts/chat-stub.sh --dry-run --prompt "hello"

printf '\n[DONE]  mock e2e smoke path completed\n'
