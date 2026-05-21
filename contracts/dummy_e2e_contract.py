#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Offline dummy end-to-end launcher run.

This contract wires the stage-1 dummy Gemma weight manifest into the offline
AXI command mock backend and emits fake token chunks as a ResultStream. It does
not touch a board, open SSH, read Hugging Face assets, read configuration, or
start a real runtime.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from contracts.axi_cmd_channel import AxiCmdMockBackend, NpuCmd, NpuStat
from contracts.gemma_weight_prep_contract import GemmaWeightPrep, Manifest


SCHEMA_VERSION = "pccx.dummyE2EResultStream.v0"
TOKEN_COUNT = 6


@dataclass(frozen=True)
class CommandTrace:
    """One scripted command issued to the offline AXI mock backend."""

    name: str
    command: NpuCmd
    status: NpuStat
    mmio_cmd: int
    mmio_stat: int


@dataclass(frozen=True)
class FakeToken:
    """One deterministic fake token emitted by the dummy ResultStream."""

    index: int
    text: str


@dataclass(frozen=True)
class ResultStream:
    """Deterministic, offline-only fake token stream for launcher tests."""

    schema_version: str
    stream_id: str
    seed: int
    manifest_id: str
    model_id: str
    command_trace: tuple[CommandTrace, ...]
    tokens: tuple[FakeToken, ...]
    completed: bool
    limitations: tuple[str, ...]
    safety_flags: tuple[tuple[str, bool], ...]

    @property
    def token_count(self) -> int:
        return len(self.tokens)

    @property
    def text(self) -> str:
        return " ".join(token.text for token in self.tokens)


def dummy_e2e(seed: int) -> ResultStream:
    """Run the offline dummy manifest -> AXI mock -> ResultStream path."""

    manifest = GemmaWeightPrep().prepare_dummy(seed)
    commands = _scripted_commands(seed, manifest)

    traces: list[CommandTrace] = []
    with AxiCmdMockBackend(_scripted_replies(commands)) as backend:
        for name, command, _status in commands:
            backend.issue(command)
            status = backend.poll_stat()
            registers = backend.snapshot_registers()
            traces.append(
                CommandTrace(
                    name=name,
                    command=command,
                    status=status,
                    mmio_cmd=registers["MMIO_CMD"],
                    mmio_stat=registers["MMIO_STAT"],
                ),
            )
        backend.assert_script_consumed()

    return ResultStream(
        schema_version=SCHEMA_VERSION,
        stream_id=f"dummy_e2e_seed_{seed}",
        seed=seed,
        manifest_id=manifest.manifest_id,
        model_id=manifest.model_id,
        command_trace=tuple(traces),
        tokens=_fake_tokens(seed, manifest),
        completed=True,
        limitations=(
            "dummy_manifest_only",
            "fake_tokens_only",
            "no_board_access",
            "no_ssh",
            "no_hf_download_or_weight_load",
        ),
        safety_flags=(
            ("offlineOnly", True),
            ("deterministic", True),
            ("dummyManifestOnly", True),
            ("fakeTokensOnly", True),
            ("boardAccess", False),
            ("sshExecution", False),
            ("hfTouched", False),
            ("networkCalls", False),
            ("environmentRead", False),
            ("modelExecution", False),
        ),
    )


def format_dummy_e2e_summary(stream: ResultStream) -> str:
    """Render concise CLI output for the dummy-e2e subcommand."""

    return "\n".join(
        (
            "dummy_e2e: ok",
            f"seed: {stream.seed}",
            f"manifest: {stream.manifest_id}",
            f"commands: {len(stream.command_trace)}",
            f"stream: {stream.stream_id}",
            f"tokens: {stream.token_count}",
            f"text: {stream.text}",
            "offline: board=false ssh=false hf=false network=false",
        ),
    ) + "\n"


def _scripted_commands(
    seed: int,
    manifest: Manifest,
) -> tuple[tuple[str, NpuCmd, NpuStat], ...]:
    packed_head = int.from_bytes(manifest.tiles[0].packed_nibbles[:4], "little")
    seed_byte = seed & 0xFF
    tile_count = len(manifest.tiles)
    token_count = TOKEN_COUNT
    return (
        (
            "load_dummy_manifest",
            NpuCmd(opcode=1, arg0=seed_byte, arg1=tile_count, arg2=packed_head, flags=1),
            NpuStat(completion_count=1, last_opcode=1, status_code=0),
        ),
        (
            "prime_fake_stream",
            NpuCmd(opcode=2, arg0=token_count, arg1=seed_byte, arg2=packed_head, flags=2),
            NpuStat(completion_count=2, last_opcode=2, status_code=0),
        ),
        (
            "finish_fake_stream",
            NpuCmd(opcode=3, arg0=token_count, arg1=tile_count, arg2=packed_head, flags=4),
            NpuStat(completion_count=3, last_opcode=3, status_code=0),
        ),
    )


def _scripted_replies(
    commands: tuple[tuple[str, NpuCmd, NpuStat], ...],
) -> tuple[tuple[NpuCmd, NpuStat], ...]:
    return tuple((command, status) for _name, command, status in commands)


def _fake_tokens(seed: int, manifest: Manifest) -> tuple[FakeToken, ...]:
    vocabulary = (
        "dummy",
        "gemma",
        "axi",
        "stream",
        "offline",
        "tile",
        "mock",
        "result",
    )
    packed_seed = int.from_bytes(manifest.tiles[0].packed_nibbles[-4:], "little")
    rng = random.Random((seed << 32) ^ packed_seed)
    return tuple(
        FakeToken(index=index, text=f"{rng.choice(vocabulary)}_{rng.randrange(16):x}")
        for index in range(TOKEN_COUNT)
    )
