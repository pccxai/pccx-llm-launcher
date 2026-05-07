#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Mock-only Gemma end-to-end launcher orchestrator."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

from contracts.axi_cmd_channel import AxiCmdChannel, AxiCmdMockBackend, NpuCmd, NpuStat
from contracts.gemma_arch_spec import GemmaArchSpec, default_gemma3n_e4b_kv260_arch_spec
from contracts.gemma_chat_template import GemmaChatMessage, GemmaChatTemplate
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
    history: list[tuple[str, str]] = field(default_factory=list)
    chat_template: GemmaChatTemplate = field(default_factory=GemmaChatTemplate)

    def send(self, prompt: str) -> GemmaE2EResult:
        """Send one user turn through the mock orchestrator and store the reply."""

        context = self.context_for(prompt)
        result = run_mock_gemma_chat(context, self.arch_spec, seed=self.seed)
        self.history.append((prompt, result.output_text))
        return result

    def context_for(self, prompt: str) -> str:
        """Build a Gemma-style chat prompt including prior turns."""

        messages: list[GemmaChatMessage] = []
        for user_text, assistant_text in self.history:
            messages.append(GemmaChatMessage(role="user", content=user_text))
            messages.append(GemmaChatMessage(role="assistant", content=assistant_text))
        messages.append(GemmaChatMessage(role="user", content=prompt))
        return self.chat_template.format(messages, add_generation_prompt=True)


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
