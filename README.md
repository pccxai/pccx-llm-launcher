# pccx-llm-launcher

Lightweight launcher for PCCX-oriented local LLM workflows.

## Status

This repository is the **user-facing launcher track for PCCX**. It is
intended for users who want a guided local LLM workflow without
understanding the full PCCX / FPGA internals. It is currently a planning
skeleton — there is no working KV260 inference path yet.

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

## Future direction

- Coding-assistant mode.
- VS Code extension bridge.
- Additional models.
- Additional edge devices.
- Integration with `pccx-lab` diagnostics.

## Non-goals

- No current KV260 inference claim — wait for the FPGA repo to publish
  verified bring-up logs before claiming an end-to-end run.
- No benchmark overclaim.
- No kernel development requirement for normal users.
- No production-ready claim.

## Related

- [pccxai/pccx][pccx] — spec / docs / roadmap / release coordination
- [pccxai/pccx-FPGA-NPU-LLM-kv260][pccx-fpga] — RTL / Sail / KV260 / hardware evidence
- [pccxai/pccx-lab][pccx-lab] — verification lab + analysis backend
- [pccxai/pccx-systemverilog-ide][pccx-ide] — SystemVerilog IDE spin-out

## License

Apache License 2.0 — see [LICENSE](./LICENSE).

[pccx]: https://github.com/pccxai/pccx
[pccx-fpga]: https://github.com/pccxai/pccx-FPGA-NPU-LLM-kv260
[pccx-lab]: https://github.com/pccxai/pccx-lab
[pccx-ide]: https://github.com/pccxai/pccx-systemverilog-ide
