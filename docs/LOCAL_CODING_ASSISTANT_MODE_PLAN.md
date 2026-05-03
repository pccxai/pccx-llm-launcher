# Local Coding-Assistant Mode Plan

## Status

This is a later-track launcher-side plan for a local coding-assistant mode in
PCCX workflows. It records the user flow, context boundaries, and safety gates
needed before the launcher can expose coding help through a local model.

This plan does not implement a chat runtime, execute a model, call providers,
capture prompts, store transcripts, invoke pccx-lab, invoke
systemverilog-ide, access hardware, or write project files.

## Goal

Local coding-assistant mode should provide reviewed, context-aware help for
PCCX projects while keeping users in control of all execution and file
changes.

The launcher-owned role is to coordinate:

- model/runtime readiness state
- device/session state
- chat/session state
- bounded context references from editor or lab surfaces
- user-visible blocked or unavailable states

The launcher should not duplicate pccx-lab analysis logic or
systemverilog-ide editor logic.

## Planned Data Inputs

The mode should be built on existing data-first surfaces:

| Surface | Use |
|---|---|
| `pccx.launcherIdeStatus.v0` | top-level launcher/editor status and disabled future operation |
| `pccx.runtimeReadiness.v0` | whether the target runtime has evidence to move beyond blocked |
| `pccx.deviceSessionStatus.v0` | device/session rows, launch flow state, and error taxonomy |
| `pccx.chatSession.v0` | chat/session controls and message envelope vocabulary |
| `pccx.diagnosticsHandoff.v0` | read-only diagnostics references for pccx-lab |

Future context inputs from editors or lab tools should stay bounded:

- repository-relative paths
- selected ranges or symbol references
- diagnostic summaries
- run/report identifiers
- readiness and status summaries
- short snippets only when a user explicitly approves them

No checked fixture or public contract should include private paths, secrets,
tokens, prompt bodies, transcripts, model weight paths, generated artifacts, or
raw hardware logs.

## User Flow

The planned flow is:

1. Launcher shows local readiness, device/session, and chat/session state.
2. User opens a coding-assistant surface only when the status data allows it.
3. User chooses bounded context from editor or pccx-lab summaries.
4. Assistant output is presented as suggestions, explanations, or proposal
   seeds.
5. Any validation or file change remains a separate explicit user-approved
   action.

Blocked states should remain visible. If runtime, model, device, or evidence
state is unavailable, the assistant surface should explain that status instead
of silently falling back to another backend.

## Safety Boundary

Local coding-assistant mode must not add:

- model execution before a separately reviewed local runtime path exists
- provider or network calls
- prompt, response, or transcript persistence by default
- automatic file edits, commits, pushes, releases, uploads, or write-back
- pccx-lab execution outside an explicitly reviewed CLI/core boundary
- systemverilog-ide execution outside an explicitly reviewed editor contract
- KV260 runtime access, serial access, SSH, board probing, or inference claims
- model weight paths, generated blobs, private paths, secrets, or tokens
- MCP/LSP implementation, package publishing, or marketplace flow

Every future write-capable action should have bounded inputs, explicit user
approval, deterministic failure states, and tests that block private data and
unsupported claims.

## Acceptance Gates Before Implementation

Before adding runtime behavior, the launcher should have:

- a narrowed context-envelope shape for local coding-assistant input
- checked fixtures that prove prompt and transcript bodies are absent
- explicit disabled/blocked state mapping for readiness, device/session, and
  chat/session data
- tests for provider/network/runtime/hardware non-execution in disabled mode
- documentation for how suggestions become reviewed proposals, not direct file
  changes
- a separate implementation issue and PR for any executable local runtime path

## Issue Alignment

This plan addresses
[`pccx-llm-launcher#12`](https://github.com/pccxai/pccx-llm-launcher/issues/12)
by recording the local coding-assistant mode direction while keeping the
current launcher work data-only and evidence-gated.
