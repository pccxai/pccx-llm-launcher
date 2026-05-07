#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Full-mock Gemma W4 path integration test."""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TEST_PATH = Path(__file__).resolve()

from contracts.axi_cmd_channel import AxiCmdMockBackend, NpuCmd, NpuStat
from contracts.gemma_weight_prep_contract import GemmaWeightPrep
from contracts.kv260_serial_connection import KV260SerialConnection
from contracts.token_stream_over_serial import (
    DEFAULT_EOS_TOKEN_ID,
    OP_BEGIN_INPUT,
    OP_END_INPUT,
    OP_READ_OUTPUT,
    TokenStreamOverSerial,
    encode_input_stream,
    encode_output_stream,
)


GROUP_SIZE = 64
OP_LOAD_W4_MANIFEST = 0x40
EXPECTED_PACKED_HEX = "103e5c7ac4a5a687"
EXPECTED_PACKED_SHA256 = (
    "fcd9cc6de77604e760378ed7f7bc7446317e418c2c457f304e3d47207090302d"
)
EXPECTED_OUTPUT_TOKENS = [4242132077, 3883271399, DEFAULT_EOS_TOKEN_ID]


class FakeSerial:
    instances: list["FakeSerial"] = []
    reads: list[bytes] = []

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        self.writes: list[bytes] = []
        self.reads = list(type(self).reads)
        self.closed = False
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


@dataclass(frozen=True)
class GemmaMockRun:
    manifest_id: str
    manifest_sha256: str
    packed_hex: str
    prompt_tokens: tuple[int, ...]
    output_tokens: tuple[int, ...]
    register_snapshot: tuple[tuple[str, int], ...]
    serial_payload: bytes


def reset_fake_serial(reads: list[bytes]) -> None:
    FakeSerial.instances = []
    FakeSerial.reads = list(reads)


def fixed_bf16_shaped_weights() -> np.ndarray:
    return np.array(
        [
            [0.0, 0.5, -1.0, 1.5, -2.0, 2.5, -3.0, 3.5],
            [4.0, -4.5, 5.0, -5.5, 6.0, -6.5, 7.0, -7.5],
        ],
        dtype=np.float32,
    )


def make_connection() -> KV260SerialConnection:
    return KV260SerialConnection.from_env(
        {"KVFPGA_TTY": "/tmp/pccx-token-stream-mock"},
        serial_factory=FakeSerial,
    )


def output_tokens_from_sha256(packed_sha256: str) -> list[int]:
    return [
        int(packed_sha256[0:8], 16),
        int(packed_sha256[8:16], 16),
        DEFAULT_EOS_TOKEN_ID,
    ]


def run_full_mock_gemma_path() -> GemmaMockRun:
    manifest = GemmaWeightPrep().prepare_real(
        fixed_bf16_shaped_weights(),
        group_size=GROUP_SIZE,
    )
    tile = manifest.tiles[0]
    packed = tile.packed_nibbles
    prompt_tokens = list(packed)
    output_tokens = output_tokens_from_sha256(manifest.packed_sha256)

    reset_fake_serial([encode_output_stream(output_tokens)])
    checksum_prefix = int(manifest.packed_sha256[0:8], 16)
    commands = [
        (
            NpuCmd(
                opcode=OP_LOAD_W4_MANIFEST,
                arg0=len(packed),
                arg1=GROUP_SIZE,
                arg2=checksum_prefix,
            ),
            NpuStat(completion_count=1, last_opcode=OP_LOAD_W4_MANIFEST),
        ),
        (
            NpuCmd(opcode=OP_BEGIN_INPUT, arg0=len(prompt_tokens)),
            NpuStat(completion_count=2, last_opcode=OP_BEGIN_INPUT),
        ),
        (
            NpuCmd(opcode=OP_END_INPUT, arg0=len(prompt_tokens)),
            NpuStat(completion_count=3, last_opcode=OP_END_INPUT),
        ),
        (
            NpuCmd(opcode=OP_READ_OUTPUT, arg0=0),
            NpuStat(completion_count=4, last_opcode=OP_READ_OUTPUT),
        ),
    ]

    with AxiCmdMockBackend(commands) as axi:
        axi.issue(commands[0][0])
        assert axi.poll_stat() == commands[0][1]
        stream = TokenStreamOverSerial(
            connection=make_connection(),
            axi_channel=axi,
            output_timeout_s=0.05,
        )
        observed_output = stream.infer(prompt_tokens)
        axi.assert_script_consumed()
        register_snapshot = tuple(sorted(axi.snapshot_registers().items()))

    assert len(FakeSerial.instances) == 1
    serial_payload = b"".join(FakeSerial.instances[0].writes)
    assert FakeSerial.instances[0].closed is True

    return GemmaMockRun(
        manifest_id=manifest.manifest_id,
        manifest_sha256=manifest.packed_sha256,
        packed_hex=packed.hex(),
        prompt_tokens=tuple(prompt_tokens),
        output_tokens=tuple(observed_output),
        register_snapshot=register_snapshot,
        serial_payload=serial_payload,
    )


