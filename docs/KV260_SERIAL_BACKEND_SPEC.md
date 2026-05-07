# KV260 Serial Backend Spec

This document defines the implemented launcher-side
`KV260SerialConnection` backend for issue #72. It is a USB TTY serial
console backend for KV260 status checks and guarded target command
queries.

Current answer: **serial console access is implemented for explicit
status checks only**. It does not claim model execution, KV260 inference,
runtime readiness, bitstream readiness, performance, or release
stability.

Implementation references:

- `contracts/kv260_serial_connection.py`
- `scripts/tests/kv260_serial_connection_test.py`

## Scope

`KV260SerialConnection` implements the `KV260ConnectionProtocol` methods:

| Method | Behavior |
|---|---|
| `is_reachable()` | Opens a serial session, sends a newline, and returns whether a login, password, or shell prompt can be observed. |
| `kernel_uname()` | Logs in, runs `uname -a`, requires exit status `0`, and returns cleaned command output. |
| `xrt_present()` | Logs in and checks for XRT tooling or library files with a shell command. |
| `xmutil_listapps()` | Logs in, runs `xmutil listapps`, and returns non-empty output lines when the command exits `0`. |

The backend is intentionally narrow:

- USB TTY serial console only.
- No SSH, socket, HTTP, or provider path.
- No subprocess command execution on the host.
- No model load, runtime launch, inference request, telemetry upload, or
  write-back.
- No public status field, repr output, print output, or log output may
  expose raw environment values or credentials.

## Configuration

The backend reads configuration from a mapping passed to `from_env()` or
from the process environment when no mapping is supplied.

| Name | Required | Use |
|---|---:|---|
| `KVFPGA_TTY` | No | Explicit serial TTY override. When present, it is the first and only TTY candidate. |
| `KVFPGA_USER` | Yes for login and command methods | Login user name written to the serial console only after a login prompt is observed. |
| `KVFPGA_PASSWORD` | Yes for login and command methods | Login password written to the serial console only after a password prompt is observed. |
| `KVFPGA_HOST` | No | Ignored by this backend. Host/network access is out of scope. |

`from_env()` stores raw TTY, user, and password values in private fields
with `repr=False`. The public dataclass fields expose only presence
booleans:

- `tty_configured`
- `user_configured`
- `password_configured`

`is_configured()` returns `True` only when both user and password are
configured. TTY presence is not required for this boolean because the
backend can auto-detect a candidate TTY at open time.

## TTY Discovery

TTY discovery is deterministic:

1. If `KVFPGA_TTY` is set, return that path as the only candidate.
2. Otherwise, scan `/dev/serial/by-id` when it exists and keep entries
   whose file name contains `kv260`, case-insensitive.
3. Append sorted `/dev/ttyUSB*` paths.
4. De-duplicate while preserving order.

`detect_kv260_tty()` returns the first candidate or `None`.
`_open_serial()` raises `KV260SerialUnavailable` when no candidate exists.

## Serial Session Parameters

Default serial parameters are:

| Parameter | Value |
|---|---:|
| Baud rate | `115200` |
| Read timeout passed to pyserial | `0.1` seconds |
| Write timeout | `1.0` second |
| Prompt timeout | `4.0` seconds |
| Command timeout | `12.0` seconds |
| Read chunk size | `1024` bytes |

`_open_serial()` uses an injected `serial_factory` in tests. Without an
injected factory, it imports `serial` and opens `serial.Serial` with the
selected port, baud rate, read timeout, and write timeout. Missing
pyserial raises `KV260SerialUnavailable`.

## Prompt Framing

All launcher writes are bytes written to the serial session and flushed
when the session object provides `flush()`.

Line writes use UTF-8 encoding plus CRLF:

```text
<line>\r\n
```

Prompt reads accumulate bytes until a timeout. Prompt matching is
case-insensitive for login/password prompts and accepts prompts at the
start of a buffer or after a newline.

Recognized prompts:

| Prompt kind | Accepted shape |
|---|---|
| Login | A line ending in `login:` |
| Password | A line ending in `password:` |
| Shell | A line ending in `$` or `#`, with optional trailing spaces |

`_read_until_prompt()` returns:

- `"login"` plus the accumulated buffer for a login prompt.
- `"password"` plus the accumulated buffer for a password prompt.
- `"shell"` plus the accumulated buffer for a shell prompt.
- `None` plus the accumulated buffer after prompt timeout.

`is_reachable()` does not authenticate. It only opens the serial port,
sends CRLF, waits for any recognized prompt, closes the port, and returns
a boolean. It catches `OSError` and `KV260SerialError` and reports
unreachable as `False`.

## Login Flow

Authenticated methods enter the connection as a context manager.

