# PCCX Launcher Quickstart

This guide verifies the public launcher scaffold from a clean checkout.

## Requirements

- Bash
- Python 3.9 or newer

## Run The Local Checks

```bash
bash scripts/check.sh
bash scripts/status-stub.sh
bash scripts/runtime-readiness-stub.sh --model gemma3n-e4b --target kv260
bash scripts/device-session-status-stub.sh --model gemma3n-e4b --target kv260
```

## Preview The Chat Surface

```bash
bash scripts/chat-surface-preview.sh --model gemma3n-e4b --target kv260
```

The preview renders checked local contract data only. It does not accept
prompts, execute a model, contact providers, touch hardware, read model assets,
or write transcripts.

## Run The Smoke Test

```bash
bash scripts/smoke.sh
```

## Next Files

- [README.md](./README.md) for product scope and the full script inventory
- [CONTRIBUTING.md](./CONTRIBUTING.md) for pull request expectations
- [SECURITY.md](./SECURITY.md) for vulnerability reporting
- [docs/RELEASE.md](./docs/RELEASE.md) for release operator steps
