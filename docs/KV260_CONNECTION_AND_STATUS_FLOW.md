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
