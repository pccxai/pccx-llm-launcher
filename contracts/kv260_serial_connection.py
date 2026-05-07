#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""TTY serial backend for KV260 launcher-side status checks.

The backend uses USB serial console access only. Credentials come from
`KVFPGA_USER` and `KVFPGA_PASSWORD`; `KVFPGA_HOST` is intentionally ignored.
Raw environment values are not exposed through repr or public status fields.
"""

from __future__ import annotations

import os
import random
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence, TypeVar, runtime_checkable


DEFAULT_BAUDRATE = 115200
DEFAULT_PROMPT_TIMEOUT = 4.0
DEFAULT_COMMAND_TIMEOUT = 12.0
DEFAULT_WRITE_TIMEOUT = 1.0
READ_CHUNK_SIZE = 1024
END_MARKER = "__PCCX_KV260_SERIAL_DONE__"
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_BASE_DELAY = 0.1
DEFAULT_RETRY_MAX_DELAY = 1.0
DEFAULT_RETRY_JITTER_RATIO = 0.25

LOGIN_PROMPT = re.compile(rb"(?im)(?:^|\r?\n)[^\r\n]*login:\s*$")
PASSWORD_PROMPT = re.compile(rb"(?im)(?:^|\r?\n)[^\r\n]*password:\s*$")
SHELL_PROMPT = re.compile(rb"(?m)(?:^|\r?\n)[^\r\n]*[$#]\s*$")
COMMAND_DONE = re.compile((END_MARKER + r":(\d+)").encode("ascii"))
T = TypeVar("T")


class KV260SerialError(RuntimeError):
    """Base error for serial backend failures."""


class KV260SerialUnavailable(KV260SerialError):
    """Raised when a tty port or pyserial backend is unavailable."""


@runtime_checkable
class KV260ConnectionProtocol(Protocol):
    """Method contract shared by KV260 connection backends."""

    def is_reachable(self) -> bool:
        """Return whether a serial console prompt can be reached."""

    def kernel_uname(self) -> str:
        """Return `uname -a` from the KV260 serial session."""

    def xrt_present(self) -> bool:
        """Return whether XRT tooling or libraries are visible on the target."""

    def xmutil_listapps(self) -> Sequence[str]:
        """Return `xmutil listapps` output lines from the target."""


@dataclass(frozen=True)
class SerialCommandResult:
    """Target command output with shell exit status."""

    exit_status: int
    output: str


SerialFactory = Callable[..., Any]
Sleeper = Callable[[float], None]
RandomSource = Callable[[], float]


@dataclass(frozen=True)
class RetryPolicy:
    """Retry settings for transient KV260 serial port failures."""

    max_attempts: int = DEFAULT_RETRY_ATTEMPTS
    base_delay: float = DEFAULT_RETRY_BASE_DELAY
    max_delay: float = DEFAULT_RETRY_MAX_DELAY
    jitter_ratio: float = DEFAULT_RETRY_JITTER_RATIO
    random_source: RandomSource = field(
        default=random.random,
        repr=False,
        compare=False,
    )
    sleeper: Sleeper = field(default=time.sleep, repr=False, compare=False)

    def retry_delay(self, failure_index: int) -> float:
        """Return exponential backoff delay with bounded jitter."""

        if self.base_delay <= 0 or self.max_delay <= 0:
            return 0.0

        exponential = self.base_delay * (2**failure_index)
        delay = min(exponential, self.max_delay)
        jitter_ratio = max(0.0, self.jitter_ratio)
        if jitter_ratio == 0:
            return delay

        jitter = ((self.random_source() * 2.0) - 1.0) * jitter_ratio
        return max(0.0, delay * (1.0 + jitter))

    def sleep_after_failure(self, failure_index: int) -> None:
        """Sleep before the next retry attempt."""

        delay = self.retry_delay(failure_index)
        if delay > 0:
            self.sleeper(delay)


def kv260_tty_candidates(env: Mapping[str, str] | None = None) -> tuple[str, ...]:
    """Return candidate KV260 serial tty paths, with env override first."""

    source = os.environ if env is None else env
    override = source.get("KVFPGA_TTY")
    if override:
        return (override,)

    candidates: list[str] = []
    by_id = Path("/dev/serial/by-id")
    if by_id.is_dir():
        for path in sorted(by_id.iterdir()):
            if "kv260" in path.name.lower():
                candidates.append(str(path))

    candidates.extend(str(path) for path in sorted(Path("/dev").glob("ttyUSB*")))
    return tuple(dict.fromkeys(candidates))


def detect_kv260_tty(env: Mapping[str, str] | None = None) -> str | None:
    """Return the first configured or auto-detected KV260 serial tty path."""

    candidates = kv260_tty_candidates(env)
    return candidates[0] if candidates else None


@dataclass
class KV260SerialConnection:
    """USB tty serial implementation of the KV260 connection method contract."""

    tty_configured: bool
    user_configured: bool
    password_configured: bool
    baudrate: int = DEFAULT_BAUDRATE
    prompt_timeout: float = DEFAULT_PROMPT_TIMEOUT
    command_timeout: float = DEFAULT_COMMAND_TIMEOUT
    write_timeout: float = DEFAULT_WRITE_TIMEOUT
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    _tty: str | None = field(default=None, repr=False, compare=False)
    _user: str | None = field(default=None, repr=False, compare=False)
    _password: str | None = field(default=None, repr=False, compare=False)
    _serial_factory: SerialFactory | None = field(
        default=None,
        repr=False,
        compare=False,
    )
    _active_serial: Any | None = field(default=None, repr=False, compare=False)

    @classmethod
    def from_env(
        cls,
        env: Mapping[str, str] | None = None,
        serial_factory: SerialFactory | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> "KV260SerialConnection":
        source = os.environ if env is None else env
        tty = source.get("KVFPGA_TTY")
        user = source.get("KVFPGA_USER")
        password = source.get("KVFPGA_PASSWORD")
        return cls(
            tty_configured=bool(tty),
            user_configured=bool(user),
            password_configured=bool(password),
            _tty=tty,
            _user=user,
            _password=password,
            _serial_factory=serial_factory,
            retry_policy=retry_policy or RetryPolicy(),
        )

    def is_configured(self) -> bool:
        """Return whether required serial credentials are present."""

        return self.user_configured and self.password_configured

    def is_reachable(self) -> bool:
        """Open the tty, send a newline, and check for login or shell prompt."""

        def probe() -> bool:
            serial_session = None
            try:
                serial_session = self._open_serial()
                self._write(serial_session, b"\r\n")
                prompt, _buffer = self._read_until_prompt(
                    serial_session,
                    timeout=self.prompt_timeout,
                )
                return prompt is not None
            except (OSError, KV260SerialUnavailable):
                raise
            except KV260SerialError:
                return False
            finally:
                self._close_serial(serial_session)

        try:
            return self._retry_transient_port_errors(probe)
        except (OSError, KV260SerialUnavailable):
            return False

    def kernel_uname(self) -> str:
        def probe() -> str:
            with self as connection:
                result = connection._run_command("uname -a")
            if result.exit_status != 0:
                raise KV260SerialError("uname command failed")
            return result.output.strip()

        return self._retry_transient_port_errors(probe)

    def xrt_present(self) -> bool:
        command = (
            "command -v xrt-smi >/dev/null 2>&1 || "
            "command -v xbutil >/dev/null 2>&1 || "
            "test -e /usr/lib/libxrt_core.so || "
            "test -e /usr/lib/aarch64-linux-gnu/libxrt_core.so"
        )

        def probe() -> bool:
            with self as connection:
                result = connection._run_command(command)
            return result.exit_status == 0

        return self._retry_transient_port_errors(probe)

    def xmutil_listapps(self) -> Sequence[str]:
        with self as connection:
            result = connection._run_command("xmutil listapps")
        if result.exit_status != 0:
            return ()
        return tuple(line for line in result.output.splitlines() if line.strip())

    def __enter__(self) -> "KV260SerialConnection":
        serial_session = self._open_serial()
        try:
            self._login(serial_session)
        except Exception:
            self._close_serial(serial_session)
            raise
        self._active_serial = serial_session
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.logout()

    def logout(self) -> None:
        serial_session = self._active_serial
        self._active_serial = None
        if serial_session is None:
            return
        try:
            self._write(serial_session, b"exit\r\n")
        finally:
            self._close_serial(serial_session)

    def _retry_transient_port_errors(self, operation: Callable[[], T]) -> T:
        attempts = max(1, self.retry_policy.max_attempts)
        for failure_index in range(attempts):
            try:
                return operation()
            except (OSError, KV260SerialUnavailable) as exc:
                if not self._is_transient_port_error(exc):
                    raise
                if failure_index >= attempts - 1:
                    raise
                self.retry_policy.sleep_after_failure(failure_index)

        raise KV260SerialError("retry operation did not run")

    def _is_transient_port_error(
        self,
        exc: OSError | KV260SerialUnavailable,
    ) -> bool:
        if isinstance(exc, OSError):
            return True
        message = str(exc).lower()
        return "tty" in message or "port" in message or "device" in message

    def _open_serial(self) -> Any:
        tty = self._tty or detect_kv260_tty()
        if not tty:
            raise KV260SerialUnavailable("no KV260 serial tty detected")

        factory = self._serial_factory
        if factory is None:
            try:
                import serial  # type: ignore[import-not-found]
            except ImportError as exc:
                raise KV260SerialUnavailable("pyserial is not installed") from exc
            factory = serial.Serial

        return factory(
            port=tty,
            baudrate=self.baudrate,
            timeout=0.1,
            write_timeout=self.write_timeout,
        )

    def _login(self, serial_session: Any) -> None:
        if not self._user or not self._password:
            raise KV260SerialUnavailable("KVFPGA serial credentials are incomplete")

        self._write(serial_session, b"\r\n")
        prompt, _buffer = self._read_until_prompt(
            serial_session,
            timeout=self.prompt_timeout,
        )
        if prompt == "login":
            self._write_line(serial_session, self._user)
            prompt, _buffer = self._read_until_prompt(
                serial_session,
                timeout=self.prompt_timeout,
            )
        if prompt == "password":
            self._write_line(serial_session, self._password)
            prompt, _buffer = self._read_until_prompt(
                serial_session,
                timeout=self.prompt_timeout,
            )
        if prompt != "shell":
            raise KV260SerialError("serial shell prompt was not reached")

    def _run_command(self, command: str) -> SerialCommandResult:
        serial_session = self._active_serial
        if serial_session is None:
            raise KV260SerialError("serial session is not open")

        wrapped = f"{command}; printf '\\n{END_MARKER}:%s\\n' \"$?\""
        self._write_line(serial_session, wrapped)
        raw = self._read_until_pattern(
            serial_session,
            COMMAND_DONE,
            timeout=self.command_timeout,
        )
        match = COMMAND_DONE.search(raw)
        if match is None:
            raise KV260SerialError("command completion marker was not observed")

        exit_status = int(match.group(1).decode("ascii"))
        output = self._clean_command_output(command, raw[: match.start()])
        return SerialCommandResult(exit_status=exit_status, output=output)

    def _read_until_prompt(
        self,
        serial_session: Any,
        timeout: float,
    ) -> tuple[str | None, bytes]:
        deadline = time.monotonic() + timeout
        buffer = bytearray()
        while time.monotonic() < deadline:
            chunk = serial_session.read(READ_CHUNK_SIZE)
            if chunk:
                buffer.extend(chunk)
                data = bytes(buffer)
                if LOGIN_PROMPT.search(data):
                    return "login", data
                if PASSWORD_PROMPT.search(data):
                    return "password", data
                if SHELL_PROMPT.search(data):
                    return "shell", data
            else:
                time.sleep(0.02)
        return None, bytes(buffer)

    def _read_until_pattern(
        self,
        serial_session: Any,
        pattern: re.Pattern[bytes],
        timeout: float,
    ) -> bytes:
        deadline = time.monotonic() + timeout
        buffer = bytearray()
        while time.monotonic() < deadline:
            chunk = serial_session.read(READ_CHUNK_SIZE)
            if chunk:
                buffer.extend(chunk)
                data = bytes(buffer)
                if pattern.search(data):
                    return data
            else:
                time.sleep(0.02)
        raise KV260SerialError("serial read timed out")

    def _write_line(self, serial_session: Any, line: str) -> None:
        self._write(serial_session, line.encode("utf-8") + b"\r\n")

    def _write(self, serial_session: Any, payload: bytes) -> None:
        serial_session.write(payload)
        flush = getattr(serial_session, "flush", None)
        if flush is not None:
            flush()

    def _clean_command_output(self, command: str, raw: bytes) -> str:
        text = raw.decode("utf-8", errors="replace").replace("\r", "")
        lines = text.split("\n")
        cleaned: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped == command or stripped.startswith(f"{command}; "):
                continue
            if (
                command in stripped
                and "printf" in stripped
                and END_MARKER in stripped
            ):
                continue
            if stripped.endswith("$") or stripped.endswith("#"):
                continue
            cleaned.append(line.rstrip())
        return "\n".join(cleaned)

    def _close_serial(self, serial_session: Any | None) -> None:
        if serial_session is None:
            return
        close = getattr(serial_session, "close", None)
        if close is not None:
            close()
