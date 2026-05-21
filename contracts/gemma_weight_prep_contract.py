#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Stage-1 Gemma weight-prep contract and deterministic dummy manifest.

This module is a data-only contract for the future Gemma weight-preparation
pipeline. Stage 1 intentionally avoids Hugging Face downloads, filesystem
weight loads, and real W4 quantization. The dummy path exists only to exercise
manifest shape, invariants, and deterministic test coverage.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


SCHEMA_VERSION = "pccx.gemmaWeightPrepManifest.v1"
DUMMY_MODEL_ID = "gemma3n-e4b-dummy"
DUMMY_TILE_ID = "gemma3n_e4b_layer0_attn_q_proj_tile0_dummy"
DUMMY_SCALE_ID = "gemma3n_e4b_layer0_attn_q_proj_tile0_scale_dummy"
DUMMY_SOURCE_SHAPE = (4, 8)
DUMMY_TILE_SHAPE = (4, 8)


def _product(shape: tuple[int, ...]) -> int:
    total = 1
    for dim in shape:
        total *= dim
    return total


@dataclass(frozen=True)
class Scale:
    """Per-tile scale metadata for a placeholder W4 tile.

    Invariants:
    - `scale_id` is non-empty and unique within its manifest.
    - `tile_id` points to exactly one `WeightTile` in the same manifest.
    - `dtype` and `quantization_label` carry `_dummy` to prevent real-W4 claims.
    - `shape` contains positive dimensions and matches the value count.
    - `values` are finite positive placeholders, not calibrated scales.
    """

    scale_id: str
    tile_id: str
    dtype: str
    shape: tuple[int, ...]
    values: tuple[float, ...]
    quantization_label: str

    def __post_init__(self) -> None:
        if not self.scale_id:
            raise ValueError("scale_id must be non-empty")
        if not self.tile_id:
            raise ValueError("tile_id must be non-empty")
        if not self.dtype.endswith("_dummy"):
            raise ValueError("dtype must be labelled _dummy")
        if not self.quantization_label.endswith("_dummy"):
            raise ValueError("quantization_label must be labelled _dummy")
        if not self.shape or any(dim <= 0 for dim in self.shape):
            raise ValueError("shape must contain positive dimensions")
        if len(self.values) != _product(self.shape):
            raise ValueError("values must match shape element count")
        if any((not math.isfinite(value)) or value <= 0.0 for value in self.values):
            raise ValueError("scale values must be finite and positive")


@dataclass(frozen=True)
class WeightTile:
    """Packed placeholder W4 tile derived from BF16-shaped dummy data.

    Invariants:
    - `tile_id` is non-empty and unique within its manifest.
    - `source_dtype` and `packed_dtype` carry `_dummy` labels.
    - `source_shape` and `tile_shape` have the same rank and positive dimensions.
    - `packed_nibbles` has two placeholder W4 nibbles per byte, rounded up.
    - `scale_id` points to exactly one `Scale` in the same manifest.
    - The bytes are deterministic dummy payload, not a real W4 algorithm output.
    """

    tile_id: str
    source_dtype: str
    source_shape: tuple[int, ...]
    tile_shape: tuple[int, ...]
    packed_dtype: str
    quantization_label: str
    packed_nibbles: bytes
    scale_id: str

    def __post_init__(self) -> None:
        if not self.tile_id:
            raise ValueError("tile_id must be non-empty")
        if not self.source_dtype.endswith("_dummy"):
            raise ValueError("source_dtype must be labelled _dummy")
        if not self.packed_dtype.endswith("_dummy"):
            raise ValueError("packed_dtype must be labelled _dummy")
        if not self.quantization_label.endswith("_dummy"):
            raise ValueError("quantization_label must be labelled _dummy")
        if not self.source_shape or any(dim <= 0 for dim in self.source_shape):
            raise ValueError("source_shape must contain positive dimensions")
        if len(self.tile_shape) != len(self.source_shape):
            raise ValueError("tile_shape must have the same rank as source_shape")
        if any(dim <= 0 for dim in self.tile_shape):
            raise ValueError("tile_shape must contain positive dimensions")
        if any(
            tile_dim > source_dim
            for tile_dim, source_dim in zip(self.tile_shape, self.source_shape)
        ):
            raise ValueError("tile_shape cannot exceed source_shape")
        if not self.scale_id:
            raise ValueError("scale_id must be non-empty")

        expected_bytes = (_product(self.tile_shape) + 1) // 2
        if len(self.packed_nibbles) != expected_bytes:
            raise ValueError("packed_nibbles must match placeholder W4 byte count")


