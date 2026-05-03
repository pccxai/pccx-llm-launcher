#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Fixture tests for the runtime readiness contract."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "runtime_readiness_contract.py"
FIXTURE_PATH = (
    ROOT
    / "contracts"
    / "fixtures"
    / "runtime-readiness.gemma3n-e4b-kv260.json"
)
SCRIPT_PATH = ROOT / "scripts" / "runtime-readiness-stub.sh"
DOC_PATH = ROOT / "docs" / "RUNTIME_READINESS_STATUS.md"
README_PATH = ROOT / "README.md"
TEST_PATH = Path(__file__).resolve()
CI_PATH = ROOT / ".github" / "workflows" / "ci.yml"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "runtime_readiness_contract",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def flatten(value) -> str:
    return json.dumps(value, sort_keys=True)


def iter_state_values(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            if key == "state" or key.endswith("State"):
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
        "gemini",
        "modelcontextprotocol",
        "vscode-languageclient",
        "vsce",
        "watchdog",
        "filewatcher",
        "websocket",
        "xbutil",
        "xrt",
        "/proc/device-tree",
    ]
    lowered = source.lower()
    for term in forbidden:
        assert term not in lowered, term


def assert_no_provider_configs(value) -> None:
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
    }
    for key in iter_keys(value):
        assert key not in forbidden_keys, key


def assert_no_unsupported_claims(text: str) -> None:
    literal_claims = [
        "production-ready",
        "marketplace-ready",
        "stable API",
        "stable ABI",
        "KV260 inference works",
        "Gemma 3N E4B runs on KV260",
        "20 tok/s achieved",
        "timing closed",
        "bitstream ready",
        "launcher executes pccx-lab",
        "IDE controls launcher",
        "AI provider integration is live",
    ]
    lowered = text.lower()
    for claim in literal_claims:
        assert claim.lower() not in lowered, claim

    asserted_claim_patterns = [
        r"\bMCP\s+(?:server|client)\s+(?:is\s+)?implemented\b",
        r"\bLSP\s+(?:server|client)\s+(?:is\s+)?implemented\b",
        r"\bAI\s+provider\s+(?:is\s+)?implemented\b",
        r"\bKV260\s+run\s+(?:is\s+)?claimed\b",
    ]
    for pattern in asserted_claim_patterns:
        assert not re.search(pattern, text, re.IGNORECASE), pattern


def assert_no_readiness_invocation_flags(source: str) -> None:
    forbidden_patterns = [
        r"--backend\s+pccx-lab",
        r"\bPCCX_LAB_BIN\b",
        r"\bpccx-lab\s+(?:status|diagnostics|diagnostics-handoff|validate)\b",
        r"\bsystemverilog-ide\s+--",
        r"\bsystemverilog-ide\s+(?:open|run|status|validate|launch)\b",
        r"\b(?:curl|wget)\b",
        r"\b(?:upload|telemetry|write-back)\s+(?:enabled|true)\b",
    ]
    for pattern in forbidden_patterns:
        assert not re.search(pattern, source, re.IGNORECASE), pattern


def test_readiness_matches_fixture_and_is_deterministic() -> None:
    module = load_module()
    generated = module.create_gemma3n_e4b_kv260_runtime_readiness()
    fixture = json.loads(read_text(FIXTURE_PATH))

    assert generated == fixture
    assert module.readiness_json(generated) == module.readiness_json(generated)
    assert module.readiness_json(generated).endswith("\n")
    assert json.loads(module.readiness_json(generated)) == fixture


def test_cli_stub_outputs_deterministic_json() -> None:
    fixture = json.loads(read_text(FIXTURE_PATH))
    command = [
        "bash",
        str(SCRIPT_PATH),
        "--model",
        "gemma3n-e4b",
        "--target",
        "kv260",
    ]
    first = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    second = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )

    assert first.stderr == ""
    assert first.stdout == second.stdout
    assert first.stdout.endswith("\n")
    assert json.loads(first.stdout) == fixture


def test_required_fields_and_allowed_states() -> None:
    module = load_module()
    readiness = module.create_gemma3n_e4b_kv260_runtime_readiness()
    allowed = set(module.READINESS_STATE_VALUES)

    assert tuple(readiness.keys()) == module.READINESS_FIELDS
    assert readiness["schemaVersion"] == "pccx.runtimeReadiness.v0"
    assert set(readiness["stateVocabulary"]) == allowed

    states = list(iter_state_values(readiness))
    assert states
    for state in states:
        assert state in allowed, state

    assert "target" in states
    assert "blocked" in states
    assert "ready_for_inputs" in states
    assert "evidence_present" in states
    assert "measured" not in states
    assert "measured" in readiness["stateVocabulary"]


