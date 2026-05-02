# Model / Runtime Descriptor Boundary

This note defines the launcher-side descriptor boundary for future model
and runtime integration. It is a data-only contract. It describes how the
launcher can name models, runtimes, target devices, compatibility, and
lifecycle states before any real runtime path is wired in.

The implementation lives in:

- `contracts/model_runtime_descriptor_contract.py`
- `contracts/fixtures/model-runtime-descriptor.gemma3n-e4b-kv260-placeholder.json`
- `scripts/tests/model_runtime_descriptor_test.py`

## What Is Implemented

The contract currently provides:

- a model descriptor schema
- a runtime descriptor schema
- a deterministic compatibility sketch
- a checked Gemma 3N E4B plus KV260 PCCX placeholder example
- fixture tests that scan for private paths, bundled assets, secrets,
  provider configuration, runtime execution, hardware access, and
  unsupported claims

The descriptors are deliberately conservative. They are meant to give the
launcher, future editor consumers, and pccx-lab handoff code one shared
vocabulary without making the launcher a separate logic island.

## Model Descriptor

The model descriptor records model identity and asset status:

- `schemaVersion`
- `modelId`
- `modelFamily`
- `modelVariant`
- `parameterScale`
- `tokenizerKind`
- `weightFormat`
- `weightLocationKind`
- `weightPresence`
- `loadState`
- `quantization`
- `expectedRuntimeKinds`
- `measurementState`
- `evidenceState`
- `limitations`
- `safetyFlags`

The checked placeholder uses `gemma3n_e4b_placeholder`. Its assets are
external/user-provided, not bundled, and not loaded. Measurement and
evidence states remain `not_measured` and `evidence_required`.

## Runtime Descriptor

The runtime descriptor records the planned runtime path and target state:

- `schemaVersion`
- `runtimeId`
- `runtimeKind`
- `targetKind`
- `targetDevice`
- `acceleratorKind`
- `availabilityState`
- `configurationState`
- `lifecycleStates`
- `supportedModelFamilies`
- `requiredArtifacts`
- `statusChecks`
- `evidenceRequirements`
- `compatibilityNotes`
- `safetyFlags`

The checked KV260 runtime uses `kv260_pccx_placeholder`. It is planned,
unavailable, and not configured. Status checks are descriptor-only and
explicitly record no hardware access and no runtime execution.

The model descriptor also names `cpu_reference_placeholder` as an
expected future runtime kind. That is vocabulary only; this PR does not
add a CPU runtime descriptor or execution path.

## Lifecycle Vocabulary

The descriptor names the future lifecycle states:

- `load`
- `warm`
- `run`
- `unload`

All four are marked `planned` and `descriptor_only`. No lifecycle state
starts a process, loads model assets, touches a target device, or calls a
provider.

## Compatibility Sketch

`resolve_model_runtime_compatibility(model, runtime)` compares only the
data supplied in the descriptors.

It checks:

- whether the runtime kind is listed by the model descriptor
- whether the model family is listed by the runtime descriptor
- whether required artifacts and evidence are still missing
- whether the runtime is unavailable or not configured
- whether the model remains not measured

The result contains:

- `compatible`
- `compatibilityState`
- `reason`
- `requiredEvidence`
- `missingArtifacts`
- `warnings`
- `nextActionKind`

For the Gemma 3N E4B plus KV260 placeholder, the resolver returns
`compatible: false` with `compatibilityState: provisional`. The descriptor
match is visible, but evidence is required before the launcher can make a
runtime claim.

The resolver does not inspect hardware, inspect model directories,
execute commands, call network APIs, call providers, read private paths,
or look for generated caches.

## Placeholder Example

The checked example shows:

- model identity: `gemma3n_e4b_placeholder`
- runtime identity: `kv260_pccx_placeholder`
- model assets: external/user-provided and not bundled
- model load state: `not_loaded`
- runtime state: planned, unavailable, and not configured
- compatibility: provisional
- evidence: required before runtime claims
- performance: not measured
- launcher/IDE reference: data-only through `model.runtime.descriptor`

There is no bundled weight file, no provider configuration, no KV260
hardware access, no runtime execution, no throughput claim, and no
versioned API or ABI commitment in this descriptor boundary.

## Launcher / IDE Status Relationship

The existing launcher/IDE status contract already exposes the planned
operation `model.runtime.descriptor`. The descriptor example includes a
small reference to that operation:

- `operationId: model.runtime.descriptor`
- `referenceKind: descriptor_only`
- `coupling: data_reference_only`
- `executesRuntime: false`
- `touchesHardware: false`

The status contract does not import this descriptor module. Future editor
or launcher code can read both contracts without turning the status
boundary into runtime logic.

## pccx-lab Boundary

pccx-lab remains CLI-first and core-first. Future diagnostics handoff
should use pccx-lab/core contracts for evidence and analysis. This
launcher descriptor boundary only names the model/runtime vocabulary that
future launcher runtime integration can refer to.

Issue #5 diagnostics integration should wait until this descriptor shape
has settled enough to avoid inventing a second model/runtime vocabulary.

## Non-Goals

This descriptor boundary does not add:

- model weight loading
- bundled or copied weights
- model runtime execution
- KV260 device access
- hardware probing
- provider or network calls
- MCP implementation
- LSP implementation
- marketplace or publisher flow
- release or tag behavior
- API or ABI stability commitment

Evidence from the lower runtime, device, and pccx-lab/core layers is
required before any future runtime support or performance claim.
