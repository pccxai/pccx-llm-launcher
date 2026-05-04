#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
# Print the data-only chat action-bar contract.

set -eu

SCRIPT_DIR="$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)"
ROOT_DIR="$(CDPATH='' cd -- "$SCRIPT_DIR/.." && pwd)"

python3 "$ROOT_DIR/contracts/chat_action_bar_contract.py" "$@"
