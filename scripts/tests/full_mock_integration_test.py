#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Full-mock integration test for the offline launcher harness."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from contracts.axi_cmd_channel import AxiCmdMockBackend, NpuStat
from contracts.dummy_e2e_contract import dummy_e2e, dummy_e2e_trace_frames
from contracts.kv260_connection_mock import KV260ConnectionMock
from contracts.trace_capture_client import (
    PCCX_TRACE_BEGIN_MARKER,
    TraceCaptureClient,
    serial_frame_crc32,
)


TEST_PATH = Path(__file__).resolve()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_trace(path: Path) -> list[dict[str, object]]:
    lines = read_text(path).splitlines()
    assert lines[0] == PCCX_TRACE_BEGIN_MARKER
    assert lines[-1] == f"===PCCX_TRACE_END seq={len(lines[1:-1])}==="

    frames: list[dict[str, object]] = []
    for seq, line in enumerate(lines[1:-1]):
        frame = json.loads(line)
        assert frame["seq"] == seq
        assert frame["crc32"] == serial_frame_crc32(
            seq=int(frame["seq"]),
            frame_idx=int(frame["frame_idx"]),
            axi_stat=int(frame["axi_stat"]),
            engine_completion=int(frame["engine_completion"]),
            cycles=int(frame["cycles"]),
            err=frame["err"] if isinstance(frame["err"], str) else None,
        )
        frames.append(frame)
    return frames


def test_happy_path_full_mock_dummy_e2e_trace_capture() -> None:
    connection = KV260ConnectionMock.from_scenario("happy_path")

    assert connection.is_reachable() is True
    assert connection.xrt_present() is True
    assert connection.xrt_version() == "XRT mock 2.16.0"
    assert "app: pccx-npu" in connection.xmutil_listapps()

    stream = dummy_e2e(42)
    expected_statuses = tuple(trace.status for trace in stream.command_trace)
    expected_axi_stats = tuple(status.register_value() for status in expected_statuses)

    with AxiCmdMockBackend() as axi:
        for trace, expected_status in zip(stream.command_trace, expected_statuses):
            axi.issue(trace.command)
            observed_status = axi.poll_stat()
            registers = axi.snapshot_registers()

            assert observed_status == expected_status
            assert observed_status.error is False
            assert registers["MMIO_CMD"] == trace.command.register_value()
            assert registers["MMIO_STAT"] == expected_status.register_value()
        assert axi.completion_count == len(stream.command_trace)

    with tempfile.TemporaryDirectory() as temp_dir:
        trace_path = Path(temp_dir) / "full-mock-dummy-e2e.trace.jsonl"
        client = TraceCaptureClient(file_path=trace_path)
        try:
            client.capture(dummy_e2e_trace_frames(stream))
        finally:
            client.close()
        frames = parse_trace(trace_path)

    assert len(frames) == len(stream.command_trace)
    assert len(frames) == 3
    assert [frame["frame_idx"] for frame in frames] == [0, 1, 2]
    assert [frame["axi_stat"] for frame in frames] == list(expected_axi_stats)
    assert [frame["engine_completion"] for frame in frames] == [
        status.completion_count for status in expected_statuses
    ]
    assert [frame["cycles"] for frame in frames] == [128, 256, 384]
    assert all(frame["err"] is None for frame in frames)
    assert all(
        status == NpuStat(index, index, False, False, 0)
        for index, status in enumerate(expected_statuses, 1)
    )
    assert stream.completed is True
    assert dict(stream.safety_flags)["boardAccess"] is False
    assert dict(stream.safety_flags)["networkCalls"] is False
    assert dict(stream.safety_flags)["environmentRead"] is False


def test_source_has_full_mock_claim_guard() -> None:
    source = read_text(TEST_PATH)
    lowered = source.lower()

    forbidden_runtime_terms = [
        "huggingface" + "_hub",
        "hf_hub" + "_download",
        "request" + "s",
        "url" + "lib",
        "sock" + "et",
        "param" + "iko",
        "fab" + "ric",
        "os." + "environ",
        "get" + "env",
        "/dev/" + "mem",
        "serial." + "serial",
    ]
    for term in forbidden_runtime_terms:
        assert term not in lowered, term

    forbidden_private_patterns = [
        "/" + r"home/[^\s\"']+",
        "/" + r"Users/[^\s\"']+",
        r"[A-Za-z]:\\" + r"Users\\",
        r"\b(?:api[_-]?key|authorization|bearer|password|secret|tok"
        r"en)\b\s*[:=]",
    ]
    for pattern in forbidden_private_patterns:
        assert not re.search(pattern, source, re.IGNORECASE), pattern


def test_source_headers_for_touched_test_file() -> None:
    assert read_text(TEST_PATH).splitlines()[:3] == [
        "#!/usr/bin/env python3",
        "# SPDX-License-Identifier: Apache-2.0",
        "# Copyright 2026 pccxai",
    ]


test_happy_path_full_mock_dummy_e2e_trace_capture()
test_source_has_full_mock_claim_guard()
test_source_headers_for_touched_test_file()

print("full mock integration tests ok")
