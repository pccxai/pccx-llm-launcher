#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Gemma weight-prep contract and deterministic W4 manifests.

This module is a data-only contract for Gemma weight preparation. It never
downloads Hugging Face assets and never reads weights from disk. Real W4
preparation accepts caller-supplied BF16-shaped numeric weights as an argument;
the caller is responsible for sourcing those values.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from typing import Any

import numpy as np


SCHEMA_VERSION = "pccx.gemmaWeightPrepManifest.v1"
ACT_SCALE_POLICY = "ACT_SCALE_EMAX_BFP"
DEFAULT_GROUP_SIZE = 64
INT4_BITS = 4
INT4_MIN = -8
INT4_MAX = 7
DUMMY_MODEL_ID = "gemma3n-e4b-dummy"
DUMMY_TILE_ID = "gemma3n_e4b_layer0_attn_q_proj_tile0_dummy"
DUMMY_SCALE_ID = "gemma3n_e4b_layer0_attn_q_proj_tile0_scale_dummy"
DUMMY_SOURCE_SHAPE = (4, 8)
DUMMY_TILE_SHAPE = (4, 8)
REAL_MODEL_ID = "gemma3n-e4b-caller-supplied"
REAL_TILE_ID = "gemma3n_e4b_w4_tile0"
REAL_SCALE_ID = "gemma3n_e4b_w4_tile0_scale"
REAL_SOURCE_DTYPE = "bf16"
REAL_SCALE_DTYPE = "float32"
REAL_PACKED_DTYPE = "int4_packed_uint8"
REAL_WEIGHT_FORMAT = "w4_int4_emax_bfp_pow2"
REAL_QUANTIZATION_LABEL = "w4_emax_bfp_pow2"


def _product(shape: tuple[int, ...]) -> int:
    total = 1
    for dim in shape:
        total *= dim
    return total


def _validate_group_size(group_size: int) -> int:
    if isinstance(group_size, bool) or not isinstance(group_size, int):
        raise ValueError("group_size must be a positive int")
    if group_size <= 0:
        raise ValueError("group_size must be a positive int")
    return group_size


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_sha256_hex(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)


def _normalise_weights(weights: Any) -> np.ndarray:
    array = np.asarray(weights, dtype=np.float32)
    if array.size == 0:
        raise ValueError("weights must contain at least one value")
    if any(dim <= 0 for dim in array.shape):
        raise ValueError("weights must not contain empty dimensions")
    if not bool(np.all(np.isfinite(array))):
        raise ValueError("weights must contain only finite values")
    return np.ascontiguousarray(array, dtype=np.float32)


def _channel_rows(array: np.ndarray) -> np.ndarray:
    if array.ndim == 0:
        return array.reshape(1, 1)
    if array.ndim == 1:
        return array.reshape(1, array.shape[0])
    trailing_shape = tuple(int(dim) for dim in array.shape[1:])
    return array.reshape(array.shape[0], _product(trailing_shape))


def _emax_bfp_pow2_scale(group: np.ndarray) -> float:
    max_abs = float(np.max(np.abs(group)))
    if max_abs == 0.0:
        return 1.0

    e_max = math.floor(math.log2(max_abs))
    # INT4 carries one sign bit and three magnitude positions; `e_max - 2`
    # keeps the BFP exponent shared while matching the signed INT4 lane width.
    return math.ldexp(1.0, e_max - (INT4_BITS - 2))


def _quantize_signed_int4(group: np.ndarray, scale: float) -> np.ndarray:
    rounded = np.rint(group.astype(np.float64) / scale)
    return np.clip(rounded, INT4_MIN, INT4_MAX).astype(np.int8)


