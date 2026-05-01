# Source Provenance

## Origin

`pccx-llm-launcher` was bootstrapped in part from the launcher-era of the
upstream project `hkimw/llm-bottleneck-lab` (formerly `llm-lite`). The
chosen import point is:

| Field | Value |
|---|---|
| Repository | `hkimw/llm-bottleneck-lab` |
| Commit SHA | `129c524e84668214e500c6b58f59874f2c227982` |
| Short SHA | `129c524` |
| Date | 2026-04-26 |
| Subject | `feat: Add PCCX accelerator and Multi-Model architecture support` |

The reasons that commit was selected as the import point:

1. It is the **last launcher-shaped snapshot** in that repository's history
   before it was refactored into a benchmark / bottleneck-analysis lab.
2. It is the snapshot in which a PCCX-aware accelerator track first
   appeared, which matches the goal of this repo (a user-facing launcher
   for PCCX-targeted local LLM workflows).
3. The launcher script surface area (`install.sh`, `launch.sh`,
   `launch_gui.sh`) is largely settled by this point and is the most
   reusable scaffolding for future user-facing flows.

## What was imported

| Imported as | Source path at `129c524` | Notes |
|---|---|---|
| `scripts/legacy/install.sh.snapshot` | `install.sh` | Stored read-only as `.snapshot`; not directly runnable. |
| `scripts/legacy/launch.sh.snapshot` | `launch.sh` | Stored read-only. |
| `scripts/legacy/launch_gui.sh.snapshot` | `launch_gui.sh` | Stored read-only. |
| `assets/icon.svg` | `icon.svg` | Neutral asset; reused as launcher icon. |
| `.gitignore` | `.gitignore` | Ignore patterns adopted with light pruning. |

## What was deliberately NOT imported

- `README.md` and the `docs/Gemma3N_Reference_Manual.md` /
  `docs/Speculative_Decoding_Research.md` documents — they made claims
  about a working inference pipeline that has not been verified end-to-end
  on KV260, and they referenced research workstreams that belong with
  `llm-bottleneck-lab` rather than with a launcher.
- `x64/gemma3N_E4B/` in its entirety (Python inference engine, weight
  caches, smoke tests, profiling artifacts, CSV results) — this is the
  research surface, not the launcher surface.
- `native/` in its entirety — the in-tree `DEPRECATED.md` already states
  that the Dear ImGui native GUI is no longer the supported front-end.
- `native/build/` — CMake / FetchContent build artifacts.
- `run.sh` — referenced an absolute personal path on the original
  author's machine.
- `llm-lite.desktop` — referenced absolute personal paths and was tied to
  the `llm-lite` branding.
- `.github/workflows/ci.yml` from upstream — its build steps depended on
  `x64/gemma3N_E4B/build.sh` and `smoke_test.py`, which are not part of
  this repo.

## Status of the imported scripts

The scripts under `scripts/legacy/` are **frozen reference snapshots**.
They are useful as a shape for future install / launch flows once a real
launcher engine is wired up, but they are not expected to run as-is in
this repository today. Treat them as documentation of past intent.

## Authoritative inference path

Hardware-side inference readiness for `pccx-llm-launcher` depends on the
bring-up and verification work that is happening in
`pccxai/pccx-FPGA-NPU-LLM-kv260`. No release of this repository should
claim KV260 inference until that repository publishes a verified
end-to-end path (RTL bring-up, simulation evidence, timing closure).

---

*See also*:
[AI-assisted engineering discipline](https://github.com/pccxai/pccxai/blob/main/docs/AI_ASSISTED_ENGINEERING.md) —
org-level evidence-first release rules that apply to launcher and device bridge work.
