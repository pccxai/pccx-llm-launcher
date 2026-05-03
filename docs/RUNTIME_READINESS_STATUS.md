# Runtime Readiness Status

This note defines the launcher-side runtime readiness surface for the
planned KV260-oriented launcher path. It is data-only and evidence-aware.
It answers whether the Gemma 3N E4B plus KV260 target is ready to run,
blocked, or backed by checked evidence.

Current answer: **blocked / not yet evidence-backed**.

The implementation lives in:

- `contracts/runtime_readiness_contract.py`
- `contracts/fixtures/runtime-readiness.gemma3n-e4b-kv260.json`
- `scripts/runtime-readiness-stub.sh`
- `scripts/tests/runtime_readiness_contract_test.py`

## What Is Implemented

The readiness contract records:

- fixture version and last-updated source boundary
- target model and target board identity
- top-level readiness and evidence states
- descriptor, input, bitstream, synthesis, timing, implementation, board
  smoke, runtime, throughput, and compatibility states
- a small state vocabulary: `target`, `blocked`, `ready_for_inputs`,
  `evidence_present`, and `measured`
- blockers and next inputs required
- safety flags for the read-only boundary
- evidence references that separate checked non-runtime evidence from
  missing runtime and measurement evidence

The checked fixture is deterministic JSON. The stub command prints that
JSON for the supported model and target pair:

```bash
bash scripts/runtime-readiness-stub.sh --model gemma3n-e4b --target kv260
```

The stub does not probe hardware, load weights, run inference, call a
provider, invoke pccx-lab, invoke systemverilog-ide, upload telemetry,
or write artifacts.

## Current Evidence

The fixture reflects the current PCCX ecosystem state as launcher data:

- the launcher has a checked model/runtime descriptor fixture for Gemma
  3N E4B and the KV260 placeholder runtime
- pccx-FPGA-NPU-LLM-kv260 v002 repo-local xsim evidence reports 11
  passed and 0 failed
- Vivado synthesis evidence exists, but that is not hardware closure
- post-synthesis DRC and timing issues remain closure blockers
- implementation is incomplete
- a generated bitstream is not proven by this launcher surface
- KV260 board smoke is blocked by missing board, model, bitstream, and
  runtime environment
- Gemma 3N E4B has no KV260 hardware runtime evidence in this launcher
  fixture
- throughput measurement is unavailable
- 20 tok/s remains a target until measured

## State Separation

The readiness states are deliberately narrow:

- `target`: named planned target only
- `blocked`: a required input, artifact, closure step, or evidence item
  is missing
- `ready_for_inputs`: the launcher can describe a needed input without
  bundling or reading it
- `evidence_present`: checked non-runtime evidence exists
- `measured`: runtime or hardware measurement exists

The current Gemma 3N E4B plus KV260 fixture uses `target`,
`blocked`, `ready_for_inputs`, and `evidence_present`. It does not use
`measured` for the current target because runtime and throughput
measurement evidence are absent.

## Coordination Boundary

pccx-lab remains CLI-first and core-boundary-first, with GUI work
second. It is the diagnostics and verification backend for future
evidence handling. This launcher repository only provides a read-only
diagnostics handoff contract and this readiness data surface; the
readiness stub does not invoke pccx-lab.

systemverilog-ide may consume launcher or lab data later as read-only
context. The IDE side has diagnostics handoff consumer, context bundle,
validation proposal, and preflight audit work, but this launcher change
does not add an IDE invocation path or control surface.

## Non-Goals

This readiness surface does not add:

- KV260 runtime execution
- model loading or model weight paths
- provider or network calls
- pccx-lab invocation
- systemverilog-ide invocation
- MCP implementation
- LSP implementation
- marketplace flow
- telemetry, upload, or write-back
- release or tag behavior
- versioned API or ABI commitment
- a performance achievement claim

Evidence from FPGA closure, KV260 board smoke, runtime execution, and
throughput measurement is required before this status can move beyond
blocked for the Gemma 3N E4B plus KV260 target.
