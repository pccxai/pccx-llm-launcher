#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Launcher-side trace capture client for lab-compatible v2 framing.

The client emits line-delimited serial trace framing compatible with
``pccxai/pccx-lab#163``. It writes only caller-provided frame data and does not
open a board connection, inspect the environment, or execute a runtime.
"""

from __future__ import annotations

import json
import sys
import zlib
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Protocol, runtime_checkable


PCCX_TRACE_BEGIN_MARKER = "===PCCX_TRACE_BEGIN seq=0==="
PCCX_TRACE_END_PREFIX = "===PCCX_TRACE_END seq="
PCCX_TRACE_MARKER_SUFFIX = "==="


@runtime_checkable
class TextTraceSink(Protocol):
    def write(self, text: str) -> object:
        ...

    def flush(self) -> object:
        ...


@runtime_checkable
class BinaryTraceSink(Protocol):
    def write(self, data: bytes) -> object:
        ...

    def flush(self) -> object:
        ...


TraceSink = TextTraceSink | BinaryTraceSink


class Closeable(Protocol):
    def close(self) -> object:
        ...


@dataclass(frozen=True)
class TraceCaptureFrame:
    """One v2 serial trace frame before CRC decoration."""

    frame_idx: int
    axi_stat: int
    engine_completion: int
    cycles: int
    err: str | None = None


class TraceCaptureClient:
    """Write v2-framed trace JSON lines to stdout, a file, or a serial sink."""

    def __init__(
        self,
        serial_port: TraceSink | str | PathLike[str] | None = None,
        file_path: str | PathLike[str] | None = None,
    ) -> None:
        if serial_port is not None and file_path is not None:
            raise ValueError("configure either serial_port or file_path, not both")

        self._owned_sink: Closeable | None = None
        self._begun = False
        self._next_seq = 0
        self._ended = False

        if file_path is not None:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            self._sink: TraceSink = path.open("w", encoding="utf-8", newline="\n")
            self._owned_sink = self._sink
        elif isinstance(serial_port, (str, PathLike)):
            self._sink = Path(serial_port).open("wb")
            self._owned_sink = self._sink
        elif serial_port is not None:
            self._sink = serial_port
        else:
            self._sink = sys.stdout

    def __enter__(self) -> "TraceCaptureClient":
        self.begin()
        return self

    def __exit__(self, _exc_type: object, _exc: object, _tb: object) -> None:
        self.close()

    def begin(self) -> None:
        """Emit the v2 begin marker."""

        if self._begun:
            raise RuntimeError("trace capture has already begun")
        self._write_line(PCCX_TRACE_BEGIN_MARKER)
        self._begun = True

    def write_frame(self, frame: TraceCaptureFrame) -> None:
        """Emit one v2 JSON frame with an IEEE CRC32."""

        if self._ended:
            raise RuntimeError("cannot write frames after trace capture ended")
        if not self._begun:
            self.begin()
        payload = _crc_payload(
            seq=self._next_seq,
            frame_idx=frame.frame_idx,
            axi_stat=frame.axi_stat,
            engine_completion=frame.engine_completion,
            cycles=frame.cycles,
            err=frame.err,
        )
        crc32 = serial_frame_crc32(
            seq=self._next_seq,
            frame_idx=frame.frame_idx,
            axi_stat=frame.axi_stat,
            engine_completion=frame.engine_completion,
            cycles=frame.cycles,
            err=frame.err,
        )
        line = _compact_json({**payload, "crc32": crc32})
        self._write_line(line)
        self._next_seq += 1

    def end(self) -> None:
        """Emit the v2 end marker using the next expected sequence number."""

        if not self._ended:
            if not self._begun:
                self.begin()
            self._write_line(
                f"{PCCX_TRACE_END_PREFIX}{self._next_seq}{PCCX_TRACE_MARKER_SUFFIX}",
            )
            self._ended = True

    def capture(self, frames: tuple[TraceCaptureFrame, ...]) -> None:
        """Emit begin marker, all frames, and end marker."""

        self.begin()
        for frame in frames:
            self.write_frame(frame)
        self.end()

    def close(self) -> None:
        """Finish the trace and close an owned file target."""

        self.end()
        self._flush()
        if self._owned_sink is not None:
            self._owned_sink.close()

    @property
    def next_seq(self) -> int:
        return self._next_seq

    def _write_line(self, line: str) -> None:
        text = f"{line}\n"
        try:
            self._sink.write(text)  # type: ignore[arg-type]
        except TypeError:
            self._sink.write(text.encode("utf-8"))  # type: ignore[arg-type]
        self._flush()

    def _flush(self) -> None:
        self._sink.flush()


def serial_frame_crc32(
    seq: int,
    frame_idx: int,
    axi_stat: int,
    engine_completion: int,
    cycles: int,
    err: str | None,
) -> int:
    """Return lab-compatible IEEE CRC32 over the canonical v2 payload."""

    payload = _compact_json(
        _crc_payload(
            seq=seq,
            frame_idx=frame_idx,
            axi_stat=axi_stat,
            engine_completion=engine_completion,
            cycles=cycles,
            err=err,
        ),
    ).encode("utf-8")
    return zlib.crc32(payload) & 0xFFFF_FFFF


def _crc_payload(
    seq: int,
    frame_idx: int,
    axi_stat: int,
    engine_completion: int,
    cycles: int,
    err: str | None,
) -> dict[str, int | str | None]:
    return {
        "seq": _u64("seq", seq),
        "frame_idx": _u32("frame_idx", frame_idx),
        "axi_stat": _u32("axi_stat", axi_stat),
        "engine_completion": _u8("engine_completion", engine_completion),
        "cycles": _u64("cycles", cycles),
        "err": err,
    }


def _compact_json(payload: dict[str, int | str | None]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _u8(name: str, value: int) -> int:
    if not 0 <= value <= 0xFF:
        raise ValueError(f"{name} must fit u8")
    return value


def _u32(name: str, value: int) -> int:
    if not 0 <= value <= 0xFFFF_FFFF:
        raise ValueError(f"{name} must fit u32")
    return value


def _u64(name: str, value: int) -> int:
    if not 0 <= value <= 0xFFFF_FFFF_FFFF_FFFF:
        raise ValueError(f"{name} must fit u64")
    return value
