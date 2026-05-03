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
  tool boundary). The later-track plan is tracked in
  [docs/LOCAL_CODING_ASSISTANT_MODE_PLAN.md](./docs/LOCAL_CODING_ASSISTANT_MODE_PLAN.md).
- VS Code and other editor bridge planning for guided launches and log
  inspection.
- Additional target models beyond Gemma 3N E4B and additional edge devices
  beyond KV260. The later-track plan is tracked in
  [docs/MULTI_MODEL_DEVICE_SUPPORT_PLAN.md](./docs/MULTI_MODEL_DEVICE_SUPPORT_PLAN.md).
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
| [`scripts/status-stub.sh`](./scripts/status-stub.sh) | Launcher state summary. Default mode: local scaffold output, always exits 0. With `--include-chat-model-status`, adds read-only blocked chat model-status display data. With `--include-chat-session`, adds read-only blocked chat/session and lifecycle summaries. With `--include-device-session`, adds a read-only device/session status panel. With `--include-runtime-readiness`, adds a read-only runtime readiness summary. With `--backend pccx-lab`, calls `pccx-lab status --format json` and forwards the run-status envelope (exits non-zero if binary is missing or output is invalid). |
| [`scripts/device-session-status-stub.sh`](./scripts/device-session-status-stub.sh) | Data-only device/session status JSON for the Gemma 3N E4B + KV260 target. Reports connection, model load, session, diagnostics, readiness, discovery paths, flow steps, and error taxonomy as placeholder / blocked. |
| [`scripts/runtime-readiness-stub.sh`](./scripts/runtime-readiness-stub.sh) | Data-only runtime readiness JSON for the Gemma 3N E4B + KV260 target. Reports blocked / not yet evidence-backed. |
| [`scripts/chat-session-stub.sh`](./scripts/chat-session-stub.sh) | Data-only standalone chat/session JSON for the Gemma 3N E4B + KV260 target. Reports disabled send controls, inactive session state, no prompt/response persistence, and readiness handoff references. |
| [`scripts/chat-session-lifecycle-stub.sh`](./scripts/chat-session-lifecycle-stub.sh) | Data-only chat session lifecycle JSON for the Gemma 3N E4B + KV260 target. Reports create, restore, clear, close, and export-summary operations as disabled, blocked, inactive, or unavailable. |
| [`scripts/chat-model-status-stub.sh`](./scripts/chat-model-status-stub.sh) | Data-only chat model-status JSON for the Gemma 3N E4B + KV260 target. Reports descriptor, asset, load, runtime, context, and response display rows as blocked, disabled, or unavailable. |
| [`scripts/chat-surface-preview.sh`](./scripts/chat-surface-preview.sh) | Read-only terminal preview of the standalone chat surface. Renders the checked chat/session contract as blocked UI state without accepting prompts, executing a model, or writing artifacts. |
| [`scripts/launch-stub.sh`](./scripts/launch-stub.sh) | Dry-run preview of the intended launch sequence. Requires `--dry-run`; exits 1 without it. |
| [`scripts/chat-stub.sh`](./scripts/chat-stub.sh) | Dry-run chat stub. Requires `--dry-run`; exits 1 without it. Accepts `--prompt "..."` or stdin. No model is executed. |