def test_full_mock_gemma_w4_path_is_deterministic() -> None:
    first = run_full_mock_gemma_path()
    second = run_full_mock_gemma_path()

    assert first == second
    assert first.manifest_id == "gemma_weight_prep_real_w4_fcd9cc6de776"
    assert first.manifest_sha256 == EXPECTED_PACKED_SHA256
    assert first.packed_hex == EXPECTED_PACKED_HEX
    assert first.prompt_tokens == (16, 62, 92, 122, 196, 165, 166, 135)
    assert first.output_tokens == tuple(EXPECTED_OUTPUT_TOKENS)
    assert first.serial_payload == encode_input_stream(first.prompt_tokens)


def test_manifest_checksum_matches_packed_bytes() -> None:
    manifest = GemmaWeightPrep().prepare_real(
        fixed_bf16_shaped_weights(),
        group_size=GROUP_SIZE,
    )
    packed = manifest.tiles[0].packed_nibbles

    assert manifest.group_size == GROUP_SIZE
    assert manifest.hf_touched is False
    assert manifest.tiles[0].packed_sha256 == EXPECTED_PACKED_SHA256
    assert manifest.packed_sha256 == EXPECTED_PACKED_SHA256
    assert packed == bytes.fromhex(EXPECTED_PACKED_HEX)
    assert hashlib.sha256(packed).hexdigest() == EXPECTED_PACKED_SHA256


def test_source_has_offline_and_claim_guards() -> None:
    source = TEST_PATH.read_text(encoding="utf-8")
    lowered = source.lower()

    forbidden_runtime_terms = [
        "trans" + "formers",
        "hugging" + "face_hub",
        "hf_hub_" + "download",
        "from_" + "pretrained",
        ".safe" + "tensors",
        ".g" + "guf",
        ".p" + "t",
        ".p" + "th",
        "req" + "uests",
        "url" + "lib",
        "sub" + "process",
        "sock" + "et",
        "/dev/" + "mem",
        "/dev/" + "tty",
        "serial" + ".serial",
    ]
    for term in forbidden_runtime_terms:
        assert term not in lowered, term

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
    for claim in forbidden_claims:
        assert claim.lower() not in lowered, claim


def test_source_headers_for_integration_test() -> None:
    assert TEST_PATH.read_text(encoding="utf-8").splitlines()[:3] == [
        "#!/usr/bin/env python3",
        "# SPDX-License-Identifier: Apache-2.0",
        "# Copyright 2026 pccxai",
    ]


test_full_mock_gemma_w4_path_is_deterministic()
test_manifest_checksum_matches_packed_bytes()
test_source_has_offline_and_claim_guards()
test_source_headers_for_integration_test()

print("full-mock Gemma W4 path integration test ok")
