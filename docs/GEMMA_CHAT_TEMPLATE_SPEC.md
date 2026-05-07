# Gemma Chat Template Spec

This note documents the launcher-side `GemmaChatTemplate` formatter used
by the mock Gemma chat path. It is a string-formatting contract only: it
does not tokenize text, load Gemma assets, execute a runtime, contact
Hugging Face, call a provider, touch KV260 hardware, or validate model
quality.

The implementation lives in:

- `contracts/gemma_chat_template.py`
- `contracts/gemma_e2e_orchestrator.py`
- `scripts/tests/gemma_chat_template_test.py`
- `scripts/tests/gemma_e2e_orchestrator_test.py`

## Source

Canonical Gemma prompt formatting uses `user` and `model` roles with
`<start_of_turn>` and `<end_of_turn>` markers, and uses
`<start_of_turn>model\n` as the generation prefix.

Source URL:
https://ai.google.dev/gemma/docs/core/prompt-structure

The local formatter also records the Gemma 3N E4B IT model-template
source URL in `GEMMA3N_E4B_CHAT_TEMPLATE_URL`:

https://huggingface.co/google/gemma-3n-E4B-it/blob/main/chat_template.jinja

## Input Shape

`GemmaChatTemplate.format(messages, add_generation_prompt=True)` accepts
a non-empty sequence of either:

- `GemmaChatMessage(role="user", content="...")`
- mappings with `role` and `content` string fields

Supported input roles are:

- `system`
- `user`
- `assistant`
- `model`

`assistant` is rendered as Gemma's `model` role. A `system` message is
only supported as the first message. It is not rendered as a separate
Gemma turn; its stripped content is prepended to the first user turn,
followed by one blank line.

After the optional first `system` message, roles must alternate:

```text
user, assistant, user, assistant, ...
```

or:

```text
user, model, user, model, ...
```

Each message `content` value must be a string. The formatter strips
leading and trailing whitespace from message content before rendering.
Multimodal Hugging Face `content` lists are outside this launcher
contract.

## Rendered Format

Each completed turn is rendered as:

```text
<start_of_turn>{role}
{content}<end_of_turn>
```

The actual string includes a newline after `{role}` and another newline
after `<end_of_turn>`:

```text
<start_of_turn>{role}\n{content}<end_of_turn>\n
```

When `add_generation_prompt` is true, the final message must be a user
turn. The formatter appends an open model turn:

```text
<start_of_turn>model\n
```

That open model turn deliberately has no `<end_of_turn>` marker because
it is the prefix for generated model output.

If `bos_token` is configured on `GemmaChatTemplate`, it is prepended
before the first rendered turn. The default `bos_token` is the empty
string.

## Example: Single User Turn

Input:

```python
from contracts.gemma_chat_template import GemmaChatMessage, GemmaChatTemplate

formatted = GemmaChatTemplate().format(
    [GemmaChatMessage(role="user", content="What is Cramer's Rule?")]
)
```

Output:

```text
<start_of_turn>user
What is Cramer's Rule?<end_of_turn>
<start_of_turn>model
```

Escaped string form:

```python
"<start_of_turn>user\n"
"What is Cramer's Rule?<end_of_turn>\n"
"<start_of_turn>model\n"
```

## Example: System Instructions

Input:

```python
formatted = GemmaChatTemplate().format(
    [
        {"role": "system", "content": "You are concise."},
        {"role": "user", "content": " first "},
    ]
)
```

Output:

```text
<start_of_turn>user
You are concise.

first<end_of_turn>
<start_of_turn>model
```

The `system` text becomes part of the first user turn. It is separated
from the user prompt by a blank line.

## Example: Multi-Turn History

Input:

```python
formatted = GemmaChatTemplate().format(
    [
        GemmaChatMessage(role="user", content="first"),
        GemmaChatMessage(role="assistant", content="reply"),
        GemmaChatMessage(role="user", content="second"),
    ]
)
```

Output:

```text
<start_of_turn>user
first<end_of_turn>
<start_of_turn>model
reply<end_of_turn>
<start_of_turn>user
second<end_of_turn>
<start_of_turn>model
```

## Example: Completed Transcript

Set `add_generation_prompt=False` when the caller needs a closed
transcript instead of an open generation prefix.

Input:

```python
formatted = GemmaChatTemplate().format(
    [
        {"role": "user", "content": "first"},
        {"role": "model", "content": "reply"},
    ],
    add_generation_prompt=False,
)
```

Output:

```text
<start_of_turn>user
first<end_of_turn>
<start_of_turn>model
reply<end_of_turn>
```

## Rejection Rules

The formatter raises `GemmaChatTemplateError` when:

- `messages` is empty
- a mapping message lacks `role` or `content`
- a role is not one of `system`, `user`, `assistant`, or `model`
- no user message remains after an optional first `system` message
- turns do not alternate user/model after the optional first `system`
- `add_generation_prompt=True` and the final rendered turn is not `user`

It raises `TypeError` when message content is not a string.

## Boundary

This formatter is intentionally smaller than a full Hugging Face chat
template processor. It does not execute Jinja, inspect tokenizer
metadata, accept multimodal content lists, insert media sentinels, or
resolve model-specific assets. Future real-runtime integration should
compare this local string contract against the checked model tokenizer
and processor before claiming inference compatibility.
