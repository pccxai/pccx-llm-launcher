#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only device/session status contract for the planned KV260 path.

The contract describes status-panel rows, discovery paths, a gated connection
and launch flow, and user-facing errors without probing hardware, opening a
serial or network connection, loading models, invoking pccx-lab, or starting
runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.deviceSessionStatus.v0"

STATUS_FIELDS = (
    "schemaVersion",
    "statusId",
    "fixtureVersion",
    "lastUpdatedSource",
    "targetDevice",
    "targetBoard",
    "targetModel",
    "statusAnswer",
    "connectionState",
    "discoveryState",
    "authenticationState",
    "runtimeState",
    "modelLoadState",
    "sessionState",
    "logStreamState",
    "diagnosticsState",
    "readinessState",
    "statusPanel",
    "discoveryPaths",
    "connectionLaunchFlow",
    "errorTaxonomy",
    "pccxLabDiagnostics",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

PANEL_ROW_FIELDS = (
    "rowId",
    "label",
    "state",
    "summary",
    "nextAction",
)

DISCOVERY_PATH_FIELDS = (
    "pathId",
    "transport",
    "state",
    "summary",
    "suggestedUserAction",
)

FLOW_STEP_FIELDS = (
    "stepId",
    "order",
    "stage",
    "state",
    "userAction",
    "launcherAction",
    "statusPanelUpdate",
    "sideEffectPolicy",
)

ERROR_FIELDS = (
    "errorId",
    "stage",
    "severity",
    "state",
    "userMessage",
    "suggestedRemediation",
    "claimBoundary",
)

DEVICE_SESSION_STATE_VALUES = (
    "target",
    "planned",
    "placeholder",
    "not_configured",
    "not_started",
    "requires_configuration",
    "ready_for_inputs",
    "blocked",
    "inactive",
    "not_loaded",
    "available_as_placeholder",
    "future_only",
)

_DEVICE_SESSION_STATUS = {
    "schemaVersion": SCHEMA_VERSION,
    "statusId": "device_session_status_gemma3n_e4b_kv260_placeholder",
    "fixtureVersion": "device-session-status.gemma3n-e4b-kv260.2026-05-03",
    "lastUpdatedSource": "pccx_launcher_issues_2_10_boundary_2026-05-03",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetModel": "gemma3n-e4b",
    "statusAnswer": "device_session_status_placeholder_blocked",
    "connectionState": "not_configured",
    "discoveryState": "not_started",
    "authenticationState": "not_configured",
    "runtimeState": "planned",
    "modelLoadState": "not_loaded",
    "sessionState": "inactive",
    "logStreamState": "not_started",
    "diagnosticsState": "available_as_placeholder",
    "readinessState": "blocked",
    "statusPanel": [
        {
            "rowId": "device_connection",
            "label": "device connection",
            "state": "not_configured",
            "summary": "No KV260 target connection is configured by this fixture.",
            "nextAction": "Run a read-only status check after a target is explicitly configured.",
        },
        {
            "rowId": "model_load",
            "label": "model load",
            "state": "not_loaded",
            "summary": "Gemma 3N E4B is a target descriptor only; no model assets are loaded.",
            "nextAction": "Keep model assets external until runtime evidence exists.",
        },
        {
            "rowId": "session_activity",
            "label": "session activity",
            "state": "inactive",
            "summary": "No launcher session is active and no log stream has started.",
            "nextAction": "Keep launch controls gated until readiness inputs are present.",
        },
        {
            "rowId": "pccx_lab_diagnostics",
            "label": "pccx-lab diagnostics",
            "state": "available_as_placeholder",
            "summary": "Diagnostics handoff is represented as read-only local data only.",
            "nextAction": "Use the pccx-lab CLI/core boundary later for validation, not launcher internals.",
        },
        {
            "rowId": "runtime_readiness",
            "label": "runtime readiness",
            "state": "blocked",
            "summary": "Runtime, bitstream, board-smoke, and measurement evidence are still required.",
            "nextAction": "Do not present the launch path as available until evidence-backed readiness changes.",
        },
    ],
    "discoveryPaths": [
        {
            "pathId": "usb_serial_hint",
            "transport": "usb_serial",
            "state": "planned",
            "summary": "Read-only USB and serial enumeration can provide a local device hint.",
            "suggestedUserAction": "Connect the KV260 carrier-board USB path and rerun the status panel check.",
        },
        {
            "pathId": "network_host_target",
            "transport": "network_host",
            "state": "requires_configuration",
            "summary": "A network target must be provided explicitly; the launcher does not scan networks.",
            "suggestedUserAction": "Configure the target host through a future explicit settings surface.",
        },
        {
            "pathId": "serial_console_target",
            "transport": "serial_console",
            "state": "future_only",
            "summary": "Serial-console interaction is a future explicit target path, not active in this fixture.",
            "suggestedUserAction": "Use read-only enumeration until a reviewed serial boundary exists.",
        },
    ],
    "connectionLaunchFlow": [
        {
            "stepId": "open_status_panel",
            "order": 1,
            "stage": "status_panel",
            "state": "placeholder",
            "userAction": "Open the launcher status panel.",
            "launcherAction": "Render deterministic local status rows.",
            "statusPanelUpdate": "Show connection, model load, session, diagnostics, and readiness rows.",
            "sideEffectPolicy": "local_render_only",
        },
        {
            "stepId": "select_kv260_target",
            "order": 2,
            "stage": "target_selection",
            "state": "planned",
            "userAction": "Select a KV260-class target when configuration exists.",
            "launcherAction": "Record the selected target as status data only.",
            "statusPanelUpdate": "Move target selection from placeholder to configured in a future implementation.",
            "sideEffectPolicy": "no_hardware_access",
        },
        {
            "stepId": "run_read_only_discovery",
            "order": 3,
            "stage": "discovery",
            "state": "planned",
            "userAction": "Request a status refresh.",
            "launcherAction": "Use reviewed read-only discovery paths when implemented.",
            "statusPanelUpdate": "Report detected, missing, or not configured discovery state.",
            "sideEffectPolicy": "no_mutation_no_network_scan",
        },
        {
            "stepId": "prepare_authentication",
            "order": 4,
            "stage": "authentication",
            "state": "requires_configuration",
            "userAction": "Provide target access details through a future explicit settings surface.",
            "launcherAction": "Check only whether required inputs are present.",
            "statusPanelUpdate": "Report authentication as not configured, configured, or blocked.",
            "sideEffectPolicy": "no_secret_echo_no_login_attempt",
        },
        {
            "stepId": "check_runtime_readiness",
            "order": 5,
            "stage": "readiness",
            "state": "blocked",
            "userAction": "Review readiness blockers before launch controls are enabled.",
            "launcherAction": "Read local readiness data and keep launch controls gated.",
            "statusPanelUpdate": "Show runtime, bitstream, board-smoke, and measurement blockers.",
            "sideEffectPolicy": "data_only",
        },
        {
            "stepId": "preview_launch",
            "order": 6,
            "stage": "launch_preview",
            "state": "planned",
            "userAction": "Review the planned launch sequence.",
            "launcherAction": "Show the dry-run launch preview only.",
            "statusPanelUpdate": "Keep the session inactive and logs not started.",
            "sideEffectPolicy": "dry_run_only",
        },
        {
            "stepId": "start_runtime_when_evidence_backed",
            "order": 7,
            "stage": "runtime_start",
            "state": "blocked",
            "userAction": "Start runtime only after the readiness gate changes.",
            "launcherAction": "Refuse runtime start while evidence is missing.",
            "statusPanelUpdate": "Keep runtime and session states blocked or inactive.",
            "sideEffectPolicy": "blocked_until_evidence_backed",
        },
        {
            "stepId": "stream_logs_when_session_exists",
            "order": 8,
            "stage": "logs",
            "state": "blocked",
            "userAction": "Inspect logs after a real session exists.",
            "launcherAction": "Do not stream logs when no session exists.",
            "statusPanelUpdate": "Show log stream as not started.",
            "sideEffectPolicy": "no_log_stream_without_session",
        },
    ],
    "errorTaxonomy": [
        {
            "errorId": "kv260_device_not_detected",
            "stage": "discovery",
            "severity": "blocked",
            "state": "planned",
            "userMessage": "No KV260 target is visible to the configured discovery path.",
            "suggestedRemediation": "Check power, cabling, and the selected discovery path, then rerun a read-only status refresh.",
            "claimBoundary": "No runtime or performance claim follows from discovery status.",
        },
        {
            "errorId": "target_access_not_configured",
            "stage": "authentication",
            "severity": "blocked",
            "state": "requires_configuration",
            "userMessage": "Target access inputs are not configured.",
            "suggestedRemediation": "Configure the target host and access method through a future explicit settings surface.",
            "claimBoundary": "The launcher must not guess hosts, scan networks, or print access inputs.",
        },
        {
            "errorId": "authentication_not_available",
            "stage": "authentication",
            "severity": "blocked",
            "state": "planned",
            "userMessage": "The reviewed authentication handshake is not implemented in this fixture.",
            "suggestedRemediation": "Keep connection controls disabled until the authentication boundary is implemented and tested.",
            "claimBoundary": "No login attempt is performed by this status surface.",
        },
        {
            "errorId": "runtime_evidence_missing",
            "stage": "readiness",
            "severity": "blocked",
            "state": "blocked",
            "userMessage": "Runtime evidence is missing for the KV260 target path.",
            "suggestedRemediation": "Wait for checked runtime evidence before enabling start controls.",
            "claimBoundary": "The target remains blocked and not evidence-backed.",
        },
        {
            "errorId": "model_assets_not_configured",
            "stage": "model",
            "severity": "blocked",
            "state": "ready_for_inputs",
            "userMessage": "Model assets are external and not configured by the launcher fixture.",
            "suggestedRemediation": "Keep model asset selection explicit and outside repository fixtures.",
            "claimBoundary": "No model is loaded or referenced by local path.",
        },
        {
            "errorId": "bitstream_evidence_missing",
            "stage": "readiness",
            "severity": "blocked",
            "state": "blocked",
            "userMessage": "Bitstream and board-smoke evidence are missing for the launch path.",
            "suggestedRemediation": "Keep launch controls gated until lower-layer evidence is available.",
            "claimBoundary": "No bitstream or board-smoke success is claimed here.",
        },
        {
            "errorId": "lab_diagnostics_unavailable",
            "stage": "diagnostics",
            "severity": "placeholder",
            "state": "available_as_placeholder",
            "userMessage": "pccx-lab diagnostics are represented as a read-only placeholder handoff.",
            "suggestedRemediation": "Use the explicit pccx-lab CLI/core validator when that integration is requested.",
            "claimBoundary": "The launcher does not execute pccx-lab for this status surface.",
        },
        {
            "errorId": "session_inactive",
            "stage": "session",
            "severity": "placeholder",
            "state": "inactive",
            "userMessage": "No launcher session is active.",
            "suggestedRemediation": "Show session controls as disabled until the readiness gate changes.",
            "claimBoundary": "No inference session is started.",
        },
        {
            "errorId": "log_stream_not_started",
            "stage": "logs",
            "severity": "placeholder",
            "state": "not_started",
            "userMessage": "No log stream exists because no runtime session exists.",
            "suggestedRemediation": "Show logs as pending rather than empty success.",
            "claimBoundary": "No runtime logs are produced or collected.",
        },
    ],
    "pccxLabDiagnostics": {
        "state": "planned",
        "mode": "read_only_handoff",
        "lowerBoundary": "pccx-lab CLI/core",
        "automaticUpload": False,
        "writeBack": False,
        "executesPccxLab": False,
    },
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "writesArtifacts": False,
        "touchesHardware": False,
        "kv260Access": False,
        "opensSerialPort": False,
        "serialWrites": False,
        "networkCalls": False,
        "networkScan": False,
        "sshExecution": False,
        "authenticationAttempt": False,
        "runtimeExecution": False,
        "modelLoaded": False,
        "modelExecution": False,
        "modelWeightPathsIncluded": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
        "generatedBlobsIncluded": False,
        "hardwareDumpsIncluded": False,
        "providerCalls": False,
        "telemetry": False,
        "automaticUpload": False,
        "writeBack": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "firmwareFlashing": False,
        "packageInstallation": False,
        "stableApiAbiClaim": False,
    },
    "limitations": [
        "Data-only status panel fixture; no runtime is executed.",
        "No USB, serial, network, SSH, or authentication command is run by this contract.",
        "No model assets are bundled, loaded, or referenced by path.",
        "No KV260 hardware access, board programming, runtime start, provider call, telemetry, upload, or write-back is performed.",
        "The connection and launch flow is a gated plan until checked readiness evidence exists.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#10",
        "pccxai/pccx-llm-launcher#2",
    ],
}


def create_gemma3n_e4b_kv260_device_session_status() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 status fixture."""
    return copy.deepcopy(_DEVICE_SESSION_STATUS)


def device_session_status_json(status: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        status
        if status is not None
        else create_gemma3n_e4b_kv260_device_session_status(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only device/session status JSON.",
    )
    parser.add_argument(
        "--model",
        default="gemma3n-e4b",
        choices=("gemma3n-e4b",),
        help="model descriptor target",
    )
    parser.add_argument(
        "--target",
        default="kv260",
        choices=("kv260",),
        help="target board/device",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    parse_args(sys.argv[1:] if argv is None else argv)
    sys.stdout.write(device_session_status_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
