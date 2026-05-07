#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Tests for the KV260 USB tty serial connection backend."""

from __future__ import annotations

import importlib.util
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "kv260_serial_connection.py"
TEST_PATH = Path(__file__).resolve()
TEST_PASSWORD_VALUE = "kv260-" + "serial-" + "secret-for-test"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "kv260_serial_connection",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class FakeSerial:
    instances: list["FakeSerial"] = []

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        self.writes: list[bytes] = []
        self.closed = False
        self.reads = list(type(self).reads)
        type(self).instances.append(self)

    reads: list[bytes] = []

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


def reset_fake(reads: list[bytes]) -> None:
    FakeSerial.instances = []
    FakeSerial.reads = reads


class TransientFailingSerialFactory:
    def __init__(self, failures_before_success: int) -> None:
        self.failures_before_success = failures_before_success
        self.calls = 0

    def __call__(self, *args, **kwargs) -> FakeSerial:
        self.calls += 1
        if self.calls <= self.failures_before_success:
            raise OSError("transient serial port busy")
        return FakeSerial(*args, **kwargs)


def test_type_contract_and_env_presence_only() -> None:
    module = load_module()
    fake_env = {
        "KVFPGA_HOST": "ignored-host.example.invalid",
        "KVFPGA_TTY": "/dev/ttyUSB-kv260-test",
        "KVFPGA_USER": "kv260-user-for-test",
        "KVFPGA_PASSWORD": TEST_PASSWORD_VALUE,
    }
    connection = module.KV260SerialConnection.from_env(
        fake_env,
        serial_factory=FakeSerial,
    )
    rendered = repr(connection)

    assert isinstance(connection, module.KV260ConnectionProtocol)
    assert connection.is_configured() is True
    assert connection.tty_configured is True
    assert connection.user_configured is True
    assert connection.password_configured is True
    assert "ignored-host" not in rendered
    assert fake_env["KVFPGA_TTY"] not in rendered
    assert fake_env["KVFPGA_USER"] not in rendered
    assert fake_env["KVFPGA_PASSWORD"] not in rendered


def test_tty_override_and_auto_detect_helpers() -> None:
    module = load_module()

    assert module.kv260_tty_candidates({"KVFPGA_TTY": "/tmp/tty-kv260"}) == (
        "/tmp/tty-kv260",
    )
    assert module.detect_kv260_tty({"KVFPGA_TTY": "/tmp/tty-kv260"}) == (
        "/tmp/tty-kv260"
    )
    assert isinstance(module.kv260_tty_candidates({}), tuple)


def test_reachable_accepts_login_or_shell_prompt() -> None:
    module = load_module()
    fake_env = {"KVFPGA_TTY": "/tmp/tty-kv260"}

    reset_fake([b"kv260 login: "])
    login_connection = module.KV260SerialConnection.from_env(
        fake_env,
        serial_factory=FakeSerial,
    )
    assert login_connection.is_reachable() is True
    assert FakeSerial.instances[-1].closed is True

    reset_fake([b"root@kv260:~$ "])
    shell_connection = module.KV260SerialConnection.from_env(
        fake_env,
        serial_factory=FakeSerial,
    )
    assert shell_connection.is_reachable() is True
    assert FakeSerial.instances[-1].closed is True


def test_retry_policy_recovers_after_three_transient_port_failures() -> None:
    module = load_module()
    fake_env = {"KVFPGA_TTY": "/tmp/tty-kv260"}
    retry_delays: list[float] = []
    retry_policy = module.RetryPolicy(
        max_attempts=4,
        base_delay=0.01,
        max_delay=1.0,
        jitter_ratio=0.0,
        sleeper=retry_delays.append,
    )
    serial_factory = TransientFailingSerialFactory(failures_before_success=3)

    reset_fake([b"kv260 login: "])
    connection = module.KV260SerialConnection.from_env(
        fake_env,
        serial_factory=serial_factory,
        retry_policy=retry_policy,
    )

    assert connection.is_reachable() is True
    assert serial_factory.calls == 4
    assert retry_delays == [0.01, 0.02, 0.04]
    assert len(FakeSerial.instances) == 1
    assert FakeSerial.instances[-1].closed is True


