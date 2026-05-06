#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Tests for the stage-1 Gemma weight-prep contract."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


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


def test_real_w4_algo_is_stage_2_only() -> None:
    module = load_module()
    try:
        module.GemmaWeightPrep().prepare_real_w4()
    except NotImplementedError as exc:
        assert "real algo in stage 2" in str(exc)
    else:
        raise AssertionError("expected real W4 path to remain unimplemented")


def test_source_has_claim_and_hf_guards() -> None:
    source = read_text(MODULE_PATH)
    lowered_source = source.lower()

    forbidden_runtime_terms = [
        "transformers",
        "huggingface_hub",
        "hf_hub_download",
        ".safetensors",
        ".gguf",
        ".pt",
        ".pth",
        "open(",
        "read_bytes",
        "read_text",
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
test_real_w4_algo_is_stage_2_only()
test_source_has_claim_and_hf_guards()
test_source_headers_for_touched_code_files()

print("gemma weight prep contract tests ok")
