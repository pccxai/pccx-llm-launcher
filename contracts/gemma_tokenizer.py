#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Deterministic local tokenizer shim for Gemma mock orchestration.

This tokenizer is intentionally byte-level and local-only. It does not load
SentencePiece, Hugging Face assets, model files, or tokenizer configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from contracts.gemma_arch_spec import GemmaArchSpec


class GemmaTokenizerError(ValueError):
    """Raised when token IDs cannot be encoded or decoded."""


@dataclass(frozen=True)
class GemmaTokenizer:
    """Byte-level deterministic tokenizer for offline Gemma launcher tests."""

    arch_spec: GemmaArchSpec

    def encode(self, text: str) -> list[int]:
        """Encode prompt text to local mock token IDs."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")
        byte_values = text.encode("utf-8")
        tokens = [self.arch_spec.bos_token_id]
        tokens.extend(self.arch_spec.byte_token_offset + value for value in byte_values)
        tokens.append(self.arch_spec.eos_token_id)
        if len(tokens) > self.arch_spec.context_length:
            raise GemmaTokenizerError("encoded prompt exceeds context_length")
        return tokens

    def encode_generated_text(self, text: str) -> list[int]:
        """Encode generated text without adding a BOS token."""

        if not isinstance(text, str):
            raise TypeError("text must be a string")
        tokens = [
            self.arch_spec.byte_token_offset + value
            for value in text.encode("utf-8")
        ]
        tokens.append(self.arch_spec.eos_token_id)
        return tokens

    def decode(self, token_ids: Sequence[int]) -> str:
        """Decode mock output token IDs to text, stopping at EOS."""

        byte_values: list[int] = []
        for token_id in token_ids:
            if not isinstance(token_id, int):
                raise TypeError("token IDs must be integers")
            if token_id == self.arch_spec.eos_token_id:
                break
            if token_id == self.arch_spec.bos_token_id:
                continue
            value = token_id - self.arch_spec.byte_token_offset
            if value < 0 or value > 255:
                raise GemmaTokenizerError(f"token ID is outside byte range: {token_id}")
            byte_values.append(value)
        return bytes(byte_values).decode("utf-8", errors="strict")
