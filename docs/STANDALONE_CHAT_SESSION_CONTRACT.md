# Standalone Chat Session Contract

This note defines the launcher-side standalone chat/session surface for
the planned local chat entry point. It is data-only and keeps the current
answer blocked until model, runtime, and target-session evidence exists.

Current answer: **blocked / no local chat runtime is active**.

The implementation lives in:

- `contracts/chat_session_contract.py`
- `contracts/chat_model_status_contract.py`
- `contracts/chat_model_selection_policy_contract.py`
- `contracts/chat_context_policy_contract.py`
- `contracts/chat_model_load_request_contract.py`
- `contracts/chat_session_lifecycle_contract.py`
- `contracts/chat_surface_layout_contract.py`
- `contracts/chat_empty_state_contract.py`
- `contracts/chat_local_only_policy_contract.py`
- `contracts/chat_preferences_contract.py`
- `contracts/chat_session_index_contract.py`
- `contracts/chat_session_store_policy_contract.py`
- `contracts/chat_session_title_policy_contract.py`
- `contracts/chat_readiness_contract.py`
- `contracts/chat_composer_contract.py`
- `contracts/chat_send_result_contract.py`
- `contracts/chat_transcript_policy_contract.py`
- `contracts/chat_audit_event_contract.py`
- `contracts/chat_error_taxonomy_contract.py`
- `contracts/chat_message_list_contract.py`
- `contracts/chat_action_bar_contract.py`
- `contracts/chat_clipboard_policy_contract.py`
- `contracts/chat_redaction_policy_contract.py`
- `contracts/chat_attachment_policy_contract.py`
- `contracts/chat_shortcut_map_contract.py`
- `contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-model-status.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-model-selection-policy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-context-policy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-model-load-request.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-session-lifecycle.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-surface-layout.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-empty-state.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-local-only-policy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-preferences.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-session-index.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-session-store-policy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-session-title-policy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-readiness.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-composer.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-send-result.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-transcript-policy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-audit-event.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-error-taxonomy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-message-list.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-action-bar.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-clipboard-policy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-redaction-policy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-attachment-policy.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-shortcut-map.gemma3n-e4b-kv260-placeholder.json`
- `scripts/chat-session-stub.sh`
- `scripts/chat-model-status-stub.sh`
- `scripts/chat-model-selection-policy-stub.sh`
- `scripts/chat-context-policy-stub.sh`
- `scripts/chat-model-load-request-stub.sh`
- `scripts/chat-session-lifecycle-stub.sh`
- `scripts/chat-surface-layout-stub.sh`
- `scripts/chat-empty-state-stub.sh`
- `scripts/chat-local-only-policy-stub.sh`
- `scripts/chat-preferences-stub.sh`
- `scripts/chat-session-index-stub.sh`
- `scripts/chat-session-store-policy-stub.sh`
- `scripts/chat-session-title-policy-stub.sh`
- `scripts/chat-readiness-stub.sh`
- `scripts/chat-composer-stub.sh`
- `scripts/chat-send-result-stub.sh`
- `scripts/chat-transcript-policy-stub.sh`
- `scripts/chat-audit-event-stub.sh`
- `scripts/chat-error-taxonomy-stub.sh`
- `scripts/chat-message-list-stub.sh`
- `scripts/chat-action-bar-stub.sh`
- `scripts/chat-clipboard-policy-stub.sh`
- `scripts/chat-redaction-policy-stub.sh`
- `scripts/chat-attachment-policy-stub.sh`
- `scripts/chat-shortcut-map-stub.sh`
- `scripts/chat-surface-preview.sh`
- `scripts/tests/chat_session_contract_test.py`
- `scripts/tests/chat_model_status_contract_test.py`
- `scripts/tests/chat_model_selection_policy_contract_test.py`
- `scripts/tests/chat_context_policy_contract_test.py`
- `scripts/tests/chat_model_load_request_contract_test.py`
- `scripts/tests/chat_session_lifecycle_contract_test.py`
- `scripts/tests/chat_surface_layout_contract_test.py`
- `scripts/tests/chat_empty_state_contract_test.py`
- `scripts/tests/chat_local_only_policy_contract_test.py`
- `scripts/tests/chat_preferences_contract_test.py`
- `scripts/tests/chat_session_index_contract_test.py`
- `scripts/tests/chat_session_store_policy_contract_test.py`
- `scripts/tests/chat_session_title_policy_contract_test.py`
- `scripts/tests/chat_readiness_contract_test.py`
- `scripts/tests/chat_composer_contract_test.py`
- `scripts/tests/chat_send_result_contract_test.py`
- `scripts/tests/chat_transcript_policy_contract_test.py`
- `scripts/tests/chat_audit_event_contract_test.py`
- `scripts/tests/chat_error_taxonomy_contract_test.py`
- `scripts/tests/chat_message_list_contract_test.py`
- `scripts/tests/chat_action_bar_contract_test.py`
- `scripts/tests/chat_clipboard_policy_contract_test.py`
- `scripts/tests/chat_redaction_policy_contract_test.py`
- `scripts/tests/chat_attachment_policy_contract_test.py`
- `scripts/tests/chat_shortcut_map_contract_test.py`
- `scripts/tests/chat_surface_preview_test.py`
- `scripts/tests/status-chat-model-status.sh`
- `scripts/tests/status-chat-model-selection-policy.sh`
- `scripts/tests/status-chat-context-policy.sh`
- `scripts/tests/status-chat-model-load-request.sh`
- `scripts/tests/status-chat-surface-layout.sh`
- `scripts/tests/status-chat-empty-state.sh`
- `scripts/tests/status-chat-local-only-policy.sh`
- `scripts/tests/status-chat-preferences.sh`
- `scripts/tests/status-chat-session-index.sh`
- `scripts/tests/status-chat-session-store-policy.sh`
- `scripts/tests/status-chat-session-title-policy.sh`
- `scripts/tests/status-chat-readiness.sh`
- `scripts/tests/status-chat-composer.sh`
- `scripts/tests/status-chat-send-result.sh`
- `scripts/tests/status-chat-transcript-policy.sh`
- `scripts/tests/status-chat-audit-event.sh`
- `scripts/tests/status-chat-error-taxonomy.sh`
- `scripts/tests/status-chat-response-stream.sh`
- `scripts/tests/status-chat-message-list.sh`
- `scripts/tests/status-chat-action-bar.sh`
- `scripts/tests/status-chat-clipboard-policy.sh`
- `scripts/tests/status-chat-redaction-policy.sh`
- `scripts/tests/status-chat-attachment-policy.sh`
- `scripts/tests/status-chat-shortcut-map.sh`

