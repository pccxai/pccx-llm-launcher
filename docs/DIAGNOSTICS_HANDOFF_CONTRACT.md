# Diagnostics Handoff Contract

This note defines the first launcher-side diagnostics handoff boundary
for future pccx-lab consumers. It is a data-only contract and a checked
fixture. It does not execute pccx-lab, start launcher runtime code, probe
hardware, load a model, call a provider, or publish user data.

The implementation lives in:

- `contracts/diagnostics_handoff_contract.py`
- `contracts/fixtures/diagnostics-handoff.gemma3n-e4b-kv260-placeholder.json`
- `scripts/tests/diagnostics_handoff_contract_test.py`

## What Is Implemented

The contract currently provides:

- a deterministic diagnostics handoff shape
- a compact diagnostic item shape
- a checked Gemma 3N E4B plus KV260 placeholder handoff fixture
- references to the launcher/IDE status contract and model/runtime
  descriptor fixture
- read-only, no-upload, no-telemetry, and no-write-back flags
- transport sketches for future JSON file, stdout JSON, and read-only
  local artifact reference use

This is enough for review and future pccx-lab alignment without binding
either side to runtime execution.

## Handoff Shape

The handoff records:

- `schemaVersion`
- `handoffId`
- `handoffKind`
- `producer`
- `consumer`
- `createdAt`
- `sessionId`
- `launcherStatusRef`
- `modelDescriptorRef`
- `runtimeDescriptorRef`
- `targetKind`
- `targetDevice`
- `diagnostics`
- `evidenceRefs`
- `artifactRefs`
- `privacyFlags`
- `safetyFlags`
- `transport`
- `limitations`
- `issueRefs`

The producer is `pccx-llm-launcher`. The consumer is pccx-lab as a
future CLI/core consumer. The current fixture uses placeholder values and
checked references only.

## Diagnostic Items

Each diagnostic item records:

- `diagnosticId`
- `severity`
- `category`
- `source`
- `title`
- `summary`
- `relatedContractRefs`
- `suggestedNextAction`
- `evidenceState`
- `redactionState`

Severity values are `info`, `warning`, `blocked`, and `error`.

Category values are `configuration`, `model_descriptor`,
`runtime_descriptor`, `target_device`, `evidence`, `safety`, and
`diagnostics_handoff`.

The fixture uses sanitized summaries only. It does not include raw full
logs, prompts, source code, private paths, secrets, tokens, provider
configuration, generated blobs, or model weight paths.

## Placeholder Fixture

The checked fixture shows a conservative launcher summary for Gemma 3N
E4B and the KV260 PCCX placeholder runtime:

- launcher target: not configured
- model descriptor: referenced by `gemma3n_e4b_placeholder`
- runtime descriptor: referenced by `kv260_pccx_placeholder`
- target device: placeholder, not configured, no hardware access
- compatibility state: provisional by reference to the descriptor
  boundary
- evidence: required before hardware or performance claims
- telemetry: disabled
- automatic upload: disabled
- write-back: disabled

The fixture does not embed model/runtime descriptor bodies. It only
references their checked fixture and identifiers. That keeps this
handoff from becoming a second model/runtime contract.

## Transport Sketch

The current contract names three future-safe transport options:

- JSON file handoff
- stdout JSON handoff
- read-only local artifact reference

These are sketches, not implementations. This PR does not add a file
watcher, background daemon, network transport, plugin execution, MCP
server/client, LSP flow, marketplace flow, or pccx-lab command
invocation.

## pccx-lab Boundary

pccx-lab remains CLI-first and core-first. Future pccx-lab work may read
the handoff as a local artifact and validate the schema before any
deeper integration. That consumer should not scrape launcher internals,
call launcher commands, or turn GUI/editor code into the source of
verification logic.

The launcher may produce a sanitized, read-only summary. pccx-lab may
consume that summary later as evidence-adjacent input. This repository
does not implement that pccx-lab consumer in this PR.

pccx-lab now has a matching read-only validation boundary:

```bash
pccx-lab diagnostics-handoff validate --file <path> --format json
```

That command lives on the pccx-lab side and validates a local JSON file.
This launcher repository does not invoke it, require it, watch for it,
or write back from it. Fixture sync is manual while the handoff remains
pre-compatibility.

## Safety Notes

This boundary does not add:

- launcher runtime execution
- pccx-lab execution
- KV260 hardware access
- model execution
- provider calls
- network calls
- telemetry
- automatic upload
- automatic write-back
- MCP implementation
- LSP implementation
- editor bridge runtime
- marketplace or publisher flow
- release or tag behavior
- a versioned API or ABI commitment

No stronger runtime, hardware, or performance claim should be made from
this fixture. Evidence is required before those claims belong in public
status output.
