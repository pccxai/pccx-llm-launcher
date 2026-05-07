# Chat UI Redesign Brief

This brief records a potential redesign direction for the standalone chat
surface. It is a planning document only. It does not change launcher UI code,
enable chat controls, start a runtime, read prompts, persist transcripts, load
model assets, call providers, invoke pccx-lab, or touch KV260 hardware.

Current answer: **brief only / no UI implementation change**.

The current chat surface remains governed by
[`STANDALONE_CHAT_SESSION_CONTRACT.md`](./STANDALONE_CHAT_SESSION_CONTRACT.md)
and the checked data-only fixtures under `contracts/fixtures/`.

## Context

The launcher now has a blocked standalone chat surface boundary, pccx-UI theme
assets, and a read-only shell preview. Those pieces are useful enough to discuss
the next product shape, but they are not enough to enable a real chat workflow.
Runtime readiness, model loading, prompt capture, transcript policy, session
storage, redaction, clipboard, attachment, accessibility, and review evidence
remain separate gates.

The redesign should make the launcher feel like an operational local inference
tool rather than a marketing page or generic chat clone. The first real chat
view should help a user answer four questions quickly:

- Which target and model am I looking at?
- Why is chat available, degraded, or blocked?
- What action can I safely take next?
- What local data will be read, written, or retained if I proceed?

## Design Goals

- Keep target, model, runtime, and readiness state visible without forcing users
  to leave the conversation view.
- Make blocked states explicit and reviewable instead of hiding disabled
  controls behind generic empty UI.
- Preserve local-only expectations: no cloud fallback, telemetry, provider call,
  automatic upload, or hidden hardware action.
- Treat the chat transcript as the primary work area once enabled, with status
  and diagnostics as supporting surfaces.
- Use the existing pccx-UI brand tokens and launcher shell conventions rather
  than introducing a separate visual system.
- Support future editor and diagnostics handoff without making the chat view
  responsible for pccx-lab analysis logic.

## Non-Goals

- No implementation in this branch.
- No HTML, CSS, JavaScript, script, fixture, or contract behavior change.
- No model catalog, model picker, runtime adapter, session store, transcript
  database, or hardware probe.
- No benchmark, throughput, timing, KV260 readiness, or end-to-end inference
  claim.
- No provider fallback, network dependency, telemetry, or upload flow.
- No compatibility promise for a final UI API.

## Proposed Surface Shape

The future chat surface should keep the launcher shell dense and task-oriented:

- **Header:** model, target, runtime readiness, local-only indicator, and a
  single primary action that reflects the current gate.
- **Left rail:** session index once storage exists; before that, a compact
  blocked/empty session area sourced from the session-index boundary.
- **Main region:** transcript/message list. While blocked, it should show the
  empty-state explanation from checked metadata, not sample user content.
- **Composer:** disabled until prompt capture, send-result, redaction, and
  transcript policies are reviewed together.
- **Right/detail region:** readiness, model status, evidence, and diagnostics
  handoff summaries. This should stay secondary to the transcript but visible
  enough for blocked-state triage.
- **Footer/status strip:** local-only, retention, audit, and safety summaries in
  compact text or status chips.

The design should avoid a decorative hero, oversized cards, or onboarding copy
as the first screen. The useful application state should be visible immediately.

## State Model

The UI should render from explicit state boundaries rather than inferring
availability from missing data.

| User-visible state | Required backing boundary | Expected behavior |
|---|---|---|
| Chat blocked | `chat_readiness`, `chat_model_status`, `runtime_readiness` | Show why chat cannot start and what evidence is missing. |
| Empty local session | `chat_session_index`, `chat_message_list`, `chat_empty_state` | Show no transcript content and no generated placeholders. |
| Composer disabled | `chat_composer`, `chat_send_result`, `chat_redaction_policy` | Keep focus and send unavailable until prompt capture is reviewed. |
| Model not loaded | `chat_model_load_request`, `chat_model_selection_policy` | Show target metadata without reading model paths or assets. |
| Local-only enforced | `chat_local_only_policy` | Make cloud/provider fallback unavailable and visible. |
| Transcript disabled | `chat_transcript_policy`, `chat_session_store_policy` | Show retention/export state without reading or writing transcript data. |
| Diagnostics available | `diagnostics_handoff`, `launcher_ide_status` | Offer read-only handoff summaries without running pccx-lab implicitly. |

## Privacy And Safety Requirements

The redesign should keep the current conservative defaults:

- Prompt and response content must not appear in blocked fixtures or previews.
- Disabled controls must remain visibly disabled and non-dispatching.
- Clipboard, attachment, export, copy, retry, stop, clear, and session actions
  need explicit policy review before they become active.
- Any future transcript persistence must show retention, storage location,
  exportability, and deletion behavior before the first write.
- Provider calls, cloud fallbacks, network scans, and telemetry must remain
  absent unless a later reviewed policy explicitly changes that stance.
- Hardware access and pccx-lab execution must stay behind explicit user action
  and reviewed lower-boundary contracts.

## Suggested Implementation Phases

1. **Read-only composition:** render the full blocked surface from existing
   checked fixtures, keeping all actions inert.
2. **State-driven shell:** connect the shell to status summaries while
   preserving data-only boundaries and fixture-backed tests.
3. **Reviewed local input:** enable composer focus only after prompt capture,
   redaction, send-result, audit, and transcript policy gates are approved.
4. **Session persistence:** add session index, retention, export, rename, clear,
   and deletion behavior after storage policy and tests exist.
5. **Runtime handoff:** enable model load and send only after runtime readiness,
   target evidence, diagnostics, and failure handling are reviewed.

Each phase should be reviewable independently and should leave blocked states
honest when later gates are incomplete.

## Review Checklist For A Future UI PR

- The PR states whether it is read-only, interactive, or runtime-enabled.
- The UI reads from explicit contract data or reviewed runtime boundaries.
- Disabled controls have no hidden dispatch path.
- Prompt, response, transcript, file, clipboard, and model-path data handling is
  covered by tests.
- Local-only behavior is visible and enforced.
- Empty and blocked states do not contain sample private content.
- Accessibility covers landmarks, focus order, disabled controls, live-region
  behavior, keyboard access, contrast, and reduced motion.
- Failure states explain next steps without claiming unsupported hardware or
  model readiness.

## Open Questions

- Should the first enabled chat surface keep diagnostics visible in a right rail,
  or move diagnostics into a drawer to leave more room for transcripts?
- Which state transition should unlock composer focus: runtime readiness alone,
  or runtime readiness plus transcript/redaction/audit review?
- How much model-selection UI is needed while Gemma 3N E4B on KV260 is the only
  named target?
- Should transcript persistence be opt-in per session, global with per-session
  override, or disabled until a later storage milestone?
- What is the minimum evidence packet required before the launcher can present a
  non-blocked local chat state?
