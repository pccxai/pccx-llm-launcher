#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Board-less KV260 connection mock for launcher integration tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from contracts.kv260_serial_connection import KV260ConnectionProtocol


@dataclass(frozen=True)
class KV260MockBoardState:
    """In-memory KV260 board state returned by the mock connection."""

    kernel_uname: str
    xrt_present: bool
    xrt_version: str
    xmutil_listapps: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.kernel_uname:
            raise ValueError("kernel_uname must be non-empty")
        if not isinstance(self.xrt_present, bool):
            raise TypeError("xrt_present must be a bool")
        if not isinstance(self.xrt_version, str):
            raise TypeError("xrt_version must be a string")
        if not all(isinstance(app, str) and app for app in self.xmutil_listapps):
            raise ValueError("xmutil_listapps must contain non-empty strings")


@dataclass(frozen=True)
class KV260ConnectionMock(KV260ConnectionProtocol):
    """Board-less implementation of the KV260 connection method contract."""

    state: KV260MockBoardState

    @classmethod
    def happy_path(cls) -> "KV260ConnectionMock":
        """Build the default reachable board-less target."""

        return cls.from_state(
            kernel_uname=(
                "Linux kv260-mock 6.6.0-pccx-mock #1 SMP PREEMPT "
                "aarch64 GNU/Linux"
            ),
            xrt_present=True,
            xrt_version="XRT mock 2.16.0",
            xmutil_listapps=("app: pccx-npu", "app: diagnostics"),
        )

    @classmethod
    def from_state(
        cls,
        *,
        kernel_uname: str,
        xrt_present: bool | None = None,
        xrt_version: str = "",
        xmutil_listapps: Sequence[str] = (),
    ) -> "KV260ConnectionMock":
        """Build a mock directly from in-memory state."""

        if xrt_present is None:
            xrt_present = bool(xrt_version)
        return cls(
            KV260MockBoardState(
                kernel_uname=kernel_uname,
                xrt_present=xrt_present,
                xrt_version=xrt_version,
                xmutil_listapps=tuple(xmutil_listapps),
            ),
        )

    def is_reachable(self) -> bool:
        """Return true for board-less tests without touching hardware."""

        return True

    def kernel_uname(self) -> str:
        """Return the configured mock uname string."""

        return self.state.kernel_uname

    def xrt_present(self) -> bool:
        """Return the configured mock XRT availability."""

        return self.state.xrt_present

    def xrt_version(self) -> str:
        """Return the configured mock XRT version string."""

        return self.state.xrt_version

    def xmutil_listapps(self) -> Sequence[str]:
        """Return the configured mock xmutil listapps output lines."""

        return self.state.xmutil_listapps
