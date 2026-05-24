#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the desktop installer distribution contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "desktop_installer_distribution_contract.py"
FIXTURE_PATH = (
    ROOT / "contracts" / "fixtures" / "desktop-installer-distribution.multi-os-placeholder.json"
)
SCRIPT_PATH = ROOT / "scripts" / "desktop-installer-distribution-stub.sh"
DOC_PATH = ROOT / "docs" / "DESKTOP_INSTALLER_DISTRIBUTION.md"
SMOKE_PATH = ROOT / "scripts" / "smoke.sh"
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "desktop_installer_distribution_contract",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def iter_state_values(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            if (
                key == "state"
                or key.endswith("State")
                or key.endswith("Status")
            ) and isinstance(nested, str):
                yield nested
            yield from iter_state_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_state_values(nested)


def iter_keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key
            yield from iter_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_keys(nested)


def assert_no_private_or_generated_data(text: str) -> None:
    forbidden_patterns = [
        r"/home/[^\s\"']+",
        r"/Users/[^\s\"']+",
        r"[A-Za-z]:\\Users\\",
        r"\b(?:api[_-]?key|authorization|bearer|client[_-]?secret|password|private[_-]?key|secret|token)\b\s*[:=]",
        r"\.(?:gguf|safetensors|ckpt|pt|pth|onnx)\b",
        r"(?:weights|model_weights|model-cache)/(?:[^\"'\s]+)",
        r"(?:raw[_-]?full[_-]?logs|hardware[_-]?dump|generated[_-]?blob)\s*[:=]",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, text, re.IGNORECASE), pattern


def assert_no_runtime_implementation_terms(source: str) -> None:
    forbidden = [
        "subprocess",
        "os.system",
        "popen",
        "socket",
        "urllib",
        "requests",
        "http.client",
        "openai",
        "anthropic",
        "gem" + "ini",
        "modelcontextprotocol",
        "websocket",
        "shell=True",
    ]
    lowered = source.lower()
    for term in forbidden:
        assert term.lower() not in lowered, term


def assert_no_secret_or_provider_configs(value) -> None:
    forbidden_keys = {
        "apiKey",
        "accessToken",
        "refreshToken",
        "authorization",
        "bearerToken",
        "provider",
        "providers",
        "providerConfig",
        "providerConfigs",
        "licensePath",
        "licenseFile",
        "secretValue",
    }
    for key in iter_keys(value):
        assert key not in forbidden_keys, key


def assert_no_unsupported_claims(text: str) -> None:
    literal_claims = [
        "production" + "-ready",
        "marketplace" + "-ready",
        "stable " + "API",
        "stable " + "ABI",
        "KV260 inference " + "works",
        "Gemma 3N E4B " + "runs on KV260",
        "20 tok/s " + "achieved",
        "timing " + "closed",
        "bitstream " + "ready",
        "cloud provider " + "ready",
    ]
    lowered = text.lower()
    for claim in literal_claims:
        assert claim.lower() not in lowered, claim


def test_desktop_installer_distribution_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_desktop_installer_distribution()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert (
        module.desktop_installer_distribution_json(generated)
        == module.desktop_installer_distribution_json(generated)
    )
    assert module.desktop_installer_distribution_json(generated).endswith("\n")
    assert json.loads(module.desktop_installer_distribution_json(generated)) == fixture


def test_cli_stub_outputs_deterministic_json() -> None:
    fixture = json.loads(read_text(FIXTURE_PATH))
    command = ["bash", str(SCRIPT_PATH), "--product", "pccx-launcher"]
    first = subprocess.run(command, check=True, capture_output=True, text=True)
    second = subprocess.run(command, check=True, capture_output=True, text=True)

    assert first.stderr == ""
    assert first.stdout == second.stdout
    assert first.stdout.endswith("\n")
    assert json.loads(first.stdout) == fixture


def test_cli_rejects_other_products() -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH), "--product", "other"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert "only --product pccx-launcher" in result.stderr


def test_required_fields_and_allowed_states() -> None:
    module = load_module()
    distribution = module.create_desktop_installer_distribution()
    allowed = set(module.DESKTOP_INSTALLER_STATE_VALUES)

    assert tuple(distribution.keys()) == module.DESKTOP_INSTALLER_DISTRIBUTION_FIELDS
    assert distribution["schemaVersion"] == "pccx.desktopInstallerDistribution.v0"

    states = list(iter_state_values(distribution))
    assert states
    for state in states:
        assert state in allowed, state

    for platform in distribution["supportedHostPlatforms"]:
        assert tuple(platform.keys()) == module.PLATFORM_FIELDS
    for channel in distribution["distributionChannels"]:
        assert tuple(channel.keys()) == module.CHANNEL_FIELDS
    for artifact in distribution["releaseArtifacts"]:
        assert tuple(artifact.keys()) == module.ARTIFACT_FIELDS
    assert tuple(distribution["updatePolicy"].keys()) == module.UPDATE_POLICY_FIELDS
    for toolchain in distribution["toolchainDetectionPlan"]:
        assert tuple(toolchain.keys()) == module.TOOLCHAIN_DETECTION_FIELDS
    assert tuple(distribution["localSynthesisPlan"].keys()) == module.LOCAL_SYNTHESIS_FIELDS
    assert tuple(distribution["cloudSyncPlan"].keys()) == module.CLOUD_SYNC_FIELDS
    for boundary in distribution["moduleBoundaries"]:
        assert tuple(boundary.keys()) == module.BOUNDARY_FIELDS
    for gate in distribution["securityGates"]:
        assert tuple(gate.keys()) == module.GATE_FIELDS
    for reason in distribution["blockedReasons"]:
        assert tuple(reason.keys()) == module.BLOCKED_REASON_FIELDS
    for ref in distribution["handoffRefs"]:
        assert tuple(ref.keys()) == module.HANDOFF_REF_FIELDS


