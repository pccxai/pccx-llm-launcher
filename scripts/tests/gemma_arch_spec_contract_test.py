#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Tests for the config-only Gemma architecture spec."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "gemma_arch_spec_contract.py"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "gemma3n-e4b.config.json"
TEST_PATH = Path(__file__).resolve()


def load_module():
    spec = importlib.util.spec_from_file_location(
        "gemma_arch_spec_contract",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_loads_gemma3n_e4b_placeholder_config() -> None:
    module = load_module()
    arch_spec = module.GemmaArchSpec.from_config_path(FIXTURE_PATH)

    assert isinstance(arch_spec, module.GemmaArchSpec)
    assert arch_spec.model_id == "gemma3n-e4b"
    assert arch_spec.model_type == "gemma3n_text"
    assert arch_spec.hidden_size == 2048
    assert arch_spec.num_layers == 35
    assert arch_spec.num_heads == 8
    assert arch_spec.num_key_value_heads == 2
    assert arch_spec.head_dim == 256
    assert arch_spec.vocab_size == 262400
    assert arch_spec.vocab_size_per_layer_input == 262144
    assert arch_spec.hidden_size_per_layer_input == 256
    assert arch_spec.intermediate_size == (16384,) * 35
    assert arch_spec.max_position_embeddings == 32768
    assert arch_spec.sliding_window == 512
    assert arch_spec.altup_num_inputs == 4
    assert arch_spec.laurel_rank == 64
    assert arch_spec.num_kv_shared_layers == 15
    assert arch_spec.tie_word_embeddings is True
    assert arch_spec.attention_bias is False
    assert len(arch_spec.layer_types) == 35
    assert arch_spec.layer_types.count("full_attention") == 7
    assert arch_spec.layer_types[-1] == "full_attention"
    assert len(arch_spec.activation_sparsity_pattern) == 35
    assert arch_spec.activation_sparsity_pattern[:10] == (0.95,) * 10
    assert arch_spec.activation_sparsity_pattern[10:] == (0.0,) * 25
    assert "huggingface.co/docs/transformers" in arch_spec.source_url


def test_expected_w4_packed_size_math_for_e4b_fixture() -> None:
    module = load_module()
    arch_spec = module.GemmaArchSpec.from_config_path(FIXTURE_PATH)

    hidden_size = 2048
    num_layers = 35
    num_heads = 8
    num_kv_heads = 2
    head_dim = 256
    hidden_size_per_layer_input = 256
    altup_inputs = 4
    laurel_rank = 64
    intermediate_size = 16384

    token_embedding = 262400 * hidden_size
    per_layer_embedding = 262144 * num_layers * hidden_size_per_layer_input
    per_layer_model_projection = hidden_size * num_layers * hidden_size_per_layer_input
    global_altup_projection = 2 * (altup_inputs - 1) * hidden_size * hidden_size

    q_out = num_heads * head_dim
    kv_out = num_kv_heads * head_dim
    attention_per_layer = (
        hidden_size * q_out
        + hidden_size * kv_out
        + hidden_size * kv_out
        + q_out * hidden_size
    )
    mlp_per_layer = 3 * hidden_size * intermediate_size
    laurel_per_layer = 2 * hidden_size * laurel_rank
    per_layer_input_per_layer = 2 * hidden_size * hidden_size_per_layer_input
    altup_per_layer = (
        altup_inputs * altup_inputs + altup_inputs**3 + hidden_size * altup_inputs
    )

    expected_elements = (
        token_embedding
        + per_layer_embedding
        + per_layer_model_projection
        + global_altup_projection
        + num_layers
        * (
            attention_per_layer
            + mlp_per_layer
            + laurel_per_layer
            + per_layer_input_per_layer
            + altup_per_layer
        )
    )

    assert expected_elements == 6866103024
    assert arch_spec.expected_w4_weight_element_count() == expected_elements
    assert arch_spec.expected_w4_packed_size_bytes() == 3433051512


def test_from_nested_text_config_and_defaults_are_supported() -> None:
    module = load_module()
    fixture = json.loads(read_text(FIXTURE_PATH))
    nested = {
        "model_id": "nested-gemma3n-e4b",
        "tie_word_embeddings": True,
        "text_config": {
            key: value
            for key, value in fixture.items()
            if key not in {"_comment", "source_url"}
        },
        "source_url": fixture["source_url"],
    }
    del nested["text_config"]["layer_types"]
    del nested["text_config"]["activation_sparsity_pattern"]

    arch_spec = module.GemmaArchSpec.from_config(nested)

    assert arch_spec.model_id == "nested-gemma3n-e4b"
    assert arch_spec.layer_types == tuple(fixture["layer_types"])
    assert arch_spec.activation_sparsity_pattern == tuple(
        fixture["activation_sparsity_pattern"],
    )
    assert arch_spec.expected_w4_packed_size_bytes() == 3433051512


def test_arch_spec_rejects_inconsistent_config() -> None:
    module = load_module()
    fixture = json.loads(read_text(FIXTURE_PATH))

    bad_hidden = dict(fixture)
    bad_hidden["hidden_size"] = 4096
    try:
        module.GemmaArchSpec.from_config(bad_hidden)
    except ValueError as exc:
        assert "hidden_size" in str(exc)
    else:
        raise AssertionError("expected inconsistent hidden size to fail")

    bad_layers = dict(fixture)
    bad_layers["intermediate_size"] = [16384]
    try:
        module.GemmaArchSpec.from_config(bad_layers)
    except ValueError as exc:
        assert "intermediate_size" in str(exc)
    else:
        raise AssertionError("expected bad intermediate_size length to fail")


def test_source_has_claim_and_weight_load_guards() -> None:
    source = read_text(MODULE_PATH)
    fixture = read_text(FIXTURE_PATH)
    lowered_source = source.lower()
    lowered_fixture = fixture.lower()

    forbidden_runtime_terms = [
        "transformers",
        "huggingface_hub",
        "hf_hub_download",
        "from_pretrained",
        ".safetensors",
        ".gguf",
        ".pt",
        ".pth",
        "np.load",
        "fromfile",
        "memmap",
        "requests",
        "urllib",
        "subprocess",
        "socket",
    ]
    for term in forbidden_runtime_terms:
        assert term not in lowered_source, term

    forbidden_fixture_terms = [
        ".safetensors",
        ".gguf",
        "tokenizer.model",
        "checksum",
        "manifest",
        "/home/",
        "/users/",
    ]
    for term in forbidden_fixture_terms:
        assert term not in lowered_fixture, term

    forbidden_claims = [
        "production-ready",
        "marketplace-ready",
        "stable API",
        "stable ABI",
        "KV260 inference works",
        "Gemma 3N E4B runs on KV260",
        "20 tok/s achieved",
        "timing closed",
        "bitstream ready",
    ]
    scan_text = (source + fixture).lower()
    for claim in forbidden_claims:
        assert claim.lower() not in scan_text, claim


def test_source_headers_for_touched_code_files() -> None:
    expected_headers = {
        MODULE_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        TEST_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
    }
    for path, header in expected_headers.items():
        assert read_text(path).splitlines()[: len(header)] == header, path


test_loads_gemma3n_e4b_placeholder_config()
test_expected_w4_packed_size_math_for_e4b_fixture()
test_from_nested_text_config_and_defaults_are_supported()
test_arch_spec_rejects_inconsistent_config()
test_source_has_claim_and_weight_load_guards()
test_source_headers_for_touched_code_files()

print("gemma arch spec contract tests ok")
