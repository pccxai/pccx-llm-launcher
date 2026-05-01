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
  MCP-style interface).
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
| [`scripts/check.sh`](./scripts/check.sh) | Probe host info, tooling availability, edge-device hints. |
| [`scripts/check-device-stub.sh`](./scripts/check-device-stub.sh) | Narrowly scoped device-tree / FPGA-node probe (KV260 / Kria detection only). |
| [`scripts/install-stub.sh`](./scripts/install-stub.sh) | Preview of the planned install flow; reports which host runtime pieces are present, lists device-side pieces as future deliverables. |
| [`scripts/launch-stub.sh`](./scripts/launch-stub.sh) | Dry-run preview of the intended launch sequence (host check → device bind → model pick → handoff → diagnostics). |

```bash
bash scripts/check.sh
bash scripts/check-device-stub.sh
bash scripts/install-stub.sh
bash scripts/launch-stub.sh
```

All four are exit-0 by design. They will be replaced by real
implementations only after `pccxai/pccx-FPGA-NPU-LLM-kv260` publishes
verified bring-up evidence.

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
