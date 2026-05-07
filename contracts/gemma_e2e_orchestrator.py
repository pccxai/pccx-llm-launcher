#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Mock-only Gemma end-to-end launcher orchestrator."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from contracts.axi_cmd_channel import AxiCmdChannel, AxiCmdMockBackend, NpuCmd, NpuStat
from contracts.gemma_arch_spec import GemmaArchSpec, default_gemma3n_e4b_kv260_arch_spec
from contracts.gemma_tokenizer import GemmaTokenizer
from contracts.gemma_weight_prep_contract import GemmaWeightPrep, Manifest
from contracts.kv260_connection_mock import KV260ConnectionMock
from contracts.kv260_serial_connection import KV260ConnectionProtocol, KV260SerialConnection
from contracts.token_stream_over_serial import (
    OP_BEGIN_INPUT,
    OP_END_INPUT,
    OP_READ_OUTPUT,
    TokenStreamOverSerial,
    encode_output_stream,
)


OP_LOAD_W4_MANIFEST = 0x40
MOCK_TTY = "/tmp/pccx-gemma-e2e-mock"


class GemmaE2EOrchestratorError(RuntimeError):
    """Raised when the mock Gemma orchestration path cannot continue."""


class RealSerialGemmaE2ENotImplemented(NotImplementedError):
    """Raised when callers request the future real serial path."""


@dataclass(frozen=True)
class GemmaE2EResult:
    """Observable output from one Gemma mock orchestration run."""

    output_text: str
    prompt_tokens: tuple[int, ...]
    output_tokens: tuple[int, ...]
    manifest_id: str
    manifest_sha256: str
    serial_payload: bytes
    axi_completion_count: int


