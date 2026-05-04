# Standalone Chat Session Contract

This note defines the launcher-side standalone chat/session surface for
the planned local chat entry point. It is data-only and keeps the current
answer blocked until model, runtime, and target-session evidence exists.

Current answer: **blocked / no local chat runtime is active**.

The implementation lives in:

- `contracts/chat_session_contract.py`
- `contracts/chat_model_status_contract.py`
- `contracts/chat_session_lifecycle_contract.py`
- `contracts/chat_session_index_contract.py`
- `contracts/chat_readiness_contract.py`
- `contracts/chat_composer_contract.py`
- `contracts/chat_send_result_contract.py`
- `contracts/chat_transcript_policy_contract.py`
- `contracts/chat_audit_event_contract.py`
- `contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-session-lifecycle.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-session-index.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-send-result.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-audit-event.gemma3n-e4b-kv260-placeholder.json`
- `scripts/chat-session-stub.sh`
- `scripts/chat-model-status-stub.sh`
- `scripts/chat-session-lifecycle-stub.sh`
- `scripts/chat-session-index-stub.sh`
- `scripts/chat-readiness-stub.sh`
- `scripts/chat-composer-stub.sh`
- `scripts/chat-send-result-stub.sh`
- `scripts/chat-transcript-policy-stub.sh`
- `scripts/chat-audit-event-stub.sh`
- `scripts/chat-surface-preview.sh`
- `scripts/tests/chat_session_contract_test.py`
- `scripts/tests/chat_model_status_contract_test.py`
- `scripts/tests/chat_session_lifecycle_contract_test.py`
- `scripts/tests/chat_session_index_contract_test.py`
- `scripts/tests/chat_readiness_contract_test.py`
- `scripts/tests/chat_composer_contract_test.py`
- `scripts/tests/chat_send_result_contract_test.py`
- `scripts/tests/chat_transcript_policy_contract_test.py`
- `scripts/tests/chat_audit_event_contract_test.py`
- `scripts/tests/chat_surface_preview_test.py`
- `scripts/tests/status-chat-model-status.sh`
- `scripts/tests/status-chat-session-index.sh`
- `scripts/tests/status-chat-readiness.sh`
- `scripts/tests/status-chat-composer.sh`
- `scripts/tests/status-chat-send-result.sh`
- `scripts/tests/status-chat-transcript-policy.sh`
- `scripts/tests/status-chat-audit-event.sh`

## What Is Implemented

The chat/session contract records:

- target model and KV260-class target identity
- chat surface, model-load, input, send, and session states
- disabled session controls for new session, model status, send,
  clear, and export actions
- an empty session index/list surface with disabled refresh, selection,
  restore, rename, and delete controls
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

The chat model-status fixture records the display boundary for model
descriptor, asset, load, runtime, context, and response rows:

```bash
bash scripts/chat-model-status-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-model-status
```

Model loading stays blocked and disabled. The model-status fixture does
not read model paths, load weights, start runtimes, generate responses,
touch hardware, call providers, invoke pccx-lab, or write artifacts.

The lifecycle fixture records the session-management boundary for create,
restore, clear, close, and export-summary operations:

```bash
bash scripts/chat-session-lifecycle-stub.sh --model gemma3n-e4b --target kv260
```

Every lifecycle operation is disabled, blocked, inactive, or unavailable
until runtime readiness, model-load evidence, a reviewed local session
store, and explicit export/redaction rules exist. The fixture does not
read or write manifests, transcripts, summaries, prompts, responses, or
model paths.

The chat session index fixture records the list/sidebar boundary for
future local chat sessions:

```bash
bash scripts/chat-session-index-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-session-index
```

It reports an empty, not-configured session index and keeps refresh,
selection, restore, rename, and delete actions disabled, inactive,
unavailable, or blocked. The fixture does not read a session store,
session manifest, session title, transcript, summary, prompt, response,
model path, private path, or raw log, and it does not write, delete,
refresh, import, export, or persist artifacts.

The chat readiness fixture records the checklist and recovery-action
boundary used to decide whether the standalone chat surface can move
beyond preview state:

```bash
bash scripts/chat-readiness-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-readiness
```

