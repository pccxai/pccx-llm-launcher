# PCCX local mode module

This module is the desktop and editor boundary for local PCCX use. It keeps
project metadata, offline state, local build requests, and optional cloud sync
separate from the launcher UI.

Local mode means:

- synthesis uses the user's installed Vivado or Quartus toolchain;
- network access is not required for local synthesis;
- provider chat uses user-owned Claude, GPT, or Gemini credentials outside this
  repository;
- project and result sync is optional and gated by an entitlement check.

## Layout

- `interfaces/` defines `LocalProject`, `SyncStatus`, and `LocalBuild`.
- `core/` owns pure project state, sync decision, and offline detection logic.
- `adapters/` owns the local toolchain, filesystem, and cloud-sync boundaries.
- `ui/` maps the same module to DesktopApp and IDE extension surfaces.

## Boundaries

The launcher may render this module directly, but all tool execution stays in an
adapter. The UI must not build shell strings, read credentials, upload build
outputs by default, or silently fall back to cloud behavior when offline.
