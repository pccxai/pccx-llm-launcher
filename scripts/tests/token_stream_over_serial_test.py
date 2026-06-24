#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Tests for first-pass token streaming over the KV260 serial tty."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MODULE_PATH = ROOT / "contracts" / "token_stream_over_serial.py"
TEST_PATH = Path(__file__).resolve()

from contracts.axi_cmd_channel import AxiCmdMockBackend, NpuCmd, NpuStat


def load_module():
    spec = importlib.util.spec_from_file_location(
        "token_stream_over_serial",
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
    reads: list[bytes] = []

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        self.writes: list[bytes] = []
        self.closed = False
        self.reads = list(type(self).reads)
        type(self).instances.append(self)

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


def reset_fake(reads: list[bytes] | None = None) -> None:
    FakeSerial.instances = []
    FakeSerial.reads = list(reads or [])


def make_connection(module, fake_env: dict[str, str] | None = None):
    env = fake_env or {"KVFPGA_TTY": "/tmp/tty-kv260-token-test"}
    return module.KV260SerialConnection.from_env(
        env,
        serial_factory=FakeSerial,
    )


def test_type_contract_runs_without_tty_or_board() -> None:
    module = load_module()
    reset_fake()
    stream = module.TokenStreamOverSerial(connection=make_connection(module))

    assert isinstance(stream, module.TokenStreamProtocol)
    assert stream.eos_token_id == module.DEFAULT_EOS_TOKEN_ID
    assert stream.chunk_token_count == module.DEFAULT_CHUNK_TOKEN_COUNT


def test_input_tokens_use_marker_wrapped_length_prefixed_binary_chunks() -> None:
    module = load_module()
    payload = module.encode_input_stream([2, 65536, 9], chunk_token_count=2)

    assert payload.startswith(module.INPUT_BEGIN_MARKER)
    assert payload.endswith(module.INPUT_END_MARKER)
    assert payload.count(module.INPUT_CHUNK_TAG) == 2
    assert b"\x00\x00\x00\x08\x00\x00\x00\x02\x00\x01\x00\x00" in payload
    assert b"\x00\x00\x00\x04\x00\x00\x00\x09" in payload


def test_mock_axi_backend_simulates_full_round_trip() -> None:
    module = load_module()
    reset_fake([module.encode_output_stream([201, 202, module.DEFAULT_EOS_TOKEN_ID])])
    commands = [
        (
            NpuCmd(module.OP_BEGIN_INPUT, arg0=3),
            NpuStat(completion_count=1, last_opcode=module.OP_BEGIN_INPUT),
        ),
        (
            NpuCmd(module.OP_END_INPUT, arg0=3),
            NpuStat(completion_count=2, last_opcode=module.OP_END_INPUT),
        ),
        (
            NpuCmd(module.OP_READ_OUTPUT, arg0=0),
            NpuStat(completion_count=3, last_opcode=module.OP_READ_OUTPUT),
        ),
    ]

    with AxiCmdMockBackend(commands) as axi:
        stream = module.TokenStreamOverSerial(
            connection=make_connection(module),
            axi_channel=axi,
        )
        output_tokens = stream.infer([101, 102, 103])
        axi.assert_script_consumed()

    assert output_tokens == [201, 202, module.DEFAULT_EOS_TOKEN_ID]
    assert len(FakeSerial.instances) == 1
    written = b"".join(FakeSerial.instances[0].writes)
    assert written == module.encode_input_stream([101, 102, 103])
    assert FakeSerial.instances[0].closed is True


def test_recv_output_tokens_returns_partial_tokens_on_timeout() -> None:
    module = load_module()
    reset_fake([module.OUTPUT_BEGIN_MARKER])
    stream = module.TokenStreamOverSerial(connection=make_connection(module))

    assert stream.recv_output_tokens(timeout_s=0.01) == []
    assert FakeSerial.instances[-1].closed is True


def test_live_serial_probe_skips_without_tty() -> None:
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

    stream = module.TokenStreamOverSerial.from_env()
    assert isinstance(stream, module.TokenStreamProtocol)


def test_source_has_no_credential_leaks_or_unsupported_paths() -> None:
    source = read_text(MODULE_PATH)
    test_source = read_text(TEST_PATH)
    scan_text = source + "\n" + test_source

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


test_type_contract_runs_without_tty_or_board()
test_input_tokens_use_marker_wrapped_length_prefixed_binary_chunks()
test_mock_axi_backend_simulates_full_round_trip()
test_recv_output_tokens_returns_partial_tokens_on_timeout()
test_live_serial_probe_skips_without_tty()
test_source_has_no_credential_leaks_or_unsupported_paths()
test_source_headers_for_touched_python_files()

print("token stream over serial tests ok")
