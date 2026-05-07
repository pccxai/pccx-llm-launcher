# Clean-Room Install

This is the current contributor install path for a fresh checkout. It installs
the repository in editable mode and runs the mock-only end-to-end smoke path.

The mock path does not install runtime dependencies, download model assets,
contact KV260 hardware, call providers, or run inference. It only exercises the
checked local launcher stubs that are available in this repository today.

## Prerequisites

- `git`
- `python3` with `venv`
- `bash`

## Fresh Clone

```bash
git clone https://github.com/pccxai/pccx-llm-launcher.git
cd pccx-llm-launcher
```

## Editable Install

Use a virtual environment so the editable install stays isolated from the host
Python environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Mock E2E Smoke

Run the checked mock path from the repository root:

```bash
bash scripts/tests/mock-e2e.sh
```

The mock e2e script runs:

- host and device-hint probes
- install-flow preview
- launcher status summaries
- dry-run launch preview
- dry-run chat stub

All commands stay local and read-only except for normal process output.
