# Launcher Overview And Offline Walkthrough

This document summarizes the launcher-side contracts introduced across
the current KV260 launcher slices and shows an offline walkthrough for
developers. It is documentation only.

The walkthrough uses the dummy end-to-end CLI from PR #75. It does not
require a KV260 board, does not open a serial port, does not read Hugging
Face assets, and does not start a Gemma runtime.

## Source PRs

| PR | Slice | Launcher surface |
|---|---|---|
| [#70](https://github.com/pccxai/pccx-llm-launcher/pull/70) | Data-only readiness scaffold | Typed launcher interfaces for KV260 connection data, NPU status, Gemma weight prep, AXI command/status, and result streaming. |
| [#71](https://github.com/pccxai/pccx-llm-launcher/pull/71) | pccx-UI integration | Read-only launcher preview styling and branding for blocked states. |
| [#72](https://github.com/pccxai/pccx-llm-launcher/pull/72) | TTY serial backend | USB tty serial implementation of the KV260 connection method contract. |
| [#73](https://github.com/pccxai/pccx-llm-launcher/pull/73) | Gemma weight prep stage 1 | Deterministic dummy Gemma weight-prep manifest and invariants. |
| [#74](https://github.com/pccxai/pccx-llm-launcher/pull/74) | AXI command mock backend | Offline `AxiCmdMockBackend` for command/status tests without MMIO. |
| [#75](https://github.com/pccxai/pccx-llm-launcher/pull/75) | Dummy e2e run | `pccx-launcher dummy-e2e --seed N` over dummy manifest, AXI mock, and fake result stream. |

## Typed Interfaces

### `KV260Connection`

`KV260Connection` is the launcher-side target connection shape from
PR #70. It records whether expected connection inputs are configured
without exposing raw values in public representations.

The scaffold methods cover the future readiness questions:

- `is_reachable()`
- `kernel_uname()`
- `xrt_present()`
- `xmutil_listapps()`

PR #70 keeps those methods as data-only placeholders. PR #72 adds a
TTY serial backend for the same method contract.

### `NPUStatus`

`NPUStatus` is the read-only status snapshot shape from PR #70. It is
intended for launcher status panels that need to display bitstream,
AXI register, and last-error fields while still treating all values as
reported status data.

This interface does not load a bitstream, inspect hardware, or assert
that a board-side runtime is available.

### `GemmaWeightPrep`

`GemmaWeightPrep` describes the weight-preparation boundary. PR #70
defines the planned load, quantize, and manifest handoff shape. PR #73
adds the stage-1 implementation:

```python
GemmaWeightPrep().prepare_dummy(seed=42)
```

The stage-1 path emits a deterministic dummy manifest with `_dummy`
labels, dummy BF16-shaped inputs, placeholder W4 packing, positive scale
metadata, and explicit evidence/limitation fields. It does not download
or load model weights.

### `AxiCmdChannel`

`AxiCmdChannel` is the minimal launcher command-channel protocol:

- `issue(cmd: NpuCmd) -> None`
- `poll_stat() -> NpuStat`

PR #74 adds `AxiCmdMockBackend`, a thread-safe in-memory backend that
models `MMIO_CMD` and `MMIO_STAT` for offline tests. It supports default
completion statuses and scripted command/status pairs.

The mock backend is not an MMIO transport and does not talk to a driver,
device file, or KV260 board.

### `ResultStream`

`ResultStream` is the typed output boundary. PR #70 defines the iterator
shape for future output items. PR #75 adds a dummy e2e result stream with
deterministic fake token chunks.

The dummy stream is useful for exercising launcher plumbing and CLI
formatting. It is not Gemma inference output.

## TTY Serial Backend

PR #72 adds a USB tty serial backend for the KV260 connection method
contract. It reads:

- `KVFPGA_TTY`
- `KVFPGA_USER`
- `KVFPGA_PASSWORD`

`KVFPGA_HOST` is intentionally ignored by the serial backend. TTY
detection checks an explicit `KVFPGA_TTY` first, then local
`/dev/serial/by-id/*kv260*` and `/dev/ttyUSB*` candidates.

The backend can answer connection-readiness methods through a serial
console when explicitly configured. The dummy walkthrough below does not
use this backend and does not need serial credentials.

## Stage 1 And Stage 2

The launcher work is split into two stages:

| Stage | Purpose | Included in these slices |
|---|---|---|
| Stage 1 | Contract shape, deterministic dummy data, offline command/status wiring, and CLI smoke coverage. | `prepare_dummy(seed)`, `AxiCmdMockBackend`, and `dummy-e2e`. |
| Stage 2 | Real model asset handling, reviewed quantization, board/runtime handoff, and evidence-backed launch behavior. | Not included in PRs #70-#75. |

Stage 1 is allowed to prove that the launcher can move typed data through
the planned boundaries. Stage 2 is the only place where real Gemma weight
handling or a runtime handoff can be added.

## Offline Walkthrough

Use the PR #75 branch or any later branch that contains
`scripts/pccx-launcher`. No board is required.

```bash
git fetch origin pull/75/head:pr-75-dummy-e2e
git switch pr-75-dummy-e2e
PATH="$PWD/scripts:$PATH" pccx-launcher dummy-e2e --seed 42
```

Expected shape:

```text
dummy_e2e: ok
seed: 42
manifest: gemma_weight_prep_seed_42_dummy
commands: 3
stream: dummy_e2e_seed_42
tokens: 6
text: axi_3 gemma_e offline_f tile_1 dummy_f stream_4
offline: board=false ssh=false hf=false network=false
```

The same command can be run without changing `PATH`:

```bash
python3 scripts/pccx-launcher dummy-e2e --seed 42
```

The output is deterministic for the same seed. It exercises only the
stage-1 dummy manifest, offline AXI mock backend, and fake result stream.

## Claim Guard

This overview intentionally makes no board claim and no Gemma runtime
claim. The documented offline walkthrough is limited to:

- deterministic dummy weight-prep manifest data
- in-memory AXI command/status modeling
- fake token stream formatting
- no serial, SSH, HF, network, MMIO, bitstream, provider, or runtime
  side effects