The login sequence is:

1. Open the serial port.
2. Send CRLF to wake or redraw the console prompt.
3. Read until a recognized prompt or prompt timeout.
4. If the prompt is `login`, write the configured user as one CRLF
   terminated line and read the next prompt.
5. If the prompt is `password`, write the configured password as one CRLF
   terminated line and read the next prompt.
6. Require a final `shell` prompt.
7. Store the active serial session for command execution.

The flow also supports a console that is already logged in: if the first
recognized prompt is `shell`, no user or password line is written.

Login failure cases:

- Missing user or password raises `KV260SerialUnavailable`.
- Missing TTY or missing pyserial raises `KV260SerialUnavailable`.
- A prompt timeout or an unexpected final prompt raises
  `KV260SerialError`.
- Any exception during login closes the serial session before the
  exception is re-raised.

`logout()` writes `exit\r\n` when an active session exists, then closes
the serial session. The active session reference is cleared before the
write, so repeated logout calls are no-ops after the first close.

## Command Framing

Target commands are private backend commands selected by the launcher
code. This method is not a user-input shell execution boundary.

`_run_command(command)` requires an active serial session. It wraps the
command with a completion marker:

```text
<command>; printf '\n__PCCX_KV260_SERIAL_DONE__:%s\n' "$?"
```

The wrapper is written as a UTF-8 CRLF-terminated line. The target shell
runs the command, then prints the reserved marker plus the shell exit
status.

The reserved marker is:

```text
__PCCX_KV260_SERIAL_DONE__
```

The command reader accumulates serial bytes until it sees:

```text
__PCCX_KV260_SERIAL_DONE__:<decimal-exit-status>
```

The decimal status is parsed into `SerialCommandResult.exit_status`.
Output before the marker is cleaned into `SerialCommandResult.output`.

The marker is reserved for backend framing. Backend commands must not be
chosen so their normal output emits this marker before command
completion.

## Output Cleaning

Command output is decoded as UTF-8 with replacement for malformed bytes.
Carriage returns are removed. The cleaner drops:

- blank lines
- the exact command echo
- the echoed wrapped command line
- echoed lines containing the command, `printf`, and the reserved marker
- prompt-only lines ending in `$` or `#`

Remaining lines are right-trimmed and joined with `\n`. The cleaned
output is the only command output returned by public command helpers.
The completion marker and shell exit status are not returned as output.

## Error Handling

The error hierarchy is:

| Error | Meaning |
|---|---|
| `KV260SerialError` | Base serial backend failure. |
| `KV260SerialUnavailable` | A required local prerequisite is unavailable, such as TTY discovery, pyserial, or credentials. |

Specific behavior:

- `is_reachable()` converts `OSError` and serial backend errors into
  `False`.
- `kernel_uname()` raises `KV260SerialError` when `uname -a` exits
  non-zero.
- `xrt_present()` returns `True` only when the XRT probe command exits
  `0`; non-zero means `False`.
- `xmutil_listapps()` returns an empty tuple when `xmutil listapps` exits
  non-zero.
- `_run_command()` raises `KV260SerialError` if no active session exists,
  if reading times out, or if the completion marker is not observed.
- `_read_until_pattern()` raises `KV260SerialError` on command timeout.
- `_read_until_prompt()` returns `None` on prompt timeout so the caller
  can decide whether timeout means unreachable or failed login.

Sessions are closed in `finally` paths for reachability checks, failed
login attempts, and context manager exit.

## Standard Output And Logging Boundary

`KV260SerialConnection` does not print or log. It must not write raw TTY,
user, password, host, command output, or serial buffers to stdout or
stderr.

Tests may print skip reasons and a final success line, but they must not
print environment values. Documentation and user-facing status text may
name environment variable names only.

## Security And Privacy Boundary

The backend writes credentials only to the target serial session after
matching the expected prompts. It does not expose credentials through:

- dataclass repr output
- public status fields
- shell command output
- print statements
- logging calls
- JSON fixtures

Host values are not consumed for network access. `KVFPGA_HOST` is
explicitly ignored so this backend cannot silently switch from serial to
network transport.

## Contract Test Coverage

The checked tests cover:

- protocol compatibility and public configuration booleans
- raw environment value absence from repr output
- ignored host configuration
- explicit TTY override and discovery helper shape
- reachability for login and shell prompts
- login, command execution, command marker parsing, cleaned `uname`
  output, logout, and close behavior
- XRT and `xmutil listapps` command use
- graceful live-probe skips when no TTY, no pyserial, or no credentials
  are available
- source-level guards against unsupported host execution, network paths,
  credential leaks, and overclaim language

These tests are host-side contract checks. They do not prove KV260
runtime readiness or model execution.
