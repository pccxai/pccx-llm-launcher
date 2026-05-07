# NpuStat Error Codes

This note documents the launcher-side meaning of `NpuStat` values produced by
the offline AXI command mock backend. The mock backend models `MMIO_CMD` and
`MMIO_STAT` in memory for tests; it does not touch a board, driver, device
file, runtime transport, or model.

Source surface:

- `contracts/axi_cmd_channel.py`
- `AxiCmdMockBackend.issue(cmd)`
- `AxiCmdMockBackend.poll_stat()`
- `NpuStat.register_value()`

## Status Register Layout

`NpuStat.register_value()` packs a deterministic 32-bit `MMIO_STAT` value:

| Bits | Field | Source value | Meaning |
|---|---|---|---|
| 31:16 | `completion_count` | `completion_count & 0xffff` | Number of commands completed by the mock backend, truncated in the register view. |
| 13:8 | `status_code` | `status_code & 0x3f` | Six-bit scenario status code. |
| 7:2 | `last_opcode` | `last_opcode & 0x3f` | Opcode of the last accepted command, truncated in the register view. |
| 1 | `error` | `1` when `error` is true | Scripted failure flag. |
| 0 | `busy` | `1` when `busy` is true | Scripted in-progress flag. |

The Python `NpuStat` object stores non-negative integers for
`completion_count`, `last_opcode`, and `status_code`. The packed MMIO view only
preserves the low bits shown above.

## Error Code Semantics

The mock backend does not define hardware-global error numbers. It defines a
small contract for interpreting `status_code`, `busy`, and `error` together.

| `status_code` | `busy` | `error` | Mock backend semantics | Launcher/display guidance |
|---|---|---|---|---|
| `0` | `false` | `false` | Success/default completion. The unscripted backend returns this after each accepted command. | Treat the command as completed successfully. Show the `last_opcode` and `completion_count` only when useful for diagnostics. |
| `1..63` | `false` | `false` | Scripted non-failing status. The scenario owns the code meaning; the mock only preserves the numeric code. | Treat as completed without failure, but include the code in debug/test output as `scripted_status_code`. Do not present it as a hardware error. |
| `1..63` | `false` | `true` | Scripted failing status. The scenario owns the exact cause. The mock test suite uses this shape to verify error propagation. | Treat as a blocked command result. Surface the numeric code, `last_opcode`, and scenario name or test fixture when available. |
| Any | `true` | `false` | Scripted in-progress status. The default backend does not emit this shape, but a scripted reply can. | Keep result-dependent UI disabled or pending. Poll again according to the owning test harness. |
| Any | `true` | `true` | Scripted in-progress status with an error flag. This is legal fixture data but should be considered internally inconsistent unless the scenario explains it. | Prefer blocked/pending display with a diagnostic note. Tests should document why both bits are set. |
| `>=64` | Any | Any | Object-level code is accepted, but the packed `MMIO_STAT` register exposes only `status_code & 0x3f`. | Avoid values above `63` in new fixtures. When decoding from `MMIO_STAT`, report only the six-bit code. |

Known in-repository scripted examples:

| Code | Shape | Example purpose | Semantics |
|---|---|---|---|
| `0` | `busy=false`, `error=false` | Default command completion and full-mock dummy E2E statuses. | Command accepted and completed without a mock error. |
| `7` | `busy=false`, `error=false` | Scripted reply test coverage. | Non-failing scenario-specific status; no global error meaning. |
| `12` | `busy=false`, `error=true` | Scripted reply test coverage. | Failing scenario-specific status; display as a scripted mock error. |

## Claim Boundary

These codes describe the offline mock backend only. They are not a stable
hardware ABI, driver ABI, pccx-lab result code table, KV260 runtime status
table, model error taxonomy, or release compatibility promise.
