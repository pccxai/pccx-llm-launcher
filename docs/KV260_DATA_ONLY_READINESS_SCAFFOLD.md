# KV260 Data-Only Readiness Scaffold

This page documents the launcher-side readiness scaffold added for the
planned KV260 path. It is data-only: it defines typed shapes for future
connection checks, NPU status, Gemma weight preparation metadata, AXI command
status, and result streams without touching a board or reading model assets.

## Scope

- `KV260Connection` records whether `KVFPGA_HOST`, `KVFPGA_USER`, and
  `KVFPGA_PASSWORD` are present. It does not print those values.
- `NPUStatus` is a read-only status snapshot with bitstream, AXI, and error
  fields.
- `GemmaWeightPrep` names the future `load_hf -> quantize_W4 -> quantize_A8
  -> emit_manifest` flow. Each step raises `NotImplementedError`.
- `GemmaWeightManifest` documents the future manifest shape without creating
  artifacts or reading weight files.
- `AxiCmdChannel` exposes `issue(cmd)` and `poll_stat()` as type-only methods.
  The current mirror records the sibling driver's 64-bit instruction split
  into low/high 32-bit words and the 32-bit status register shape.
- `ResultStream` is a typed iterator over future token or tensor outputs.

The opcode and AXI command/status vocabulary is a narrow mirror of the sibling
KV260 `isa_pkg.sv` source. See
[`ISA_MIRROR_SYNC_POLICY.md`](./ISA_MIRROR_SYNC_POLICY.md) for the source path,
placeholder location, and sync rules.

## Boundaries

The scaffold does not open SSH, run target commands, scan networks, read XRT
state, call `xmutil`, access MMIO, load a bitstream, download from Hugging
Face, load or copy model weights, start inference, stream responses, or write
artifacts.

Readiness can move beyond these placeholders only after lower-layer evidence
is supplied by reviewed FPGA/runtime work. Until then, this launcher surface
must keep runtime and hardware claims blocked or target-only.
