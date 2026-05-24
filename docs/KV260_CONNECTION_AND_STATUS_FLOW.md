# KV260 Connection And Status Flow

This note defines the launcher-side device/session status panel and the
planned KV260 connection and launch flow. The implementation is data-only
and evidence-gated.

Current answer: **status is placeholder / blocked until required evidence
and target configuration exist**.

The implementation lives in:

- `contracts/device_session_status_contract.py`
- `contracts/fixtures/device-session-status.gemma3n-e4b-kv260.json`
- `scripts/device-session-status-stub.sh`
- `scripts/tests/device_session_status_contract_test.py`
- `scripts/tests/status-device-session.sh`

## What Is Implemented

The launcher now exposes a deterministic local status shape for:

- device connection status
- model load status
- session activity
- pccx-lab diagnostics handoff status
- runtime readiness status
- discovery paths for USB/serial hints, explicit network targets, and
  future serial-console use
- a gated connection and launch flow
- user-facing error taxonomy with remediation text

The status data is read-only. It does not probe hardware, open serial
ports, scan networks, attempt authentication, load model assets, invoke
pccx-lab, start runtime code, stream logs, upload telemetry, or write
artifacts.

## Status Panel

The status panel rows are:

| Row | Current state | Meaning |
|---|---|---|
| Device connection | `not_configured` | No KV260 target connection is configured by the fixture. |
| Model load | `not_loaded` | Gemma 3N E4B is a target descriptor only; no model assets are loaded. |
| Session activity | `inactive` | No launcher session is active and no log stream has started. |
| pccx-lab diagnostics | `available_as_placeholder` | Diagnostics handoff is read-only local data only. |
| Runtime readiness | `blocked` | Runtime, bitstream, board-smoke, and measurement evidence are still required. |

The terminal status surface can show this panel with:

```bash
bash scripts/status-stub.sh --include-device-session
```

Raw JSON is available with:

```bash
bash scripts/device-session-status-stub.sh --model gemma3n-e4b --target kv260
```

## KV260 Connection Quickstart

This quickstart is for the planned USB-serial connection path. It keeps
the current launcher boundary intact: status commands are still
read-only, and serial login / runtime start remain unavailable until the
reviewed backend and readiness evidence land.

### 1. Check the local status surface first

Run the checked local status before configuring target access:

```bash
bash scripts/status-stub.sh --include-device-session
bash scripts/device-session-status-stub.sh --model gemma3n-e4b --target kv260
```

The expected answer is still `not_configured` / `blocked`. Treat any
future connection work as setup for a reviewed backend, not as proof that
inference or board bring-up works.

### 2. Choose a tty without printing env values

List candidate serial devices, then choose one in your shell. Prefer a
stable `/dev/serial/by-id` symlink when it exists; use `/dev/ttyUSB*`
only when the by-id path is unavailable.

```bash
find /dev/serial/by-id -maxdepth 1 -type l -print 2>/dev/null
find /dev -maxdepth 1 -type c -name 'ttyUSB*' -print 2>/dev/null
```

Set `KVFPGA_TTY` without echoing the selected value back to the
terminal:

```bash
read -r -s -p 'KVFPGA_TTY: ' KVFPGA_TTY; printf '\n'
export KVFPGA_TTY
```

Use presence-only checks when confirming configuration:

```bash
[ -n "${KVFPGA_TTY:-}" ] && printf 'KVFPGA_TTY configured\n'
```

Do not run `env`, `printenv`, `set`, or shell traces while these values
are present unless output is redirected through a reviewed redaction
path.

### 3. Set serial login env vars

The planned USB-serial backend uses these environment variable names:

| Variable | Purpose | Notes |
|---|---|---|
| `KVFPGA_TTY` | Optional tty override | If unset, the backend may try reviewed tty auto-detection. |
| `KVFPGA_USER` | Serial-console user name | Required before login-style serial checks. |
| `KVFPGA_PASSWORD` | Serial-console credential | Required before login-style serial checks; never print or commit it. |
| `KVFPGA_HOST` | Not used by USB serial | The serial backend ignores this; the launcher must not scan or guess hosts. |