```bash
bash scripts/check.sh
bash scripts/check-device-stub.sh
bash scripts/install-stub.sh
bash scripts/status-stub.sh
bash scripts/status-stub.sh --include-chat-model-status
bash scripts/status-stub.sh --include-chat-session
bash scripts/status-stub.sh --include-device-session
bash scripts/status-stub.sh --include-runtime-readiness
bash scripts/device-session-status-stub.sh --model gemma3n-e4b --target kv260
bash scripts/runtime-readiness-stub.sh --model gemma3n-e4b --target kv260
bash scripts/chat-model-status-stub.sh --model gemma3n-e4b --target kv260
bash scripts/chat-session-stub.sh --model gemma3n-e4b --target kv260
bash scripts/chat-session-lifecycle-stub.sh --model gemma3n-e4b --target kv260
bash scripts/chat-surface-preview.sh --model gemma3n-e4b --target kv260
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
The later-track JetBrains and generic editor direction is tracked in
[docs/OTHER_EDITOR_BRIDGE_PLAN.md](./docs/OTHER_EDITOR_BRIDGE_PLAN.md).
The later-track local coding-assistant mode direction is tracked in
[docs/LOCAL_CODING_ASSISTANT_MODE_PLAN.md](./docs/LOCAL_CODING_ASSISTANT_MODE_PLAN.md).

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
The later-track multi-model and multi-device direction is tracked in
[docs/MULTI_MODEL_DEVICE_SUPPORT_PLAN.md](./docs/MULTI_MODEL_DEVICE_SUPPORT_PLAN.md).

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

pccx-lab has a separate read-only validator for this JSON shape. The
launcher does not invoke that command or depend on it at runtime.

### Runtime readiness status (planned)

The launcher now has a data-only, evidence-aware runtime readiness
surface for the Gemma 3N E4B + KV260 target:

```bash
python3 contracts/runtime_readiness_contract.py --model gemma3n-e4b --target kv260
bash scripts/runtime-readiness-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-runtime-readiness
python3 scripts/tests/runtime_readiness_contract_test.py
```

The checked fixture reports the current answer as blocked / not yet
evidence-backed. It includes a deterministic fixture version,
last-updated source boundary, top-level readiness/evidence states,
descriptor evidence, xsim evidence of 11 passed and 0 failed, and Vivado
synthesis evidence while keeping timing, implementation, bitstream,
KV260 smoke, runtime evidence, and throughput measurement in blocked or
target-only states. 20 tok/s remains a target until measured.

The status command reads the same local readiness stub and prints a
short human summary. It is still read-only status data.

This surface does not load weights, execute a runtime, touch KV260
hardware, call providers, invoke pccx-lab, invoke systemverilog-ide,
upload telemetry, or write artifacts. See
[docs/RUNTIME_READINESS_STATUS.md](./docs/RUNTIME_READINESS_STATUS.md).

### Device/session status panel and KV260 flow (planned)

The launcher now has a data-only status panel and connection-flow
contract for the planned Gemma 3N E4B + KV260 path:

```bash
python3 contracts/device_session_status_contract.py --model gemma3n-e4b --target kv260
bash scripts/device-session-status-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-device-session
python3 scripts/tests/device_session_status_contract_test.py
bash scripts/tests/status-device-session.sh
```

The checked fixture reports device connection as not configured, model
load as not loaded, session activity as inactive, pccx-lab diagnostics
as a read-only placeholder, and runtime readiness as blocked. It also
documents planned discovery paths, a gated connection and launch flow,
and an error taxonomy with user remediation text.

This surface does not probe hardware, open serial ports, scan networks,
attempt authentication, load model assets, invoke pccx-lab, start a
runtime, stream logs, upload telemetry, or write artifacts. See
[docs/KV260_CONNECTION_AND_STATUS_FLOW.md](./docs/KV260_CONNECTION_AND_STATUS_FLOW.md).

### Standalone chat/session contract (planned)

The launcher now has a data-only standalone chat/session contract for
the planned local chat entry point:

```bash
python3 contracts/chat_session_contract.py --model gemma3n-e4b --target kv260
python3 contracts/chat_model_status_contract.py --model gemma3n-e4b --target kv260
bash scripts/chat-model-status-stub.sh --model gemma3n-e4b --target kv260
bash scripts/chat-session-stub.sh --model gemma3n-e4b --target kv260
bash scripts/chat-session-lifecycle-stub.sh --model gemma3n-e4b --target kv260
bash scripts/chat-surface-preview.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-model-status
bash scripts/status-stub.sh --include-chat-session
python3 scripts/tests/chat_session_contract_test.py
python3 scripts/tests/chat_model_status_contract_test.py
python3 scripts/tests/chat_session_lifecycle_contract_test.py
python3 scripts/tests/chat_surface_preview_test.py
bash scripts/tests/status-chat-model-status.sh
bash scripts/tests/status-chat-session.sh
```

The checked chat/session fixture reports the chat surface as blocked,
the session as inactive, and send controls as disabled. The checked chat
model-status fixture adds descriptor, asset, load, runtime, context, and
response display rows for the planned model-status panel. Model loading
stays disabled and blocked. These fixtures define display and message
envelope shapes without storing prompts, responses, transcripts, model
paths, generated artifacts, private paths, secrets, or tokens. They
reference the model/runtime descriptor, runtime readiness,
device/session status, and chat/session fixtures as local data only.

The lifecycle fixture defines the session-management boundary for create,
restore, clear, close, and export-summary operations. All operations stay
disabled, blocked, inactive, or unavailable until readiness evidence, model
load evidence, a reviewed local session store, and explicit export/redaction
rules exist. It does not read or write manifests, transcripts, summaries,
prompts, responses, or model paths.

The preview command renders that same contract as a deterministic
terminal chat surface sketch with disabled controls, blocked reasons, and
an unavailable assistant response. It does not accept or echo prompts.

This surface does not execute a model, generate responses, persist
transcripts, touch KV260 hardware, open serial ports, scan networks, call
providers, invoke pccx-lab, invoke systemverilog-ide, upload telemetry,
read artifacts, or write artifacts. See
[docs/STANDALONE_CHAT_SESSION_CONTRACT.md](./docs/STANDALONE_CHAT_SESSION_CONTRACT.md).

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