## What Is Implemented

The chat/session contract records:

- target model and KV260-class target identity
- chat surface, model-load, input, send, and session states
- a disabled model-selection policy boundary for static target option,
  model catalog, picker, asset discovery, provider fallback, persistence,
  and load-request gates
- a disabled context-policy boundary for context windows, tokenization,
  token counting, transcript context, summaries, truncation, context
  assembly, and runtime handoff
- a disabled model-load request boundary for descriptor selection, asset
  paths, checksums, runtime preflight, load, warmup, and unload gates
- disabled session controls for new session, model status, send,
  clear, and export actions
- planned shell regions and navigation items for the blocked chat
  surface layout
- static empty-state display slots and disabled hints for the blocked
  chat surface without command dispatch or action execution
- local-only policy metadata that keeps cloud/provider/network fallback
  paths disabled or not used
- planned preferences panels for model/target display, privacy,
  local-only mode, transcript policy, and session settings without
  configuration reads or preference writes
- an empty session index/list surface with disabled refresh, selection,
  restore, rename, and delete controls
- a chat session-store policy with disabled store configuration, path,
  manifest, read, write, delete, retention, and migration gates
- a chat session-title policy with static placeholder display names and
  disabled stored-title read, title generation, rename, and persistence
  controls
- a message envelope vocabulary without prompt or response content
- links to the runtime readiness and device/session status fixtures
- blocked reasons that explain what must exist before send controls can
  be enabled
