#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STUB="$ROOT/scripts/local-synth.sh"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

fail() {
    printf '[FAIL] %s\n' "$*" >&2
    exit 1
}

require_contains() {
    local output="$1"
    local expected="$2"
    case "$output" in
        *"$expected"*) ;;
        *) fail "missing expected text: $expected" ;;
    esac
}

cat >"$TMPDIR/vivado" <<'SH'
#!/usr/bin/env bash
printf 'fake-vivado %s\n' "$*"
SH
chmod +x "$TMPDIR/vivado"

cat >"$TMPDIR/quartus_sh" <<'SH'
#!/usr/bin/env bash
printf 'fake-quartus %s\n' "$*"
SH
chmod +x "$TMPDIR/quartus_sh"

cat >"$TMPDIR/build.tcl" <<'TCL'
puts "local synth fixture"
TCL

OUTPUT="$(PATH="$TMPDIR:$PATH" bash "$STUB" --detect-only --vendor auto)"
require_contains "$OUTPUT" "vendor     : vivado"
require_contains "$OUTPUT" "offline    : supported"

OUTPUT="$(PATH="$TMPDIR:$PATH" bash "$STUB" --vendor vivado --script "$TMPDIR/build.tcl" --dry-run)"
require_contains "$OUTPUT" "mode       : dry-run"
require_contains "$OUTPUT" "command    :"
require_contains "$OUTPUT" "-mode"
require_contains "$OUTPUT" "-source"

OUTPUT="$(PATH="$TMPDIR:$PATH" bash "$STUB" --vendor quartus --script "$TMPDIR/build.tcl" --run)"
require_contains "$OUTPUT" "mode       : run"
require_contains "$OUTPUT" "fake-quartus -t"

if grep -E '\b(curl|wget|ssh|scp|rsync|nc)\b' "$STUB" >/dev/null; then
    fail "local synth wrapper must not contain network transfer commands"
fi

printf '[DONE] local synthesis wrapper tests passed\n'
