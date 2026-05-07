#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Config-only Gemma architecture spec.

This module only parses caller-supplied JSON configuration data. It does not
download model assets, open weight files, construct model objects, or inspect
tokenizer files.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_LAYER_PATTERN = (
    "sliding_attention",
    "sliding_attention",
    "sliding_attention",
    "sliding_attention",
    "full_attention",
)
DEFAULT_ACTIVATION_SPARSITY_PREFIX = 10
DEFAULT_ACTIVATION_SPARSITY = 0.95
W4_BITS_PER_ELEMENT = 4


def _require_positive_int(config: dict[str, Any], key: str) -> int:
    value = config.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{key} must be a positive int")
    return value


def _positive_int_alias(config: dict[str, Any], primary: str, alias: str) -> int:
    key = primary if primary in config else alias
    return _require_positive_int(config, key)


def _normalise_intermediate_sizes(value: Any, num_layers: int) -> tuple[int, ...]:
    if isinstance(value, bool):
        raise ValueError("intermediate_size must be an int or list of ints")
    if isinstance(value, int):
        if value <= 0:
            raise ValueError("intermediate_size must contain positive ints")
        return (value,) * num_layers
    if not isinstance(value, list) or len(value) != num_layers:
        raise ValueError("intermediate_size list length must match num_layers")
    sizes: list[int] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
            raise ValueError("intermediate_size must contain positive ints")
        sizes.append(item)
    return tuple(sizes)


def _default_layer_types(num_layers: int) -> tuple[str, ...]:
    layer_types = [
        DEFAULT_LAYER_PATTERN[index % len(DEFAULT_LAYER_PATTERN)]
        for index in range(num_layers)
    ]
    layer_types[-1] = "full_attention"
    return tuple(layer_types)


def _normalise_layer_types(value: Any, num_layers: int) -> tuple[str, ...]:
    if value is None:
        return _default_layer_types(num_layers)
    if not isinstance(value, list) or len(value) != num_layers:
        raise ValueError("layer_types list length must match num_layers")
    layer_types = tuple(value)
    allowed = {"sliding_attention", "full_attention"}
    if any(not isinstance(item, str) or item not in allowed for item in layer_types):
        raise ValueError("layer_types must contain supported attention labels")
    return layer_types


def _normalise_activation_sparsity(value: Any, num_layers: int) -> tuple[float, ...]:
    if value is None:
        prefix = min(DEFAULT_ACTIVATION_SPARSITY_PREFIX, num_layers)
        return (DEFAULT_ACTIVATION_SPARSITY,) * prefix + (0.0,) * (num_layers - prefix)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        sparsity = float(value)
        if sparsity < 0.0 or sparsity >= 1.0:
            raise ValueError("activation_sparsity_pattern values must be in [0, 1)")
        return (sparsity,) * num_layers
    if not isinstance(value, list) or len(value) != num_layers:
        raise ValueError("activation_sparsity_pattern length must match num_layers")
    pattern: list[float] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError("activation_sparsity_pattern must contain numbers")
        sparsity = float(item)
        if sparsity < 0.0 or sparsity >= 1.0:
            raise ValueError("activation_sparsity_pattern values must be in [0, 1)")
        pattern.append(sparsity)
    return tuple(pattern)


def _w4_packed_bytes(element_count: int) -> int:
    if element_count < 0:
        raise ValueError("element_count must not be negative")
    return (element_count * W4_BITS_PER_ELEMENT + 7) // 8


