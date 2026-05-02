# pccx-llm-launcher

Lightweight launcher for PCCX-oriented local LLM workflows.

## What this repo is

The user-facing launcher track for PCCX. It is intended to grow into a
guided local LLM workflow that runs on supported edge devices (target:
Xilinx Kria KV260) without requiring users to assemble a kernel /
RTL stack themselves.

This repo is **not** the inference engine, **not** the RTL, and **not**
the verification lab. Those live in their own PCCX repositories (see
*Related* below). This repo is where the install / connect / launch flow
will be wired up once the hardware side ships verified bring-up.

## Status

Currently a planning skeleton bootstrapped from a curated snapshot of the
upstream `llm-lite` launcher era. There is no working KV260 inference
path yet, and no model is actually executed by anything in this
repository today. See [docs/PROVENANCE.md](./docs/PROVENANCE.md) for the
exact source commit and what was / was not imported.

## Intended workflow (target)

1. Install supporting packages on the host or KV260-class device.
2. Run a connection / status check against the target device.
3. Pick a target model (initially Gemma 3N E4B) and a precision mode.
4. Hand control to the launcher to start the local inference flow and
   surface logs / diagnostics.

Steps 3–4 will only become real once the PCCX FPGA / KV260 bring-up
publishes a verified end-to-end path.

## Target user

- Owns or uses a supported edge device such as Xilinx Kria KV260.
- Wants a guided launcher workflow rather than a hand-built kernel stack.
- Does not want to work directly on kernel / RTL internals.
- Wants a path toward local model execution and, later, coding-assistant
  workflows.

## v002 target

- KV260-oriented setup path.
- Gemma 3N E4B as a *target model*, not a current working claim.
- Button-driven launch flow.
- Connection / status checks.
- Guided logs and diagnostics.

## Roadmap

- Coding-assistant mode (AI-assisted local workflow with a controlled
  tool boundary).
- VS Code extension bridge for guided launches and log inspection.
- Additional target models beyond Gemma 3N E4B.
- Additional edge devices beyond KV260.
- Integration with `pccx-lab` diagnostics so device / kernel state can be
  surfaced through the launcher UI.

Release readiness depends on verification evidence published by
`pccxai/pccx-FPGA-NPU-LLM-kv260` (RTL bring-up, simulation, timing
closure). This repository will not cut a non-alpha release until that
evidence lands.

## Non-goals

- No current KV260 inference claim — wait for the FPGA repo to publish
  verified bring-up logs before claiming an end-to-end run.
- No benchmark overclaim.
- No kernel development requirement for normal users.
- This repo is not labelled as stable or as ready for unattended use.

## Usage

The current scripts are all **probe / preview** helpers — none of them
runs inference, contacts a remote device, or installs anything. They
exist so contributors can see the planned shape of the launcher flow
and verify host-side prerequisites before the real engine lands.

| Script | What it does |
|---|---|
| [`scripts/check.sh`](./scripts/check.sh) | Probe host info, tooling availability, edge-device hints. Always exits 0. |
| [`scripts/check-device-stub.sh`](./scripts/check-device-stub.sh) | Narrowly scoped device-tree / FPGA-node probe (KV260 / Kria detection only). Always exits 0. |
| [`scripts/install-stub.sh`](./scripts/install-stub.sh) | Preview of the planned install flow; reports which host runtime pieces are present, lists device-side pieces as future deliverables. Always exits 0. |
| [`scripts/status-stub.sh`](./scripts/status-stub.sh) | Launcher state summary. Default mode: local scaffold output, always exits 0. With `--backend pccx-lab`, calls `pccx-lab status --format json` and forwards the run-status envelope (exits non-zero if binary is missing or output is invalid). |
| [`scripts/launch-stub.sh`](./scripts/launch-stub.sh) | Dry-run preview of the intended launch sequence. Requires `--dry-run`; exits 1 without it. |
| [`scripts/chat-stub.sh`](./scripts/chat-stub.sh) | Dry-run chat stub. Requires `--dry-run`; exits 1 without it. Accepts `--prompt "..."` or stdin. No model is executed. |

```bash
bash scripts/check.sh
bash scripts/check-device-stub.sh
bash scripts/install-stub.sh
bash scripts/status-stub.sh
bash scripts/launch-stub.sh --dry-run
bash scripts/chat-stub.sh --dry-run --prompt "hello"
```

The `--dry-run` scripts exit 1 without the flag as a deliberate guard —
there is no real inference engine to hand off to. They will be replaced
by real implementations only after `pccxai/pccx-FPGA-NPU-LLM-kv260`
publishes verified bring-up evidence.

### pccx-lab status backend (opt-in)

