# ISA Mirror Sync Policy

This note documents the launcher-side mirror of the KV260 v002 ISA
vocabulary. The launcher does not own the ISA. It carries only the minimum
data-only mirror needed to describe future readiness, command, and status
surfaces before any board access is enabled.

## Authoritative Source

The source of truth is the sibling KV260 repository:

- Repository: `pccxai/pccx-FPGA-NPU-LLM-kv260`
- Source file:
  `hw/rtl/NPU_Controller/NPU_Control_Unit/ISA_PACKAGE/isa_pkg.sv`

`isa_pkg.sv` owns the architectural opcode table, instruction body widths,
instruction layouts, CVO function codes, routing enums, flag structs, shape
types, and micro-op structs. Launcher code must treat those definitions as
read-only input.

## Launcher Placeholder

The launcher placeholder introduced by PR #70 lives in:

- `contracts/kv260_readiness_scaffold.py`
- `docs/KV260_DATA_ONLY_READINESS_SCAFFOLD.md`

The mirror in `contracts/kv260_readiness_scaffold.py` is intentionally small:

- `NpuOpcode` mirrors the five 4-bit opcode values from `opcode_e`.
- `NpuCmd` records the 64-bit instruction value and exposes the low/high
  32-bit AXI-Lite write words used by the sibling driver boundary.
- `NpuStat` records the 32-bit status word shape for busy/done display.
- `UCA_REG_INSTR_LO`, `UCA_REG_INSTR_HI`, `UCA_REG_STATUS`,
  `UCA_STAT_BUSY`, and `UCA_STAT_DONE` document the current register and bit
  vocabulary used by the readiness scaffold.

This placeholder is descriptor-only. It must not parse, assemble, execute, or
validate real instructions; it must not open MMIO, SSH, serial, XRT, Vivado, or
board runtime paths.

## Sync Rules

When `isa_pkg.sv` changes in the KV260 repository, update the launcher mirror
only after the KV260 change has reviewed evidence and a stable source path.
The launcher change should stay data-only and should include:

1. The KV260 commit or PR reference that changed `isa_pkg.sv`.
2. The specific mirrored fields that changed.
3. The launcher file paths updated.
4. A statement that no runtime execution, board access, model loading, provider
   call, generated artifact, or benchmark claim was added.

If the KV260 change alters instruction layouts, routing enums, CVO functions,
shape types, or micro-op structs, do not broaden the launcher mirror by
default. Add launcher vocabulary only when a visible launcher status or
readiness surface needs it. Otherwise, cite the KV260 source and keep the
launcher boundary narrow.

## Review Checklist

Before merging a launcher mirror update, verify:

- `NpuOpcode` values still match `opcode_e` in `isa_pkg.sv`.
- The instruction width remains represented as a 64-bit value with low/high
  32-bit words.
- Status bits are still display-only and do not imply a live AXI read.
- New launcher docs name `isa_pkg.sv` as authoritative.
- Tests cover value bounds for any changed mirrored constants.
- The PR body says the update is documentation/data-only unless a separate
  reviewed runtime boundary is intentionally included.

If any item cannot be verified from reviewed KV260 evidence, leave the launcher
placeholder unchanged and file a follow-up against the KV260 source first.
