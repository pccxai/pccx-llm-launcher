#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Board-less KV260 connection mock for launcher-side integration tests.

The mock implements the same method contract as ``KV260SerialConnection`` but
keeps all board state in memory. Scenario fixtures are local test data only;
loading them never opens a tty, starts a process, or probes host devices.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from contracts.kv260_serial_connection import KV260ConnectionProtocol


SCENARIO_DIR = (
    Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "scenarios"
)
SCENARIO_EXTENSIONS = (".yaml", ".json")


class KV260ConnectionMockScenarioError(ValueError):
    """Raised when a mock scenario fixture is missing or invalid."""


@dataclass(frozen=True)
class KV260MockBoardState:
    """In-memory KV260 board state returned by the mock connection."""

    kernel_uname: str
    xrt_present: bool
    xrt_version: str
    xmutil_listapps: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "KV260MockBoardState":
        kernel_uname = _require_string(payload, "kernel_uname")
        xrt_version = _optional_string(payload, "xrt_version")
        xrt_present = _optional_bool(payload, "xrt_present")
        if xrt_present is None:
            xrt_present = bool(xrt_version)

        return cls(
            kernel_uname=kernel_uname,
            xrt_present=xrt_present,
            xrt_version=xrt_version,
            xmutil_listapps=_require_string_tuple(payload, "xmutil_listapps"),
        )


@dataclass(frozen=True)
class KV260ConnectionMock(KV260ConnectionProtocol):
    """Board-less implementation of the KV260 connection method contract."""

    state: KV260MockBoardState

    @classmethod
    def from_scenario(
        cls,
        name: str,
        scenario_dir: Path | None = None,
    ) -> "KV260ConnectionMock":
        """Load a named scenario from tests/fixtures/scenarios."""

        if not name or Path(name).name != name:
            raise KV260ConnectionMockScenarioError("scenario name must be a file stem")

        directory = SCENARIO_DIR if scenario_dir is None else scenario_dir
        path = _scenario_path(directory, name)
        payload = _load_fixture(path)
        return cls(KV260MockBoardState.from_mapping(payload))

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

        state = KV260MockBoardState.from_mapping(
            {
                "kernel_uname": kernel_uname,
                "xrt_present": xrt_present,
                "xrt_version": xrt_version,
                "xmutil_listapps": list(xmutil_listapps),
            },
        )
        return cls(state)

    def is_reachable(self) -> bool:
        """Return true for board-less tests without touching hardware."""

        return True

    def kernel_uname(self) -> str:
        """Return the configured mock ``uname -a`` string."""

        return self.state.kernel_uname

    def xrt_present(self) -> bool:
        """Return the configured mock XRT availability."""

        return self.state.xrt_present

    def xrt_version(self) -> str:
        """Return the configured mock XRT version string."""

        return self.state.xrt_version

    def xmutil_listapps(self) -> Sequence[str]:
        """Return the configured mock ``xmutil listapps`` output lines."""

        return self.state.xmutil_listapps


def _scenario_path(directory: Path, name: str) -> Path:
    for extension in SCENARIO_EXTENSIONS:
        candidate = directory / f"{name}{extension}"
        if candidate.is_file():
            return candidate
    expected = ", ".join(f"{name}{extension}" for extension in SCENARIO_EXTENSIONS)
    raise KV260ConnectionMockScenarioError(f"scenario fixture not found: {expected}")


def _load_fixture(path: Path) -> Mapping[str, Any]:
    if path.suffix == ".json":
        with path.open(encoding="utf-8") as fh:
            payload = json.load(fh)
    elif path.suffix == ".yaml":
        payload = _load_simple_yaml(path)
    else:
        raise KV260ConnectionMockScenarioError(
            f"unsupported scenario extension: {path.suffix}",
        )

    if not isinstance(payload, Mapping):
        raise KV260ConnectionMockScenarioError("scenario fixture must be an object")
    return payload


def _load_simple_yaml(path: Path) -> Mapping[str, Any]:
    parsed: dict[str, Any] = {}
    pending_key: str | None = None
    pending_list: list[Any] = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped.startswith("- "):
            if pending_key is None:
                raise KV260ConnectionMockScenarioError("list item without key")
            pending_list.append(_parse_scalar(stripped[2:]))
            continue

        if pending_key is not None:
            parsed[pending_key] = tuple(pending_list)
            pending_key = None
            pending_list = []

        if ":" not in stripped:
            raise KV260ConnectionMockScenarioError(f"invalid yaml line: {raw_line}")
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise KV260ConnectionMockScenarioError("empty yaml key")
        if value:
            parsed[key] = _parse_scalar(value)
        else:
            pending_key = key
            pending_list = []

    if pending_key is not None:
        parsed[pending_key] = tuple(pending_list)

    return parsed


def _parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none", "~"}:
        return None
    if value == "[]":
        return ()
    if value.startswith(('"', "'")) and value.endswith(value[0]):
        if value[0] == '"':
            return json.loads(value)
        return value[1:-1]
    return value


def _require_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise KV260ConnectionMockScenarioError(f"{key} must be a non-empty string")
    return value


def _optional_string(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise KV260ConnectionMockScenarioError(f"{key} must be a string")
    return value


def _optional_bool(payload: Mapping[str, Any], key: str) -> bool | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise KV260ConnectionMockScenarioError(f"{key} must be a bool")
    return value


def _require_string_tuple(payload: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = payload.get(key)
    if value is None:
        raise KV260ConnectionMockScenarioError(f"{key} must be present")
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise KV260ConnectionMockScenarioError(f"{key} must be a list of strings")
    values = tuple(value)
    if not all(isinstance(item, str) and item for item in values):
        raise KV260ConnectionMockScenarioError(f"{key} must be a list of strings")
    return values
