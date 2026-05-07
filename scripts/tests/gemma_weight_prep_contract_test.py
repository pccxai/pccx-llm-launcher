#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Tests for the Gemma weight-prep contract."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "gemma_weight_prep_contract.py"
TEST_PATH = Path(__file__).resolve()


def load_module():
    spec = importlib.util.spec_from_file_location(
        "gemma_weight_prep_contract",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_prepare_dummy_seed_42_manifest_invariants() -> None:
    module = load_module()
    manifest = module.GemmaWeightPrep().prepare_dummy(42)

    assert isinstance(manifest, module.Manifest)
    assert manifest.schema_version == module.SCHEMA_VERSION
    assert manifest.manifest_id == "gemma_weight_prep_seed_42_dummy"
    assert manifest.model_id == module.DUMMY_MODEL_ID
    assert manifest.seed == 42
    assert manifest.source_dtype == "bf16_dummy"
    assert manifest.weight_format == "w4_placeholder_dummy"
    assert manifest.pipeline_label == "prepare_dummy"
    assert manifest.real_algo_stage == "stage2"
    assert manifest.hf_touched is False
    assert "real_w4_algo_in_stage2" in manifest.limitations
    assert "no_hf_download_or_weight_load" in manifest.limitations

    assert len(manifest.tiles) == 1
    assert len(manifest.scales) == 1
    tile = manifest.tiles[0]
    scale = manifest.scales[0]
    assert isinstance(tile, module.WeightTile)
    assert isinstance(scale, module.Scale)
    assert tile.tile_id.endswith("_dummy")
    assert scale.scale_id.endswith("_dummy")
    assert tile.source_dtype == "bf16_dummy"
    assert tile.source_shape == module.DUMMY_SOURCE_SHAPE
    assert tile.tile_shape == module.DUMMY_TILE_SHAPE
    assert tile.packed_dtype == "uint4_packed_dummy"
    assert tile.quantization_label == "w4_placeholder_quantize_dummy"
    assert scale.quantization_label == "w4_placeholder_scale_dummy"
    assert tile.scale_id == scale.scale_id
    assert scale.tile_id == tile.tile_id

    expected_byte_count = (4 * 8 + 1) // 2
    assert len(tile.packed_nibbles) == expected_byte_count
    assert tile.packed_nibbles.hex() == "c3d6e639acddb4768c77b7a1f67236bb"
    assert manifest.artifact_ids == ("gemma_weight_tile_0_memory_only_dummy",)
    assert all(artifact.endswith("_dummy") for artifact in manifest.artifact_ids)


def test_prepare_dummy_is_deterministic_and_seeded() -> None:
    module = load_module()
    prep = module.GemmaWeightPrep()
    manifest_a = prep.prepare_dummy(42)
    manifest_b = prep.prepare_dummy(42)
    manifest_c = prep.prepare_dummy(43)

    assert manifest_a == manifest_b
    assert manifest_a.tiles[0].packed_nibbles != manifest_c.tiles[0].packed_nibbles


def test_prepare_real_quantizes_fixture_with_emax_bfp_scales() -> None:
    module = load_module()
    weights = np.array(
        [
            [0.0, 1.0, -1.5, 3.25, -4.0],
            [0.125, -0.25, 0.5, 8.0, -9.25],
        ],
        dtype=np.float32,
    )

    manifest = module.prepare_real(weights, group_size=3)

    assert isinstance(manifest, module.Manifest)
    assert manifest.schema_version == module.SCHEMA_VERSION
    assert manifest.model_id == module.REAL_MODEL_ID
    assert manifest.seed is None
    assert manifest.source_dtype == "bf16"
    assert manifest.weight_format == "w4_int4_emax_bfp_pow2"
    assert manifest.pipeline_label == "prepare_real"
    assert manifest.real_algo_stage == "stage2"
    assert manifest.group_size == 3
    assert manifest.act_scale_policy == module.ACT_SCALE_POLICY
    assert manifest.hf_touched is False
    assert manifest.limitations == (
        "caller_supplied_weights_only",
        "offline_quantization_only",
        "no_hf_download_or_weight_load",
    )

    assert len(manifest.tiles) == 1
    assert len(manifest.scales) == 1
    tile = manifest.tiles[0]
    scale = manifest.scales[0]
    assert isinstance(tile, module.WeightTile)
    assert isinstance(scale, module.Scale)
    assert tile.source_shape == (2, 5)
    assert tile.tile_shape == (2, 5)
    assert tile.packed_dtype == "int4_packed_uint8"
    assert tile.quantization_label == "w4_emax_bfp_pow2"
    assert scale.dtype == "float32"
    assert scale.shape == (2, 2)
    assert scale.values == (0.25, 1.0, 0.125, 2.0)
    assert scale.quantization_label == "w4_emax_bfp_pow2"
    assert tile.scale_id == scale.scale_id
    assert scale.tile_id == tile.tile_id

    expected_packed = bytes.fromhex("403a1c4eb4")
    expected_sha256 = "276f0bbe6289b92fff8b30b97a69588a33e2ccb96941edad9cd2c42496088af0"
    assert tile.packed_nibbles == expected_packed
    assert tile.packed_sha256 == expected_sha256
    assert manifest.packed_sha256 == expected_sha256
    assert hashlib.sha256(tile.packed_nibbles).hexdigest() == expected_sha256


def test_prepare_real_seeded_numpy_fixture_is_deterministic_and_configurable() -> None:
    module = load_module()
    rng = np.random.default_rng(20260507)
    weights = rng.normal(loc=0.0, scale=1.75, size=(3, 7)).astype(np.float32)
    prep = module.GemmaWeightPrep()

    manifest_a = prep.prepare_real(weights, group_size=4)
    manifest_b = prep.prepare_real_w4(weights, group_size=4)
    manifest_c = prep.prepare_real(weights, group_size=2)

    assert manifest_a == manifest_b
    assert manifest_a.group_size == 4
    assert manifest_c.group_size == 2
    assert manifest_a.scales[0].shape == (3, 2)
    assert manifest_c.scales[0].shape == (3, 4)
    assert len(manifest_a.tiles[0].packed_nibbles) == (weights.size + 1) // 2
    assert len(manifest_c.tiles[0].packed_nibbles) == (weights.size + 1) // 2
    assert manifest_a.tiles[0].packed_nibbles[-1] >> 4 == 0
    assert manifest_a.packed_sha256 != manifest_c.packed_sha256
    assert manifest_a.hf_touched is False
    assert manifest_c.hf_touched is False


def test_prepare_real_accepts_higher_rank_array_like_shapes() -> None:
    module = load_module()
    weights = (
        np.arange(30, dtype=np.float32).reshape(2, 3, 5) / np.float32(8.0)
    ) - np.float32(1.5)

    manifest = module.GemmaWeightPrep().prepare_real(weights.tolist(), group_size=4)

    assert manifest.tiles[0].source_shape == (2, 3, 5)
    assert manifest.tiles[0].tile_shape == (2, 3, 5)
    assert manifest.scales[0].shape == (2, 4)
    assert len(manifest.scales[0].values) == 8
    assert len(manifest.tiles[0].packed_nibbles) == (weights.size + 1) // 2
    assert manifest.hf_touched is False


def test_prepare_real_rejects_invalid_inputs() -> None:
    module = load_module()
    prep = module.GemmaWeightPrep()
    valid = np.array([1.0, -1.0], dtype=np.float32)

    for bad_group_size in (0, -1, True, 1.5):
        try:
            prep.prepare_real(valid, group_size=bad_group_size)
        except ValueError as exc:
            assert "group_size" in str(exc)
        else:
            raise AssertionError("expected invalid group_size to fail")

    invalid_weight_sets = (
        np.array([], dtype=np.float32),
        np.array([1.0, np.inf], dtype=np.float32),
        np.array([1.0, np.nan], dtype=np.float32),
    )
    for bad_weights in invalid_weight_sets:
        try:
            prep.prepare_real(bad_weights)
        except ValueError as exc:
            assert "weights" in str(exc)
        else:
            raise AssertionError("expected invalid weights to fail")


def test_source_has_claim_and_hf_guards() -> None:
    source = read_text(MODULE_PATH)
    lowered_source = source.lower()

    forbidden_runtime_terms = [
        "transformers",
        "huggingface_hub",
        "hf_hub_download",
        "from_pretrained",
        ".safetensors",
        ".gguf",
        ".pt",
        ".pth",
        "open(",
        "read_bytes",
        "read_text",
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
    scan_text = source.lower()
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


test_prepare_dummy_seed_42_manifest_invariants()
test_prepare_dummy_is_deterministic_and_seeded()
test_prepare_real_quantizes_fixture_with_emax_bfp_scales()
test_prepare_real_seeded_numpy_fixture_is_deterministic_and_configurable()
test_prepare_real_accepts_higher_rank_array_like_shapes()
test_prepare_real_rejects_invalid_inputs()
test_source_has_claim_and_hf_guards()
test_source_headers_for_touched_code_files()

print("gemma weight prep contract tests ok")
