#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Gemma chat-template formatting for launcher-side prompt construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


GEMMA3N_E4B_CHAT_TEMPLATE_URL = (
    "https://huggingface.co/google/gemma-3n-E4B-it/blob/main/chat_template.jinja"
)


class GemmaChatTemplateError(ValueError):
    """Raised when chat messages cannot be formatted as Gemma turns."""


@dataclass(frozen=True)
class GemmaChatMessage:
    """One normalized chat message consumed by GemmaChatTemplate."""

    role: str
    content: str


@dataclass(frozen=True)
class GemmaChatTemplate:
    """Format chat messages with Gemma user/model turn markers.

    Source: Gemma 3N E4B IT documents this shape in chat_template.jinja at
    https://huggingface.co/google/gemma-3n-E4B-it/blob/main/chat_template.jinja
    """

    bos_token: str = ""

    def format(
        self,
        messages: Sequence[GemmaChatMessage | Mapping[str, str]],
        add_generation_prompt: bool = True,
    ) -> str:
        """Return the rendered Gemma chat-template string."""

        normalized = tuple(_normalize_message(message) for message in messages)
        if not normalized:
            raise GemmaChatTemplateError("messages must not be empty")

        system_prefix = ""
        loop_messages = normalized
        if normalized[0].role == "system":
            system_prefix = normalized[0].content.strip() + "\n\n"
            loop_messages = normalized[1:]
        if not loop_messages:
            raise GemmaChatTemplateError("a user message is required")

        rendered: list[str] = []
        if self.bos_token:
            rendered.append(self.bos_token)

        for index, message in enumerate(loop_messages):
            role = _template_role(message.role)
            expected_role = "user" if index % 2 == 0 else "model"
            if role != expected_role:
                raise GemmaChatTemplateError(
                    "conversation roles must alternate user/assistant/user/assistant",
                )

            content = message.content.strip()
            if index == 0:
                content = system_prefix + content
            rendered.append(f"<start_of_turn>{role}\n{content}<end_of_turn>\n")

        if add_generation_prompt:
            if _template_role(loop_messages[-1].role) != "user":
                raise GemmaChatTemplateError(
                    "generation prompts require the last message to be user",
                )
            rendered.append("<start_of_turn>model\n")

        return "".join(rendered)


def _normalize_message(
    message: GemmaChatMessage | Mapping[str, str],
) -> GemmaChatMessage:
    if isinstance(message, GemmaChatMessage):
        normalized = message
    else:
        try:
            normalized = GemmaChatMessage(
                role=message["role"],
                content=message["content"],
            )
        except KeyError as exc:
            raise GemmaChatTemplateError("messages require role and content") from exc

    if normalized.role not in {"system", "user", "assistant", "model"}:
        raise GemmaChatTemplateError(f"unsupported role: {normalized.role}")
    if not isinstance(normalized.content, str):
        raise TypeError("message content must be a string")
    return normalized


def _template_role(role: str) -> str:
    if role == "assistant":
        return "model"
    return role