@dataclass
class ChatSession:
    """Stateful mock Gemma chat session with deterministic turn history."""

    arch_spec: GemmaArchSpec | None = None
    seed: int = 0
    history_file: Path | None = None
    history: list[tuple[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.history_file is not None:
            self.history.extend(load_chat_history(self.history_file))

    def send(self, prompt: str) -> GemmaE2EResult:
        """Send one user turn through the mock orchestrator and store the reply."""

        context = self.context_for(prompt)
        result = run_mock_gemma_chat(context, self.arch_spec, seed=self.seed)
        turn = (("user", prompt), ("assistant", result.output_text))
        self.history.extend(turn)
        if self.history_file is not None:
            append_chat_history(self.history_file, turn)
        return result

    def context_for(self, prompt: str) -> str:
        """Build a Gemma-style chat prompt including prior turns."""

        turns: list[str] = []
        for role, content in self.history:
            gemma_role = "model" if role == "assistant" else role
            turns.extend(
                [
                    f"<start_of_turn>{gemma_role}",
                    content,
                    "<end_of_turn>",
                ],
            )
        turns.extend(
            [
                "<start_of_turn>user",
                prompt,
                "<end_of_turn>",
                "<start_of_turn>model",
            ],
        )
        return "\n".join(turns)


def load_chat_history(path: Path) -> list[tuple[str, str]]:
    """Load role/content history tuples from a JSONL file if it exists."""

    if not path.exists():
        return []
    history: list[tuple[str, str]] = []
    with path.open("r", encoding="utf-8") as history_stream:
        for line_number, line in enumerate(history_stream, start=1):
            line = line.strip()
            if line == "":
                continue
            value = json.loads(line)
            if (
                not isinstance(value, list)
                or len(value) != 2
                or not isinstance(value[0], str)
                or not isinstance(value[1], str)
            ):
                raise ValueError(
                    f"invalid chat history tuple at {path}:{line_number}",
                )
            role, content = value
            if role not in {"user", "assistant"}:
                raise ValueError(
                    f"invalid chat history role at {path}:{line_number}: {role}",
                )
            history.append((role, content))
    return history


def append_chat_history(path: Path, entries: Sequence[tuple[str, str]]) -> None:
    """Append role/content history tuples to a JSONL file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as history_stream:
        for role, content in entries:
            history_stream.write(json.dumps([role, content], sort_keys=True) + "\n")


class ScriptedSerialSession:
    """Small serial-session fake used by TokenStreamOverSerial in mock mode."""

    def __init__(self, read_chunks: Sequence[bytes]) -> None:
        self.reads = list(read_chunks)
        self.writes: list[bytes] = []
        self.closed = False

    def read(self, _size: int) -> bytes:
        if self.reads:
            return self.reads.pop(0)
        return b""

    def write(self, payload: bytes) -> int:
        self.writes.append(payload)
        return len(payload)

    def flush(self) -> None:
        return None

    def close(self) -> None:
        self.closed = True


class ScriptedSerialFactory:
    """Factory that records mock serial sessions created by the stream layer."""

    def __init__(self, read_chunks: Sequence[bytes]) -> None:
        self.read_chunks = list(read_chunks)
        self.instances: list[ScriptedSerialSession] = []

    def __call__(self, *args: Any, **kwargs: Any) -> ScriptedSerialSession:
        session = ScriptedSerialSession(self.read_chunks)
        self.instances.append(session)
        return session

    def written_payload(self) -> bytes:
        """Return all bytes written across created mock sessions."""

        return b"".join(
            payload for session in self.instances for payload in session.writes
        )


@dataclass
class GemmaE2EOrchestrator:
    """Wire tokenizer, W4 prep, token stream, and decode for mock Gemma chat."""

    arch_spec: GemmaArchSpec
    connection: KV260ConnectionProtocol
    tokenizer: GemmaTokenizer
    token_stream: TokenStreamOverSerial
    weight_prep: GemmaWeightPrep
    serial_factory: ScriptedSerialFactory | None = None
    axi_backend: AxiCmdMockBackend | None = None

    @classmethod
    def create_mock(
        cls,
        prompt: str,
        arch_spec: GemmaArchSpec | None = None,
        seed: int = 0,
    ) -> "GemmaE2EOrchestrator":
        """Create a full offline mock path with scripted serial and AXI replies."""

        spec = arch_spec or default_gemma3n_e4b_kv260_arch_spec()
        tokenizer = GemmaTokenizer(spec)
        prompt_tokens = tokenizer.encode(prompt)
        manifest = _prepare_mock_manifest(spec)
        reply_tokens = tokenizer.encode_generated_text(
            deterministic_mock_reply(prompt, spec, manifest, seed),
        )
        serial_factory = ScriptedSerialFactory([encode_output_stream(reply_tokens)])
        axi = AxiCmdMockBackend(_scripted_axi_replies(prompt_tokens, manifest, spec))
        serial_connection = KV260SerialConnection.from_env(
            {"KVFPGA_TTY": MOCK_TTY},
            serial_factory=serial_factory,
        )
        stream = TokenStreamOverSerial(
            connection=serial_connection,
            axi_channel=axi,
            eos_token_id=spec.eos_token_id,
            output_timeout_s=0.05,
        )
        return cls(
            arch_spec=spec,
            connection=KV260ConnectionMock.happy_path(),
            tokenizer=tokenizer,
            token_stream=stream,
            weight_prep=GemmaWeightPrep(),
            serial_factory=serial_factory,
            axi_backend=axi,
        )

    @classmethod
    def create_real_serial_stub(
        cls,
        _arch_spec: GemmaArchSpec | None = None,
    ) -> "GemmaE2EOrchestrator":
        """Future real serial path placeholder."""

        raise RealSerialGemmaE2ENotImplemented(
            "real Gemma serial orchestration is stubbed pending board evidence",
        )

    def run(self, prompt: str) -> GemmaE2EResult:
        """Run prompt -> encode -> send -> poll/recv -> decode in mock mode."""

        if not self.connection.is_reachable():
            raise GemmaE2EOrchestratorError("KV260 connection is not reachable")

        manifest = self.weight_prep.prepare_real(
            _mock_weights_for_arch(self.arch_spec),
            group_size=self.arch_spec.w4_group_size,
        )
        self._issue_manifest_load(manifest)
        prompt_tokens = self.tokenizer.encode(prompt)
        output_tokens = self.token_stream.infer(prompt_tokens)
        output_text = self.tokenizer.decode(output_tokens)

        if self.axi_backend is not None:
            self.axi_backend.assert_script_consumed()

        return GemmaE2EResult(
            output_text=output_text,
            prompt_tokens=tuple(prompt_tokens),
            output_tokens=tuple(output_tokens),
            manifest_id=manifest.manifest_id,
            manifest_sha256=manifest.packed_sha256,
            serial_payload=(
                self.serial_factory.written_payload()
                if self.serial_factory is not None
                else b""
            ),
            axi_completion_count=(
                self.axi_backend.completion_count
                if self.axi_backend is not None
                else 0
            ),
        )

    def _issue_manifest_load(self, manifest: Manifest) -> None:
        axi_channel = self.token_stream.axi_channel
        if axi_channel is None:
            return
        cmd = _manifest_load_cmd(manifest, self.arch_spec)
        axi_channel.issue(cmd)
        stat = axi_channel.poll_stat()
        if stat.error:
            raise GemmaE2EOrchestratorError(
                f"manifest load failed with status {stat.status_code}",
            )


def run_mock_gemma_chat(
    prompt: str,
    arch_spec: GemmaArchSpec | None = None,
    seed: int = 0,
) -> GemmaE2EResult:
    """Convenience entry point for the CLI mock chat path."""

    orchestrator = GemmaE2EOrchestrator.create_mock(prompt, arch_spec, seed)
    return orchestrator.run(prompt)


def deterministic_mock_reply(
    prompt: str,
    arch_spec: GemmaArchSpec,
    manifest: Manifest,
    seed: int = 0,
) -> str:
    """Return stable local mock output text for a prompt/config pair."""

    digest = hashlib.sha256(
        "|".join(
            [
                arch_spec.model_id,
                arch_spec.target,
                manifest.packed_sha256,
                str(seed),
                prompt,
            ],
        ).encode("utf-8"),
    ).hexdigest()
    return f"mock-gemma:{digest[:16]}"


def _prepare_mock_manifest(arch_spec: GemmaArchSpec) -> Manifest:
    return GemmaWeightPrep().prepare_real(
        _mock_weights_for_arch(arch_spec),
        group_size=arch_spec.w4_group_size,
    )


def _mock_weights_for_arch(arch_spec: GemmaArchSpec) -> np.ndarray:
    seed = hashlib.sha256(
        f"{arch_spec.model_id}|{arch_spec.target}|{arch_spec.w4_group_size}".encode(
            "utf-8",
        ),
    ).digest()
    values = [((seed[index] % 17) - 8) / 2.0 for index in range(16)]
    return np.asarray(values, dtype=np.float32).reshape(2, 8)


def _scripted_axi_replies(
    prompt_tokens: Sequence[int],
    manifest: Manifest,
    arch_spec: GemmaArchSpec,
) -> tuple[tuple[NpuCmd, NpuStat], ...]:
    commands = (
        _manifest_load_cmd(manifest, arch_spec),
        NpuCmd(opcode=OP_BEGIN_INPUT, arg0=len(prompt_tokens)),
        NpuCmd(opcode=OP_END_INPUT, arg0=len(prompt_tokens)),
        NpuCmd(opcode=OP_READ_OUTPUT, arg0=0),
    )
    return tuple(
        (
            cmd,
            NpuStat(completion_count=index + 1, last_opcode=cmd.opcode),
        )
        for index, cmd in enumerate(commands)
    )


def _manifest_load_cmd(manifest: Manifest, arch_spec: GemmaArchSpec) -> NpuCmd:
    packed_len = sum(len(tile.packed_nibbles) for tile in manifest.tiles)
    checksum_prefix = int(manifest.packed_sha256[:8], 16)
    return NpuCmd(
        opcode=OP_LOAD_W4_MANIFEST,
        arg0=packed_len,
        arg1=arch_spec.w4_group_size,
        arg2=checksum_prefix,
    )
