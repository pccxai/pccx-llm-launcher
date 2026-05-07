#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Offline AXI command-channel contract and mock backend.

This module is intentionally local-only. It models the command and status
registers in memory so tests can exercise launcher-side command flow without a
board, device file, driver, or runtime transport.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from threading import RLock
from typing import Deque, Iterable, Protocol


MMIO_CMD = "MMIO_CMD"
MMIO_STAT = "MMIO_STAT"
UINT32_MASK = 0xFFFF_FFFF


@dataclass(frozen=True)
class NpuCmd:
    """Command payload written to the modeled MMIO_CMD register."""

    opcode: int
    arg0: int = 0
    arg1: int = 0
    arg2: int = 0
    flags: int = 0

    def __post_init__(self) -> None:
        for field_name in ("opcode", "arg0", "arg1", "arg2", "flags"):
            value = getattr(self, field_name)
            if not isinstance(value, int):
                raise TypeError(f"{field_name} must be an int")
            if value < 0:
                raise ValueError(f"{field_name} must be non-negative")

    def register_value(self) -> int:
        """Return a deterministic 32-bit representation for MMIO_CMD."""

        packed = (
            (self.opcode & 0xFF)
            | ((self.flags & 0xFF) << 8)
            | ((self.arg0 & 0xFF) << 16)
            | ((self.arg1 & 0xFF) << 24)
        )
        return (packed ^ (self.arg2 & UINT32_MASK)) & UINT32_MASK


@dataclass(frozen=True)
class NpuStat:
    """Status payload read from the modeled MMIO_STAT register."""

    completion_count: int = 0
    last_opcode: int = 0
    busy: bool = False
    error: bool = False
    status_code: int = 0

    def __post_init__(self) -> None:
        for field_name in ("completion_count", "last_opcode", "status_code"):
            value = getattr(self, field_name)
            if not isinstance(value, int):
                raise TypeError(f"{field_name} must be an int")
            if value < 0:
                raise ValueError(f"{field_name} must be non-negative")
        for field_name in ("busy", "error"):
            if not isinstance(getattr(self, field_name), bool):
                raise TypeError(f"{field_name} must be a bool")

    def register_value(self) -> int:
        """Return a deterministic 32-bit representation for MMIO_STAT."""

        value = (
            (self.completion_count & 0xFFFF) << 16
            | ((self.status_code & 0x3F) << 8)
            | ((self.last_opcode & 0x3F) << 2)
            | (0x2 if self.error else 0)
            | (0x1 if self.busy else 0)
        )
        return value & UINT32_MASK


class AxiCmdChannel(Protocol):
    """Minimal command-channel interface used by launcher-side tests."""

    def issue(self, cmd: NpuCmd) -> None:
        """Issue a command to the channel."""

    def poll_stat(self) -> NpuStat:
        """Read the current command-channel status."""


class ScriptedReplyMismatch(AssertionError):
    """Raised when a scripted mock backend observes an unexpected command."""


class AxiCmdMockBackend:
    """Thread-safe in-memory AXI command backend for offline tests."""

    def __init__(
        self,
        scripted_replies: Iterable[tuple[NpuCmd, NpuStat]] | None = None,
    ) -> None:
        self._lock = RLock()
        self._registers = {MMIO_CMD: 0, MMIO_STAT: 0}
        self._scripted_replies: Deque[tuple[NpuCmd, NpuStat]] = deque(
            scripted_replies or (),
        )
        self._last_cmd: NpuCmd | None = None
        self._last_stat = NpuStat()
        self._completion_count = 0
        self._closed = False

    def __enter__(self) -> "AxiCmdMockBackend":
        with self._lock:
            self._closed = False
            return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    @property
    def completion_count(self) -> int:
        with self._lock:
            return self._completion_count

    @property
    def last_cmd(self) -> NpuCmd | None:
        with self._lock:
            return self._last_cmd

    @property
    def remaining_scripted_replies(self) -> int:
        with self._lock:
            return len(self._scripted_replies)

    def close(self) -> None:
        with self._lock:
            self._closed = True

    def issue(self, cmd: NpuCmd) -> None:
        if not isinstance(cmd, NpuCmd):
            raise TypeError("cmd must be an NpuCmd")

        with self._lock:
            self._ensure_open()
            scripted_stat = self._consume_scripted_reply(cmd)
            self._completion_count += 1
            self._last_cmd = cmd
            self._last_stat = scripted_stat or self._default_stat_for(cmd)
            self._registers[MMIO_CMD] = cmd.register_value()
            self._registers[MMIO_STAT] = self._last_stat.register_value()

    def poll_stat(self) -> NpuStat:
        with self._lock:
            self._ensure_open()
            self._registers[MMIO_STAT] = self._last_stat.register_value()
            return self._last_stat

    def snapshot_registers(self) -> dict[str, int]:
        with self._lock:
            return dict(self._registers)

    def assert_script_consumed(self) -> None:
        with self._lock:
            remaining = len(self._scripted_replies)
            if remaining:
                raise ScriptedReplyMismatch(
                    f"{remaining} scripted AXI command replies were not used",
                )

    def _consume_scripted_reply(self, cmd: NpuCmd) -> NpuStat | None:
        if not self._scripted_replies:
            return None

        expected_cmd, expected_stat = self._scripted_replies[0]
        if cmd != expected_cmd:
            raise ScriptedReplyMismatch(
                f"expected command {expected_cmd!r}, got {cmd!r}",
            )
        self._scripted_replies.popleft()
        return expected_stat

    def _default_stat_for(self, cmd: NpuCmd) -> NpuStat:
        return NpuStat(
            completion_count=self._completion_count,
            last_opcode=cmd.opcode,
            busy=False,
            error=False,
            status_code=0,
        )

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("AxiCmdMockBackend is closed")
