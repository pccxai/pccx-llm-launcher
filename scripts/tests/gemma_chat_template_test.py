#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Type-only string tests for Gemma chat-template formatting."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TEST_PATH = Path(__file__).resolve()

from contracts.gemma_chat_template import (
    GEMMA3N_E4B_CHAT_TEMPLATE_URL,
    GemmaChatMessage,
    GemmaChatTemplate,
    GemmaChatTemplateError,
)


def assert_raises(error_type, callback) -> None:
    try:
        callback()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def test_gemma_chat_template_formats_documented_turn_string() -> None:
    formatted: str = GemmaChatTemplate().format(
        [
            GemmaChatMessage(role="system", content="You are concise."),
            GemmaChatMessage(role="user", content=" first "),
            GemmaChatMessage(role="assistant", content=" reply "),
            GemmaChatMessage(role="user", content="second"),
        ],
    )
    expected: str = (
        "<start_of_turn>user\n"
        "You are concise.\n\n"
        "first<end_of_turn>\n"
        "<start_of_turn>model\n"
        "reply<end_of_turn>\n"
        "<start_of_turn>user\n"
        "second<end_of_turn>\n"
        "<start_of_turn>model\n"
    )

    assert isinstance(formatted, str)
    assert formatted == expected


def test_gemma_chat_template_accepts_mapping_messages_and_optional_bos() -> None:
    formatted: str = GemmaChatTemplate(bos_token="<bos>").format(
        [{"role": "user", "content": "hello"}],
    )

    assert formatted == (
        "<bos><start_of_turn>user\n"
        "hello<end_of_turn>\n"
        "<start_of_turn>model\n"
    )


def test_gemma_chat_template_rejects_non_alternating_roles() -> None:
    assert_raises(
        GemmaChatTemplateError,
        lambda: GemmaChatTemplate().format(
            [
                GemmaChatMessage(role="user", content="one"),
                GemmaChatMessage(role="user", content="two"),
            ],
        ),
    )


def test_source_url_is_recorded_without_runtime_claims() -> None:
    source = (ROOT / "contracts" / "gemma_chat_template.py").read_text(
        encoding="utf-8",
    )

    assert GEMMA3N_E4B_CHAT_TEMPLATE_URL in source
    assert "Gemma 3N E4B runs on KV260" not in source


def test_source_headers_for_touched_python_files() -> None:
    for path in [ROOT / "contracts" / "gemma_chat_template.py", TEST_PATH]:
        assert path.read_text(encoding="utf-8").splitlines()[:3] == [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ]


test_gemma_chat_template_formats_documented_turn_string()
test_gemma_chat_template_accepts_mapping_messages_and_optional_bos()
test_gemma_chat_template_rejects_non_alternating_roles()
test_source_url_is_recorded_without_runtime_claims()
test_source_headers_for_touched_python_files()

print("Gemma chat-template tests ok")
