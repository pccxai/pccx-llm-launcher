#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Unit tests for the offline AXI command-channel mock backend."""

from __future__ import annotations

import importlib.util
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "axi_cmd_channel.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "axi_cmd_channel",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def assert_raises(error_type, callback) -> None:
    try:
        callback()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def test_basic_issue_poll_cycle_updates_register_model() -> None:
    module = load_module()
    cmd = module.NpuCmd(opcode=3, arg0=4, arg1=5, arg2=6, flags=7)

    backend = module.AxiCmdMockBackend()
    assert backend.snapshot_registers() == {
        module.MMIO_CMD: 0,
        module.MMIO_STAT: module.NpuStat().register_value(),
    }

    with backend as channel:
        channel.issue(cmd)
        first = channel.poll_stat()
        second = channel.poll_stat()
        registers = channel.snapshot_registers()

    assert first == second
    assert first == module.NpuStat(completion_count=1, last_opcode=3)
    assert backend.completion_count == 1
    assert backend.last_cmd == cmd
    assert registers[module.MMIO_CMD] == cmd.register_value()
    assert registers[module.MMIO_STAT] == first.register_value()
    assert_raises(RuntimeError, lambda: backend.poll_stat())


def test_multiple_issue_cycles_increment_fake_completion_counter() -> None:
    module = load_module()

    with module.AxiCmdMockBackend() as channel:
        channel.issue(module.NpuCmd(opcode=1))
        assert channel.poll_stat() == module.NpuStat(
            completion_count=1,
            last_opcode=1,
        )

        channel.issue(module.NpuCmd(opcode=2, arg0=10))
        assert channel.poll_stat() == module.NpuStat(
            completion_count=2,
            last_opcode=2,
        )


def test_scripted_reply_mode_verifies_commands_and_returns_expected_status() -> None:
    module = load_module()
    first_cmd = module.NpuCmd(opcode=9, arg0=1)
    second_cmd = module.NpuCmd(opcode=10, arg0=2)
    first_stat = module.NpuStat(
        completion_count=1,
        last_opcode=9,
        status_code=7,
    )
    second_stat = module.NpuStat(
        completion_count=2,
        last_opcode=10,
        error=True,
        status_code=12,
    )

    with module.AxiCmdMockBackend(
        scripted_replies=[
            (first_cmd, first_stat),
            (second_cmd, second_stat),
        ],
    ) as channel:
        channel.issue(first_cmd)
        assert channel.poll_stat() == first_stat
        assert channel.remaining_scripted_replies == 1

        channel.issue(second_cmd)
        assert channel.poll_stat() == second_stat
        assert channel.completion_count == 2
        assert channel.remaining_scripted_replies == 0
        channel.assert_script_consumed()


def test_scripted_reply_mode_rejects_unexpected_command_without_side_effect() -> None:
    module = load_module()
    expected_cmd = module.NpuCmd(opcode=1)
    unexpected_cmd = module.NpuCmd(opcode=2)
    expected_stat = module.NpuStat(completion_count=1, last_opcode=1)

    with module.AxiCmdMockBackend(
        scripted_replies=[(expected_cmd, expected_stat)],
    ) as channel:
        assert_raises(
            module.ScriptedReplyMismatch,
            lambda: channel.issue(unexpected_cmd),
        )
        assert channel.completion_count == 0
        assert channel.remaining_scripted_replies == 1
        assert channel.snapshot_registers() == {
            module.MMIO_CMD: 0,
            module.MMIO_STAT: module.NpuStat().register_value(),
        }


def test_issue_and_poll_are_safe_under_concurrent_test_use() -> None:
    module = load_module()

    with module.AxiCmdMockBackend() as channel:

        def issue_and_poll(index: int):
            channel.issue(module.NpuCmd(opcode=index + 1))
            return channel.poll_stat()

        with ThreadPoolExecutor(max_workers=4) as executor:
            stats = list(executor.map(issue_and_poll, range(8)))

        assert channel.completion_count == 8
        assert len(stats) == 8
        assert all(isinstance(stat, module.NpuStat) for stat in stats)
        assert channel.poll_stat().completion_count == 8


test_basic_issue_poll_cycle_updates_register_model()
test_multiple_issue_cycles_increment_fake_completion_counter()
test_scripted_reply_mode_verifies_commands_and_returns_expected_status()
test_scripted_reply_mode_rejects_unexpected_command_without_side_effect()
test_issue_and_poll_are_safe_under_concurrent_test_use()

print("AXI command mock backend tests ok")
