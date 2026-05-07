# ChatSession State Lifecycle

This note documents the planned launcher-side `ChatSession` state lifecycle
for the standalone chat surface. The current implementation is data-only:
it renders checked fixture state, but it does not create an active runtime
session, append message bodies, persist transcripts, or close a real model
session.

Current answer: **open is placeholder-only; append, persist, and close are
blocked, disabled, inactive, or not configured**.

The lifecycle boundary is represented by:

- `contracts/chat_session_contract.py`
- `contracts/chat_session_lifecycle_contract.py`
- `contracts/chat_message_list_contract.py`
- `contracts/chat_send_result_contract.py`
- `contracts/chat_response_stream_contract.py`
- `contracts/chat_transcript_policy_contract.py`
- `contracts/chat_session_store_policy_contract.py`
- `contracts/fixtures/chat-session.gemma3n-e4b-kv260-placeholder.json`
- `contracts/fixtures/chat-session-lifecycle.gemma3n-e4b-kv260-placeholder.json`

Raw lifecycle JSON is available with:

```bash
bash scripts/chat-session-lifecycle-stub.sh --model gemma3n-e4b --target kv260
```

The aggregate status surface can include the same data with:

```bash
bash scripts/status-stub.sh --include-chat-session
```

## State Model

The planned `ChatSession` lifecycle has four user-visible phases:

| Phase | Current fixture state | Meaning |
|---|---|---|
| Open | `placeholder` / `blocked` | The chat surface can render deterministic local fixture data, but no launcher-owned active session is created. |
| Append | `disabled` / `blocked` | User and assistant message append paths are described by contracts, but no prompt, response, stream chunk, token count, or transcript item is accepted or stored. |
| Persist | `not_configured` / `disabled` | Session store, transcript persistence, retention, title persistence, and export remain unavailable until explicit local storage and redaction boundaries exist. |
| Close | `inactive` | Close is a no-op because no active runtime session or launcher-owned transcript exists. |

These phases are documentation for the intended state machine. They are
not a claim that chat execution, prompt capture, transcript storage, or
model runtime teardown exists today.

## Open

Opening the chat surface consumes checked local fixtures and moves the
display from `inactive` to `placeholder`:

```text
inactive --open_chat_surface--> placeholder
```

The open phase may render target model, target board, readiness, empty
conversation, disabled controls, and lifecycle metadata. It must not
start runtime code, load model assets, touch KV260 hardware, call
providers, read a session store, or emit private paths.

Creating or restoring a real session remains blocked until all of these
boundaries are reviewed:

- runtime readiness evidence
- model-load evidence
- local session-store schema and retention policy
- session manifest restore rules

## Append

Append covers future mutations to the in-memory message list:

- user message accepted from the composer
- assistant response chunk appended from a response stream
- system notice appended by the launcher
- message order assigned within the active local session

The current checked fixtures do not perform any append. The message-list
contract reports an empty collection, the send-result contract reports a
blocked send path, and the response-stream contract reports disabled
streaming. Prompt bodies, response bodies, stream chunks, token counts,
and transcript entries remain absent from fixture data.

A future append transition must be session-scoped and monotonic:

```text
open_session --append_user_message--> dirty_session
dirty_session --append_assistant_message--> dirty_session
```

The transition cannot become enabled until prompt capture, response
capture, redaction, runtime handoff, stop/retry behavior, and transcript
mutation rules are reviewed.

## Persist

Persist covers future durable storage of session metadata and transcript
state. It is currently not configured:

- `chat_session_contract.py` reports transcript persistence as
  `not_configured`.
- `chat_session_lifecycle_contract.py` reports `storageState` as
  `not_configured`.
- `chat_session_store_policy_contract.py` keeps store path, manifest,
  read, write, delete, retention, and migration gates disabled.
- `chat_transcript_policy_contract.py` keeps transcript retention,
  export, and persistence unavailable.

A future persist transition must be explicit and local:

```text
dirty_session --persist_transcript--> clean_session
```

Before this transition exists, the launcher needs a reviewed local store
path policy, manifest schema, redaction policy, retention/delete rules,
rollback behavior, and user-controlled export behavior. Fixture data must
continue to avoid storing prompts, responses, transcripts, summaries,
model paths, private paths, secrets, tokens, or generated artifacts.

## Close

Close currently remains inactive:

```text
inactive --close_session--> inactive
```

Because no launcher-owned active session exists, closing the session is a
no-op. It does not flush transcripts, unload a model, stop a runtime,
write artifacts, clear a store, or mutate any prompt/response content.

A future close transition should separate three concerns:

- stop accepting new appends for the session
- finish or cancel any active response stream through reviewed runtime
  controls
- persist, discard, or export only according to explicit user policy

Close must not silently persist, delete, upload, or summarize a session.

## Handoff Rules

The lifecycle remains blocked until separate evidence closes the runtime,
model, session-store, transcript, redaction, and export boundaries. Until
then, launcher surfaces must preserve these invariants:

- no prompt or response body is included in checked fixtures
- no transcript, summary, manifest, title, model path, private path, or
  raw log is read or written
- no model is loaded and no runtime session is started
- no KV260 hardware, serial port, network path, provider, pccx-lab command,
  telemetry, upload, or write-back path is invoked
- close, clear, restore, export, and persist controls stay disabled,
  blocked, inactive, unavailable, or not configured
