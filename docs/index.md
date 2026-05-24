# Launcher Documentation Overview

This page is the launcher documentation index. It groups the checked contract
docs that are already in this tree and the companion documentation added during
the 2026-05-07 launcher documentation pass.

The launcher remains data-first and evidence-gated. These docs describe current
contracts, mock-only paths, and planned KV260/Gemma boundaries without claiming
that this repository runs a real KV260 inference path today.

## Core Contracts

- [Launcher / IDE Bridge Contract](./LAUNCHER_IDE_BRIDGE_CONTRACT.md) -
  top-level launcher status boundary for future editor integrations.
- [Model / Runtime Descriptor Boundary](./MODEL_RUNTIME_DESCRIPTOR_BOUNDARY.md) -
  shared vocabulary for model descriptors, runtime descriptors, targets,
  compatibility, and lifecycle states.
- [Runtime Readiness Status](./RUNTIME_READINESS_STATUS.md) -
  evidence-aware readiness state for the planned Gemma 3N E4B plus KV260
  launcher path.
- [KV260 Connection And Status Flow](./KV260_CONNECTION_AND_STATUS_FLOW.md) -
  placeholder device/session status panel and gated KV260 connection flow.
- [Standalone Chat Session Contract](./STANDALONE_CHAT_SESSION_CONTRACT.md) -
  data-only chat/session surface that keeps local chat blocked until model,
  runtime, and session evidence exists.
- [Diagnostics Handoff Contract](./DIAGNOSTICS_HANDOFF_CONTRACT.md) -
  read-only diagnostics handoff shape for future pccx-lab consumers.

## 2026-05-07 Companion Docs

- [Clean-Room Install](./INSTALL.md) - fresh checkout setup, editable install,
  and mock e2e smoke path.
- [Gemma Chat Template Spec](./GEMMA_CHAT_TEMPLATE_SPEC.md) - launcher-side
  Gemma message formatting contract for the mock chat path.
- [20 tok/s Target Rationale](./PERFORMANCE_TARGET.md) - planning target
  boundary for the Gemma 3N E4B plus KV260 path.
- [KV260 Serial Backend Spec](./KV260_SERIAL_BACKEND_SPEC.md) - guarded serial
  console backend contract for explicit KV260 status checks.
- [AXI Command Channel Semantics](./AXI_CMD_CHANNEL.md) - launcher-facing AXI
  command boundary for future runtime integration and offline tests.
- [NpuStat Error Codes](./NPU_STAT_ERROR_CODES.md) - launcher-side meaning of
  offline AXI command mock status values.
- [ISA Mirror Sync Policy](./ISA_MIRROR_SYNC_POLICY.md) - launcher-side mirror
  policy for the KV260 v002 ISA vocabulary.
- [KV260 Data-Only Readiness Scaffold](./KV260_DATA_ONLY_READINESS_SCAFFOLD.md) -
  typed readiness shapes for future connection, NPU status, weight prep, AXI
  status, and result stream surfaces.
- [XRT Vs Raw Devmem Policy](./XRT_VS_DEVMEM_POLICY.md) - future runtime-access
  policy for XRT and raw device-memory paths.

## Quality And Governance

- [Test Coverage Snapshot](./test-coverage.md) - generated source-level
  coverage summary for the current KV260/offline mock slice.
- [Test Taxonomy](./TEST_TAXONOMY.md) - contract, mock, integration, and e2e
  labels for launcher tests.
- [Python Dependency Policy](./PYTHON_DEPENDENCY_POLICY.md) - dependency
  selection rules for launcher-side Python packages.
- [Security Policy](../SECURITY.md) - vulnerability reporting and supported
  security posture.
- [Changelog](../CHANGELOG.md) - launcher landing history for the current
  documentation and mock-path ramp.
- [pccx-UI Asset Notice](../assets/PCCX_UI_NOTICE.md) - provenance and license
  notice for copied launcher UI assets.

## Later-Track Plans

- [Local Workflow Mode Plan](./LOCAL_WORKFLOW_MODE_PLAN.md) - planned local
  workflow mode, bounded context inputs, and safety gates.
- [Multi-Model And Device Support Plan](./MULTI_MODEL_DEVICE_SUPPORT_PLAN.md) -
  planned catalog, selection, device-manager, and evidence boundaries for
  multiple models and targets.
- [Other Editor Bridge Plan](./OTHER_EDITOR_BRIDGE_PLAN.md) - planned
  JetBrains and generic editor bridge approach using the same launcher-owned
  data contracts.

## Repository Context

- [Source Provenance](./PROVENANCE.md) - import origin, deliberately excluded
  upstream artifacts, and current evidence expectations for launcher releases.
