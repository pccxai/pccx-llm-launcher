#!/usr/bin/env bash
# PCCX Launcher public smoke test.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

bash scripts/check.sh >/dev/null
bash scripts/status-stub.sh >/dev/null
bash scripts/status-stub.sh --include-runtime-readiness >/dev/null
bash scripts/runtime-readiness-stub.sh --model gemma3n-e4b --target kv260 >/dev/null
bash scripts/device-session-status-stub.sh --model gemma3n-e4b --target kv260 >/dev/null
bash scripts/chat-surface-preview.sh --model gemma3n-e4b --target kv260 >/dev/null
python3 scripts/tests/launcher_ide_contract_test.py >/dev/null
python3 scripts/tests/runtime_readiness_contract_test.py >/dev/null
python3 scripts/tests/model_runtime_descriptor_test.py >/dev/null

echo "pccx-launcher smoke ok"
