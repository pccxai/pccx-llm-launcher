# v002 Consumption Path

This note defines how `pccx-llm-launcher` is allowed to consume the
pccx v002 IP-core. It is an architecture boundary for maintainers, not a
runtime implementation.

Current answer: **the launcher reaches v002 through the KV260 integration
repository. It does not consume `pccx-v002` directly.**

## Dependency Chain

The ownership chain is:

```text
pccx-llm-launcher
  -> pccx-FPGA-NPU-LLM-kv260
       -> third_party/pccx-v002
```

`pccx-FPGA-NPU-LLM-kv260` is the board integration repository. It owns
the KV260 wrapper, Vivado flow, driver surface, runtime evidence, and the
submodule pin for the reusable v002 IP-core.

`pccx-v002` is the reusable IP-core source tree consumed by that KV260
integration repository through `third_party/pccx-v002`.

`pccx-llm-launcher` is the user-facing launcher. It should consume the
KV260 integration boundary, runtime descriptors, evidence summaries, and
future driver/runtime entry points. It should not import RTL, filelists,
Vivado wrappers, or the v002 IP-core submodule itself.

## Launcher Boundary

The launcher may refer to v002 only as target metadata:

- target architecture: `pccx v002`
- target board: `xilinx_kria_kv260`
- target model path: Gemma 3N E4B on KV260
- runtime descriptor: `kv260_pccx_placeholder` until real evidence lands
- evidence source: the KV260 integration repository and pccx-lab handoff

The launcher must not:

- add a direct `pccx-v002` git submodule
- vendor or copy v002 RTL
- parse `third_party/pccx-v002` paths directly
- own the v002 commit pin
- build Vivado projects or filelists
- claim that a v002 bitstream or model path works without KV260
  integration evidence

That separation keeps the launcher stable while the lower hardware
repositories update their RTL, wrappers, drivers, and evidence packs.

## KV260 Integration Boundary

The KV260 integration repository is the authoritative consumer of the
reusable v002 IP-core. It is responsible for:

- pinning `third_party/pccx-v002`
- maintaining the Vivado filelist and wrapper integration
- adapting the reusable IP-core to the KV260 board flow
- publishing driver, bitstream, smoke, timing, and runtime evidence
- exposing any future launcher-facing status or launch boundary

When the launcher needs to answer "what v002 core am I targeting?", it
should resolve that through the KV260 integration release, evidence
manifest, or runtime descriptor. It should not resolve it by opening a
local `pccx-v002` checkout.

## Runtime Readiness

The current launcher state remains blocked and descriptor-only. A future
launcher control can become enabled only after the KV260 integration path
publishes evidence that covers the full route:

```text
model selection
  -> launcher runtime descriptor
  -> KV260 integration runtime/driver boundary
  -> KV260 bitstream and board evidence
  -> v002 IP-core pin through third_party/pccx-v002
```

Evidence must be attached at the KV260 integration layer because that is
where reusable v002 RTL becomes a board-specific system. A direct
`pccx-v002` pin is insufficient for launcher readiness: it does not prove
Vivado integration, driver behavior, board smoke, model execution, or
performance.

## Review Checklist

Maintainers should reject launcher changes that:

- introduce `pccx-v002` as a direct dependency
- add RTL paths under launcher configuration
- use `third_party/pccx-v002` paths as launcher inputs
- bypass the KV260 integration repository for v002 evidence
- turn v002 architecture docs into runtime readiness claims

Maintainers may accept launcher changes that:

- name v002 as target metadata
- link to the KV260 integration repository for hardware evidence
- read checked launcher fixtures or descriptors
- add future adapters to a reviewed KV260 runtime or pccx-lab boundary
- keep runtime, model-load, and hardware controls blocked until evidence
  changes

## Related Documents

- [`MODEL_RUNTIME_DESCRIPTOR_BOUNDARY.md`](./MODEL_RUNTIME_DESCRIPTOR_BOUNDARY.md)
- [`RUNTIME_READINESS_STATUS.md`](./RUNTIME_READINESS_STATUS.md)
- [`KV260_CONNECTION_AND_STATUS_FLOW.md`](./KV260_CONNECTION_AND_STATUS_FLOW.md)
- [`PROVENANCE.md`](./PROVENANCE.md)