It records local fixture availability, target model display, model asset
state, runtime readiness, device session state, chat runtime state,
session-store state, and no-provider mode. Recovery actions are disabled,
blocked, planned, or local data only. The fixture does not read prompts,
model assets, paths, manifests, transcripts, summaries, logs, device
state, or provider configuration.

The chat composer fixture records the input-control and validation shape
for the standalone chat surface:

```bash
bash scripts/chat-composer-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-composer
```

It keeps prompt capture, prompt echo, prompt persistence, attachment
reads, clipboard access, model execution, runtime startup, provider
calls, hardware access, pccx-lab invocation, and artifact writes out of
scope. Send controls remain disabled until the reviewed runtime,
session-store, model-load, and attachment boundaries exist.

The chat send-result fixture records the blocked result shape shown when
a send action is unavailable:

```bash
bash scripts/chat-send-result-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-send-result
```

It keeps the attempted-send result in blocked local data: no prompt is
accepted, captured, echoed, stored, or persisted; no assistant response
is generated; no model/runtime handoff is attempted; and no transcript
or artifact is written.

The chat transcript policy fixture records the retention, export,
storage, and privacy policy shape for future transcript UI surfaces:

```bash
bash scripts/chat-transcript-policy-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-transcript-policy
```

It keeps transcript handling disabled local data: no prompt, response,
message, transcript, or summary content is read, generated, exported,
stored, or persisted; no reviewed local store or retention period is
configured; and export remains disabled until an explicit user-action
and redaction boundary exists.

The chat audit-event fixture records a blocked audit metadata shape for
future chat UI events:

```bash
bash scripts/chat-audit-event-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-audit-event
```

It keeps audit handling as summary-only local data: event ids, event
states, blocked reason ids, redaction policy, and fixture references can
be rendered, but no prompt, response, transcript, actor identifier,
runtime trace, raw log, model path, private path, or artifact content is
read, logged, exported, stored, or persisted. Audit logging and local
audit history remain disabled and not configured.

The terminal preview command renders the same checked contract as a
read-only chat surface sketch:

```bash
bash scripts/chat-surface-preview.sh --model gemma3n-e4b --target kv260
```

The preview shows the blocked chat surface, inactive session state,
disabled controls, blocked reasons, and unavailable assistant response.
It does not accept or echo prompts, persist transcripts, execute a
model, touch hardware, call providers, invoke pccx-lab, or write
artifacts.

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
- `not_used`: no external provider state is used
- `unavailable`: output is not available
- `available_as_data`: local fixture shape is available as data only
- `empty_not_captured`: no prompt draft is captured or stored

The lifecycle states keep session management separate from chat message
content:

- `blocked`: a required readiness or policy boundary is missing
- `disabled`: a UI command is intentionally unavailable
- `inactive`: no launcher-owned chat session exists
- `not_configured`: no local session store or retention rule exists
- `not_loaded`: model assets are not loaded
- `placeholder`: deterministic local fixture state only
- `planned`: described for a future reviewed boundary
- `requires_evidence`: future operation needs evidence before enablement
- `unavailable`: no prior local session can be restored
- `available_as_data`: referenced local fixture shape is available as data only

The session-index states keep list/sidebar display separate from local
session storage and transcript content:

- `available_as_data`: the empty index surface can be rendered from
  checked fixture data
- `blocked`: a required local store or manifest boundary is missing
- `disabled`: selection or title-changing controls are intentionally
  unavailable
- `empty_not_captured`: no session titles, summaries, prompts, or
  responses are captured
- `inactive`: no launcher-owned local chat session is active or
  selectable
- `not_configured`: no local session store or index refresh source
  exists
- `planned`: described for a future reviewed boundary
- `requires_evidence`: a future artifact-read path needs evidence and
  tests first
- `summary_only`: privacy state contains metadata only
- `unavailable`: restore output or indexed sessions are unavailable

The readiness states keep send-control gating separate from model-status
display and lifecycle operations:

- `available_as_data`: referenced local fixture data is available without
  executing anything
- `blocked`: a required evidence item or reviewed boundary is missing
- `disabled`: a UI command is intentionally unavailable
- `external_not_configured`: user-provided model assets are not configured
- `inactive`: no target device or runtime session exists
- `not_configured`: no local store or retention policy exists
- `not_loaded`: model assets are not loaded
- `not_started`: no local chat runtime has started
- `not_used`: external provider state is not part of this boundary
- `planned`: described for a future reviewed boundary
- `requires_evidence`: future enablement requires evidence first
- `target_selected`: target descriptor data can be displayed
- `unavailable`: output or operation state is unavailable