- safety flags for the read-only boundary
- grouped chat error taxonomy metadata for future banners and status rows
- blocked chat response stream metadata for disabled progress, token,
  stop-control, and assistant response placeholders
- empty chat message-list metadata for the conversation viewport without
  message bodies or transcript reads
- disabled action-bar metadata for new, clear, export, retry, copy, stop,
  and attach controls without side effects
- disabled redaction-policy metadata for redaction rules, content scan,
  PII, secret, prompt, response, transcript, message, attachment,
  clipboard, audit, and result-persistence gates without side effects
- disabled attachment-policy metadata for file picker, file read, upload,
  import, preview, and persistence gates without side effects
- disabled shortcut-map metadata for planned keyboard accelerators,
  focus, and navigation without listeners, capture, dispatch, or side
  effects

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

The chat model-selection policy fixture records the disabled local picker
and model catalog boundary for future chat model selection:

```bash
bash scripts/chat-model-selection-policy-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-model-selection-policy
```

It reports one static placeholder option plus disabled catalog, picker,
asset discovery, provider fallback, selection persistence, and
load-request gates. The fixture does not read configuration files,
environment values, model catalogs, model paths, asset paths, model
weights, tokenizer files, checksum manifests, private paths, prompts,
responses, transcripts, runtime logs, or artifacts, and it does not
accept or persist model selections, call providers, validate assets,
load models, start runtimes, or write model-selection data.

The chat context-policy fixture records the disabled context-window,
tokenization, and context-assembly boundary for future chat turns:

```bash
bash scripts/chat-context-policy-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-context-policy
```

It reports context-window, token budget, tokenizer, prompt-context,
transcript-context, summary, truncation, context assembly, and runtime
handoff gates as disabled, blocked, not configured, or not generated. The
fixture does not read prompts, responses, transcripts, message bodies,
summaries, session stores, configuration files, environment values, model
paths, tokenizer paths, runtime logs, private paths, or artifacts, and it
does not count tokens, truncate context, assemble a runtime payload,
generate summaries, load models, start runtimes, call providers, or write
context data.

The chat model-load request fixture records the disabled local load
boundary for future chat model loading:

```bash
bash scripts/chat-model-load-request-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-model-load-request
```

It reports descriptor selection, asset path, checksum, runtime preflight,
load, warmup, unload, and persistence gates. The fixture does not read
configuration files, environment values, model paths, asset paths, model
weights, tokenizer files, checksum manifests, private paths, prompts,
responses, transcripts, runtime logs, or artifacts, and it does not
validate, load, unload, warm up, execute, import, export, persist, upload,
or write model-load request data.

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

The chat surface layout fixture records the shell-region and navigation
boundary for the planned standalone chat UI:

```bash
bash scripts/chat-surface-layout-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-surface-layout
```

It reports local metadata for the session sidebar, model-status header,
readiness banner, transcript region, composer bar, send-result region,
and audit footer. The fixture does not implement an app shell, read
prompt/response/transcript/session-store content, focus the composer,
start runtime code, load a model, touch hardware, call providers,
invoke pccx-lab, or write artifacts.

The chat empty-state fixture records static placeholder display slots
and disabled hints for the planned standalone chat UI:

```bash
bash scripts/chat-empty-state-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-empty-state
```

It reports target, empty transcript, readiness, disabled composer, and
local-only display slots plus disabled hints for future session, model,
readiness, and composer affordances. The fixture does not read prompts,
responses, transcripts, session stores, model paths, configuration,
environment values, runtime logs, private paths, or artifacts, and it
does not accept input, dispatch commands, change focus, load models,
start runtimes, access a target, call providers, invoke pccx-lab, or
write artifacts.

