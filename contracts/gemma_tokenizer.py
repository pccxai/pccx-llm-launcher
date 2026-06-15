#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Offline Gemma tokenizer adapter.

The adapter reads a local JSON tokenizer config only. It does not fetch
tokenizers, model weights, or provider data.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOKENIZER_CONFIG_PATH = (
    ROOT / "tests" / "fixtures" / "tokenizer" / "gemma3n-e4b.tokenizer.json"
)


class GemmaTokenizer:
    """Small local tokenizer wrapper for placeholder and BPE-style configs."""

    def __init__(self, config_path: str | Path | None = None) -> None:
        self.config_path = (
            Path(config_path) if config_path is not None else DEFAULT_TOKENIZER_CONFIG_PATH
        )
        self.config = self._load_config(self.config_path)
        self.kind = self._detect_kind(self.config)
        self.vocab = self._load_vocab(self.config)
        self.id_to_piece = {token_id: piece for piece, token_id in self.vocab.items()}
        self.unknown_id = self._lookup_unknown_id()
        self.merges = self._load_merges(self.config)
        self.merge_ranks = {pair: rank for rank, pair in enumerate(self.merges)}

    def encode(self, text: str) -> list[int]:
        """Encode text as local tokenizer ids."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if self.kind == "bpe":
            return self._encode_bpe(text)
        return self._encode_whitespace(text)

    def decode(self, ids: list[int]) -> str:
        """Decode local tokenizer ids back to text."""
        pieces = []
        for token_id in ids:
            if not isinstance(token_id, int):
                raise TypeError("token ids must be integers")
            piece = self.id_to_piece.get(token_id)
            if piece is None:
                pieces.append(self.id_to_piece.get(self.unknown_id, "<unk>"))
            else:
                pieces.append(piece)

        if self.kind == "bpe":
            text = "".join(pieces).replace("▁", " ")
            return " ".join(text.strip().split())

        special_ids = self._special_ids()
        return " ".join(
            piece
            for token_id, piece in zip(ids, pieces)
            if token_id not in special_ids
        )

    @staticmethod
    def _load_config(path: Path) -> dict:
        try:
            with path.open(encoding="utf-8") as fh:
                value = json.load(fh)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"tokenizer config not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"tokenizer config is not valid JSON: {path}") from exc

        if not isinstance(value, dict):
            raise ValueError("tokenizer config must be a JSON object")
        return value

    @staticmethod
    def _detect_kind(config: dict) -> str:
        tokenizer_type = str(config.get("tokenizerType", "")).lower()
        model = config.get("model")
        model_type = str(model.get("type", "")).lower() if isinstance(model, dict) else ""
        if tokenizer_type in {"sentencepiece_bpe", "bpe"} or model_type == "bpe":
            return "bpe"
        return "whitespace"

    @staticmethod
    def _load_vocab(config: dict) -> dict[str, int]:
        model = config.get("model")
        raw_vocab = model.get("vocab") if isinstance(model, dict) else config.get("vocab")
        if not isinstance(raw_vocab, dict) or not raw_vocab:
            raise ValueError("tokenizer config must include a non-empty vocab object")

        vocab: dict[str, int] = {}
        for piece, token_id in raw_vocab.items():
            if not isinstance(piece, str) or not isinstance(token_id, int):
                raise ValueError("vocab entries must map string pieces to integer ids")
            vocab[piece] = token_id
        return vocab

    @staticmethod
    def _load_merges(config: dict) -> list[tuple[str, str]]:
        model = config.get("model")
        raw_merges = model.get("merges") if isinstance(model, dict) else config.get("merges", [])
        if raw_merges is None:
            return []
        if not isinstance(raw_merges, list):
            raise ValueError("BPE merges must be a list")

        merges = []
        for item in raw_merges:
            if isinstance(item, str):
                parts = item.split()
            elif isinstance(item, list):
                parts = item
            else:
                raise ValueError("BPE merge entries must be strings or two-item lists")
            if len(parts) != 2 or not all(isinstance(part, str) for part in parts):
                raise ValueError("BPE merge entries must contain exactly two string pieces")
            merges.append((parts[0], parts[1]))
        return merges

    def _lookup_unknown_id(self) -> int:
        configured_id = self.config.get("unknownId")
        if isinstance(configured_id, int):
            return configured_id
        for piece in ("<unk>", "<UNK>", "[UNK]", "▁<unk>"):
            token_id = self.vocab.get(piece)
            if token_id is not None:
                return token_id
        raise ValueError("tokenizer config must include an unknown token id")

    def _special_ids(self) -> set[int]:
        special_ids = self.config.get("specialIds", [])
        if isinstance(special_ids, list) and all(isinstance(value, int) for value in special_ids):
            return set(special_ids)
        return {
            token_id
            for piece, token_id in self.vocab.items()
            if piece.startswith("<") and piece.endswith(">")
        }

    def _encode_whitespace(self, text: str) -> list[int]:
        return [self.vocab.get(piece, self.unknown_id) for piece in text.split()]

    def _encode_bpe(self, text: str) -> list[int]:
        ids = []
        for word in text.split():
            pieces = self._apply_bpe(list("▁" + word))
            for piece in pieces:
                ids.append(self.vocab.get(piece, self.unknown_id))
        return ids

    def _apply_bpe(self, pieces: list[str]) -> list[str]:
        if not self.merge_ranks:
            return pieces

        while len(pieces) > 1:
            candidates = [
                (self.merge_ranks[pair], index, pair)
                for index, pair in enumerate(zip(pieces, pieces[1:]))
                if pair in self.merge_ranks
            ]
            if not candidates:
                break
            _, index, pair = min(candidates)
            pieces = pieces[:index] + [pair[0] + pair[1]] + pieces[index + 2 :]
        return pieces


def load_default_gemma_tokenizer() -> GemmaTokenizer:
    """Return the default offline Gemma tokenizer."""
    return GemmaTokenizer()
