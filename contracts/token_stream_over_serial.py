#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Token stream transport over the KV260 serial tty.

This is first-pass framing; refine after first board run. The control-plane
wire format uses ASCII begin/end markers around length-prefixed binary chunks,
matching the lab trace framing shape while keeping token payloads binary.
"""

from __future__ import annotations

import struct
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator, List, Protocol, Sequence, runtime_checkable

from contracts.axi_cmd_channel import AxiCmdChannel, NpuCmd
from contracts.kv260_serial_connection import (
    KV260SerialConnection,
    detect_kv260_tty,
)


INPUT_BEGIN_MARKER = b"PCCX_TOKEN_INPUT_BEGIN_V1\n"
INPUT_END_MARKER = b"PCCX_TOKEN_INPUT_END_V1\n"
OUTPUT_BEGIN_MARKER = b"PCCX_TOKEN_OUTPUT_BEGIN_V1\n"
OUTPUT_END_MARKER = b"PCCX_TOKEN_OUTPUT_END_V1\n"
INPUT_CHUNK_TAG = b"ITOK"
OUTPUT_CHUNK_TAG = b"OTOK"
UINT32_MAX = 0xFFFF_FFFF
DEFAULT_EOS_TOKEN_ID = 1
DEFAULT_CHUNK_TOKEN_COUNT = 256
DEFAULT_OUTPUT_TIMEOUT_S = 5.0
READ_CHUNK_SIZE = 1024

OP_BEGIN_INPUT = 0x31
OP_END_INPUT = 0x32
OP_READ_OUTPUT = 0x33


class TokenStreamError(RuntimeError):
    """Base error for token-stream transport failures."""


class TokenStreamFramingError(TokenStreamError):
    """Raised when received token framing is malformed."""


@runtime_checkable
class TokenStreamProtocol(Protocol):
    """Method contract for launcher-side token streaming."""

    def send_input_tokens(self, token_ids: List[int]) -> None:
        """Send prompt token IDs to the KV260 control-plane tty."""

    def recv_output_tokens(self, timeout_s: float) -> List[int]:
        """Receive generated token IDs until EOS, end marker, or timeout."""

    def infer(self, prompt_token_ids: List[int]) -> List[int]:
        """Send prompt token IDs and return generated output token IDs."""


@dataclass
class TokenStreamOverSerial:
    """Length-prefixed token transport using a KV260 serial connection."""

    connection: KV260SerialConnection
    axi_channel: AxiCmdChannel | None = None
    eos_token_id: int = DEFAULT_EOS_TOKEN_ID
    chunk_token_count: int = DEFAULT_CHUNK_TOKEN_COUNT
    output_timeout_s: float = DEFAULT_OUTPUT_TIMEOUT_S
    _active_serial: Any | None = field(default=None, init=False, repr=False)

    @classmethod
    def from_env(
        cls,
        serial_factory: Any | None = None,
        axi_channel: AxiCmdChannel | None = None,
    ) -> "TokenStreamOverSerial":
        """Build a token stream from KV260 serial environment settings."""

        return cls(
            connection=KV260SerialConnection.from_env(
                serial_factory=serial_factory,
            ),
            axi_channel=axi_channel,
        )

    def __post_init__(self) -> None:
        if self.eos_token_id < 0 or self.eos_token_id > UINT32_MAX:
            raise ValueError("eos_token_id must fit uint32")
        if self.chunk_token_count <= 0:
            raise ValueError("chunk_token_count must be positive")
        if self.output_timeout_s < 0:
            raise ValueError("output_timeout_s must be non-negative")

    def __enter__(self) -> "TokenStreamOverSerial":
        if self._active_serial is None:
            self._active_serial = self.connection._open_serial()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def close(self) -> None:
        """Close the active serial session when this wrapper opened one."""

        serial_session = self._active_serial
        self._active_serial = None
        self.connection._close_serial(serial_session)

    def send_input_tokens(self, token_ids: List[int]) -> None:
        """Encode prompt tokens and write them to the KV260 serial tty."""

        tokens = _validate_tokens(token_ids)
        self._issue_axi(OP_BEGIN_INPUT, len(tokens))
        payload = encode_input_stream(tokens, self.chunk_token_count)
        with self._serial_for_call() as serial_session:
            self.connection._write(serial_session, payload)
        self._issue_axi(OP_END_INPUT, len(tokens))

    def recv_output_tokens(self, timeout_s: float) -> List[int]:
        """Read output token framing until EOS, output end, or timeout."""

        if timeout_s < 0:
            raise ValueError("timeout_s must be non-negative")

        self._issue_axi(OP_READ_OUTPUT, 0)
        deadline = time.monotonic() + timeout_s
        buffer = bytearray()
        tokens: list[int] = []
        parser_offset = 0
        saw_begin = False

        with self._serial_for_call() as serial_session:
            while time.monotonic() <= deadline:
                chunk = serial_session.read(READ_CHUNK_SIZE)
                if chunk:
                    buffer.extend(chunk)
                    state = _parse_output_buffer(
                        bytes(buffer),
                        parser_offset,
                        tokens,
                        self.eos_token_id,
                        saw_begin,
                    )
                    parser_offset = state.offset
                    saw_begin = state.saw_begin
                    if state.done:
                        return list(tokens)
                    continue
                time.sleep(0.02)

        return list(tokens)

    def infer(self, prompt_token_ids: List[int]) -> List[int]:
        """Send prompt tokens and return output tokens over one tty session."""

        if self._active_serial is not None:
            self.send_input_tokens(prompt_token_ids)
            return self.recv_output_tokens(self.output_timeout_s)

        with self:
            self.send_input_tokens(prompt_token_ids)
            return self.recv_output_tokens(self.output_timeout_s)

    @contextmanager
    def _serial_for_call(self) -> Iterator[Any]:
        if self._active_serial is not None:
            yield self._active_serial
            return

        serial_session = self.connection._open_serial()
        try:
            yield serial_session
        finally:
            self.connection._close_serial(serial_session)

    def _issue_axi(self, opcode: int, arg0: int) -> None:
        if self.axi_channel is None:
            return
        self.axi_channel.issue(NpuCmd(opcode=opcode, arg0=arg0))
        stat = self.axi_channel.poll_stat()
        if stat.error:
            raise TokenStreamError(
                f"AXI command {opcode} failed with status {stat.status_code}",
            )


@dataclass(frozen=True)
class _ParseState:
    offset: int
    saw_begin: bool
    done: bool = False


def encode_input_stream(
    token_ids: Sequence[int],
    chunk_token_count: int = DEFAULT_CHUNK_TOKEN_COUNT,
) -> bytes:
    """Return first-pass control-plane input framing for token IDs."""

    tokens = _validate_tokens(token_ids)
    if chunk_token_count <= 0:
        raise ValueError("chunk_token_count must be positive")

    chunks = [INPUT_BEGIN_MARKER]
    for start in range(0, len(tokens), chunk_token_count):
        chunk_tokens = tokens[start : start + chunk_token_count]
        payload = _pack_tokens(chunk_tokens)
        chunks.append(INPUT_CHUNK_TAG + struct.pack(">I", len(payload)) + payload)
    chunks.append(INPUT_END_MARKER)
    return b"".join(chunks)


def encode_output_stream(token_ids: Sequence[int]) -> bytes:
    """Return output framing for mock tests and future fixture capture."""

    tokens = _validate_tokens(token_ids)
    payload = _pack_tokens(tokens)
    return (
        OUTPUT_BEGIN_MARKER
        + OUTPUT_CHUNK_TAG
        + struct.pack(">I", len(payload))
        + payload
        + OUTPUT_END_MARKER
    )


def _parse_output_buffer(
    buffer: bytes,
    offset: int,
    tokens: list[int],
    eos_token_id: int,
    saw_begin: bool,
) -> _ParseState:
    if not saw_begin:
        marker_at = buffer.find(OUTPUT_BEGIN_MARKER, offset)
        if marker_at < 0:
            keep_from = max(0, len(buffer) - len(OUTPUT_BEGIN_MARKER))
            return _ParseState(offset=keep_from, saw_begin=False)
        offset = marker_at + len(OUTPUT_BEGIN_MARKER)
        saw_begin = True

    while offset < len(buffer):
        if buffer.startswith(OUTPUT_END_MARKER, offset):
            return _ParseState(
                offset=offset + len(OUTPUT_END_MARKER),
                saw_begin=saw_begin,
                done=True,
            )
        if OUTPUT_END_MARKER.startswith(buffer[offset:]):
            return _ParseState(offset=offset, saw_begin=saw_begin)
        header_size = len(OUTPUT_CHUNK_TAG) + 4
        if len(buffer) - offset < header_size:
            return _ParseState(offset=offset, saw_begin=saw_begin)
        tag = buffer[offset : offset + len(OUTPUT_CHUNK_TAG)]
        if tag != OUTPUT_CHUNK_TAG:
            raise TokenStreamFramingError("unexpected output token chunk tag")
        size_offset = offset + len(OUTPUT_CHUNK_TAG)
        payload_len = struct.unpack(">I", buffer[size_offset : size_offset + 4])[0]
        if payload_len % 4:
            raise TokenStreamFramingError("token payload length must be uint32 aligned")
        payload_offset = size_offset + 4
        payload_end = payload_offset + payload_len
        if len(buffer) < payload_end:
            return _ParseState(offset=offset, saw_begin=saw_begin)
        chunk_tokens = _unpack_tokens(buffer[payload_offset:payload_end])
        tokens.extend(chunk_tokens)
        if eos_token_id in chunk_tokens:
            return _ParseState(offset=payload_end, saw_begin=saw_begin, done=True)
        offset = payload_end

    return _ParseState(offset=offset, saw_begin=saw_begin)


def _validate_tokens(token_ids: Sequence[int]) -> list[int]:
    tokens = list(token_ids)
    for token_id in tokens:
        if not isinstance(token_id, int):
            raise TypeError("token IDs must be integers")
        if token_id < 0 or token_id > UINT32_MAX:
            raise ValueError("token IDs must fit uint32")
    return tokens


def _pack_tokens(token_ids: Sequence[int]) -> bytes:
    if not token_ids:
        return b""
    return struct.pack(f">{len(token_ids)}I", *token_ids)


def _unpack_tokens(payload: bytes) -> list[int]:
    if not payload:
        return []
    return list(struct.unpack(f">{len(payload) // 4}I", payload))