def test_login_uname_and_logout_over_serial() -> None:
    module = load_module()
    fake_env = {
        "KVFPGA_TTY": "/tmp/tty-kv260",
        "KVFPGA_USER": "kv260-user-for-test",
        "KVFPGA_PASSWORD": TEST_PASSWORD_VALUE,
    }
    reset_fake(
        [
            b"kv260 login: ",
            b"Password: ",
            b"root@kv260:~$ ",
            (
                b"root@kv260:~$ uname -a; printf "
                b"'\\n__PCCX_KV260_SERIAL_DONE__:%s\\n' \"$?\"\r\n"
                b"Linux kv260 6.6.0-test #1 SMP PREEMPT aarch64 GNU/Linux\r\n"
                b"__PCCX_KV260_SERIAL_DONE__:0\r\n"
                b"root@kv260:~$ "
            ),
        ],
    )
    connection = module.KV260SerialConnection.from_env(
        fake_env,
        serial_factory=FakeSerial,
    )

    assert connection.kernel_uname() == (
        "Linux kv260 6.6.0-test #1 SMP PREEMPT aarch64 GNU/Linux"
    )
    writes = b"".join(FakeSerial.instances[-1].writes)
    assert b"uname -a" in writes
    assert writes.endswith(b"exit\r\n")
    assert FakeSerial.instances[-1].closed is True


def test_xrt_present_and_xmutil_listapps_use_serial_commands() -> None:
    module = load_module()
    fake_env = {
        "KVFPGA_TTY": "/tmp/tty-kv260",
        "KVFPGA_USER": "kv260-user-for-test",
        "KVFPGA_PASSWORD": TEST_PASSWORD_VALUE,
    }

    reset_fake([b"$ ", b"__PCCX_KV260_SERIAL_DONE__:0\r\n$ "])
    connection = module.KV260SerialConnection.from_env(
        fake_env,
        serial_factory=FakeSerial,
    )
    assert connection.xrt_present() is True

    reset_fake(
        [
            b"$ ",
            (
                b"$ xmutil listapps; printf "
                b"'\\n__PCCX_KV260_SERIAL_DONE__:%s\\n' \"$?\"\r\n"
                b"accelerated_app\r\n"
                b"diagnostic_app\r\n"
                b"__PCCX_KV260_SERIAL_DONE__:0\r\n$ "
            ),
        ],
    )
    listapps_connection = module.KV260SerialConnection.from_env(
        fake_env,
        serial_factory=FakeSerial,
    )
    assert listapps_connection.xmutil_listapps() == (
        "accelerated_app",
        "diagnostic_app",
    )


def test_live_serial_probe_skips_gracefully_without_tty() -> None:
    module = load_module()
    tty = module.detect_kv260_tty()
    if tty is None:
        print("skip: no KV260 tty device detected")
        return
    try:
        import serial  # type: ignore[import-not-found]  # noqa: F401
    except ImportError:
        print("skip: pyserial is not installed")
        return
    if not os.environ.get("KVFPGA_USER") or not os.environ.get("KVFPGA_PASSWORD"):
        print("skip: KVFPGA serial credentials are incomplete")
        return

    connection = module.KV260SerialConnection.from_env()
    assert isinstance(connection.is_reachable(), bool)


def test_source_has_no_credential_leaks_or_unsupported_paths() -> None:
    source = read_text(MODULE_PATH)
    test_source = read_text(TEST_PATH)
    scan_text = source

    forbidden_terms = [
        "param" + "iko",
        "s" + "cp ",
        "subprocess",
        "os.system",
        "popen",
        "socket",
        "requests",
        "urllib",
        "transformers",
        "huggingface_hub",
        "/dev/mem",
    ]
    lowered_source = source.lower()
    for term in forbidden_terms:
        assert term not in lowered_source, term

    assert "print(" not in source
    assert "logging." not in source
    assert TEST_PASSWORD_VALUE not in source
    assert ("serial-" + "secret-for-test") not in test_source

    forbidden_claims = [
        "production-" + "ready",
        "marketplace-" + "ready",
        "stable " + "API",
        "stable " + "ABI",
        "KV260 inference " + "works",
        "Gemma 3N E4B " + "runs on KV260",
        "20 tok/s " + "achieved",
        "timing " + "closed",
        "bitstream " + "ready",
    ]
    lowered = scan_text.lower()
    for claim in forbidden_claims:
        assert claim.lower() not in lowered, claim

    assert not re.search(r"\bssh\s+[^\"']+", source, re.IGNORECASE)


def test_source_headers_for_touched_python_files() -> None:
    expected_headers = {
        MODULE_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        TEST_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
    }
    for path, header in expected_headers.items():
        assert read_text(path).splitlines()[: len(header)] == header, path


test_type_contract_and_env_presence_only()
test_tty_override_and_auto_detect_helpers()
test_reachable_accepts_login_or_shell_prompt()
test_retry_policy_recovers_after_three_transient_port_failures()
test_login_uname_and_logout_over_serial()
test_xrt_present_and_xmutil_listapps_use_serial_commands()
test_live_serial_probe_skips_gracefully_without_tty()
test_source_has_no_credential_leaks_or_unsupported_paths()
test_source_headers_for_touched_python_files()

print("kv260 serial connection tests ok")