The send-result states keep blocked UI feedback separate from prompt
content and assistant output:

- `available_as_data`: checked blocked-result fixture data is available
  without executing anything
- `blocked`: a required readiness or execution boundary is missing
- `disabled`: send controls are intentionally unavailable
- `empty_not_captured`: no prompt draft is captured or stored
- `inactive`: no target device, runtime, or launcher-owned chat session
  exists
- `not_configured`: no local store or retention policy exists
- `not_generated`: no assistant response has been produced
- `not_loaded`: model assets are not loaded
- `not_started`: no local chat runtime has started

The transcript policy states keep retention and export rules separate
from message content:

- `available_as_data`: checked policy data is available without
  executing anything
- `blocked`: a required storage, redaction, or user-action boundary is
  missing
- `disabled`: transcript persistence or export is intentionally
  unavailable
- `empty_not_captured`: no prompt or response body is captured or stored
- `inactive`: no launcher-owned transcript exists
- `not_configured`: no local store, retention period, or deletion rule
  exists
- `not_generated`: no assistant response or transcript summary exists
- `planned`: described for a future reviewed boundary
- `summary_only`: future summaries must stay separate from raw content

The audit-event states keep blocked event metadata separate from
message content, identity data, runtime traces, and persistence:

- `available_as_data`: checked audit metadata is available without
  executing anything
- `blocked`: a required readiness, logging, or storage boundary is
  missing
- `disabled`: audit persistence or transcript persistence is
  intentionally unavailable
- `empty_not_captured`: no prompt or message body is captured or stored
- `not_configured`: no audit logger, local store, or retention rule
  exists
- `not_generated`: no response content or event timestamp exists
- `not_started`: no local chat runtime has started
- `placeholder`: deterministic local fixture state only
- `redacted`: actor identifiers stay outside checked fixture data
- `summary_only`: audit data is limited to metadata and references
- `target_selected`: planned target identity can be displayed as local
  data only

## Coordination Boundary

The standalone chat surface depends on the existing launcher model
descriptor, readiness, and device/session status contracts. The
model-status contract adds reviewable display rows for model-load state.
The lifecycle contract adds a reviewable session-management shape, but
these contracts do not add runtime execution, model loading, provider
calls, persistence, target access, artifact reads, or artifact writes.
The readiness contract ties those display and lifecycle states into a
single checklist and recovery-action view without enabling any send,
load, restore, or export action.
The session-index contract adds a reviewable empty list/sidebar boundary
without enabling manifest reads, transcript reads, title capture,
restore, rename, delete, refresh, persistence, or artifact writes.
The composer contract adds a reviewable input-control and validation
shape without prompt capture, prompt echo, prompt persistence, attachment
reads, clipboard access, or send enablement.
The send-result contract adds a reviewable blocked-result display shape
without prompt acceptance, prompt echo, response generation, runtime
execution, model loading, persistence, or writes.
The transcript policy contract adds a reviewable retention/export
policy shape without message content, transcript persistence, summary
generation, artifact reads, artifact writes, runtime execution, model
loading, provider calls, or target access.
The audit-event contract adds a reviewable blocked event metadata shape
without prompt capture, prompt echo, response content, transcript
content, actor identifiers, runtime traces, audit persistence, artifact
reads, artifact writes, runtime execution, model loading, provider
calls, or target access.

pccx-lab remains a separate CLI/core diagnostics and verification
backend. systemverilog-ide may consume launcher data later as read-only
context. This launcher contract does not invoke either repo.

## Non-Goals

This chat/session surface does not add:

- model execution or generated responses
- prompt, response, or transcript persistence
- composer prompt capture, echo, persistence, attachment reads, or
  clipboard access
- send acceptance, prompt echo, response generation, or send-result
  persistence
- transcript retention, transcript export, local transcript storage,
  transcript summaries, or transcript message content
- audit logging, audit persistence, actor identifiers, event timestamps,
  runtime traces, raw logs, or audit export behavior
- session creation, restore, clear, close, or export behavior
- readiness recovery execution
- manifest, transcript, summary, or lifecycle artifact reads or writes
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
