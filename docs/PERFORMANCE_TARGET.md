# 20 tok/s target rationale

This note records launcher-side planning data for the Gemma 3N E4B plus
KV260 path. It is a target document only. The launcher does not run the
model, load weights, program a bitstream, touch KV260 hardware, or
publish throughput evidence.

## Target Boundary

The 20 tok/s target is an end-to-end decode-throughput goal for the
future verified runtime path after model load, tokenizer setup, and
warmup are outside the measured window. It is not a current runtime
status, release gate result, benchmark result, or board-smoke result.

The target maps to a 50 ms/token end-to-end decode budget. That budget
is useful now because it gives the launcher, runtime adapter, and future
pccx-lab handoff one shared limit for how much host-side software
overhead can consume before it crowds the accelerator and runtime work.

## Current SW Timing Budget

The current SW timing budget reserves no more than 10 ms/token
of the 50 ms/token target window for host-side orchestration. The
remaining 40 ms/token stays reserved for tokenizer/runtime integration,
accelerator execution, memory movement, and device-side synchronization
that must be verified below the launcher boundary.

| Software segment | Budget | Scope |
|---|---:|---|
| Runtime adapter dispatch | 3 ms/token | Planned call handoff, stream polling, and back-pressure checks. |
| Token stream marshaling | 2 ms/token | Planned conversion between runtime chunks and launcher response events. |
| UI/state update path | 1 ms/token | Planned append/render notification work outside heavy layout or persistence. |
| Diagnostics accounting | 1 ms/token | Planned counters, timestamps, and readiness labels without log upload. |
| Cancellation/status checks | 1 ms/token | Planned cooperative stop and session-state checks. |
| Software guard band | 2 ms/token | Reserved for integration variance before the target is tested. |
| **Total launcher-side software budget** | **10 ms/token** | Target planning limit, not measured evidence. |

This budget is intentionally conservative for the launcher layer. If
future integration shows launcher-side software over this limit, the
runtime path should reduce event frequency, batch response updates, or
move work out of the per-token loop before any performance claim is made.

## Evidence Required

Before the 20 tok/s target can become a performance claim, the project
needs evidence from lower layers:

- timing and implementation closure from the FPGA/KV260 repository
- generated bitstream evidence tied to the tested design
- KV260 board smoke for the target board and runtime environment
- Gemma 3N E4B model asset, tokenizer, and runtime-load evidence
- throughput measurement with the measured window and token-counting
  method recorded
- pccx-lab or equivalent diagnostics handoff that preserves the evidence
  source and measurement conditions

Until those inputs exist, launcher surfaces should render this only as a
target and keep readiness/performance states blocked or target-only.
