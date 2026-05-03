# Other Editor Bridge Plan

## Status

This is a later-track launcher-side plan for editor integrations beyond the
local VS Code-oriented path. It records how JetBrains and generic editor
bridges should consume launcher data without creating a second launcher runtime
or a single-editor dependency.

This is not a JetBrains plugin, not a generic editor protocol implementation,
not an LSP or MCP server, not a package distribution flow, and not a stable
compatibility promise.

## Goal

The launcher should expose the same conservative status and handoff data to
multiple editor families:

- VS Code and the `systemverilog-ide` prototype
- future JetBrains plugin work
- future generic editor adapters or local scripts

Editor-specific UI code should stay thin. It should translate launcher data
into native editor presentation while leaving model/runtime state, device
status, readiness, diagnostics handoff, and chat/session state in the launcher
contracts.

## Launcher-Owned Data

Future editor bridges should consume these launcher-owned surfaces first:

| Surface | Purpose |
|---|---|
| `pccx.launcherIdeStatus.v0` | top-level launcher/editor status and future operation list |
| `pccx.runtimeReadiness.v0` | evidence-aware runtime readiness summary |
| `pccx.deviceSessionStatus.v0` | device/session rows, flow steps, and error taxonomy |
| `pccx.chatSession.v0` | blocked standalone chat/session state and disabled controls |
| `pccx.diagnosticsHandoff.v0` | read-only diagnostics handoff references for pccx-lab |

The shapes are still pre-compatibility and may change before a versioned
interface is declared.

## Editor Families

### VS Code / SystemVerilog IDE

The VS Code-facing path may consume launcher data through
`systemverilog-ide` adapters. The launcher remains the owner of the data
contracts; the editor presents summaries, disabled actions, and future
handoff state.

### JetBrains

A future JetBrains bridge should map the same launcher data into tool windows,
status bar entries, and explicit user actions. It should not invent a separate
device manager, runtime launcher, diagnostics handoff, or chat/session state
machine.

### Generic Editors

Generic editor adapters should prefer deterministic JSON from explicit local
commands or checked local files. They should preserve launcher exit codes,
surface unavailable or blocked states directly, and avoid silent fallback from
an explicitly requested backend.

## Safety Boundary

Editor bridges must not:

- execute launcher runtime code without a separately reviewed path
- load model weights or include model weight paths
- claim KV260 inference works or measured throughput exists
- probe hardware, open serial ports, scan networks, or attempt authentication
- invoke pccx-lab except through an explicitly reviewed CLI/core boundary
- implement MCP, LSP, package publishing, marketplace distribution, telemetry,
  upload, or write-back flows as part of this plan
- store prompts, transcripts, private paths, secrets, or tokens

Every write-capable action should be a future explicit user-approved flow with
bounded inputs, clear failure states, and tests.

## Acceptance Gates Before Implementation

Before adding editor-specific code, the launcher should have:

- a narrowed contract versioning policy for editor-facing JSON
- checked fixtures for any new fields
- tests that block private data, unsupported hardware/runtime claims, and
  accidental provider or network calls
- documentation for how unavailable, blocked, and evidence-required states map
  into editor UI
- a separate issue and PR for each editor family implementation

## Issue Alignment

This plan addresses
[`pccx-llm-launcher#11`](https://github.com/pccxai/pccx-llm-launcher/issues/11)
by recording JetBrains and generic editor direction while keeping the current
launcher work data-only and pre-compatibility.