def _pack_signed_int4_low_nibble_first(values: np.ndarray) -> bytes:
    flat = np.asarray(values, dtype=np.int8).reshape(-1)
    if bool(np.any(flat < INT4_MIN)) or bool(np.any(flat > INT4_MAX)):
        raise ValueError("values must be in signed INT4 range")

    packed = bytearray()
    for index in range(0, len(flat), 2):
        low = int(flat[index]) & 0x0F
        high = int(flat[index + 1]) & 0x0F if index + 1 < len(flat) else 0
        packed.append(low | (high << 4))
    return bytes(packed)


def _real_w4_quantize(
    weights: Any,
    group_size: int,
) -> tuple[tuple[int, ...], tuple[int, int], tuple[float, ...], bytes]:
    group_size = _validate_group_size(group_size)
    array = _normalise_weights(weights)
    source_shape = tuple(int(dim) for dim in array.shape)
    rows = _channel_rows(array)
    channel_count, channel_width = rows.shape
    groups_per_channel = math.ceil(channel_width / group_size)

    scales: list[float] = []
    quantized = np.zeros(rows.shape, dtype=np.int8)
    for channel_index in range(channel_count):
        row = rows[channel_index]
        for group_index in range(groups_per_channel):
            start = group_index * group_size
            stop = min(start + group_size, channel_width)
            group = row[start:stop]
            scale = _emax_bfp_pow2_scale(group)
            scales.append(scale)
            quantized[channel_index, start:stop] = _quantize_signed_int4(group, scale)

    packed = _pack_signed_int4_low_nibble_first(quantized)
    return source_shape, (channel_count, groups_per_channel), tuple(scales), packed