@dataclass(frozen=True)
class Manifest:
    """Data-only Gemma weight-prep manifest.

    Invariants:
    - `schema_version` is `SCHEMA_VERSION`.
    - `seed` records the deterministic dummy RNG seed.
    - `weight_format`, `source_dtype`, `pipeline_label`, and artifact ids carry
      `_dummy` labels.
    - Tile and scale identifiers are unique, non-empty, and cross-referenced.
    - `real_algo_stage` is `stage2`; stage 1 must not claim real W4 support.
    - `hf_touched` is always false; this contract never reads HF cache/assets.
    """

    schema_version: str
    manifest_id: str
    model_id: str
    seed: int
    source_dtype: str
    weight_format: str
    pipeline_label: str
    tiles: tuple[WeightTile, ...]
    scales: tuple[Scale, ...]
    artifact_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    real_algo_stage: str
    hf_touched: bool

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("schema_version mismatch")
        if not self.manifest_id:
            raise ValueError("manifest_id must be non-empty")
        if not self.model_id:
            raise ValueError("model_id must be non-empty")
        if not isinstance(self.seed, int):
            raise ValueError("seed must be an int")
        if not self.source_dtype.endswith("_dummy"):
            raise ValueError("source_dtype must be labelled _dummy")
        if not self.weight_format.endswith("_dummy"):
            raise ValueError("weight_format must be labelled _dummy")
        if not self.pipeline_label.endswith("_dummy"):
            raise ValueError("pipeline_label must be labelled _dummy")
        if not self.tiles:
            raise ValueError("manifest must contain at least one tile")
        if not self.scales:
            raise ValueError("manifest must contain at least one scale")
        if any(not artifact_id.endswith("_dummy") for artifact_id in self.artifact_ids):
            raise ValueError("artifact ids must be labelled _dummy")
        if self.real_algo_stage != "stage2":
            raise ValueError("real_algo_stage must be stage2")
        if self.hf_touched is not False:
            raise ValueError("hf_touched must be false")

        tile_ids = tuple(tile.tile_id for tile in self.tiles)
        scale_ids = tuple(scale.scale_id for scale in self.scales)
        if len(set(tile_ids)) != len(tile_ids):
            raise ValueError("tile ids must be unique")
        if len(set(scale_ids)) != len(scale_ids):
            raise ValueError("scale ids must be unique")

        scales_by_tile = {scale.tile_id for scale in self.scales}
        for tile in self.tiles:
            if tile.scale_id not in scale_ids:
                raise ValueError("tile scale_id must reference a manifest scale")
            if tile.tile_id not in scales_by_tile:
                raise ValueError("each tile must have a matching scale")


class GemmaWeightPrep:
    """Stage-1 Gemma weight-prep boundary.

    `prepare_dummy()` is the only implemented pipeline. The real W4 algorithm
    belongs in stage 2 and remains explicitly unimplemented here.
    """

    def prepare_dummy(self, seed: int) -> Manifest:
        """Create a deterministic dummy manifest without loading real weights."""

        rng = random.Random(seed)
        bf16_words = tuple(rng.getrandbits(16) for _ in range(_product(DUMMY_SOURCE_SHAPE)))
        packed = self._placeholder_w4_quantize_dummy(bf16_words)
        scale = Scale(
            scale_id=DUMMY_SCALE_ID,
            tile_id=DUMMY_TILE_ID,
            dtype="float32_dummy",
            shape=(1,),
            values=(1.0,),
            quantization_label="w4_placeholder_scale_dummy",
        )
        tile = WeightTile(
            tile_id=DUMMY_TILE_ID,
            source_dtype="bf16_dummy",
            source_shape=DUMMY_SOURCE_SHAPE,
            tile_shape=DUMMY_TILE_SHAPE,
            packed_dtype="uint4_packed_dummy",
            quantization_label="w4_placeholder_quantize_dummy",
            packed_nibbles=packed,
            scale_id=scale.scale_id,
        )
        return Manifest(
            schema_version=SCHEMA_VERSION,
            manifest_id=f"gemma_weight_prep_seed_{seed}_dummy",
            model_id=DUMMY_MODEL_ID,
            seed=seed,
            source_dtype="bf16_dummy",
            weight_format="w4_placeholder_dummy",
            pipeline_label="prepare_dummy",
            tiles=(tile,),
            scales=(scale,),
            artifact_ids=("gemma_weight_tile_0_memory_only_dummy",),
            evidence_refs=("stage1_dummy_manifest_test",),
            limitations=(
                "dummy_data_only",
                "real_w4_algo_in_stage2",
                "no_hf_download_or_weight_load",
            ),
            real_algo_stage="stage2",
            hf_touched=False,
        )

    def prepare_real_w4(self) -> Manifest:
        raise NotImplementedError("real algo in stage 2")

    @staticmethod
    def _placeholder_w4_quantize_dummy(bf16_words: tuple[int, ...]) -> bytes:
        """Pack deterministic dummy nibbles; this is not real W4 quantization."""

        nibbles = tuple((word >> 8) & 0x0F for word in bf16_words)
        packed = bytearray()
        for index in range(0, len(nibbles), 2):
            lo = nibbles[index]
            hi = nibbles[index + 1] if index + 1 < len(nibbles) else 0
            packed.append(lo | (hi << 4))
        return bytes(packed)
