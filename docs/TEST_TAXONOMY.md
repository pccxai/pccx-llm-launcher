# Test Taxonomy

This repository uses four test labels for launcher work: contract, mock,
integration, and e2e. The labels describe what a test is allowed to prove, not
how important the test is.

The current suite is mostly contract tests and local mock/smoke tests. Real
hardware, model, provider, and pccx-lab execution are not part of the default
test path.

## Contract Tests

Contract tests verify deterministic data boundaries and checked fixtures. They
are the default test type for planned launcher surfaces because most current
features are data-only placeholders.

Use this label when a test:

- compares generated JSON with a checked fixture
- checks required fields, enum/state vocabulary, and fixture references
- verifies safety flags and blocked states
- scans docs, scripts, and sources for private data or unsupported claims
- avoids hardware, model loading, providers, network calls, and artifact writes

Existing examples:

- `scripts/tests/launcher_ide_contract_test.py`
- `scripts/tests/runtime_readiness_contract_test.py`
- `scripts/tests/device_session_status_contract_test.py`
- `scripts/tests/chat_session_contract_test.py`
- `scripts/tests/chat_error_taxonomy_contract_test.py`
- `scripts/tests/chat_evidence_manifest_contract_test.py`

These tests should remain deterministic and runnable on a normal CI host with
only Python and the repository checkout.

## Mock Tests

Mock tests exercise launcher scripts or command boundaries with local fake
inputs. They verify routing, output summaries, failure behavior, and guardrails
without depending on real pccx-lab, KV260 hardware, model assets, providers, or
network state.

Use this label when a test:

- creates a fake executable or fake command output
- runs a `*-stub.sh` script and checks conservative terminal output
- verifies refusal paths such as missing `--dry-run`
- checks that no silent fallback or unsupported runtime claim is printed
- stays local and hermetic

Existing examples:

- `scripts/tests/status-backend.sh` creates fake `pccx-lab` binaries to test
  `scripts/status-stub.sh --backend pccx-lab`.
- `scripts/tests/status-chat-session.sh` checks the local chat/session status
  summary.
- `scripts/tests/status-readiness.sh` checks the runtime readiness summary.
- `scripts/tests/status-chat-response-stream.sh` checks the disabled response
  stream summary.
- CI refusal checks run `scripts/launch-stub.sh` and `scripts/chat-stub.sh`
  without `--dry-run` and expect non-zero exits.

Mock tests may execute shell scripts, but they should not turn on real external
systems. If a fake binary, fake JSON envelope, or blocked fixture is involved,
the test belongs here rather than in integration.

## Integration Tests

Integration tests verify a reviewed boundary against a real external component.
They may call another PCCX CLI, runtime adapter, device bridge, or filesystem
artifact boundary when that dependency is intentionally provided for the test.

Use this label when a test:

- executes a real dependency instead of a fake executable
- validates an agreed inter-repository command or JSON envelope
- preserves explicit failure when the dependency is missing or invalid
- is gated so default CI does not accidentally require hardware, model assets,
  network, or private local paths

Current status:

- The default suite has no real integration test against pccx-lab, KV260
  hardware, a model runtime, or a provider.
- `scripts/tests/status-backend.sh` is an integration-boundary mock test. It is
  useful evidence for the command contract, but it is not proof that the real
  pccx-lab binary is present or compatible.

Future integration tests should name the external dependency in the file name
or CI job, for example `pccx_lab_status_integration_test` or
`kv260_status_probe_integration_test`, and should document the required opt-in
environment variables.

## E2E Tests

E2E tests verify a complete user-visible launcher flow across the real
components required for that flow. For this repository, true e2e coverage means
more than rendering the planned surface: it must include the reviewed launcher
flow, model/runtime readiness, target-device state, and expected user-visible
result for the scenario under test.

Use this label only when a test:

- exercises the user-facing flow from launcher entry point to final status or
  output
- uses real reviewed dependencies for the scenario
- records the target, model, runtime, evidence source, and artifact policy
- distinguishes blocked, unavailable, and successful states with concrete
  evidence
- avoids claiming KV260 inference, throughput, or release readiness unless the
  measured evidence is present

Current status:

- The default suite has no true e2e tests.
- `scripts/tests/chat_surface_preview_test.py` is a deterministic preview test,
  not e2e. It verifies blocked UI text, pccx-UI asset references, and refusal
  behavior without accepting prompts, loading a model, touching hardware, or
  calling providers.
- `scripts/tests/runtime_readiness_contract_test.py` and
  `scripts/tests/status-chat-session.sh` include guardrails that keep planned
  launcher states from being mistaken for e2e evidence.

Future e2e tests should be opt-in until the required hardware/runtime evidence
is available. They should state the required environment and should not run in
default CI unless every dependency is stable, public, and reproducible for that
job.

## Quick Label Guide

| Label | Proves | Existing examples |
|---|---|---|
| Contract | Data shape, fixture determinism, safety vocabulary, claim hygiene | `scripts/tests/*_contract_test.py`, `scripts/tests/model_runtime_descriptor_test.py` |
| Mock | Local script behavior with fake or blocked dependencies | `scripts/tests/status-backend.sh`, `scripts/tests/status-chat-*.sh`, dry-run refusal checks |
| Integration | Real reviewed external boundary behavior | Not present in default CI today |
| E2E | Complete real user flow with required evidence | Not present in default CI today |

When a test could fit more than one label, choose the weakest label that
accurately describes the evidence. A test that uses a fake dependency is mock,
even if it exercises an integration-shaped command. A test that renders a
blocked preview is not e2e until real dependencies and measured evidence are in
the loop.
