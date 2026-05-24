# Desktop Installer Distribution Boundary

This document defines the first checked boundary for a PCCX Launcher desktop
installer across macOS, Windows, and Linux. The preferred shell is Tauri with a
Rust backend. Electron stays a fallback option only if the Tauri path cannot
cover a reviewed requirement.

The current repository snapshot still keeps this as a deterministic contract.
It does not add a Tauri app tree, build packages, publish releases, execute an
updater, run Vivado or Quartus, run synthesis, upload artifacts, read
credentials, or start launcher runtime code.

## Checked Surface

- `contracts/desktop_installer_distribution_contract.py`
- `contracts/fixtures/desktop-installer-distribution.multi-os-placeholder.json`
- `scripts/desktop-installer-distribution-stub.sh`
- `scripts/tests/desktop_installer_distribution_contract_test.py`

Run the checked fixture locally:

```bash
bash scripts/desktop-installer-distribution-stub.sh
python3 scripts/tests/desktop_installer_distribution_contract_test.py
```

## Module Boundary

The installer path is split into small reviewed modules:

- Desktop shell: Tauri UI, windows, menus, download-page entry point, and update
  prompts.
- Rust backend: validated local metadata and explicit command handoff.
- Installer packaging: per-platform package formats, signing metadata, checksum
  metadata, and release manifest records.
- Download page: user-facing artifact selection backed by signed release
  metadata.
- Updater: opt-in update prompts backed by signed update metadata.
- BYOL detector: Vivado and Quartus capability summary for user-owned toolchains.
- Local synthesis bridge: separate reviewed command boundary after BYOL
  detection.
- Cloud sync bridge: separate reviewed sync boundary after consent, credential,
  redaction, and conflict gates.

## Platform Targets

The contract records these host targets:

| Host | Planned package formats |
|---|---|
| macOS | `dmg`, `app` |
| Windows | `msi`, `exe` |
| Linux | `appimage`, `deb`, `rpm` |

Each package needs platform signing metadata and checksum metadata before the
download page should promote it. macOS also needs notarization metadata.

## Download Page

The download page should be metadata-driven:

1. Read reviewed release manifest metadata.
2. Show the matching host package.
3. Show checksum and signature state before download.
4. Link the user to manual package download until automatic updates have a
   reviewed signed-manifest path.

The download page is not the artifact source of truth. Release artifacts and
their checksums remain the reviewed source.

## Automatic Update Gate

Automatic update behavior is recorded as planned and gated:

- user opt-in is required;
- signed update metadata is required;
- package signature checks are required;
- downgrade behavior is blocked;
- update execution remains blocked until a separate implementation PR adds the
  reviewed updater path.

## BYOL Toolchain Detection

Vivado and Quartus are treated as BYOL dependencies. The detector boundary may
later summarize:

- toolchain name;
- version;
- edition;
- basic capability metadata.

The detector must not read license contents, credential values, tokens,
environment secret values, project contents, synthesis logs, or generated
artifacts. It must not run synthesis. The first implementation should keep
toolchain discovery local and explicit.

## Local Synthesis And Cloud Sync

Local synthesis is a separate command boundary. It needs:

- a user-selected project boundary;
- BYOL Vivado or Quartus detection first;
- a reviewed invocation policy;
- artifact and log redaction gates.

Cloud sync is a separate sync boundary. It needs:

- explicit user action;
- reviewed credential handling;
- artifact and log redaction;
- manual conflict review before remote overwrite.

This installer boundary only describes the handoff points.