@dataclass(frozen=True)
class Scale:
    """Per-tile scale metadata for a W4 tile.

    Invariants:
    - `scale_id` is non-empty and unique within its manifest.
    - `tile_id` points to exactly one `WeightTile` in the same manifest.
    - Dummy entries carry `_dummy`; real entries use `w4_emax_bfp_pow2`.
    - `shape` contains positive dimensions and matches the value count.
    - `values` are finite positive per-group scales.
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
        is_dummy = self.quantization_label.endswith("_dummy")
        if is_dummy:
            if not self.dtype.endswith("_dummy"):
                raise ValueError("dummy dtype must be labelled _dummy")
        else:
            if self.dtype != REAL_SCALE_DTYPE:
                raise ValueError("real scale dtype must be float32")
            if self.quantization_label != REAL_QUANTIZATION_LABEL:
                raise ValueError("real scale must use w4 e_max BFP label")
        if not self.shape or any(dim <= 0 for dim in self.shape):
            raise ValueError("shape must contain positive dimensions")
        if len(self.values) != _product(self.shape):
            raise ValueError("values must match shape element count")
        if any((not math.isfinite(value)) or value <= 0.0 for value in self.values):
            raise ValueError("scale values must be finite and positive")


@dataclass(frozen=True)
class WeightTile:
    """Packed W4 tile derived from BF16-shaped data.

    Invariants:
    - `tile_id` is non-empty and unique within its manifest.
    - Dummy entries carry `_dummy`; real entries use BF16 source and W4 packing.
    - `source_shape` and `tile_shape` have the same rank.
    - Non-scalar dimensions must be positive.
    - `packed_nibbles` has two signed INT4 nibbles per byte, rounded up.
    - `scale_id` points to exactly one `Scale` in the same manifest.
    - Real entries include a SHA256 digest of the packed bytes.
    """

    tile_id: str
    source_dtype: str
    source_shape: tuple[int, ...]
    tile_shape: tuple[int, ...]
    packed_dtype: str
    quantization_label: str
    packed_nibbles: bytes
    scale_id: str
    packed_sha256: str = ""

    def __post_init__(self) -> None:
        if not self.tile_id:
            raise ValueError("tile_id must be non-empty")
        is_dummy = self.quantization_label.endswith("_dummy")
        if is_dummy:
            if not self.source_dtype.endswith("_dummy"):
                raise ValueError("dummy source_dtype must be labelled _dummy")
            if not self.packed_dtype.endswith("_dummy"):
                raise ValueError("dummy packed_dtype must be labelled _dummy")
        else:
            if self.source_dtype != REAL_SOURCE_DTYPE:
                raise ValueError("real source_dtype must be bf16")
            if self.packed_dtype != REAL_PACKED_DTYPE:
                raise ValueError("real packed_dtype must be int4_packed_uint8")
            if self.quantization_label != REAL_QUANTIZATION_LABEL:
                raise ValueError("real tile must use w4 e_max BFP label")
            if not _is_sha256_hex(self.packed_sha256):
                raise ValueError("real tile must include packed-byte SHA256")
        if any(dim <= 0 for dim in self.source_shape):
            raise ValueError("source_shape dimensions must be positive")
        if len(self.tile_shape) != len(self.source_shape):
            raise ValueError("tile_shape must have the same rank as source_shape")
        if any(dim <= 0 for dim in self.tile_shape):
            raise ValueError("tile_shape dimensions must be positive")
        if any(
            tile_dim > source_dim
            for tile_dim, source_dim in zip(self.tile_shape, self.source_shape)
        ):
            raise ValueError("tile_shape cannot exceed source_shape")
        if not self.scale_id:
            raise ValueError("scale_id must be non-empty")

        expected_bytes = (_product(self.tile_shape) + 1) // 2
        if len(self.packed_nibbles) != expected_bytes:
            raise ValueError("packed_nibbles must match W4 byte count")
        if self.packed_sha256 and (
            self.packed_sha256 != _sha256_bytes(self.packed_nibbles)
        ):
            raise ValueError("packed_sha256 must match packed_nibbles")


@dataclass(frozen=True)
class Manifest:
    """Data-only Gemma weight-prep manifest.

    Invariants:
    - `schema_version` is `SCHEMA_VERSION`.
    - Dummy manifests keep `_dummy` labels for compatibility.
    - Real manifests use the caller-supplied BF16 W4 e_max BFP path.
    - Tile and scale identifiers are unique, non-empty, and cross-referenced.
    - `real_algo_stage` is `stage2`.
    - `hf_touched` is always false; this contract never reads HF cache/assets.
    """

    schema_version: str
    manifest_id: str
    model_id: str
    seed: int | None
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
    group_size: int | None = None
    act_scale_policy: str = ""
    packed_sha256: str = ""

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("schema_version mismatch")
        if not self.manifest_id:
            raise ValueError("manifest_id must be non-empty")
        if not self.model_id:
            raise ValueError("model_id must be non-empty")
        is_dummy = self.pipeline_label.endswith("_dummy")
        if self.seed is not None and not isinstance(self.seed, int):
            raise ValueError("seed must be an int")
        if is_dummy:
            if self.seed is None:
                raise ValueError("dummy seed must be an int")
            if not self.source_dtype.endswith("_dummy"):
                raise ValueError("dummy source_dtype must be labelled _dummy")
            if not self.weight_format.endswith("_dummy"):
                raise ValueError("dummy weight_format must be labelled _dummy")
            if any(
                not artifact_id.endswith("_dummy")
                for artifact_id in self.artifact_ids
            ):
                raise ValueError("dummy artifact ids must be labelled _dummy")
        else:
            if self.seed is not None:
                raise ValueError("real manifest seed must be None")
            if self.source_dtype != REAL_SOURCE_DTYPE:
                raise ValueError("real source_dtype must be bf16")
            if self.weight_format != REAL_WEIGHT_FORMAT:
                raise ValueError("real weight_format must be w4 int4 e_max BFP")
            if self.pipeline_label != "prepare_real":
                raise ValueError("real pipeline_label must be prepare_real")
            _validate_group_size(self.group_size if self.group_size is not None else 0)
            if self.act_scale_policy != ACT_SCALE_POLICY:
                raise ValueError("real act_scale_policy must match e_max BFP policy")
            if not _is_sha256_hex(self.packed_sha256):
                raise ValueError("real manifest must include packed-byte SHA256")
            if any(artifact_id.endswith("_dummy") for artifact_id in self.artifact_ids):
                raise ValueError("real artifact ids must not be labelled _dummy")
        if not self.tiles:
            raise ValueError("manifest must contain at least one tile")
        if not self.scales:
            raise ValueError("manifest must contain at least one scale")
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
        if self.packed_sha256:
            packed = b"".join(tile.packed_nibbles for tile in self.tiles)
            if self.packed_sha256 != _sha256_bytes(packed):
                raise ValueError("manifest packed_sha256 must match manifest tiles")


class GemmaWeightPrep:
    """Gemma weight-prep boundary.

    `prepare_dummy()` remains for stage-1 compatibility. `prepare_real()`
    performs offline W4 quantization for caller-supplied weights only.
    """

    def prepare_dummy(self, seed: int) -> Manifest:
        """Create a deterministic dummy manifest without loading real weights."""

        rng = random.Random(seed)
        bf16_words = tuple(
            rng.getrandbits(16) for _ in range(_product(DUMMY_SOURCE_SHAPE))
        )
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

    def prepare_real(
        self,
        weights: Any,
        group_size: int = DEFAULT_GROUP_SIZE,
    ) -> Manifest:
        """Quantize caller-supplied BF16-shaped weights to signed packed W4."""

        source_shape, scale_shape, scale_values, packed = _real_w4_quantize(
            weights,
            group_size,
        )
        packed_sha256 = _sha256_bytes(packed)
        scale = Scale(
            scale_id=REAL_SCALE_ID,
            tile_id=REAL_TILE_ID,
            dtype=REAL_SCALE_DTYPE,
            shape=scale_shape,
            values=scale_values,
            quantization_label=REAL_QUANTIZATION_LABEL,
        )
        tile = WeightTile(
            tile_id=REAL_TILE_ID,
            source_dtype=REAL_SOURCE_DTYPE,
            source_shape=source_shape,
            tile_shape=source_shape,
            packed_dtype=REAL_PACKED_DTYPE,
            quantization_label=REAL_QUANTIZATION_LABEL,
            packed_nibbles=packed,
            scale_id=scale.scale_id,
            packed_sha256=packed_sha256,
        )
        return Manifest(
            schema_version=SCHEMA_VERSION,
            manifest_id=f"gemma_weight_prep_real_w4_{packed_sha256[:12]}",
            model_id=REAL_MODEL_ID,
            seed=None,
            source_dtype=REAL_SOURCE_DTYPE,
            weight_format=REAL_WEIGHT_FORMAT,
            pipeline_label="prepare_real",
            tiles=(tile,),
            scales=(scale,),
            artifact_ids=(f"gemma_weight_tile_0_memory_only_{packed_sha256[:12]}",),
            evidence_refs=(
                "pccxai/pccx-llm-launcher#73",
                "pccxai/pccx-FPGA-NPU-LLM-kv260#80",
            ),
            limitations=(
                "caller_supplied_weights_only",
                "offline_quantization_only",
                "no_hf_download_or_weight_load",
            ),
            real_algo_stage="stage2",
            hf_touched=False,
            group_size=group_size,
            act_scale_policy=ACT_SCALE_POLICY,
            packed_sha256=packed_sha256,
        )

    def prepare_real_w4(
        self,
        weights: Any,
        group_size: int = DEFAULT_GROUP_SIZE,
    ) -> Manifest:
        """Compatibility alias for the stage-2 real W4 path."""

        return self.prepare_real(weights, group_size)

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


def prepare_real(weights: Any, group_size: int = DEFAULT_GROUP_SIZE) -> Manifest:
    """Module-level entry point for real offline W4 quantization."""

    return GemmaWeightPrep().prepare_real(weights, group_size)
