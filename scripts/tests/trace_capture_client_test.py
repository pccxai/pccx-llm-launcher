#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Type-focused tests for launcher trace capture framing."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contracts.dummy_e2e_contract import dummy_e2e, dummy_e2e_trace_frames
from contracts.trace_capture_client import (
    PCCX_TRACE_BEGIN_MARKER,
    TraceCaptureClient,
    TraceCaptureFrame,
    serial_frame_crc32,
)


CLI_PATH = ROOT / "scripts" / "pccx-launcher"
MODULE_PATH = ROOT / "contracts" / "trace_capture_client.py"
TEST_PATH = Path(__file__).resolve()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_capture(text: str) -> list[str]:
    return text.splitlines()


def assert_valid_v2_frame(line: str, seq: int) -> dict[str, object]:
    frame = json.loads(line)

    assert frame["seq"] == seq
    assert set(frame) == {
        "seq",
        "frame_idx",
        "axi_stat",
        "engine_completion",
        "cycles",
        "err",
        "crc32",
    }
    assert frame["crc32"] == serial_frame_crc32(
        seq=int(frame["seq"]),
        frame_idx=int(frame["frame_idx"]),
        axi_stat=int(frame["axi_stat"]),
        engine_completion=int(frame["engine_completion"]),
        cycles=int(frame["cycles"]),
        err=frame["err"] if isinstance(frame["err"], str) else None,
    )
    return frame


def test_crc32_matches_lab_v2_contract_fixture() -> None:
    assert serial_frame_crc32(0, 0, 1, 3, 128, None) == 230_227_294


def test_trace_capture_client_writes_stdout_style_text_sink() -> None:
    sink = io.StringIO()
    client = TraceCaptureClient(serial_port=sink)
    client.capture(
        (
            TraceCaptureFrame(
                frame_idx=0,
                axi_stat=1,
                engine_completion=3,
                cycles=128,
            ),
        ),
    )

    lines = split_capture(sink.getvalue())
    assert lines[0] == PCCX_TRACE_BEGIN_MARKER
    assert_valid_v2_frame(lines[1], seq=0)
    assert lines[2] == "===PCCX_TRACE_END seq=1==="


def test_trace_capture_client_writes_bytes_serial_sink_without_real_serial() -> None:
    sink = io.BytesIO()
    client = TraceCaptureClient(serial_port=sink)
    client.capture(
        (
            TraceCaptureFrame(
                frame_idx=7,
                axi_stat=9,
                engine_completion=1,
                cycles=512,
                err="fixture warning",
            ),
        ),
    )

    lines = split_capture(sink.getvalue().decode("utf-8"))
    frame = assert_valid_v2_frame(lines[1], seq=0)
    assert frame["frame_idx"] == 7
    assert frame["err"] == "fixture warning"


def test_dummy_e2e_trace_frames_are_v2_capture_ready() -> None:
    stream = dummy_e2e(42)
    frames = dummy_e2e_trace_frames(stream)

    assert len(frames) == len(stream.command_trace)
    assert tuple(frame.frame_idx for frame in frames) == (0, 1, 2)
    assert tuple(frame.axi_stat for frame in frames) == tuple(
        trace.mmio_stat for trace in stream.command_trace
    )
    assert tuple(frame.engine_completion for frame in frames) == (1, 2, 3)
    assert tuple(frame.cycles for frame in frames) == (128, 256, 384)


def test_cli_dummy_e2e_capture_writes_v2_framed_fixture_file() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        capture_path = Path(temp_dir) / "dummy-e2e.trace.jsonl"
        out = subprocess.run(
            [
                str(CLI_PATH),
                "dummy-e2e",
                "--seed",
                "42",
                "--capture",
                str(capture_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        assert out.stderr == ""
        assert "dummy_e2e: ok\n" in out.stdout
        lines = split_capture(read_text(capture_path))

    assert lines[0] == PCCX_TRACE_BEGIN_MARKER
    assert lines[-1] == "===PCCX_TRACE_END seq=3==="
    assert len(lines) == 5
    frames = [assert_valid_v2_frame(line, seq=index) for index, line in enumerate(lines[1:-1])]
    assert [frame["frame_idx"] for frame in frames] == [0, 1, 2]


def test_trace_capture_source_headers_and_no_runtime_claims() -> None:
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

    lowered = read_text(MODULE_PATH).lower()
    for term in ("os.environ", "getenv", "requests", "urllib", "socket", "paramiko", "fabric"):
        assert term not in lowered, term


test_crc32_matches_lab_v2_contract_fixture()
test_trace_capture_client_writes_stdout_style_text_sink()
test_trace_capture_client_writes_bytes_serial_sink_without_real_serial()
test_dummy_e2e_trace_frames_are_v2_capture_ready()
test_cli_dummy_e2e_capture_writes_v2_framed_fixture_file()
test_trace_capture_source_headers_and_no_runtime_claims()

print("trace capture client tests ok")