The chat local-only policy fixture records the cloud/provider/network
dependency boundary for the planned standalone chat UI:

```bash
bash scripts/chat-local-only-policy-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-local-only-policy
```

It reports local-only mode, provider configuration, network access, and
cloud fallback as deterministic metadata. Provider configuration,
environment secrets, tokens, network paths, cloud fallback, model
execution, runtime startup, hardware access, pccx-lab invocation,
artifact reads/writes, telemetry, upload, prompt capture, and response
generation are not used by this boundary.

The chat preferences fixture records planned settings panels and
disabled preference controls for the standalone chat UI:

```bash
bash scripts/chat-preferences-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-preferences
```

It reports target model/device display, local-only mode, cloud fallback,
transcript retention/export, session store location, and diagnostics
verbosity as deterministic metadata. The fixture does not read or write
configuration files, provider settings, environment values, secrets,
tokens, model asset paths, session-store paths, prompts, responses,
transcripts, summaries, logs, or artifacts; preference save/import/export
actions remain blocked until a separate reviewed storage boundary exists.

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

The chat session-store policy fixture records the local storage boundary
for future chat sessions:

```bash
bash scripts/chat-session-store-policy-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-session-store-policy
```

It reports disabled store configuration, store path, manifest, read,
write, delete, retention, and migration gates. The fixture does not read
configuration files, environment values, store paths, private paths,
manifests, session records, transcripts, titles, prompts, responses,
summaries, model paths, runtime logs, or artifacts, and it does not write,
delete, migrate, import, export, persist, compact, or roll back any store.

The chat session-title policy fixture records the display-name boundary
for future local chat sessions:

```bash
bash scripts/chat-session-title-policy-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-session-title-policy
```

It reports a static placeholder title label and keeps stored-title reads,
title generation, rename, and persistence disabled or blocked. The
fixture does not read session stores, manifests, stored titles,
transcripts, summaries, prompts, responses, model paths, private paths,
or raw logs, and it does not generate, rename, persist, import, export,
refresh, read, or write title artifacts.

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

The chat response stream fixture records the disabled assistant response
stream/progress shape shown after the blocked send-result boundary:

```bash
bash scripts/chat-response-stream-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-response-stream
```

It keeps response streaming as blocked local data: no stream transport
is opened, no response chunks are generated, no token counts are
measured, no stop signal is sent, no prompt or response content is read,
and no transcript or artifact is written.

The chat message-list fixture records the empty conversation viewport
shape used by the planned standalone chat surface:

```bash
bash scripts/chat-message-list-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-message-list
```

It keeps the message list as empty local data: no session store or
transcript is read, no message bodies are included, no prompt or
response content is displayed, no response stream is appended, no model
or runtime path is started, and no transcript or artifact is written.

The chat action-bar fixture records the disabled conversation action
controls used by the planned standalone chat surface:

```bash
bash scripts/chat-action-bar-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-action-bar
```

It keeps action controls as local metadata: new chat, clear, export,
retry, copy, stop, and attach controls remain disabled, blocked,
unavailable, or planned. No session store or transcript is read, no
message body is included, no transcript is exported, no clipboard or file
operation is performed, no stop signal is sent, no model or runtime path
is started, and no artifact is written.

The chat clipboard-policy fixture records the disabled clipboard boundary
used by the planned standalone chat surface:

```bash
bash scripts/chat-clipboard-policy-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-clipboard-policy
```

It keeps clipboard handling as local metadata: read, write, paste, copy,
import, export, transcript-copy, message-copy, and clipboard-backed
attachment gates remain disabled or blocked. No clipboard data, prompt
text, response text, transcript, message body, file data, model path,
runtime log, or artifact is read or written, no clipboard permission is
requested, no upload or import runs, no model/runtime path is started,
and no target access occurs.

