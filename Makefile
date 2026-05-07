# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

PYTHON ?= python3
SHELLCHECK ?= shellcheck
MODEL ?= gemma3n-e4b
TARGET ?= kv260
CHAT_PROMPT ?= hello
STATUS_STUB ?= scripts/status-stub.sh

PY_TESTS := $(sort $(wildcard scripts/tests/*_test.py))
STATUS_TESTS := $(sort $(wildcard scripts/tests/status-*.sh))
SH_SCRIPTS := $(shell find scripts -type f -name '*.sh' -not -name '*.snapshot' 2>/dev/null | sort)
PY_SOURCES := $(shell find contracts scripts/tests -type f -name '*.py' 2>/dev/null | sort)

.PHONY: test lint dummy-e2e chat-mock coverage
.PHONY: python-tests shell-tests

test: python-tests shell-tests

python-tests:
	@for test in $(PY_TESTS); do \
		printf '[TEST] %s\n' "$$test"; \
		$(PYTHON) "$$test"; \
	done

shell-tests:
	@for test in $(STATUS_TESTS); do \
		printf '[TEST] %s\n' "$$test"; \
		bash "$$test" "$(STATUS_STUB)"; \
	done

lint:
	@if command -v "$(SHELLCHECK)" >/dev/null 2>&1; then \
		printf '[LINT] shellcheck scripts\n'; \
		"$(SHELLCHECK)" $(SH_SCRIPTS); \
	else \
		printf '[SKIP] shellcheck not found\n'; \
	fi
	@printf '[LINT] python syntax\n'
	@$(PYTHON) -c 'import ast, pathlib, sys; [ast.parse(pathlib.Path(p).read_text(encoding="utf-8"), filename=p) for p in sys.argv[1:]]' $(PY_SOURCES)

dummy-e2e:
	@bash scripts/check.sh
	@bash scripts/check-device-stub.sh
	@bash scripts/install-stub.sh
	@bash scripts/status-stub.sh --include-device-session
	@bash scripts/status-stub.sh --include-runtime-readiness
	@bash scripts/chat-surface-preview.sh --model "$(MODEL)" --target "$(TARGET)"
	@bash scripts/launch-stub.sh --dry-run
	@bash scripts/chat-stub.sh --dry-run --prompt "$(CHAT_PROMPT)"

chat-mock:
	@bash scripts/chat-stub.sh --dry-run --prompt "$(CHAT_PROMPT)"

coverage:
	@$(PYTHON) -c 'import coverage' >/dev/null 2>&1 || { \
		printf '[ERROR] python coverage module is required. Install with: %s -m pip install coverage\n' "$(PYTHON)" >&2; \
		exit 1; \
	}
	@$(PYTHON) -m coverage erase
	@for test in $(PY_TESTS); do \
		printf '[COV] %s\n' "$$test"; \
		$(PYTHON) -m coverage run --append "$$test"; \
	done
	@$(PYTHON) -m coverage report -m contracts/*.py scripts/tests/*_test.py
