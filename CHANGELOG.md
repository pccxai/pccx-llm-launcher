# Changelog

All notable changes to this repository are tracked in this file.

This file follows the Keep a Changelog structure. Entries in `Unreleased`
describe PR-scoped work that has not yet been cut as a repository release.

## [Unreleased]

### Evidence boundary

- Captured on 2026-05-07 from GitHub PR metadata for PRs
  [#70](https://github.com/pccxai/pccx-llm-launcher/pull/70)
  through [#82](https://github.com/pccxai/pccx-llm-launcher/pull/82).
- All listed PRs were `OPEN` with no `mergedAt` timestamp at capture time.
- The entries below record PR titles, changed-file scope, and validation
  claims reported in those PR bodies. They do not claim a shipped v002.1
  release, board access, serial hardware session, SSH session, HF download,
  model weight load, MMIO hardware access, bitstream load, provider call,
  pccx-lab execution, or runtime inference.

### Scaffolding

- [#70](https://github.com/pccxai/pccx-llm-launcher/pull/70)
  `feat(kv260): add data-only readiness scaffold` adds typed readiness
  interfaces and a data-only KV260 launcher boundary in `contracts/`,
  `docs/`, and direct Python tests. Reported validation includes compileall,
  readiness scaffold tests, runtime readiness tests, and claim-scan.
- [#71](https://github.com/pccxai/pccx-llm-launcher/pull/71)
  `feat(ui): integrate pccx-UI theme and logo` adds launcher-specific UI
  theme assets, logo material, README notes, and chat surface preview tests.
  Reported validation includes compileall, the chat surface preview test,
  Python and shell test loops, bash syntax checks, diff checks, and
  claim-scan on non-test changed surfaces.
- [#75](https://github.com/pccxai/pccx-llm-launcher/pull/75)
  `feat(launcher): add offline dummy end-to-end run` wires an offline
  `GemmaWeightPrep.prepare_dummy` to `AxiCmdMockBackend` to result-stream
  path and adds `scripts/pccx-launcher dummy-e2e --seed N`. Reported
  validation includes dummy e2e, Gemma weight prep, AXI mock tests, targeted
  py_compile, shell syntax checks, and claim-scan.
- [#81](https://github.com/pccxai/pccx-llm-launcher/pull/81)
  `test(integration): full-mock kv260 e2e harness` merges offline mock
  components and adds a full-mock integration test over the happy-path
  scenario, dummy e2e, AXI mock backend, and trace parsing. Reported
  validation includes the full-mock integration test, component tests,
  compileall, diff checks, and claim-scan.

### KV260 connection

- [#72](https://github.com/pccxai/pccx-llm-launcher/pull/72)
  `feat(kv260): add tty serial backend for KV260Connection` adds a lazy
  pyserial-backed tty connection path with value-hiding environment config
  and fake-serial tests. Reported validation includes serial connection,
  device session, runtime readiness, full Python and shell test loops, bash
  syntax checks, diff checks, and claim-scan.
- [#77](https://github.com/pccxai/pccx-llm-launcher/pull/77)
  `feat(kv260): add board-less mock connection` adds `KV260ConnectionMock`
  with YAML/JSON scenario fixtures for happy path, missing XRT, and partial
  apps. Reported validation includes mock connection tests, compileall, diff
  checks, claim-scan, and standalone Python tests.

### Mock backends

- [#74](https://github.com/pccxai/pccx-llm-launcher/pull/74)
  `feat(axi): add mock backend for AxiCmdChannel` adds offline AXI command
  and status shapes plus an in-memory mock backend. Reported validation
  includes AXI mock backend tests, standalone Python tests, compileall, bash
  syntax checks, and claim-scan.
- [#80](https://github.com/pccxai/pccx-llm-launcher/pull/80)
  `feat(mock): expand kv260 connection scenarios` adds boot-in-progress,
  XRT-present-without-apps, single-app-loaded, and panic-state mock
  scenarios. Reported validation includes KV260 mock and serial tests,
  compileall, standalone Python tests, shell syntax checks, `scripts/check.sh`,
  and claim-scan.

### GemmaWeightPrep

- [#73](https://github.com/pccxai/pccx-llm-launcher/pull/73)
  `feat(gemma): weight prep stage 1 - contract + dummy manifest` adds the
  stage-1 `GemmaWeightPrep` contract and deterministic dummy manifest
  generation. Reported validation includes Gemma weight prep tests,
  compileall, Python and shell test loops, diff checks, claim-scan, and an
  HF/weight-load scan on changed contract surfaces.

### Trace capture

- [#78](https://github.com/pccxai/pccx-llm-launcher/pull/78)
  `feat(trace): add capture client emitting v2 framing` adds
  `TraceCaptureClient` for v2 framing markers and CRC32 JSON lines, plus
  dummy-e2e capture output. Reported validation includes trace capture and
  dummy e2e tests, targeted py_compile, shell syntax checks, diff checks, and
  claim-scan.
- [#79](https://github.com/pccxai/pccx-llm-launcher/pull/79)
  `feat(e2e): wire dummy_e2e to capture client` routes dummy-e2e capture
  through `TraceCaptureClient.capture()` and adds smoke coverage for begin and
  end markers, frame count, and CRC-checked frames. Reported validation
  includes trace capture and dummy e2e tests, standalone Python tests,
  compileall, diff checks, and a dummy-e2e capture command.

### Docs

- [#76](https://github.com/pccxai/pccx-llm-launcher/pull/76)
  `docs(launcher): overview and offline walkthrough` adds launcher overview
  documentation for typed interfaces, tty serial, AXI mock backend, Gemma
  stage-1 dummy manifest, and dummy e2e walkthrough. Reported validation
  includes dummy-e2e walkthrough commands in a temporary worktree, diff checks,
  claim-scan, and a strict public surface scan.
- [#82](https://github.com/pccxai/pccx-llm-launcher/pull/82)
  `docs(coverage): add coverage summary and regenerator script` adds coverage
  summary documentation and a regeneration script for the KV260/offline mock
  slice. Reported validation includes the coverage summary script, shell
  syntax checks, compileall, diff checks, and claim-scan.