The chat redaction-policy fixture records the disabled redaction and
content-scanning boundary used by the planned standalone chat surface:

```bash
bash scripts/chat-redaction-policy-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-redaction-policy
```

It keeps redaction handling as local metadata: redaction rule review,
content scan, PII detection, secret detection, prompt redaction, response
redaction, transcript redaction, message redaction, attachment redaction,
clipboard redaction, audit redaction, and result persistence remain
disabled, blocked, or not configured. No redaction rules, prompt text,
response text, transcript, message body, clipboard data, file data, audit
content, store content, model path, runtime log, private path, or artifact
is read or written, no detector runs, no redaction is applied, no result
is persisted, no model/runtime path is started, and no target access
occurs.

The chat attachment-policy fixture records the disabled local attachment
boundary used by the planned standalone chat surface:

```bash
bash scripts/chat-attachment-policy-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-attachment-policy
```

It keeps attachment handling as local metadata: file picker, file
metadata read, file content read, upload, import, preview, and persistence
gates remain disabled, blocked, or not configured. No file picker opens,
no file name, path, metadata, bytes, directory listing, clipboard data,
transcript, generated artifact, model path, runtime log, or artifact is
read or written, no upload is attempted, no import/export runs, no model
or runtime path is started, and no target access occurs.

The chat shortcut-map fixture records the disabled keyboard shortcut map
for the planned standalone chat surface:

```bash
bash scripts/chat-shortcut-map-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-shortcut-map
```

It keeps shortcuts as local metadata: focus composer, submit, stop, copy,
new chat, clear, export, attach, and message navigation bindings remain
disabled, blocked, inactive, unavailable, or planned. No keyboard
listener is installed, no key event is captured, no command is
dispatched, no focus change occurs, no prompt, session, transcript,
message, clipboard, or file content is read or written, no model/runtime
path is started, and no artifact is written.

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

The chat error taxonomy fixture records grouped blocked error metadata
for future chat banners, status rows, and recovery affordances:

```bash
bash scripts/chat-error-taxonomy-stub.sh --model gemma3n-e4b --target kv260
bash scripts/status-stub.sh --include-chat-error-taxonomy
```

It summarizes readiness blockers, model/runtime blockers, session and
policy blockers, and local-only/provider policy metadata as deterministic
data. It does not read prompts, responses, transcripts, configuration
files, provider settings, environment values, secrets, tokens, model
asset paths, session-store paths, logs, or artifacts. Recovery actions
remain disabled and side-effect-free.

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
- `no_external_dependency`: a planned local-only path records no cloud
  dependency
- `enforced_as_metadata`: policy state is present as fixture metadata,
  not as runtime enforcement code
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

The surface-layout states keep shell chrome separate from runtime,
message content, and local stores:

- `available_as_data`: layout or navigation metadata can be rendered
  from checked fixture data
- `blocked`: runtime readiness or content boundaries are missing
- `disabled`: composer, model, or readiness actions are intentionally
  unavailable
- `empty_not_captured`: transcript/message content is absent
- `not_configured`: no local session store exists
- `not_started`: no local chat runtime has started
- `placeholder`: deterministic local shell-region metadata only
- `summary_only`: footer/privacy metadata excludes actor and content
  identifiers

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

The response-stream states keep progress display separate from response
content, token data, runtime transport, and transcript storage:

- `available_as_data`: checked placeholder display data is available
  without executing anything
- `blocked`: a required send-result or runtime boundary is missing
- `disabled`: progress or cancellation controls are intentionally
  unavailable
- `inactive`: no launcher-owned session exists
- `not_configured`: no transcript/session store exists
- `not_generated`: no assistant response chunks have been produced
- `not_loaded`: model assets are not loaded
- `not_started`: no runtime transport or stream has started
- `requires_evidence`: future enablement requires evidence first
- `target_selected`: planned target identity can be displayed
- `unavailable`: token counts, stream completion, or response content
  are unavailable

