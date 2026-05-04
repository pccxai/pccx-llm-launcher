# Multi-Model And Device Support Plan

## Status

This is a later-track launcher-side plan for supporting multiple model
descriptors and multiple target-device descriptors. It records the catalog,
selection, and readiness boundaries needed before the launcher can expose a
model picker or device manager.

This plan does not implement a model selector UI, device manager, runtime
adapter, model loader, hardware probe, provider call, compatibility promise, or
KV260 inference path.

## Goal

The launcher should eventually let users choose from evidence-backed model and
device targets without turning the launcher into the owner of lower-level
runtime, hardware, or verification logic.

The launcher-owned role is to coordinate:

- model descriptor catalog entries
- runtime descriptor catalog entries
- target-device descriptor catalog entries
- selection state and disabled UI reasons
- readiness and evidence summaries from existing contracts
- explicit handoff references to pccx-lab or lower runtime evidence

Descriptor data should stay conservative until checked evidence supports a
stronger state.

## Planned Catalog Shape

The existing `pccx.modelDescriptor.v0`,
`pccx.runtimeDescriptor.v0`, and
`pccx.modelRuntimeCompatibility.v0` surfaces are the starting vocabulary.
Future multi-target work should extend that vocabulary with catalog-level
records rather than adding executable behavior directly to the status surface.

| Catalog | Purpose |
|---|---|
| Model catalog | Names target models, asset policies, quantization states, and evidence state. |
| Runtime catalog | Names runtime adapter families, lifecycle states, artifact requirements, and evidence requirements. |
| Device catalog | Names target-device classes, connection status, hardware access policy, and readiness blockers. |
| Compatibility matrix | Records descriptor-only compatibility results and the evidence still required before enablement. |

Gemma 3N E4B and KV260 remain target descriptors, not current working runtime
claims. Other model families and device targets should be added only as
descriptor entries until their evidence gates are satisfied.

## Model Selection Flow

A future model selection UI should:

1. Read model catalog data.
2. Show target model identity, asset policy, and evidence state.
3. Filter compatible runtime and device descriptors using descriptor data only.
4. Keep launch, chat, and local workflow controls disabled when readiness or
   evidence is blocked.
5. Explain missing evidence without silently falling back to a different model
   or provider.

The model selector should not read model directories, load weights, infer
available assets from private paths, contact providers, or execute runtime
commands as part of selection.

## Device Manager Flow

A future device manager should:

1. Read device/session status data and target-device descriptors.
2. Show configured, unavailable, blocked, and evidence-required states.
3. Keep discovery and connection actions behind separately reviewed commands.
4. Preserve explicit user choice when more than one target is visible.
5. Keep runtime start controls blocked until readiness evidence allows them.

The device manager should not scan networks, open serial ports, attempt SSH,
probe KV260 hardware, invoke pccx-lab, or start a runtime as part of this plan.

## Evidence Gates

Before a model/device pair can move beyond placeholder state, the launcher
should have checked evidence for:

- model asset policy and user-provided asset handling
- runtime adapter availability and reviewed lifecycle behavior
- target-device configuration and connection policy
- hardware and runtime readiness from lower layers
- compatibility between selected model, runtime, and device descriptors
- measured performance only after a separate evidence-backed run exists

If any gate is missing, the selected pair should remain unavailable, blocked, or
provisional in user-facing surfaces.

## Safety Boundary

Multi-model and multi-device support must not add:

- bundled model weights or generated weight artifacts
- model loading, runtime execution, or provider/network calls
- KV260 runtime access, serial access, SSH, board probing, or inference claims
- automatic pccx-lab execution outside an explicitly reviewed CLI/core boundary
- prompt, response, transcript, private path, secret, token, or model-weight
  path storage
- telemetry, upload, write-back, commits, pushes, releases, or tag behavior
- API/ABI stability, marketplace readiness, or compatibility guarantees

Every future executable action should have a separate issue, bounded inputs,
clear disabled states, user approval where needed, and tests that block private
data and unsupported claims.

## Acceptance Gates Before Implementation

Before adding executable model or device behavior, the launcher should have:

- a catalog fixture shape for model, runtime, and target-device descriptors
- tests for descriptor-only compatibility and missing-evidence states
- UI mapping for unavailable, blocked, provisional, and evidence-required
  states
- a device discovery policy that states which commands may run and when
- a model asset policy that keeps paths and weights out of checked fixtures
- separate implementation issues for model selection UI, device management,
  runtime adapter integration, and any hardware-touching command

## Issue Alignment

This plan addresses
[`pccx-llm-launcher#13`](https://github.com/pccxai/pccx-llm-launcher/issues/13)
by recording the multi-model and multi-device support direction while keeping
the current launcher work descriptor-only and evidence-gated.