def test_contract_covers_multi_os_installer_update_byol_and_sync_scope() -> None:
    distribution = load_module().create_desktop_installer_distribution()
    platforms = {platform["platformId"]: platform for platform in distribution["supportedHostPlatforms"]}
    channels = {channel["channelId"]: channel for channel in distribution["distributionChannels"]}
    artifacts = {artifact["artifactId"]: artifact for artifact in distribution["releaseArtifacts"]}
    toolchains = {
        toolchain["toolchainId"]: toolchain
        for toolchain in distribution["toolchainDetectionPlan"]
    }
    gates = {gate["gateId"]: gate for gate in distribution["securityGates"]}
    reasons = {reason["reasonId"]: reason for reason in distribution["blockedReasons"]}
    flags = distribution["safetyFlags"]

    assert distribution["preferredDesktopShell"] == "tauri"
    assert distribution["fallbackDesktopShell"] == "electron"
    assert set(platforms) == {"macos", "windows", "linux"}
    assert platforms["macos"]["packageFormats"] == ["dmg", "app"]
    assert platforms["windows"]["packageFormats"] == ["msi", "exe"]
    assert platforms["linux"]["packageFormats"] == ["appimage", "deb", "rpm"]
    assert set(channels) == {
        "user_download_page",
        "github_release_artifacts",
        "automatic_update_manifest",
    }
    assert channels["user_download_page"]["surface"] == "download_page"
    assert channels["automatic_update_manifest"]["state"] == "requires_signed_metadata"
    assert set(artifacts) == {"macos_dmg", "windows_msi", "linux_appimage"}
    assert all(artifact["checksumState"] == "requires_checksum" for artifact in artifacts.values())
    assert all(artifact["updateEligible"] is False for artifact in artifacts.values())
    assert distribution["updatePolicy"]["state"] == "gated"
    assert distribution["updatePolicy"]["userConsentRequired"] is True
    assert distribution["updatePolicy"]["downgradePolicy"] == "blocked"
    assert set(toolchains) == {"vivado", "quartus"}
    assert all(toolchain["byolRequired"] is True for toolchain in toolchains.values())
    assert toolchains["vivado"]["executionPolicy"] == "metadata_only_no_synthesis"
    assert toolchains["quartus"]["executionPolicy"] == "metadata_only_no_synthesis"
    assert distribution["localSynthesisPlan"]["state"] == "gated"
    assert distribution["cloudSyncPlan"]["state"] == "gated"
    assert distribution["cloudSyncPlan"]["syncMode"] == "explicit_user_action"
    assert gates["artifact_signing"]["state"] == "requires_signature"
    assert gates["checksum_manifest"]["state"] == "requires_checksum"
    assert gates["update_signature_manifest"]["state"] == "requires_signed_metadata"
    assert gates["toolchain_detection_review"]["state"] == "requires_review"
    assert gates["cloud_sync_review"]["state"] == "requires_review"
    assert reasons["desktop_app_tree_absent"]["state"] == "blocked"
    assert flags["readOnly"] is True
    assert flags["dataOnly"] is True
    assert flags["desktopInstallerBoundaryOnly"] is True
    assert flags["tauriPreferred"] is True
    assert flags["electronFallbackOnly"] is True
    assert flags["packageBuildAttempted"] is False
    assert flags["releasePublished"] is False
    assert flags["downloadPagePublished"] is False
    assert flags["updaterExecution"] is False
    assert flags["updateManifestFetched"] is False
    assert flags["networkCalls"] is False
    assert flags["cloudCalls"] is False
    assert flags["cloudSyncExecution"] is False
    assert flags["credentialRead"] is False
    assert flags["environmentRead"] is False
    assert flags["secretsRead"] is False
    assert flags["tokensRead"] is False
    assert flags["toolchainDetectionExecuted"] is False
    assert flags["toolchainExecutableRun"] is False
    assert flags["vivadoRun"] is False
    assert flags["quartusRun"] is False
    assert flags["synthesisExecution"] is False
    assert flags["localArtifactRead"] is False
    assert flags["localArtifactWrite"] is False
    assert flags["runtimeExecution"] is False
    assert flags["kv260Access"] is False
    assert flags["hardwareAccess"] is False


def test_contract_avoids_runtime_or_private_data() -> None:
    module_source = read_text(MODULE_PATH)
    fixture_text = read_text(FIXTURE_PATH)
    fixture = json.loads(fixture_text)

    assert_no_runtime_implementation_terms(module_source)
    assert_no_private_or_generated_data(fixture_text)
    assert_no_secret_or_provider_configs(fixture)
    assert_no_unsupported_claims(fixture_text)


def test_docs_smoke_and_ci_reference_installer_distribution_contract() -> None:
    docs = read_text(DOC_PATH)
    smoke = read_text(SMOKE_PATH)
    ci = read_text(CI_PATH)

    assert "desktop_installer_distribution_contract.py" in docs
    assert "desktop-installer-distribution-stub.sh" in docs
    assert "desktop-installer-distribution.multi-os-placeholder.json" in docs
    assert "Tauri" in docs
    assert "Electron" in docs
    assert "Vivado" in docs
    assert "Quartus" in docs
    assert "automatic update" in docs
    assert "cloud sync" in docs.lower()
    assert "desktop-installer-distribution-stub.sh" in smoke
    assert "desktop_installer_distribution_contract_test.py" in smoke
    assert "desktop-installer-distribution-stub.sh" in ci
    assert "desktop_installer_distribution_contract_test.py" in ci


if __name__ == "__main__":
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
    print("desktop installer distribution contract tests ok")