The context-policy states keep context-window and context-assembly
metadata separate from prompt content, transcript content, token data,
summaries, and runtime handoff:

- `available_as_data`: checked context-policy metadata is available
  without executing anything
- `blocked`: a required tokenizer, context, transcript, summary, or
  runtime boundary is missing
- `disabled`: truncation or context-control behavior is intentionally
  unavailable
- `empty_not_captured`: no prompt draft is captured or stored
- `not_configured`: no context window, token budget, transcript store,
  or local context source exists
- `not_generated`: no summary or assistant output has been produced
- `requires_evidence`: future enablement requires runtime or context
  evidence first
- `summary_only`: display data excludes raw content, private paths, and
  token content

The action-bar states keep user-visible conversation controls separate
from session storage, transcripts, clipboard access, file access, runtime
transport, and message content:

- `available_as_data`: checked action metadata is available without
  executing anything
- `blocked`: a required lifecycle, transcript, send-result, or stream
  boundary is missing
- `disabled`: a visible control is intentionally unavailable
- `empty_not_captured`: no prompt, response, transcript, or message body
  content is present
- `inactive`: no launcher-owned chat session exists
- `not_configured`: no local store, retention rule, or export/redaction
  boundary exists
- `not_generated`: no assistant response exists for copy or retry
- `not_started`: no local response stream exists
- `planned`: described for a future reviewed boundary
- `placeholder`: deterministic local action-bar metadata only
- `unavailable`: action output is unavailable

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

The error-taxonomy states keep user-visible error grouping separate from
runtime execution, provider state, local stores, and message content:

- `available_as_data`: checked taxonomy data is available without
  executing anything
- `blocked`: a required readiness or execution boundary is missing
- `disabled`: a referenced action remains intentionally unavailable
- `external_not_configured`: user-provided model assets are not
  configured
- `inactive`: no runtime or target session exists
- `not_configured`: no local session store or policy boundary exists
- `not_loaded`: model assets are not loaded
- `not_started`: no local chat runtime has started
- `not_used`: provider paths are not part of core local chat
- `planned`: described for a future reviewed boundary
- `requires_evidence`: future enablement requires evidence first
- `summary_only`: display data excludes raw content and private paths
- `unavailable`: input content is not read or captured

## Coordination Boundary

