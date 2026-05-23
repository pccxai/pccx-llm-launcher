# Local mode adapters

Adapters are the only layer allowed to touch external systems.

## `local-vivado`

- Detects `PCCX_VIVADO_BIN` first, then `vivado` on `PATH`.
- Runs a user-selected Tcl script with `vivado -mode batch -source <script>`.
- Does not download inputs or upload results.

## `local-quartus`

- Detects `PCCX_QUARTUS_SH_BIN` first, then `quartus_sh` on `PATH`.
- Runs a user-selected Tcl script with `quartus_sh -t <script>`.
- Does not download inputs or upload results.

## `local-fs`

- Reads and writes local project metadata, build logs, and build artifacts.
- Must not read credential files or hidden agent instruction files.

## `cloud-sync`

- Syncs project/library metadata and selected build artifacts only after user
  opt-in and entitlement confirmation.
- Supports Drive or PCCX cloud storage backends.
- Must not block local synthesis when offline or not entitled.
