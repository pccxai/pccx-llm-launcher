#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Unit tests for the board-less KV260 connection mock."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "kv260_connection_mock.py"
SERIAL_MODULE_PATH = ROOT / "contracts" / "kv260_serial_connection.py"
TEST_PATH = Path(__file__).resolve()
SCENARIO_DIR = ROOT / "tests" / "fixtures" / "scenarios"


def load_module():
    sys.path.insert(0, str(ROOT))
    serial_spec = importlib.util.spec_from_file_location(
        "contracts.kv260_serial_connection",
        SERIAL_MODULE_PATH,
    )
    serial_module = importlib.util.module_from_spec(serial_spec)
    assert serial_spec.loader is not None
    sys.modules[serial_spec.name] = serial_module
    serial_spec.loader.exec_module(serial_module)

    spec = importlib.util.spec_from_file_location(
        "contracts.kv260_connection_mock",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, serial_module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_raises(error_type, callback) -> None:
    try:
        callback()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def test_happy_path_scenario_implements_serial_connection_protocol() -> None:
    module, serial_module = load_module()

    connection = module.KV260ConnectionMock.from_scenario("happy_path")

    assert isinstance(connection, serial_module.KV260ConnectionProtocol)
    assert connection.is_reachable() is True
    assert connection.kernel_uname() == (
        "Linux kv260-happy 6.6.0-pccx-mock #1 SMP PREEMPT aarch64 GNU/Linux"
    )
    assert connection.xrt_present() is True
    assert connection.xrt_version() == "XRT mock 2.16.0"
    assert connection.xmutil_listapps() == (
        "app: pccx-npu",
        "app: diagnostics",
        "app: shell",
    )


def test_xrt_missing_scenario_keeps_board_reachable_without_xrt() -> None:
    module, _serial_module = load_module()

    connection = module.KV260ConnectionMock.from_scenario("xrt_missing")

    assert connection.is_reachable() is True
    assert connection.kernel_uname() == (
        "Linux kv260-no-xrt 6.6.0-pccx-mock #1 SMP PREEMPT aarch64 GNU/Linux"
    )
    assert connection.xrt_present() is False
    assert connection.xrt_version() == ""
    assert connection.xmutil_listapps() == ()


def test_partial_apps_scenario_returns_configured_listapps_subset() -> None:
    module, _serial_module = load_module()

    connection = module.KV260ConnectionMock.from_scenario("partial_apps")

    assert connection.is_reachable() is True
    assert connection.xrt_present() is True
    assert connection.xrt_version() == "XRT mock 2.16.0-partial"
    assert connection.xmutil_listapps() == ("app: pccx-npu",)


def test_direct_state_builder_defaults_xrt_presence_from_version() -> None:
    module, _serial_module = load_module()

    connection = module.KV260ConnectionMock.from_state(
        kernel_uname="Linux kv260-direct 6.6.0-pccx-mock aarch64",
        xrt_version="XRT mock direct",
        xmutil_listapps=["app: direct"],
    )

    assert connection.is_reachable() is True
    assert connection.kernel_uname() == "Linux kv260-direct 6.6.0-pccx-mock aarch64"
    assert connection.xrt_present() is True
    assert connection.xrt_version() == "XRT mock direct"
    assert connection.xmutil_listapps() == ("app: direct",)


def test_scenario_loader_rejects_missing_or_path_like_names() -> None:
    module, _serial_module = load_module()

    assert_raises(
        module.KV260ConnectionMockScenarioError,
        lambda: module.KV260ConnectionMock.from_scenario("../happy_path"),
    )
    assert_raises(
        module.KV260ConnectionMockScenarioError,
        lambda: module.KV260ConnectionMock.from_scenario("missing"),
    )


def test_expected_scenario_fixture_count() -> None:
    scenario_files = sorted(
        path
        for path in SCENARIO_DIR.iterdir()
        if path.suffix in {".yaml", ".json"}
    )

    assert [path.stem for path in scenario_files] == [
        "happy_path",
        "partial_apps",
        "xrt_missing",
    ]


def test_source_has_no_board_calls_or_credential_leaks() -> None:
    source = read_text(MODULE_PATH)
    test_source = read_text(TEST_PATH)
    fixture_source = "\n".join(read_text(path) for path in SCENARIO_DIR.iterdir())
    scan_text = "\n".join([source, fixture_source])

    forbidden_terms = [
        "param" + "iko",
        "s" + "cp ",
        "subprocess",
        "os.system",
        "popen",
        "socket",
        "requests",
        "urllib",
        "serial.Serial",
        "/dev/",
        "/dev/mem",
        "KVFPGA_PASSWORD",
        "KVFPGA_USER",
        "KVFPGA_HOST",
    ]
    lowered_source = source.lower()
    for term in forbidden_terms:
        assert term.lower() not in lowered_source, term

    assert "print(" not in source
    assert "logging." not in source
    assert ("raw " + "credential") not in test_source.lower()

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


test_happy_path_scenario_implements_serial_connection_protocol()
test_xrt_missing_scenario_keeps_board_reachable_without_xrt()
test_partial_apps_scenario_returns_configured_listapps_subset()
test_direct_state_builder_defaults_xrt_presence_from_version()
test_scenario_loader_rejects_missing_or_path_like_names()
test_expected_scenario_fixture_count()
test_source_has_no_board_calls_or_credential_leaks()
test_source_headers_for_touched_python_files()

print("kv260 connection mock tests ok")