`scripts/status-stub.sh` can call the `pccx-lab status --format json`
controlled CLI/core boundary and forward the run-status envelope:

```bash
# Requires pccx-lab binary on PATH or PCCX_LAB_BIN set.
bash scripts/status-stub.sh --backend pccx-lab

# Point to a specific build:
PCCX_LAB_BIN=/path/to/pccx-lab bash scripts/status-stub.sh --backend pccx-lab
```

Binary resolution order:

1. `PCCX_LAB_BIN` environment variable (if non-empty and executable).
2. `pccx-lab` on `PATH`.

**No silent fallback.** If `--backend pccx-lab` is explicitly requested
but the binary is not found or returns an error, the script exits
non-zero with a clear message. It does not fall back to local scaffold
output.

The pccx-lab status output is an early, pre-compatibility run-status envelope.
It operates in host-dry-run mode: no real KV260 device probing is
performed, no model is executed, and no inference is started. This is a
planned KV260-oriented launcher path, not a readiness claim.

### Launcher / IDE bridge contract (planned)

The launcher now has a small data-only status contract for future editor
consumers:

```bash
python3 contracts/launcher_ide_status_contract.py
python3 scripts/tests/launcher_ide_contract_test.py
```

The contract reports conservative placeholder state: configured target,
availability, runtime/model/evidence status, supported future operations,
safety flags, and a planned read-only pccx-lab diagnostics handoff.

It does not execute the launcher, call a provider, contact hardware,
load a model, implement an editor bridge, or make a compatibility
promise. See
[docs/LAUNCHER_IDE_BRIDGE_CONTRACT.md](./docs/LAUNCHER_IDE_BRIDGE_CONTRACT.md).

### Model / runtime descriptor boundary (planned)

The launcher also has a small data-only model/runtime descriptor boundary:

```bash
python3 contracts/model_runtime_descriptor_contract.py
python3 scripts/tests/model_runtime_descriptor_test.py
```

The checked fixture covers Gemma 3N E4B as a descriptor target and a
KV260 PCCX runtime placeholder. Model assets are external/user-provided
and not bundled. The runtime path is planned, unavailable, and not
configured, so compatibility remains provisional until evidence exists.

This boundary does not load weights, execute a runtime, call a provider,
touch KV260 hardware, report performance, implement MCP/LSP, or make an
API/ABI compatibility commitment. See
[docs/MODEL_RUNTIME_DESCRIPTOR_BOUNDARY.md](./docs/MODEL_RUNTIME_DESCRIPTOR_BOUNDARY.md).

### Diagnostics handoff boundary (planned)

The launcher has a read-only diagnostics handoff contract for future
pccx-lab consumers:

```bash
python3 contracts/diagnostics_handoff_contract.py
python3 scripts/tests/diagnostics_handoff_contract_test.py
```

The checked fixture references the launcher/IDE status contract and the
model/runtime descriptor fixture by id. It summarizes blocked or
not-configured placeholder state without raw logs, private paths, user
prompts, source code, secrets, tokens, provider configuration, model
weight paths, telemetry, automatic upload, or write-back.

This boundary does not execute pccx-lab, invoke launcher runtime code,
touch KV260 hardware, call providers, implement MCP/LSP, or add a
marketplace flow. See
[docs/DIAGNOSTICS_HANDOFF_CONTRACT.md](./docs/DIAGNOSTICS_HANDOFF_CONTRACT.md).

The legacy launcher scripts from the `llm-lite` era are preserved
read-only under [`scripts/legacy/`](./scripts/legacy/) as historical
reference (see that directory's README for status).

## Source provenance

The launcher-shaped pieces in this repository were taken from
`hkimw/llm-bottleneck-lab @ 129c524` (2026-04-26). Full details and the
explicit list of what was and was not imported are in
[docs/PROVENANCE.md](./docs/PROVENANCE.md).

## Related

- [pccxai/pccx][pccx] — spec / docs / roadmap / release coordination
- [pccxai/pccx-FPGA-NPU-LLM-kv260][pccx-fpga] — RTL / Sail / KV260 / hardware evidence
- [pccxai/pccx-lab][pccx-lab] — verification lab + analysis backend
- [pccxai/systemverilog-ide][pccx-ide] — SystemVerilog IDE spin-out

## License

Apache License 2.0 — see [LICENSE](./LICENSE).

[pccx]: https://github.com/pccxai/pccx
[pccx-fpga]: https://github.com/pccxai/pccx-FPGA-NPU-LLM-kv260
[pccx-lab]: https://github.com/pccxai/pccx-lab
[pccx-ide]: https://github.com/pccxai/systemverilog-ide
