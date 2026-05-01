# `scripts/legacy/` — frozen reference snapshots

The files in this directory carry the suffix `.snapshot` and are stored as
**read-only reference material**, not runnable scripts. They were taken from
the launcher era of the upstream `llm-lite` project, captured at:

```
hkimw/llm-bottleneck-lab @ 129c524
("feat: Add PCCX accelerator and Multi-Model architecture support",
 2026-04-26)
```

That repository has since pivoted to a benchmark / bottleneck-analysis
focus (`llm-bottleneck-lab`). The launcher-era pieces are preserved here as
a starting point for the user-facing launcher track that this repo
(`pccx-llm-launcher`) is meant to grow into.

## Files

| File | Original purpose |
|---|---|
| `install.sh.snapshot` | OS-aware system-package + Python venv + C++ shared library bootstrap from the llm-lite era. |
| `launch.sh.snapshot` | Web GUI launcher that previously started a Flask backend on `127.0.0.1:5000` and then attached a native GUI front-end. |
| `launch_gui.sh.snapshot` | Plain web-GUI launcher (Flask only). |

## Why they are not directly runnable

These scripts were authored against a working tree that contained an
inference engine directory (`x64/gemma3N_E4B/`), a `pynq_env/` virtualenv,
compiled `.so` shared libraries, and a deprecated native ImGui front-end.
None of that is present in this repository, and importing it is **not** the
goal of `pccx-llm-launcher`.

The launcher engine that this repo is meant to drive will instead come from
the PCCX hardware track once the FPGA / KV260 bring-up evidence is
published in `pccxai/pccx-FPGA-NPU-LLM-kv260`. Until then, these snapshots
are reference material only — they show the shape of an install / launch
pipeline that the new launcher can reuse when the engine is ready.

## What was scrubbed compared to the upstream

- Hardcoded developer paths (`/home/hwkim/...`) and personal blog URLs
  were not imported.
- The `llm-lite.desktop` entry was not imported (it embedded absolute
  paths on the original author's machine).
- Build artifacts under `native/build/` were not imported.
- Research and benchmark artifacts under `x64/gemma3N_E4B/` (CSV results,
  HTML profiles, model caches, weight stubs) were not imported.
- The deprecated native ImGui GUI (`native/main.cpp`) was not imported.
- The original `README.md` and `docs/Gemma3N_Reference_Manual.md` were not
  imported because they make claims about a working inference path that
  has not been verified end-to-end on KV260 yet.

If you want to inspect the unmodified upstream sources, follow the commit
SHA above directly in `hkimw/llm-bottleneck-lab`.
