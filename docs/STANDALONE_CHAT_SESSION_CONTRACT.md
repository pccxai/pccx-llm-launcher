# Standalone Chat Session Contract

This note defines the launcher-side standalone chat/session surface for
the planned local chat entry point. It is data-only and keeps the current
answer blocked until model, runtime, and target-session evidence exists.

Current answer: **blocked / no local chat runtime is active**.

The implementation lives in:

- `contracts/chat_session_contract.py`
- `contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json`
- `scripts/chat-session-stub.sh`
- `scripts/tests/chat_session_contract_test.py`

## What Is Implemented

The chat/session contract records:

- target model and KV260-class target identity
- chat surface, model-load, input, send, and session states
- disabled session controls for new session, model status, send,
  clear, and export actions
- a message envelope vocabulary without prompt or response content
- links to the runtime readiness and device/session status fixtures
- blocked reasons that explain what must exist before send controls can
  be enabled
- safety flags for the read-only boundary

The checked fixture is deterministic JSON. The stub command prints that
JSON for the supported model and target pair:

```bash
bash scripts/chat-session-stub.sh --model gemma3n-e4b --target kv260
```

## State Separation

The chat/session states are deliberately narrow:

- `target`: named planned target only
- `planned`: described for a future reviewed boundary
- `placeholder`: visible as deterministic local fixture data
- `blocked`: a required evidence item or boundary is missing
- `inactive`: no runtime session exists
- `disabled`: UI control is intentionally unavailable
- `ready_for_inputs`: a future reviewed boundary can accept explicit
  input, but this fixture stores none
- `not_configured`: required configuration is absent
- `not_loaded`: no model assets are loaded
- `not_started`: no transcript or log stream exists
- `unavailable`: output is not available
- `available_as_data`: local fixture shape is available as data only

## Coordination Boundary

The standalone chat surface depends on the existing launcher readiness
and device/session status contracts. It may later become the primary
user-facing entry point, but this contract does not add runtime
execution, model loading, provider calls, persistence, or target access.

pccx-lab remains a separate CLI/core diagnostics and verification
backend. systemverilog-ide may consume launcher data later as read-only
context. This launcher contract does not invoke either repo.

## Non-Goals

This chat/session surface does not add:

- model execution or generated responses
- prompt, response, or transcript persistence
- model loading or model weight paths
- KV260 runtime execution
- serial, SSH, or network target access
- provider or cloud calls
- pccx-lab invocation
- systemverilog-ide invocation
- MCP implementation
- LSP implementation
- marketplace flow
- telemetry, upload, or write-back
- release or tag behavior
- versioned compatibility commitment

Runtime readiness, explicit model/session evidence, and a reviewed local
chat execution boundary are required before send controls can move beyond
disabled for the Gemma 3N E4B plus KV260 target.