@dataclass(frozen=True)
class GemmaArchSpec:
    """Gemma 3n text architecture dimensions loaded from JSON config."""

    model_id: str
    model_type: str
    vocab_size: int
    vocab_size_per_layer_input: int
    hidden_size: int
    hidden_size_per_layer_input: int
    intermediate_size: tuple[int, ...]
    num_layers: int
    num_heads: int
    num_key_value_heads: int
    head_dim: int
    max_position_embeddings: int
    sliding_window: int
    layer_types: tuple[str, ...]
    hidden_activation: str
    rms_norm_eps: float
    attention_bias: bool
    tie_word_embeddings: bool
    altup_num_inputs: int
    laurel_rank: int
    num_kv_shared_layers: int
    activation_sparsity_pattern: tuple[float, ...]
    source_url: str = ""

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "GemmaArchSpec":
        """Create a spec from a Gemma config dict or nested `text_config` dict."""

        text_config = config.get("text_config", config)
        if not isinstance(text_config, dict):
            raise ValueError("text_config must be an object when present")

        num_layers = _positive_int_alias(text_config, "num_hidden_layers", "num_layers")
        hidden_size = _require_positive_int(text_config, "hidden_size")
        num_heads = _positive_int_alias(text_config, "num_attention_heads", "num_heads")
        head_dim = _require_positive_int(text_config, "head_dim")
        num_key_value_heads = _require_positive_int(text_config, "num_key_value_heads")
        intermediate_size = _normalise_intermediate_sizes(
            text_config.get("intermediate_size"),
            num_layers,
        )
        layer_types = _normalise_layer_types(text_config.get("layer_types"), num_layers)
        activation_sparsity_pattern = _normalise_activation_sparsity(
            text_config.get("activation_sparsity_pattern"),
            num_layers,
        )

        if hidden_size != num_heads * head_dim:
            raise ValueError("hidden_size must equal num_heads * head_dim")
        if num_key_value_heads > num_heads:
            raise ValueError("num_key_value_heads cannot exceed num_heads")
        if num_heads % num_key_value_heads != 0:
            raise ValueError("num_heads must be divisible by num_key_value_heads")

        attention_bias = text_config.get("attention_bias", False)
        tie_word_embeddings = text_config.get(
            "tie_word_embeddings",
            config.get("tie_word_embeddings", True),
        )
        if not isinstance(attention_bias, bool):
            raise ValueError("attention_bias must be a bool")
        if not isinstance(tie_word_embeddings, bool):
            raise ValueError("tie_word_embeddings must be a bool")

        rms_norm_eps = text_config.get("rms_norm_eps", 1e-6)
        if isinstance(rms_norm_eps, bool) or not isinstance(rms_norm_eps, (int, float)):
            raise ValueError("rms_norm_eps must be numeric")

        hidden_activation = text_config.get("hidden_activation", "gelu_pytorch_tanh")
        if not isinstance(hidden_activation, str) or not hidden_activation:
            raise ValueError("hidden_activation must be a non-empty string")

        source_url = text_config.get("source_url", config.get("source_url", ""))
        if not isinstance(source_url, str):
            raise ValueError("source_url must be a string")

        return cls(
            model_id=str(config.get("model_id", text_config.get("model_id", ""))),
            model_type=str(text_config.get("model_type", config.get("model_type", ""))),
            vocab_size=_require_positive_int(text_config, "vocab_size"),
            vocab_size_per_layer_input=_require_positive_int(
                text_config,
                "vocab_size_per_layer_input",
            ),
            hidden_size=hidden_size,
            hidden_size_per_layer_input=_require_positive_int(
                text_config,
                "hidden_size_per_layer_input",
            ),
            intermediate_size=intermediate_size,
            num_layers=num_layers,
            num_heads=num_heads,
            num_key_value_heads=num_key_value_heads,
            head_dim=head_dim,
            max_position_embeddings=_require_positive_int(
                text_config,
                "max_position_embeddings",
            ),
            sliding_window=_require_positive_int(text_config, "sliding_window"),
            layer_types=layer_types,
            hidden_activation=hidden_activation,
            rms_norm_eps=float(rms_norm_eps),
            attention_bias=attention_bias,
            tie_word_embeddings=tie_word_embeddings,
            altup_num_inputs=_require_positive_int(text_config, "altup_num_inputs"),
            laurel_rank=_require_positive_int(text_config, "laurel_rank"),
            num_kv_shared_layers=_require_positive_int(
                text_config,
                "num_kv_shared_layers",
            ),
            activation_sparsity_pattern=activation_sparsity_pattern,
            source_url=source_url,
        )

    @classmethod
    def from_config_path(cls, path: str | Path) -> "GemmaArchSpec":
        """Load a spec from a checked JSON config file."""

        config = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("config JSON must contain an object")
        return cls.from_config(config)

    def expected_w4_packed_size_bytes(self) -> int:
        """Return packed W4 bytes for the text matrices represented by this spec."""

        return _w4_packed_bytes(self.expected_w4_weight_element_count())

    def expected_w4_weight_element_count(self) -> int:
        """Return the uncompressed element count for W4-packed text matrices."""

        q_out = self.num_heads * self.head_dim
        kv_out = self.num_key_value_heads * self.head_dim

        total = self.vocab_size * self.hidden_size
        if not self.tie_word_embeddings:
            total += self.vocab_size * self.hidden_size

        total += (
            self.vocab_size_per_layer_input
            * self.num_layers
            * self.hidden_size_per_layer_input
        )
        total += self.hidden_size * self.num_layers * self.hidden_size_per_layer_input
        total += (
            2
            * max(0, self.altup_num_inputs - 1)
            * self.hidden_size
            * self.hidden_size
        )

        for layer_intermediate_size in self.intermediate_size:
            attention = (
                self.hidden_size * q_out
                + self.hidden_size * kv_out
                + self.hidden_size * kv_out
                + q_out * self.hidden_size
            )
            mlp = 3 * self.hidden_size * layer_intermediate_size
            laurel = 2 * self.hidden_size * self.laurel_rank
            per_layer_input = 2 * self.hidden_size * self.hidden_size_per_layer_input
            altup = (
                self.altup_num_inputs * self.altup_num_inputs
                + self.altup_num_inputs**3
                + self.hidden_size * self.altup_num_inputs
            )
            total += attention + mlp + laurel + per_layer_input + altup

        return total
