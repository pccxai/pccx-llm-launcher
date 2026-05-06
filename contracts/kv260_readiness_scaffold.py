#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Typed, data-only KV260 readiness scaffold.

This module defines launcher-side interfaces for future KV260 readiness work.
It does not open target sessions, execute target commands, read model assets,
access MMIO, load bitstreams, or contact provider services.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator, Mapping, Protocol, Sequence


UCA_REG_INSTR_LO = 0x00
UCA_REG_INSTR_HI = 0x04
UCA_REG_STATUS = 0x08
UCA_STAT_BUSY = 1 << 0
UCA_STAT_DONE = 1 << 1


class NpuOpcode(Enum):
    """pccx v002 opcode nibble mirrored from sibling `isa_pkg.sv`."""

    GEMV = 0x0
    GEMM = 0x1
    MEMCPY = 0x2
    MEMSET = 0x3
    CVO = 0x4


@dataclass(frozen=True)
class KV260Connection:
    """KV260 target configuration presence without value disclosure.

    `from_env()` reads `KVFPGA_HOST`, `KVFPGA_USER`, and `KVFPGA_PASSWORD`.
    The configured-value flags are public. Raw values are stored only for a
    future reviewed connection boundary and are excluded from repr/compare.
    """

    host_configured: bool
    user_configured: bool
    password_configured: bool
    _host: str | None = field(default=None, repr=False, compare=False)
    _user: str | None = field(default=None, repr=False, compare=False)
    _password: str | None = field(default=None, repr=False, compare=False)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "KV260Connection":
        source = os.environ if env is None else env
        host = source.get("KVFPGA_HOST")
        user = source.get("KVFPGA_USER")
        password = source.get("KVFPGA_PASSWORD")
        return cls(
            host_configured=bool(host),
            user_configured=bool(user),
            password_configured=bool(password),
            _host=host,
            _user=user,
            _password=password,
        )

    def is_configured(self) -> bool:
        return (
            self.host_configured
            and self.user_configured
            and self.password_configured
        )

    def is_reachable(self) -> bool:
        raise NotImplementedError("data-only scaffold; no target access")

    def kernel_uname(self) -> str:
        raise NotImplementedError("data-only scaffold; no target command")

    def xrt_present(self) -> bool:
        raise NotImplementedError("data-only scaffold; no target command")

    def xmutil_listapps(self) -> Sequence[str]:
        raise NotImplementedError("data-only scaffold; no target command")


@dataclass(frozen=True)
class NPUStatus:
    """Read-only snapshot shape for future launcher status panels."""

    bitstream_loaded: bool
    bitstream_uuid: str | None
    axi_base_addr: int | None
    axi_stat_register_value: int | None
    last_error: str | None


@dataclass(frozen=True)
class HFWeightSource:
    """External Hugging Face weight source descriptor.

    The descriptor names a source but does not download, load, hash, or copy
    weight files. Callers must supply any future evidence through reviewed
    lower-layer tooling.
    """

    model_id: str
    revision: str | None = None


@dataclass(frozen=True)
class LoadedHFWeights:
    """Opaque marker for a future loaded-weight handoff."""

    source: HFWeightSource


@dataclass(frozen=True)
class QuantizedW4Weights:
    """Opaque marker for future 4-bit weight quantization output."""

    source: HFWeightSource


@dataclass(frozen=True)
class QuantizedA8Weights:
    """Opaque marker for future 8-bit activation quantization metadata."""

    source: HFWeightSource


