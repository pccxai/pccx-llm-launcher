#!/usr/bin/env python3
"""Data-only launcher/IDE status contract placeholder.

The contract is intentionally static. It describes planned boundaries for
future editor consumers without starting a launcher, probing hardware, or
reading local user configuration.
"""

from __future__ import annotations

import copy
import json
import sys


SCHEMA_VERSION = "pccx.launcherIdeStatus.v0"

_CONTRACT = {
    "schemaVersion": SCHEMA_VERSION,
    "launcherMode": "placeholder",
    "configuredTarget": {
        "id": "not_configured",
        "label": "not_configured",
        "source": "default_placeholder",
    },
    "targetKind": "not_configured",
    "availabilityState": "unavailable",
    "runtimeState": "planned",
    "modelState": "not_configured",
    "evidenceState": "evidence_required",
    "supportedOperations": [
        {
            "id": "launcher.status.local",
            "label": "local launcher status",
            "state": "placeholder",
            "execution": "data_only",
            "futureConsumerCommand": "pccxLauncher.showStatus",
        },
        {
            "id": "model.runtime.descriptor",
            "label": "model/runtime descriptor availability",
            "state": "planned",
            "execution": "data_only",
            "futureConsumerCommand": "pccxLauncher.showModelRuntimeDescriptor",
        },
        {
            "id": "device.session.status",
            "label": "device/session status placeholder",
            "state": "placeholder",
            "execution": "data_only",
            "futureConsumerCommand": "pccxLauncher.showDeviceSessionStatus",
        },
        {
            "id": "pccxlab.diagnostics.handoff",
            "label": "pccx-lab diagnostics handoff placeholder",
            "state": "planned",
            "handoffMode": "read_only_handoff",
            "lowerBoundary": "pccx-lab CLI/core",
            "futureConsumerCommand": "pccxLauncher.exportDiagnosticsForLab",
        },
        {
            "id": "editor.bridge.consumer",
            "label": "future editor bridge consumer",
            "state": "planned",
            "execution": "data_only",
            "futureConsumerCommand": "pccxLauncher.prepareEditorBridgeStatus",
        },
        {
            "id": "local.workflow.consumer",
            "label": "local workflow mode consumer",
            "state": "planned",
            "execution": "disabled_by_default",
            "futureConsumerCommand": "pccxLauncher.prepareLocalCodingAssistantStatus",
        },
    ],
    "safetyFlags": {
        "dataOnly": True,
        "disabledByDefault": True,
        "executesLauncher": False,
        "touchesHardware": False,
        "kv260Access": False,
        "modelExecution": False,
        "networkCalls": False,
        "providerCalls": False,
        "mcpServerImplemented": False,
        "lspImplemented": False,
        "marketplaceFlow": False,
        "shellExecution": False,
        "rawLogsIncluded": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "modelWeightPathsIncluded": False,
    },
    "diagnosticsHandoff": {
        "state": "planned",
        "mode": "read_only_handoff",
        "lowerBoundary": "pccx-lab CLI/core",
        "automaticUpload": False,
        "writeBack": False,
        "rawLogsIncluded": False,
    },
    "futureConsumers": [
        "pccx-systemverilog-ide",
        "future editor integration consumer",
        "local workflow mode, planned",
    ],
    "limitations": [
        "No launcher runtime call is performed by this contract.",
        "No KV260 run is claimed by this contract.",
        "No AI provider integration is implemented by this contract.",
        "No MCP, LSP, packaging, or marketplace flow is implemented by this contract.",
        "Evidence is required before hardware or performance claims.",
        "The contract shape may change before a versioned compatibility commitment.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#4",
        "pccxai/pccx-llm-launcher#3",
        "pccxai/pccx-llm-launcher#5",
        "pccxai/pccx-llm-launcher#12",
    ],
}


def create_launcher_ide_status_contract() -> dict:
    """Return a defensive copy of the placeholder contract."""
    return copy.deepcopy(_CONTRACT)


def contract_json(contract: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        contract if contract is not None else create_launcher_ide_status_contract(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def main() -> int:
    sys.stdout.write(contract_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