Read the user and credential silently, then export only the names:

```bash
read -r -s -p 'KVFPGA_USER: ' KVFPGA_USER; printf '\n'
read -r -s -p 'KVFPGA_PASSWORD: ' KVFPGA_PASSWORD; printf '\n'
export KVFPGA_USER KVFPGA_PASSWORD
```

Confirm only presence, not values:

```bash
[ -n "${KVFPGA_USER:-}" ] && printf 'KVFPGA_USER configured\n'
[ -n "${KVFPGA_PASSWORD:-}" ] && printf 'KVFPGA_PASSWORD configured\n'
```

### 4. Use the current mock / fixture fallback

If no tty is visible, `pyserial` is unavailable, or credentials are not
configured, stay on the board-less path. For the current branch, that
means the checked local fixtures:

```bash
bash scripts/status-stub.sh --include-device-session
bash scripts/runtime-readiness-stub.sh --model gemma3n-e4b --target kv260
```

For the planned mock backend, use named board-less scenarios such as
`happy_path`, `partial_apps`, or `xrt_missing` in tests. Do not create
fake `KVFPGA_*` values to force a mock path; select the mock explicitly
in the test harness so serial setup remains separate from fixture setup.

### 5. Clear the shell state after a session

When finished, clear the names from the current shell:

```bash
unset KVFPGA_TTY KVFPGA_USER KVFPGA_PASSWORD KVFPGA_HOST
```

## Flow Diagram

```text
open status panel
  -> select KV260 target
  -> run reviewed read-only discovery
  -> check explicit target access inputs
  -> check runtime readiness data
  -> show dry-run launch preview
  -> keep runtime start blocked until readiness evidence changes
  -> stream logs only after a real session exists
```

The current fixture stops before any side-effecting action. Runtime start
and log streaming remain blocked because required readiness evidence and
session state are absent.

## Discovery Paths

The planned discovery paths are:

- `usb_serial_hint`: read-only USB and serial enumeration as a local
  device hint.
- `network_host_target`: explicit target host configuration only; the
  launcher must not scan networks or guess hosts.
- `serial_console_target`: future explicit serial-console path after a
  reviewed boundary exists.

## Error Taxonomy

| Error | Stage | Current state | Suggested remediation |
|---|---|---|---|
| `kv260_device_not_detected` | discovery | `planned` | Check power, cabling, and selected discovery path, then rerun a read-only status refresh. |
| `target_access_not_configured` | authentication | `requires_configuration` | Configure the target host and access method through a future explicit settings surface. |
| `authentication_not_available` | authentication | `planned` | Keep connection controls disabled until the authentication boundary is implemented and tested. |
| `runtime_evidence_missing` | readiness | `blocked` | Wait for checked runtime evidence before enabling start controls. |
| `model_assets_not_configured` | model | `ready_for_inputs` | Keep model asset selection explicit and outside repository fixtures. |
| `bitstream_evidence_missing` | readiness | `blocked` | Keep launch controls gated until lower-layer evidence is available. |
| `lab_diagnostics_unavailable` | diagnostics | `available_as_placeholder` | Use the explicit pccx-lab CLI/core validator when that integration is requested. |
| `session_inactive` | session | `inactive` | Show session controls as disabled until the readiness gate changes. |
| `log_stream_not_started` | logs | `not_started` | Show logs as pending rather than empty success. |

Every error carries a claim boundary in the JSON fixture so the launcher
can show a clear user message without implying runtime, hardware, or
performance success.

## Safety Notes

This status surface does not add:

- KV260 runtime execution
- USB, serial, network, SSH, or authentication commands
- model loading or model weight paths
- pccx-lab invocation
- systemverilog-ide invocation
- provider calls
- telemetry, upload, or write-back
- release or tag behavior
- MCP, LSP, marketplace, or versioned compatibility behavior

The connection and launch flow remains a gated plan until checked
readiness evidence exists.
