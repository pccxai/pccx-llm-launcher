#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only desktop installer distribution contract for PCCX Launcher.

The contract records the planned macOS, Windows, and Linux desktop installer
boundary, including download-page metadata, automatic update gates, BYOL
Vivado/Quartus discovery, local synthesis handoff, and cloud sync handoff.
It does not build packages, publish releases, execute an updater, scan host
toolchains, run synthesis, upload artifacts, read credentials, call providers,
touch hardware, or start launcher runtime code.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.desktopInstallerDistribution.v0"

DESKTOP_INSTALLER_DISTRIBUTION_FIELDS = (
    "schemaVersion",
    "contractId",
    "fixtureVersion",
    "lastUpdatedSource",
    "productId",
    "preferredDesktopShell",
    "fallbackDesktopShell",
    "supportedHostPlatforms",
    "distributionChannels",
    "releaseArtifacts",
    "updatePolicy",
    "toolchainDetectionPlan",
    "localSynthesisPlan",
    "cloudSyncPlan",
    "moduleBoundaries",
    "securityGates",
    "blockedReasons",
    "handoffRefs",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

PLATFORM_FIELDS = (
    "platformId",
    "osFamily",
    "packageFormats",
    "state",
    "notes",
)

CHANNEL_FIELDS = (
    "channelId",
    "surface",
    "state",
    "artifactSource",
    "userAction",
    "launcherAction",
    "securityPolicy",
)

ARTIFACT_FIELDS = (
    "artifactId",
    "targetPlatform",
    "packageFormat",
    "signingState",
    "notarizationState",
    "checksumState",
    "updateEligible",
    "state",
)

UPDATE_POLICY_FIELDS = (
    "policyId",
    "updateMode",
    "state",
    "manifestState",
    "signatureState",
    "rolloutState",
    "networkState",
    "userConsentRequired",
    "downgradePolicy",
)

TOOLCHAIN_DETECTION_FIELDS = (
    "toolchainId",
    "vendor",
    "byolRequired",
    "state",
    "detectionInputs",
    "executionPolicy",
    "secretPolicy",
    "resultPolicy",
)

LOCAL_SYNTHESIS_FIELDS = (
    "planId",
    "state",
    "projectBoundary",
    "toolchainRequirement",
    "invocationPolicy",
    "artifactPolicy",
    "logPolicy",
)

CLOUD_SYNC_FIELDS = (
    "planId",
    "state",
    "syncMode",
    "consentPolicy",
    "credentialPolicy",
    "uploadPolicy",
    "redactionPolicy",
    "conflictPolicy",
)

BOUNDARY_FIELDS = (
    "boundaryId",
    "ownerLayer",
    "state",
    "allowedResponsibility",
    "forbiddenResponsibility",
)

GATE_FIELDS = (
    "gateId",
    "state",
    "requiredBefore",
    "summary",
)

BLOCKED_REASON_FIELDS = (
    "reasonId",
    "state",
    "summary",
    "requiredBefore",
)

HANDOFF_REF_FIELDS = (
    "refId",
    "schemaVersion",
    "fixturePath",
    "state",
    "summary",
)

DESKTOP_INSTALLER_STATE_VALUES = (
    "available_as_data",
    "blocked",
    "disabled",
    "fallback_only",
    "gated",
    "local_only",
    "manual_review_required",
    "metadata_only",
    "not_applicable",
    "not_implemented",
    "not_used",
    "planned",
    "preferred",
    "requires_checksum",
    "requires_notarization",
    "requires_review",
    "requires_signature",
    "requires_signed_metadata",
    "requires_user_consent",
    "summary_only",
)

_DESKTOP_INSTALLER_DISTRIBUTION = {
    "schemaVersion": SCHEMA_VERSION,
    "contractId": "desktop_installer_distribution_multi_os_placeholder",
    "fixtureVersion": "desktop-installer-distribution.multi-os.2026-05-24",
    "lastUpdatedSource": "pccx_launcher_issue_122_desktop_installer_distribution_boundary",
    "productId": "pccx-launcher",
    "preferredDesktopShell": "tauri",
    "fallbackDesktopShell": "electron",
    "supportedHostPlatforms": [
        {
            "platformId": "macos",
            "osFamily": "darwin",
            "packageFormats": ["dmg", "app"],
            "state": "planned",
            "notes": "Tauri macOS packaging and notarization metadata are planned gates",
        },
        {
            "platformId": "windows",
            "osFamily": "windows",
            "packageFormats": ["msi", "exe"],
            "state": "planned",
            "notes": "Windows installer signing and update metadata are planned gates",
        },
        {
            "platformId": "linux",
            "osFamily": "linux",
            "packageFormats": ["appimage", "deb", "rpm"],
            "state": "planned",
            "notes": "Linux packages remain local desktop artifacts until reviewed",
        },
    ],
    "distributionChannels": [
        {
            "channelId": "user_download_page",
            "surface": "download_page",
            "state": "planned",
            "artifactSource": "signed_release_manifest",
            "userAction": "select_host_package",
            "launcherAction": "render_metadata_only",
            "securityPolicy": "show checksums and signature state before download",
        },
        {
            "channelId": "github_release_artifacts",
            "surface": "release_artifacts",
            "state": "requires_review",
            "artifactSource": "reviewed_release_job",
            "userAction": "manual_download",
            "launcherAction": "none",
            "securityPolicy": "artifacts require checksums and platform signing metadata",
        },
        {
            "channelId": "automatic_update_manifest",
            "surface": "update_manifest",
            "state": "requires_signed_metadata",
            "artifactSource": "signed_release_manifest",
            "userAction": "opt_in_update",
            "launcherAction": "blocked_until_reviewed",
            "securityPolicy": "manifest and package signatures are required before update execution",
        },
    ],
    "releaseArtifacts": [
        {
            "artifactId": "macos_dmg",
            "targetPlatform": "macos",
            "packageFormat": "dmg",
            "signingState": "requires_signature",
            "notarizationState": "requires_notarization",
            "checksumState": "requires_checksum",
            "updateEligible": False,
            "state": "planned",
        },
        {
            "artifactId": "windows_msi",
            "targetPlatform": "windows",
            "packageFormat": "msi",
            "signingState": "requires_signature",
            "notarizationState": "not_applicable",
            "checksumState": "requires_checksum",
            "updateEligible": False,
            "state": "planned",
        },
        {
            "artifactId": "linux_appimage",
            "targetPlatform": "linux",
            "packageFormat": "appimage",
            "signingState": "requires_signature",
            "notarizationState": "not_applicable",
            "checksumState": "requires_checksum",
            "updateEligible": False,
            "state": "planned",
        },
    ],
    "updatePolicy": {
        "policyId": "signed_opt_in_updates",
        "updateMode": "automatic_after_user_opt_in",
        "state": "gated",
        "manifestState": "requires_signed_metadata",
        "signatureState": "requires_signature",
        "rolloutState": "manual_review_required",
        "networkState": "requires_user_consent",
        "userConsentRequired": True,
        "downgradePolicy": "blocked",
    },
    "toolchainDetectionPlan": [
        {
            "toolchainId": "vivado",
            "vendor": "xilinx",
            "byolRequired": True,
            "state": "planned",
            "detectionInputs": [
                "PATH command lookup",
                "standard install roots",
                "user-provided toolchain setting",
            ],
            "executionPolicy": "metadata_only_no_synthesis",
            "secretPolicy": "no license, credential, token, or environment secret values",
            "resultPolicy": "name, version, edition, and capability summary only",
        },
        {
            "toolchainId": "quartus",
            "vendor": "intel",
            "byolRequired": True,
            "state": "planned",
            "detectionInputs": [
                "PATH command lookup",
                "standard install roots",
                "user-provided toolchain setting",
            ],
            "executionPolicy": "metadata_only_no_synthesis",
            "secretPolicy": "no license, credential, token, or environment secret values",
            "resultPolicy": "name, version, edition, and capability summary only",
        },
    ],
    "localSynthesisPlan": {
        "planId": "local_synthesis_handoff",
        "state": "gated",
        "projectBoundary": "user_selected_project_only",
        "toolchainRequirement": "BYOL Vivado or Quartus detection must pass first",
        "invocationPolicy": "separate reviewed command boundary",
        "artifactPolicy": "no artifact reads or writes in this contract",
        "logPolicy": "summary metadata only until reviewed log redaction exists",
    },
    "cloudSyncPlan": {
        "planId": "cloud_sync_handoff",
        "state": "gated",
        "syncMode": "explicit_user_action",
        "consentPolicy": "user consent required for every sync boundary",
        "credentialPolicy": "credential lookup and storage are out of this contract",
        "uploadPolicy": "no upload in this contract",
        "redactionPolicy": "artifact and log redaction gate required first",
        "conflictPolicy": "manual review before remote overwrite",
    },
    "moduleBoundaries": [
        {
            "boundaryId": "desktop_shell",
            "ownerLayer": "tauri_ui",
            "state": "preferred",
            "allowedResponsibility": "window, menus, download-page entry point, update prompts",
            "forbiddenResponsibility": "synthesis execution, credential storage, cloud upload",
        },
        {
            "boundaryId": "rust_backend",
            "ownerLayer": "tauri_rust_backend",
            "state": "planned",
            "allowedResponsibility": "validated local metadata and explicit command handoff",
            "forbiddenResponsibility": "silent updater, implicit toolchain run, implicit network call",
        },
        {
            "boundaryId": "toolchain_detector",
            "ownerLayer": "local_backend",
            "state": "metadata_only",
            "allowedResponsibility": "BYOL Vivado and Quartus capability summary",
            "forbiddenResponsibility": "license content reads, synthesis, project mutation",
        },
        {
            "boundaryId": "cloud_sync_bridge",
            "ownerLayer": "sync_backend",
            "state": "requires_review",
            "allowedResponsibility": "future reviewed sync request summary",
            "forbiddenResponsibility": "uploads, provider calls, credential reads",
        },
    ],
    "securityGates": [
        {
            "gateId": "artifact_signing",
            "state": "requires_signature",
            "requiredBefore": "download page promotes installer artifacts",
            "summary": "platform packages require signing metadata",
        },
        {
            "gateId": "checksum_manifest",
            "state": "requires_checksum",
            "requiredBefore": "download page exposes installer artifacts",
            "summary": "packages require checksum metadata",
        },
        {
            "gateId": "update_signature_manifest",
            "state": "requires_signed_metadata",
            "requiredBefore": "automatic update execution",
            "summary": "update manifests require signed metadata",
        },
        {
            "gateId": "toolchain_detection_review",
            "state": "requires_review",
            "requiredBefore": "automatic BYOL detection runs on a user host",
            "summary": "toolchain detection needs a reviewed local-only command boundary",
        },
        {
            "gateId": "cloud_sync_review",
            "state": "requires_review",
            "requiredBefore": "cloud sync can move artifacts or logs",
            "summary": "cloud sync needs consent, credential, redaction, and conflict gates",
        },
    ],
    "blockedReasons": [
        {
            "reasonId": "desktop_app_tree_absent",
            "state": "blocked",
            "summary": "Tauri app files are not present in this snapshot",
            "requiredBefore": "build desktop packages",
        },
        {
            "reasonId": "signed_release_manifest_absent",
            "state": "requires_signed_metadata",
            "summary": "signed release and update metadata are not present",
            "requiredBefore": "enable automatic update execution",
        },
        {
            "reasonId": "toolchain_detector_not_reviewed",
            "state": "requires_review",
            "summary": "BYOL Vivado and Quartus detection is defined as a plan only",
            "requiredBefore": "run host discovery",
        },
        {
            "reasonId": "cloud_sync_not_reviewed",
            "state": "requires_review",
            "summary": "cloud sync remains a future reviewed boundary",
            "requiredBefore": "upload or synchronize artifacts",
        },
    ],
    "handoffRefs": [
        {
            "refId": "runtime_readiness",
            "schemaVersion": "pccx.runtimeReadiness.v0",
            "fixturePath": "contracts/fixtures/runtime-readiness.gemma3n-e4b-kv260.json",
            "state": "available_as_data",
            "summary": "runtime readiness remains a separate evidence gate",
        },
        {
            "refId": "local_desktop_mode_pr",
            "schemaVersion": "pccx.launcherLocalDesktopMode.v0",
            "fixturePath": "pccxai/pccx-launcher#120",
            "state": "requires_review",
            "summary": "local synthesis mode is tracked separately from installer packaging",
        },
    ],
    "safetyFlags": {
        "readOnly": True,
        "dataOnly": True,
        "deterministic": True,
        "desktopInstallerBoundaryOnly": True,
        "tauriPreferred": True,
        "electronFallbackOnly": True,
        "packageBuildAttempted": False,
        "releasePublished": False,
        "downloadPagePublished": False,
        "updaterExecution": False,
        "updateManifestFetched": False,
        "networkCalls": False,
        "cloudCalls": False,
        "cloudSyncExecution": False,
        "providerCalls": False,
        "credentialRead": False,
        "environmentRead": False,
        "secretsRead": False,
        "tokensRead": False,
        "toolchainDetectionExecuted": False,
        "toolchainExecutableRun": False,
        "vivadoRun": False,
        "quartusRun": False,
        "synthesisExecution": False,
        "localArtifactRead": False,
        "localArtifactWrite": False,
        "modelExecution": False,
        "runtimeExecution": False,
        "kv260Access": False,
        "hardwareAccess": False,
        "telemetry": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
    },
    "limitations": [
        "contract records installer distribution metadata only",
        "Tauri app files, package builds, and release jobs are not added here",
        "automatic update execution is blocked until signed metadata and review gates exist",
        "BYOL Vivado and Quartus discovery is a plan and does not run in this contract",
        "local synthesis and cloud sync require separate reviewed command boundaries",
    ],
    "issueRefs": [
        "pccxai/pccx-launcher#122",
    ],
}


def _iter_state_values(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            if (
                key == "state"
                or key.endswith("State")
                or key.endswith("Status")
            ) and isinstance(nested, str):
                yield nested
            yield from _iter_state_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _iter_state_values(nested)


def _validate_distribution(distribution: dict) -> None:
    if tuple(distribution.keys()) != DESKTOP_INSTALLER_DISTRIBUTION_FIELDS:
        raise ValueError("desktop installer distribution fields changed")
    if distribution["schemaVersion"] != SCHEMA_VERSION:
        raise ValueError("unexpected desktop installer distribution schema version")

    allowed = set(DESKTOP_INSTALLER_STATE_VALUES)
    for state in _iter_state_values(distribution):
        if state not in allowed:
            raise ValueError(f"unexpected desktop installer distribution state: {state}")

    for platform in distribution["supportedHostPlatforms"]:
        if tuple(platform.keys()) != PLATFORM_FIELDS:
            raise ValueError("supported platform fields changed")
    for channel in distribution["distributionChannels"]:
        if tuple(channel.keys()) != CHANNEL_FIELDS:
            raise ValueError("distribution channel fields changed")
    for artifact in distribution["releaseArtifacts"]:
        if tuple(artifact.keys()) != ARTIFACT_FIELDS:
            raise ValueError("release artifact fields changed")
    if tuple(distribution["updatePolicy"].keys()) != UPDATE_POLICY_FIELDS:
        raise ValueError("update policy fields changed")
    for toolchain in distribution["toolchainDetectionPlan"]:
        if tuple(toolchain.keys()) != TOOLCHAIN_DETECTION_FIELDS:
            raise ValueError("toolchain detection fields changed")
    if tuple(distribution["localSynthesisPlan"].keys()) != LOCAL_SYNTHESIS_FIELDS:
        raise ValueError("local synthesis fields changed")
    if tuple(distribution["cloudSyncPlan"].keys()) != CLOUD_SYNC_FIELDS:
        raise ValueError("cloud sync fields changed")
    for boundary in distribution["moduleBoundaries"]:
        if tuple(boundary.keys()) != BOUNDARY_FIELDS:
            raise ValueError("module boundary fields changed")
    for gate in distribution["securityGates"]:
        if tuple(gate.keys()) != GATE_FIELDS:
            raise ValueError("security gate fields changed")
    for reason in distribution["blockedReasons"]:
        if tuple(reason.keys()) != BLOCKED_REASON_FIELDS:
            raise ValueError("blocked reason fields changed")
    for ref in distribution["handoffRefs"]:
        if tuple(ref.keys()) != HANDOFF_REF_FIELDS:
            raise ValueError("handoff ref fields changed")


def create_desktop_installer_distribution() -> dict:
    distribution = copy.deepcopy(_DESKTOP_INSTALLER_DISTRIBUTION)
    _validate_distribution(distribution)
    return distribution


def desktop_installer_distribution_json(distribution: dict | None = None) -> str:
    if distribution is None:
        distribution = create_desktop_installer_distribution()
    _validate_distribution(distribution)
    return json.dumps(distribution, indent=2, sort_keys=False) + "\n"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print the data-only PCCX Launcher desktop installer distribution fixture."
    )
    parser.add_argument("--product", default="pccx-launcher")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    if args.product != "pccx-launcher":
        print("only --product pccx-launcher is available in this fixture", file=sys.stderr)
        return 2
    sys.stdout.write(desktop_installer_distribution_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
