# PCCX local desktop mode

Local desktop mode lets users run PCCX workflows on their own machine without a
cloud dependency.

## Scope

- Launcher: local synthesis wrapper, tool detection, desktop state display.
- CLI: `pccx synth --local` and `pccx deploy --target kv260` consume the same
  local-mode concepts.
- IDE: VS Code and JetBrains surfaces call the launcher or CLI boundary with
  fixed argument arrays.
- Sync: optional project, library, and build-result backup after entitlement
  confirmation.

## BYOL and tool detection

BYOL means bring your own local toolchain. The launcher never bundles Vivado or
Quartus. Detection order is:

1. `PCCX_VIVADO_BIN` or `PCCX_QUARTUS_SH_BIN`.
2. `vivado` or `quartus_sh` on `PATH`.
3. A user-selected executable path in the desktop settings UI.

Local synthesis must work offline when the selected tool, project files, and
synthesis script are already on the machine.

## Chat provider boundary

AI chat uses user-owned Claude, GPT, or Gemini credentials. Credentials stay in
the user's OS keychain, environment, or provider-specific config, and local-mode
project records must never serialize secret values. Offline behavior is clear:
local synthesis remains available, provider chat is unavailable unless a later
local runtime adapter is selected.

## Sync boundary

Cloud sync is optional. A paid entitlement and explicit user opt-in are both
required before sync is enabled.

Sync can cover:

- project metadata;
- reusable libraries;
- selected synthesis logs and result artifacts.

Sync must not cover:

- provider credentials;
- private local paths in shared records;
- hidden agent instructions;
- raw build caches by default.

## Execution boundary

UI code renders state and sends fixed commands. Adapter code owns process
execution. The wrapper in `scripts/local-synth.sh` requires a local script path
and only calls a vendor tool when `--run` is passed.