The standalone chat surface depends on the existing launcher model
descriptor, readiness, and device/session status contracts. The
model-status contract adds reviewable display rows for model-load state.
The model-selection policy contract adds a disabled picker/catalog shape
without configuration reads, model catalog reads, model path reads, asset
path reads, provider fallback, selection persistence, runtime execution,
model loading, hardware access, or artifact access.
The context-policy contract adds a reviewable disabled context-window,
tokenization, transcript-context, summary, truncation, context assembly,
and runtime-handoff shape without prompt reads, transcript reads, token
counting, summary generation, model loading, runtime execution, provider
calls, target access, persistence, or artifact access.
The lifecycle contract adds a reviewable session-management shape, but
these contracts do not add runtime execution, model loading, provider
calls, persistence, target access, artifact reads, or artifact writes.
The model-load request contract adds a reviewable disabled load-request
shape without configuration reads, environment reads, model path reads,
asset path reads, weight reads, tokenizer reads, checksum manifest reads,
runtime preflight, model loading, model unloading, model warmup, model
execution, provider calls, hardware access, persistence, or artifact
access.
The readiness contract ties those display and lifecycle states into a
single checklist and recovery-action view without enabling any send,
load, restore, or export action.
The surface-layout contract adds a reviewable shell-region and
navigation map without starting an app shell, reading content, focusing
the composer, or enabling runtime/model/store actions.
The session-index contract adds a reviewable empty list/sidebar boundary
without enabling manifest reads, transcript reads, title capture,
restore, rename, delete, refresh, persistence, or artifact writes.
The session-store policy contract adds a reviewable disabled local store
policy shape without configuration reads, path reads, manifest reads,
session record reads, transcript reads, title reads, prompt/response reads,
store writes, deletion, migration, retention activation, artifact access,
runtime execution, model loading, provider calls, or target access.
The composer contract adds a reviewable input-control and validation
shape without prompt capture, prompt echo, prompt persistence, attachment
reads, clipboard access, or send enablement.
The send-result contract adds a reviewable blocked-result display shape
without prompt acceptance, prompt echo, response generation, runtime
execution, model loading, persistence, or writes.
The response-stream contract adds a reviewable disabled stream/progress
display shape without opening transport, generating response chunks,
counting tokens, sending cancellation signals, appending transcripts,
executing runtime code, loading models, provider calls, or target access.
The context-policy contract adds a reviewable disabled context-budget
and context-assembly shape without reading prompts, transcripts,
summaries, tokenizers, model paths, runtime logs, private paths, or
artifacts, and without token counting, truncation, context assembly,
summary generation, runtime handoff, model loading, provider calls, or
target access.
The transcript policy contract adds a reviewable retention/export
policy shape without message content, transcript persistence, summary
generation, artifact reads, artifact writes, runtime execution, model
loading, provider calls, or target access.
The audit-event contract adds a reviewable blocked event metadata shape
without prompt capture, prompt echo, response content, transcript
content, actor identifiers, runtime traces, audit persistence, artifact
reads, artifact writes, runtime execution, model loading, provider
calls, or target access.
The error taxonomy contract adds a reviewable grouped error-display shape
without prompt capture, response content, transcript content, provider
configuration reads, model asset reads, session-store reads, artifact
reads, artifact writes, runtime execution, model loading, provider calls,
or target access.
The action-bar contract adds a reviewable disabled control shape without
session creation, conversation clearing, transcript export, clipboard
writes, attachment reads, retry attempts, stop signals, runtime
execution, model loading, provider calls, artifact writes, or target
access.
The attachment-policy contract adds a reviewable disabled file-input
policy shape without opening pickers, reading file names, paths, metadata,
contents, directory listings, clipboard payloads, transcripts, generated
artifacts, model paths, runtime logs, artifact reads, uploads, imports,
persistence, runtime execution, model loading, provider calls, or target
access.

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
- response streaming, response chunk generation, token counting, stop
  signal delivery, or stream transport behavior
- context-window configuration, token-budget reads, tokenizer reads,
  prompt-context reads, transcript-context reads, summary reads,
  truncation, context assembly, runtime context handoff, or context data
  persistence
- action-bar execution, session creation, conversation clearing,
  transcript export, clipboard writes, retry attempts, stop signals, file
  attachment reads, or action persistence
- attachment-policy execution, file picker opening, file-name/path reads,
  file metadata reads, file content reads, directory scans, clipboard
  attachment reads, uploads, imports, previews, or persistence
- transcript retention, transcript export, local transcript storage,
  transcript summaries, or transcript message content
- audit logging, audit persistence, actor identifiers, event timestamps,
  runtime traces, raw logs, or audit export behavior
- error recovery execution, provider/config reads, model asset reads, or
  taxonomy persistence
- model-selection execution, model catalog reads, dynamic catalog
  discovery, model option reads from configuration, user selection
  acceptance, selection persistence, provider fallback, model path reads,
  asset path reads, model asset reads, or load-request handoff execution
- model-load request execution, configuration reads, environment reads,
  model path reads, asset path reads, weight reads, tokenizer reads,
  checksum manifest reads, runtime preflight, model loading, model
  unloading, model warmup, model execution, or load-request persistence
- session creation, restore, clear, close, or export behavior
- readiness recovery execution
- manifest, transcript, summary, or lifecycle artifact reads or writes
- session-store configuration, path, manifest, record, read, write,
  delete, retention, migration, compaction, rollback, import, or export
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
