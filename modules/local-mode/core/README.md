# Local mode core

The core layer is pure state and policy. It does not spawn processes, read
provider credentials, scan the full filesystem, or call network APIs.

Core responsibilities:

- normalize `LocalProject` metadata;
- decide whether the machine is offline from caller-supplied signals;
- decide whether sync controls are enabled from entitlement and offline state;
- produce `LocalBuild` plans for the selected local tool vendor;
- keep cloud backup optional, never a prerequisite for local synthesis.

Offline rules:

- local synthesis remains available when offline if a local tool and script are
  present;
- cloud sync is reported as paused while offline;
- chat provider calls are unavailable while offline unless the selected provider
  has a local runtime path in a later reviewed adapter;
- cached project metadata can be read from local storage.

Sync entitlement rule:

`SyncStatus.enabled` is true only when a paid entitlement is confirmed and the
user has opted in. Local synthesis and local deploy do not depend on sync.
