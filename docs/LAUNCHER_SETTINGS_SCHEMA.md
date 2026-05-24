# Launcher Settings Schema

`LauncherConfig` reads launcher settings from a flat TOML file. The
default config path is:

```text
~/.config/pccx-launcher/config.toml
```

The loader treats TOML values as authoritative. If a supported field is
missing from TOML, the loader can fill that field from its matching
environment variable. After TOML plus environment fallback are merged,
all fields are required.

Source: `contracts/launcher_config.py` defines `DEFAULT_CONFIG_PATH`,
`CONFIG_FIELDS`, `ENV_VARS`, `LOG_LEVELS`, `LOG_LEVEL_ALIASES`, and
`MAX_BAUD`; `LauncherConfig.from_sources()` raises an error when any
required field is missing after TOML and environment fallback are merged.

## Example

```toml
tty_path = "/dev/ttyUSB0"
baud = 115200
capture_dir = "~/.local/share/pccx-launcher/captures"
history_dir = "~/.local/share/pccx-launcher/history"
log_level = "INFO"
```

## Fields

| TOML field | Environment fallback | Type |
|---|---|---|
| `tty_path` | `PCCX_LAUNCHER_TTY_PATH` | String path |
| `baud` | `PCCX_LAUNCHER_BAUD` | Integer |
| `capture_dir` | `PCCX_LAUNCHER_CAPTURE_DIR` | String path |
| `history_dir` | `PCCX_LAUNCHER_HISTORY_DIR` | String path |
| `log_level` | `PCCX_LAUNCHER_LOG_LEVEL` | String |

## Defaults

`LauncherConfig` has one built-in default: the config file path is
`~/.config/pccx-launcher/config.toml` when no explicit path is supplied.

The individual settings fields do not have built-in value defaults:

| Field | Built-in default value | Source |
|---|---|---|
| `tty_path` | None; required from TOML or `PCCX_LAUNCHER_TTY_PATH` | `CONFIG_FIELDS`, `ENV_VARS`, `LauncherConfig.from_sources()` |
| `baud` | None; required from TOML or `PCCX_LAUNCHER_BAUD` | `CONFIG_FIELDS`, `ENV_VARS`, `LauncherConfig.from_sources()` |
| `capture_dir` | None; required from TOML or `PCCX_LAUNCHER_CAPTURE_DIR` | `CONFIG_FIELDS`, `ENV_VARS`, `LauncherConfig.from_sources()` |
| `history_dir` | None; required from TOML or `PCCX_LAUNCHER_HISTORY_DIR` | `CONFIG_FIELDS`, `ENV_VARS`, `LauncherConfig.from_sources()` |
| `log_level` | None; required from TOML or `PCCX_LAUNCHER_LOG_LEVEL` | `CONFIG_FIELDS`, `ENV_VARS`, `LauncherConfig.from_sources()` |

Validation constants are not value defaults. `baud` must be in
`1..4000000`, `log_level` must be one of `DEBUG`, `INFO`, `WARNING`,
`ERROR`, or `CRITICAL`, and `WARN` is normalized to `WARNING`; these
rules come from `MAX_BAUD`, `LOG_LEVELS`, and `LOG_LEVEL_ALIASES` in
`contracts/launcher_config.py`.

`tty_path`
: Serial device path used by launcher-side target access. The value must
  be a non-empty string path, and `~` is expanded.

`baud`
: Serial baud rate. The value must be an integer in `1..4000000`.
  Environment values may be decimal strings. Booleans are rejected.

`capture_dir`
: Directory reserved for launcher capture output. The value must be a
  non-empty string path, and `~` is expanded.

`history_dir`
: Directory reserved for launcher history output. The value must be a
  non-empty string path, and `~` is expanded.

`log_level`
: Launcher logging threshold. The value is case-insensitive. Accepted
  values are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`; `WARN`
  is normalized to `WARNING`.

## Precedence

For each field, the loader resolves values in this order:

1. Use the field from `config.toml` when present.
2. Use the matching environment variable only when the TOML field is
   absent.
3. Report a missing required field if neither source provides a value.

A TOML value cannot be overridden by environment for the same field.

## TOML Shape

The settings file is a single flat table. Nested tables are not part of
the schema.

Valid:

```toml
tty_path = "/dev/ttyUSB0"
baud = 115200
capture_dir = "~/captures"
history_dir = "~/history"
log_level = "info"
```

Invalid:

```toml
[serial]
tty_path = "/dev/ttyUSB0"
baud = 115200
```

Unknown fields are rejected instead of ignored. This keeps misspelled
settings from silently falling back to environment values.

## Path Handling

`tty_path`, `capture_dir`, and `history_dir` are parsed as string paths.
Leading and trailing whitespace is stripped before validation, and `~`
is expanded to the current user's home directory. Empty strings and
strings containing a NUL byte are invalid.

The loader validates path syntax only. It does not create directories,
open serial devices, write captures, write history, or check device
availability while parsing settings.

## Error Behavior

Invalid TOML syntax, a config path that points to a directory, unknown
fields, nested tables, missing required fields, and invalid field values
raise a launcher config error.

Error messages identify the affected field name or environment variable
name, but they do not echo environment variable values. This prevents
secrets, local paths, or device names supplied through the environment
from being reflected in logs or terminal output.
