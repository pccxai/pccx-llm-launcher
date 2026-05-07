# AXI Command Channel Semantics

This note documents the launcher-facing `AxiCmdChannel` command boundary
and the lower `AXIL_CMD_IN` write ingress it is meant to model. It is a
documentation-only boundary for future runtime integration and offline
tests. It does not add hardware access, a device driver, model loading,
runtime execution, or a KV260 readiness claim.

The current source references are:

- launcher-side mock contract: `contracts/axi_cmd_channel.py`
- hardware-side ingress: `AXIL_CMD_IN.sv` in the PCCX FPGA KV260 RTL tree

## Scope

`AxiCmdChannel` is a narrow command/status interface:

- `issue(cmd)`: submit exactly one logical command frame
- `poll_stat()`: read the latest channel status frame

The launcher boundary treats a command as a frame, not as a byte stream.
There is no partial command, delimiter byte, retry fragment, or streaming
payload inside this interface. Ordering is FIFO order: a later accepted
command must not overtake an earlier accepted command.

## Hardware Ingress Framing

`AXIL_CMD_IN` accepts AXI4-Lite write traffic and drains accepted words to
the NPU decoder through a small FIFO.

| Address | Frame kind | Payload semantics |
|---|---|---|
| `0x000` (`ADDR_INST`) | instruction | Enqueue `s_wdata` as one instruction word. |
| `0x008` (`ADDR_KICK`) | kick | Enqueue `64'h8000_0000_0000_0000`; the write data is ignored. |
| other | ignored write | No FIFO entry is enqueued; the response still reports OKAY. |

Current RTL semantics:

- The instruction width is `ISA_WIDTH`; current comments and kick value
  describe a 64-bit command word.
- `ADDR_KICK` is an address-selected frame kind. The hardware enqueues
  the exact kick marker value and does not preserve the incoming `s_wdata`.
- `s_wstrb` is accepted by the port list but is not interpreted by the
  current RTL. Launcher code should write full-width command words.
- `s_bresp` is tied to `OKAY` (`2'b00`); invalid addresses do not map to
  an AXI error response in this block.
- `s_bvalid` is implemented as a one-cycle pulse for an accepted W beat.
- FIFO backpressure is visible through `s_awready`; it is deasserted while
  an address is pending or while the command FIFO is full.
- `OUT_valid` means the FIFO is not empty. A word is popped only when
  `OUT_valid && IN_decoder_ready` is true.

The hardware cannot tell whether the kick marker arrived through
`ADDR_KICK` or as raw instruction data with the same value. Encoders should
reserve the exact kick marker value and use `ADDR_KICK` for kicks.

## Launcher Mock Framing

The offline launcher mock uses deterministic register-shaped frames so
tests can exercise command flow without a board, device file, driver, or
runtime transport.

### Command Frame

`NpuCmd` is the logical command payload:

| Field | Meaning |
|---|---|
| `opcode` | command operation id |
| `flags` | command flags |
| `arg0` | first small argument |
| `arg1` | second small argument |
| `arg2` | 32-bit folded argument |

For the mock `MMIO_CMD` snapshot, the command is folded into a 32-bit
test register:

```text
bits  7:0   opcode[7:0]
bits 15:8   flags[7:0]
bits 23:16  arg0[7:0]
bits 31:24  arg1[7:0]

MMIO_CMD = packed ^ arg2[31:0]
```

This 32-bit mock register is not the hardware instruction ABI. It is a
stable, local test representation for launcher-side issue/poll behavior.

### Status Frame

`NpuStat` is the logical status payload returned by `poll_stat()`:

| Bits | Field |
|---|---|
| `0` | `busy` |
| `1` | `error` |
| `7:2` | `last_opcode[5:0]` |
| `13:8` | `status_code[5:0]` |
| `15:14` | reserved, zero |
| `31:16` | `completion_count[15:0]` |

The default mock status after an accepted command is:

- `completion_count`: incremented once per accepted `issue()`
- `last_opcode`: the issued command opcode
- `busy`: false
- `error`: false
- `status_code`: zero

Scripted replies may replace the default status. In scripted mode, the
mock verifies command order. A mismatch raises before updating the
completion counter, last command, status, or register snapshot.

## Launcher State Machine

The launcher-side channel state machine is intentionally small:

```text
constructed
  -> open_ready
  -> issue_validating
  -> issue_committed
  -> open_ready
  -> closed

open_ready -> poll_status -> open_ready
open_ready -> issue_rejected -> open_ready
closed -> operation_rejected
```

| State | Entry condition | Allowed operation | Exit |
|---|---|---|---|
| `constructed` | backend object exists | enter/open | `open_ready` |
| `open_ready` | channel is open | `issue`, `poll_stat`, `close` | issue/poll/close result |
| `issue_validating` | `issue(cmd)` called | type check, closed check, scripted-order check | committed or rejected |
| `issue_committed` | command accepted | update command register, status register, last command, completion count | `open_ready` |
| `issue_rejected` | invalid command or scripted mismatch | no side effects after mismatch | `open_ready` or exception return |
| `closed` | `close()` or context exit | none | operations raise |

`poll_stat()` is observational. It refreshes the modeled status register
from the latest logical status and returns that status; it does not advance
the completion counter or consume a scripted reply.

## Hardware Write State Machine

The `AXIL_CMD_IN` write side has a separate AXI/FIFO state machine:

```text
reset_or_clear
  -> idle_accept_aw
  -> aw_latched_wait_w
  -> enqueue_or_ignore
  -> bvalid_pulse
  -> idle_accept_aw

fifo_nonempty -> decoder_ready_pop -> fifo_next
```

| State | Condition | Behavior |
|---|---|---|
| `reset_or_clear` | `!rst_n || IN_clear` | Clear address latch, pending flag, response flag, and command FIFO. |
| `idle_accept_aw` | no pending address and FIFO not full | Assert `s_awready`; latch `s_awaddr` when `s_awvalid`. |
| `aw_latched_wait_w` | address pending | Assert `s_wready`; wait for `s_wvalid`. |
| `enqueue_or_ignore` | W beat accepted | Enqueue instruction or kick for known addresses; ignore unknown addresses. |
| `bvalid_pulse` | W beat accepted | Pulse `s_bvalid` with `s_bresp == OKAY`. |
| `fifo_nonempty` | FIFO has data | Assert `OUT_valid` and expose `OUT_data`. |
| `decoder_ready_pop` | `OUT_valid && IN_decoder_ready` | Pop one FIFO entry. |

Backpressure is applied before address acceptance. Once an AW beat is
latched, the block waits for the matching W beat before accepting another
address.

## Error And Boundary Semantics

The launcher should keep these boundaries explicit:

- A locally accepted mock command is not evidence that hardware accepted a
  real AXI write.
- A successful `poll_stat()` is not evidence that a model ran or that the
  NPU decoder completed real work.
- The mock `completion_count` means "accepted by the mock backend", not
  "completed by hardware".
- `busy`, `error`, and `status_code` are launcher status vocabulary until
  a real driver/runtime maps them to checked hardware evidence.
- The command channel does not own model assets, prompts, transcripts,
  telemetry, pccx-lab execution, or release readiness.

Future real backends should preserve the same high-level `issue` and
`poll_stat` contract while documenting any stronger transport guarantees,
driver errors, timeout behavior, and status-code mapping.
