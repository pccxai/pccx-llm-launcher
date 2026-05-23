# Local mode interfaces

These interfaces are the shared contract for Launcher, CLI, and IDE consumers.

```ts
export type LocalToolVendor = "vivado" | "quartus";
export type LocalBuildState =
  | "draft"
  | "tool_missing"
  | "ready"
  | "running"
  | "succeeded"
  | "failed";

export interface LocalProject {
  id: string;
  root: string;
  topModule?: string;
  target?: "kv260" | string;
  preferredVendor?: LocalToolVendor;
  syncEnabled: boolean;
  entitlementRequired: boolean;
}

export interface SyncStatus {
  enabled: boolean;
  entitled: boolean;
  offline: boolean;
  provider: "none" | "drive" | "pccx-cloud";
  lastSuccessfulSyncAt?: string;
  pendingLocalChanges: number;
}

export interface LocalBuild {
  id: string;
  projectId: string;
  vendor: LocalToolVendor;
  toolPath?: string;
  scriptPath: string;
  workDir: string;
  state: LocalBuildState;
  artifactPaths: string[];
  logPath?: string;
}
```

Interface rules:

- `LocalProject.root`, `scriptPath`, and `workDir` are local paths only.
- `SyncStatus.enabled` must be false unless entitlement is confirmed.
- `LocalBuild.toolPath` is discovered from the user's machine or explicit env.
- Secret values are never serialized into these records.