@dataclass(frozen=True)
class GemmaWeightManifest:
    """Documented manifest emitted after future weight preparation.

    Fields:
    `schema_version`: Manifest schema identifier for compatibility gates.
    `model_id`: External model identifier, for example a Gemma target id.
    `source_revision`: Optional external revision string supplied by caller.
    `weight_format`: Prepared weight precision, expected to describe W4.
    `activation_format`: Prepared activation precision, expected to describe A8.
    `tensor_count`: Count of tensors represented by the manifest.
    `artifact_paths`: Relative artifact references supplied by a future reviewed
    packager; this scaffold never creates, reads, or validates those paths.
    `checksums`: Optional digest strings supplied by a future reviewed packager.
    `evidence_refs`: Evidence identifiers required before runtime claims change.
    `limitations`: Known gaps that keep the manifest data-only.
    """

    schema_version: str
    model_id: str
    source_revision: str | None
    weight_format: str
    activation_format: str
    tensor_count: int
    artifact_paths: tuple[str, ...]
    checksums: Mapping[str, str]
    evidence_refs: tuple[str, ...]
    limitations: tuple[str, ...]


class GemmaWeightPrep:
    """Typed pipeline shell; every step is intentionally unimplemented."""

    def load_hf(self, source: HFWeightSource) -> LoadedHFWeights:
        raise NotImplementedError("data-only scaffold; no HF download or load")

    def quantize_W4(self, weights: LoadedHFWeights) -> QuantizedW4Weights:
        raise NotImplementedError("data-only scaffold; no quantization")

    def quantize_A8(self, weights: QuantizedW4Weights) -> QuantizedA8Weights:
        raise NotImplementedError("data-only scaffold; no quantization")

    def emit_manifest(self, weights: QuantizedA8Weights) -> GemmaWeightManifest:
        raise NotImplementedError("data-only scaffold; no artifact emission")


@dataclass(frozen=True)
class NpuCmd:
    """AXI command mirror for the current sibling driver boundary.

    The sibling KV260 repo uses a 64-bit VLIW instruction, written as two
    32-bit AXI-Lite words: `UCA_REG_INSTR_LO` then `UCA_REG_INSTR_HI`.
    The opcode nibble is mirrored from `isa_pkg.sv`; status bits are mirrored
    from the sibling HAL/status handoff.
    """

    instruction: int

    def __post_init__(self) -> None:
        if not 0 <= self.instruction <= 0xFFFFFFFFFFFFFFFF:
            raise ValueError("instruction must fit in 64 bits")

    @property
    def lo32(self) -> int:
        return self.instruction & 0xFFFFFFFF

    @property
    def hi32(self) -> int:
        return (self.instruction >> 32) & 0xFFFFFFFF


@dataclass(frozen=True)
class NpuStat:
    """32-bit AXI status mirror: bit 0 busy, bit 1 done, bits 31:2 reserved."""

    raw: int

    def __post_init__(self) -> None:
        if not 0 <= self.raw <= 0xFFFFFFFF:
            raise ValueError("status must fit in 32 bits")

    @property
    def busy(self) -> bool:
        return bool(self.raw & UCA_STAT_BUSY)

    @property
    def done(self) -> bool:
        return bool(self.raw & UCA_STAT_DONE)

    @property
    def reserved(self) -> int:
        return self.raw >> 2


class AxiCmdChannel(Protocol):
    """Readiness-time command channel shape without MMIO access."""

    def issue(self, cmd: NpuCmd) -> None:
        raise NotImplementedError("data-only scaffold; no AXI write")

    def poll_stat(self) -> NpuStat:
        raise NotImplementedError("data-only scaffold; no AXI read")


@dataclass(frozen=True)
class TensorChunk:
    """Output tensor chunk descriptor supplied by a future runtime handoff."""

    name: str
    dtype: str
    shape: tuple[int, ...]
    data: bytes = field(repr=False)


@dataclass(frozen=True)
class OutputItem:
    """One result-stream item: token text, tensor data, or control marker."""

    index: int
    token: str | None = None
    tensor: TensorChunk | None = None
    finish_reason: str | None = None


class ResultStream(Protocol):
    """Typed iterator over future output tokens or tensors."""

    def __iter__(self) -> Iterator[OutputItem]:
        raise NotImplementedError("data-only scaffold; no runtime stream")


class EmptyResultStream:
    """Deterministic empty stream for type-only tests and disabled UI states."""

    def __iter__(self) -> Iterator[OutputItem]:
        return iter(())
