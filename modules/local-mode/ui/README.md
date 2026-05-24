# Local mode UI

The UI layer binds local mode to desktop and editor surfaces without owning
tool execution.

## DesktopApp

- Shows local tool detection status.
- Lets the user choose a project root and synthesis script.
- Calls the local synthesis adapter only after explicit user action.
- Shows sync status as optional and entitlement-gated.
- Lets users configure provider chat credentials outside project records.

## IdeExtension

- Presents the same `LocalProject`, `SyncStatus`, and `LocalBuild` data.
- Offers VS Code and JetBrains command entries that call the CLI or launcher
  wrapper with fixed argument arrays.
- Does not build shell strings from editor text.
- Keeps local synthesis available when cloud sync is paused or offline.