def test_gemma3n_e4b_kv260_current_state_is_blocked() -> None:
    readiness = load_module().create_gemma3n_e4b_kv260_runtime_readiness()
    evidence = {item["evidenceId"]: item for item in readiness["evidenceRefs"]}
    blocker_ids = [item["blockerId"] for item in readiness["blockers"]]
    performance = readiness["performanceTargets"][0]

    assert readiness["statusAnswer"] == "blocked_not_yet_evidence_backed"
    assert readiness["fixtureVersion"] == "runtime-readiness.gemma3n-e4b-kv260.2026-05-03"
    assert readiness["lastUpdatedSource"] == "pccx_evidence_boundary_2026-05-03"
    assert readiness["readinessState"] == "blocked"
    assert readiness["evidenceState"] == "blocked"
    assert readiness["modelId"] == "gemma3n_e4b_placeholder"
    assert readiness["modelFamily"] == "gemma3n"
    assert readiness["modelVariant"] == "e4b"
    assert readiness["targetDevice"] == "kv260"
    assert readiness["targetBoard"] == "xilinx_kria_kv260"
    assert readiness["targetState"] == "target"
    assert readiness["overallState"] == "blocked"
    assert readiness["descriptorState"] == "evidence_present"
    assert readiness["modelWeightState"] == "ready_for_inputs"
    assert readiness["boardInputState"] == "ready_for_inputs"
    assert readiness["bitstreamState"] == "blocked"
    assert readiness["simulationEvidenceState"] == "evidence_present"
    assert readiness["vivadoSynthState"] == "evidence_present"
    assert readiness["timingEvidenceState"] == "blocked"
    assert readiness["implementationState"] == "blocked"
    assert readiness["kv260SmokeState"] == "blocked"
    assert readiness["runtimeEvidenceState"] == "blocked"
    assert readiness["throughputEvidenceState"] == "target"
    assert readiness["compatibilityState"] == "blocked"

    assert evidence["fpga_v002_xsim_validation"]["state"] == "evidence_present"
    assert "11 passed and 0 failed" in evidence["fpga_v002_xsim_validation"]["summary"]
    assert evidence["fpga_v002_vivado_synth"]["state"] == "evidence_present"
    assert evidence["fpga_post_synth_drc_timing"]["state"] == "blocked"
    assert evidence["kv260_board_smoke"]["state"] == "blocked"
    assert evidence["gemma3n_e4b_kv260_runtime"]["state"] == "blocked"
    assert evidence["gemma3n_e4b_kv260_throughput"]["state"] == "target"

    assert blocker_ids == [
        "board_model_bitstream_runtime_environment_missing",
        "post_synth_drc_timing_open",
        "implementation_incomplete",
        "bitstream_not_generated",
        "gemma3n_e4b_runtime_evidence_absent",
        "throughput_measurement_absent",
    ]

    assert performance["metricId"] == "decode_throughput"
    assert performance["state"] == "target"
    assert performance["target"] == "20 tok/s"
    assert performance["measured"] is False
    assert performance["achieved"] is False


def test_nested_contract_shapes() -> None:
    module = load_module()
    readiness = module.create_gemma3n_e4b_kv260_runtime_readiness()

    for blocker in readiness["blockers"]:
        assert tuple(blocker.keys()) == module.BLOCKER_FIELDS
        assert blocker["state"] == "blocked"

    for item in readiness["nextInputsRequired"]:
        assert tuple(item.keys()) == module.NEXT_INPUT_FIELDS
        assert item["state"] == "ready_for_inputs"

    for item in readiness["evidenceRefs"]:
        assert tuple(item.keys()) == module.EVIDENCE_REF_FIELDS
        assert item["state"] in set(module.READINESS_STATE_VALUES)

    for item in readiness["performanceTargets"]:
        assert tuple(item.keys()) == module.PERFORMANCE_TARGET_FIELDS
        assert item["state"] == "target"
        assert item["measured"] is False
        assert item["achieved"] is False


def test_safety_flags_preserve_data_only_boundary() -> None:
    readiness = load_module().create_gemma3n_e4b_kv260_runtime_readiness()
    flags = readiness["safetyFlags"]

    assert flags["dataOnly"] is True
    assert flags["readOnly"] is True
    assert flags["deterministic"] is True
    assert flags["descriptorOnly"] is True
    for name in [
        "writesArtifacts",
        "touchesHardware",
        "kv260Access",
        "runtimeExecution",
        "modelLoaded",
        "modelExecution",
        "modelWeightPathsIncluded",
        "privatePathsIncluded",
        "secretsIncluded",
        "tokensIncluded",
        "generatedBlobsIncluded",
        "hardwareDumpsIncluded",
        "networkCalls",
        "providerCalls",
        "telemetry",
        "automaticUpload",
        "writeBack",
        "executesPccxLab",
        "executesSystemverilogIde",
        "mcpServerImplemented",
        "lspImplemented",
        "marketplaceFlow",
        "stableApiAbiClaim",
    ]:
        assert flags[name] is False, name


def test_no_private_data_runtime_calls_or_overclaims() -> None:
    module_source = read_text(MODULE_PATH)
    script_source = read_text(SCRIPT_PATH)
    readiness = load_module().create_gemma3n_e4b_kv260_runtime_readiness()
    scan_text = "\n".join([
        read_text(FIXTURE_PATH),
        read_text(DOC_PATH),
        read_text(README_PATH),
        flatten(readiness),
        module_source,
        script_source,
    ])
    readiness_runtime_source = "\n".join([module_source, script_source])

    assert_no_runtime_implementation_terms(module_source)
    assert_no_private_or_generated_data(scan_text)
    assert_no_provider_configs(readiness)
    assert_no_unsupported_claims(scan_text)
    assert_no_readiness_invocation_flags(readiness_runtime_source)


def test_source_headers_for_touched_code_files() -> None:
    expected_headers = {
        MODULE_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        SCRIPT_PATH: [
            "#!/usr/bin/env bash",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        TEST_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        CI_PATH: [
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
    }

    for path, header in expected_headers.items():
        assert read_text(path).splitlines()[: len(header)] == header, path


test_readiness_matches_fixture_and_is_deterministic()
test_cli_stub_outputs_deterministic_json()
test_required_fields_and_allowed_states()
test_gemma3n_e4b_kv260_current_state_is_blocked()
test_nested_contract_shapes()
test_safety_flags_preserve_data_only_boundary()
test_no_private_data_runtime_calls_or_overclaims()
test_source_headers_for_touched_code_files()

print("runtime readiness contract tests ok")
