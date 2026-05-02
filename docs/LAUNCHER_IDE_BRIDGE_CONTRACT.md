# Launcher / IDE Bridge Contract

This note describes the first launcher-side contract for future editor
integrations. It is a data-only status boundary. It does not start the
launcher, inspect a device, load a model, call a provider, or connect to
an editor.

The contract lives in:

- `contracts/launcher_ide_status_contract.py`
- `contracts/fixtures/launcher-ide-status.placeholder.json`

The fixture is the checked example for the current placeholder status.
It is deterministic and intentionally small enough to review in a pull
request.

## What Is Implemented

The contract reports a placeholder summary with:

- schema version
- launcher mode
- configured target
- target kind
- availability, runtime, model, and evidence states
- supported future operations
- safety flags
- pccx-lab diagnostics handoff status
- future consumers and limitations

All values are conservative. The default state is not configured or
planned unless there is checked evidence for something stronger.

## Planned Consumers

Future editor integrations may read this status before presenting
launcher actions to a user. `pccx-systemverilog-ide` is one possible
consumer, but this repository does not implement that integration in
this PR.

The planned mapping is:

| Contract operation | Future consumer action |
|---|---|
| `launcher.status.local` | Show local launcher status. |
| `model.runtime.descriptor` | Show model/runtime descriptor availability. |
| `device.session.status` | Show device/session status placeholder. |
| `pccxlab.diagnostics.handoff` | Prepare read-only diagnostics handoff for pccx-lab. |
| `editor.bridge.consumer` | Prepare editor bridge status. |
| `local.coding.assistant.consumer` | Prepare local coding-assistant status, disabled by default. |

These names are a draft bridge sketch, not a compatibility guarantee.
The shape may change before a versioned interface is declared.

## Model / Runtime Descriptor Reference

`model.runtime.descriptor` is backed by a separate data-only descriptor
boundary in
[`MODEL_RUNTIME_DESCRIPTOR_BOUNDARY.md`](./MODEL_RUNTIME_DESCRIPTOR_BOUNDARY.md).
That boundary names model and runtime descriptors, target placeholders,
lifecycle vocabulary, and a compatibility sketch without adding runtime
logic to this status contract.

The status contract remains a status summary. Future consumers may use
the operation id as a reference, but this module does not import the
descriptor module or execute model/runtime code.

## pccx-lab Boundary

pccx-lab remains the CLI/core lower boundary. Launcher and editor flows
should not bypass pccx-lab analysis behavior or create a separate logic
island.

Diagnostics handoff is planned as read-only first:

- no automatic upload
- no write-back
- no raw hardware log in this contract
- no user data
- no model weight path

The launcher now has a separate diagnostics handoff fixture for this
planned boundary:

- `contracts/diagnostics_handoff_contract.py`
- `contracts/fixtures/diagnostics-handoff.gemma3n-e4b-kv260-placeholder.json`
- [`DIAGNOSTICS_HANDOFF_CONTRACT.md`](./DIAGNOSTICS_HANDOFF_CONTRACT.md)

That fixture references this status operation by id. It does not execute
pccx-lab, invoke the launcher runtime, watch files, upload data, or write
back into launcher state.

## Safety Notes

This contract does not claim a KV260 run. It does not report throughput,
timing closure, or hardware readiness. Evidence is required before
hardware or performance claims.

This PR also does not add:

- launcher runtime execution
- AI provider calls
- network calls
- MCP implementation
- LSP implementation
- editor extension implementation
- packaging or publisher flow
- model weights or generated blobs

The purpose is to make future integration work easier to review by
starting with a small, testable data boundary.
