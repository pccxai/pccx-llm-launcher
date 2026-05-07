#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Offline Gemma architecture spec used by launcher-side mock paths."""

from __future__ import annotations

from dataclasses import dataclass


DEFAULT_MODEL_ID = "gemma3n-e4b"
DEFAULT_TARGET = "kv260"
DEFAULT_CONTEXT_LENGTH = 8192
DEFAULT_VOCAB_SIZE = 32000
DEFAULT_EOS_TOKEN_ID = 1
DEFAULT_BOS_TOKEN_ID = 2
DEFAULT_BYTE_TOKEN_OFFSET = 256
DEFAULT_GROUP_SIZE = 64


@dataclass(frozen=True)
class GemmaArchSpec:
    """Small validated config object for Gemma launcher mock orchestration."""

    model_id: str = DEFAULT_MODEL_ID
    target: str = DEFAULT_TARGET
    context_length: int = DEFAULT_CONTEXT_LENGTH
    vocab_size: int = DEFAULT_VOCAB_SIZE
    eos_token_id: int = DEFAULT_EOS_TOKEN_ID
    bos_token_id: int = DEFAULT_BOS_TOKEN_ID
    byte_token_offset: int = DEFAULT_BYTE_TOKEN_OFFSET
    w4_group_size: int = DEFAULT_GROUP_SIZE

    def __post_init__(self) -> None:
        if not self.model_id:
            raise ValueError("model_id must be non-empty")
        if not self.target:
            raise ValueError("target must be non-empty")
        for field_name in (
            "context_length",
            "vocab_size",
            "eos_token_id",
            "bos_token_id",
            "byte_token_offset",
            "w4_group_size",
        ):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{field_name} must be an int")
            if value <= 0:
                raise ValueError(f"{field_name} must be positive")
        if self.byte_token_offset + 255 >= self.vocab_size:
            raise ValueError("byte token range must fit vocab_size")
        if self.bos_token_id == self.eos_token_id:
            raise ValueError("BOS and EOS token IDs must differ")


def default_gemma3n_e4b_kv260_arch_spec() -> GemmaArchSpec:
    """Return the default local Gemma 3N E4B plus KV260 mock config."""

    return GemmaArchSpec()
