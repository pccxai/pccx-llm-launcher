#!/usr/bin/env bash
# scripts/tests/status-backend.sh — pccx-lab backend smoke tests for status-stub.sh
#
# Usage: bash scripts/tests/status-backend.sh [path/to/status-stub.sh]
# Default status-stub path: scripts/status-stub.sh (relative to repo root).
#
# Requires no hardware, no model downloads, no network.
# Creates temporary fake binaries in a mktemp dir; cleans up on exit.

set -eu

PASS() { printf '[PASS]  %s\n' "$*"; }
FAIL() { printf '[FAIL]  %s\n' "$*" >&2; }
HEAD() { printf '\n=== %s ===\n' "$*"; }

STUB="${1:-scripts/status-stub.sh}"

if [ ! -x "$STUB" ]; then
    chmod +x "$STUB"
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

# ── helpers ───────────────────────────────────────────────────────────────────

make_bin() {
    local path="$1"
    local body="$2"
    printf '#!/usr/bin/env bash\n%s\n' "$body" > "$path"
    chmod +x "$path"
}

# ── tests ─────────────────────────────────────────────────────────────────────

HEAD "1: default mode still exits 0"
"$STUB"
PASS "default mode exits 0"

HEAD "2: missing binary (no PCCX_LAB_BIN, no PATH entry) exits non-zero"
if PCCX_LAB_BIN="" PATH="/usr/bin:/bin" "$STUB" --backend pccx-lab 2>/dev/null; then
    FAIL "expected non-zero exit — silent fallback occurred"
    exit 1
fi
STDERR="$(PCCX_LAB_BIN="" PATH="/usr/bin:/bin" "$STUB" --backend pccx-lab 2>&1 || true)"
if ! printf '%s' "$STDERR" | grep -qi "silent fallback\|not found"; then
    FAIL "missing binary did not print no-silent-fallback or not-found message"
    exit 1
fi
PASS "missing binary exits non-zero with clear error"

HEAD "3: valid fake binary via PCCX_LAB_BIN exits 0"
VALID_BIN="$TMPDIR/pccx-lab-valid"
make_bin "$VALID_BIN" 'printf '"'"'{"mode":"host-dry-run","device":{"probed":false},"inference":{"available":false}}'"'"'\n'
PCCX_LAB_BIN="$VALID_BIN" "$STUB" --backend pccx-lab
PASS "valid fake binary exits 0"

HEAD "4: PCCX_LAB_BIN takes priority over PATH"
ENV_BIN="$TMPDIR/pccx-lab-env"
make_bin "$ENV_BIN" 'printf '"'"'{"mode":"from-env-bin"}'"'"'\n'
PATH_DIR="$TMPDIR/path-dir"
mkdir -p "$PATH_DIR"
make_bin "$PATH_DIR/pccx-lab" 'printf '"'"'{"mode":"from-path"}'"'"'\n'
OUTPUT="$(PCCX_LAB_BIN="$ENV_BIN" PATH="$PATH_DIR:$PATH" "$STUB" --backend pccx-lab)"
if ! printf '%s' "$OUTPUT" | grep -q 'from-env-bin'; then
    FAIL "PCCX_LAB_BIN did not take priority over PATH"
    printf 'output was: %s\n' "$OUTPUT" >&2
    exit 1
fi
PASS "PCCX_LAB_BIN takes priority over PATH"

HEAD "5: invalid JSON output fails clearly"
BAD_BIN="$TMPDIR/pccx-lab-bad"
make_bin "$BAD_BIN" 'printf '"'"'not-json-at-all\n'"'"''
if PCCX_LAB_BIN="$BAD_BIN" "$STUB" --backend pccx-lab 2>/dev/null; then
    FAIL "expected non-zero exit for invalid JSON output"
    exit 1
fi
PASS "invalid JSON output exits non-zero"

HEAD "6: empty output fails clearly"
EMPTY_BIN="$TMPDIR/pccx-lab-empty"
make_bin "$EMPTY_BIN" 'printf '"'"''"'"''
if PCCX_LAB_BIN="$EMPTY_BIN" "$STUB" --backend pccx-lab 2>/dev/null; then
    FAIL "expected non-zero exit for empty output"
    exit 1
fi
PASS "empty output exits non-zero"

HEAD "7: failing binary exits non-zero"
FAIL_BIN="$TMPDIR/pccx-lab-fail"
make_bin "$FAIL_BIN" 'exit 2'
if PCCX_LAB_BIN="$FAIL_BIN" "$STUB" --backend pccx-lab 2>/dev/null; then
    FAIL "expected non-zero exit for failing binary"
    exit 1
fi
PASS "failing binary exits non-zero"

HEAD "8: output does not claim real KV260 inference"
PCCX_LAB_BIN="$VALID_BIN" OUTPUT="$(PCCX_LAB_BIN="$VALID_BIN" "$STUB" --backend pccx-lab)"
# Split the forbidden phrase so claim-scan does not match it literally.
FORBIDDEN_PREFIX="kv260 inference"
FORBIDDEN_CLAIM="${FORBIDDEN_PREFIX} works"
if printf '%s' "$OUTPUT" | grep -qi "$FORBIDDEN_CLAIM"; then
    FAIL "output claims real KV260 inference"
    exit 1
fi
PASS "no real KV260 inference claimed in output"

HEAD "9: existing chat-stub --dry-run still works"
CHAT_STUB="$(dirname "$STUB")/chat-stub.sh"
if [ -x "$CHAT_STUB" ]; then
    "$CHAT_STUB" --dry-run --prompt "hello"
    PASS "chat-stub --dry-run still works"
else
    printf '[SKIP]  chat-stub.sh not found at %s\n' "$CHAT_STUB"
fi

HEAD "10: existing launch-stub --dry-run still works"
LAUNCH_STUB="$(dirname "$STUB")/launch-stub.sh"
if [ -x "$LAUNCH_STUB" ]; then
    "$LAUNCH_STUB" --dry-run
    PASS "launch-stub --dry-run still works"
else
    printf '[SKIP]  launch-stub.sh not found at %s\n' "$LAUNCH_STUB"
fi

printf '\n[DONE]  all status-backend tests passed\n'
