#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Data-only runtime readiness contract for the planned KV260 path.

The contract reports evidence-aware launcher readiness without loading model
assets, touching KV260 hardware, executing runtime commands, calling providers,
or invoking pccx-lab or editor tooling.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys


SCHEMA_VERSION = "pccx.runtimeReadiness.v0"

READINESS_STATE_VALUES = (
    "target",
    "blocked",
    "ready_for_inputs",
    "evidence_present",
    "measured",
)

READINESS_FIELDS = (
    "schemaVersion",
    "readinessId",
    "fixtureVersion",
    "lastUpdatedSource",
    "statusAnswer",
    "readinessState",
    "evidenceState",
    "modelId",
    "modelFamily",
    "modelVariant",
    "targetDevice",
    "targetBoard",
    "targetState",
    "overallState",
    "descriptorState",
    "modelWeightState",
    "boardInputState",
    "bitstreamState",
    "simulationEvidenceState",
    "vivadoSynthState",
    "timingEvidenceState",
    "implementationState",
    "kv260SmokeState",
    "runtimeEvidenceState",
    "throughputEvidenceState",
    "compatibilityState",
    "stateVocabulary",
    "blockers",
    "nextInputsRequired",
    "performanceTargets",
    "evidenceRefs",
    "coordinationNotes",
    "safetyFlags",
    "limitations",
    "issueRefs",
)

BLOCKER_FIELDS = (
    "blockerId",
    "state",
    "summary",
    "requiredBefore",
)

NEXT_INPUT_FIELDS = (
    "inputId",
    "state",
    "summary",
    "sourceBoundary",
)

EVIDENCE_REF_FIELDS = (
    "evidenceId",
    "state",
    "summary",
    "referenceKind",
)

PERFORMANCE_TARGET_FIELDS = (
    "metricId",
    "state",
    "target",
    "measured",
    "achieved",
    "summary",
)

_GEMMA3N_E4B_KV260_RUNTIME_READINESS = {
    "schemaVersion": SCHEMA_VERSION,
    "readinessId": "runtime_readiness_gemma3n_e4b_kv260",
    "fixtureVersion": "runtime-readiness.gemma3n-e4b-kv260.2026-05-03",
    "lastUpdatedSource": "pccx_evidence_boundary_2026-05-03",
    "statusAnswer": "blocked_not_yet_evidence_backed",
    "readinessState": "blocked",
    "evidenceState": "blocked",
    "modelId": "gemma3n_e4b_placeholder",
    "modelFamily": "gemma3n",
    "modelVariant": "e4b",
    "targetDevice": "kv260",
    "targetBoard": "xilinx_kria_kv260",
    "targetState": "target",
    "overallState": "blocked",
    "descriptorState": "evidence_present",
    "modelWeightState": "ready_for_inputs",
    "boardInputState": "ready_for_inputs",
    "bitstreamState": "blocked",
    "simulationEvidenceState": "evidence_present",
    "vivadoSynthState": "evidence_present",
    "timingEvidenceState": "blocked",
    "implementationState": "blocked",
    "kv260SmokeState": "blocked",
    "runtimeEvidenceState": "blocked",
    "throughputEvidenceState": "target",
    "compatibilityState": "blocked",
    "stateVocabulary": {
        "target": "Named planned target only.",
        "blocked": "A required input, artifact, closure step, or runtime evidence item is missing.",
        "ready_for_inputs": "The launcher can describe the required input without bundling or reading it.",
        "evidence_present": "Checked non-runtime evidence exists for this item.",
        "measured": "A runtime or hardware measurement exists. The current fixture does not use this state for Gemma 3N E4B on KV260.",
    },
    "blockers": [
        {
            "blockerId": "board_model_bitstream_runtime_environment_missing",
            "state": "blocked",
            "summary": "KV260 board, model assets, generated bitstream, and runtime environment are not provided by this launcher fixture.",
            "requiredBefore": "kv260_smoke_or_runtime_claim",
        },
        {
            "blockerId": "post_synth_drc_timing_open",
            "state": "blocked",
            "summary": "Post-synthesis DRC and timing issues remain open in the FPGA closure state.",
            "requiredBefore": "implementation_or_bitstream_claim",
        },
        {
            "blockerId": "implementation_incomplete",
            "state": "blocked",
            "summary": "Implementation is not complete, so hardware closure is not available.",
            "requiredBefore": "bitstream_or_board_smoke_claim",
        },
        {
            "blockerId": "bitstream_not_generated",
            "state": "blocked",
            "summary": "A generated bitstream is not proven by this launcher surface.",
            "requiredBefore": "kv260_board_smoke_claim",
        },
        {
            "blockerId": "gemma3n_e4b_runtime_evidence_absent",
            "state": "blocked",
            "summary": "Gemma 3N E4B has no KV260 hardware runtime evidence in this launcher fixture.",
            "requiredBefore": "runtime_or_performance_claim",
        },
        {
            "blockerId": "throughput_measurement_absent",
            "state": "blocked",
            "summary": "Throughput measurement is unavailable.",
            "requiredBefore": "performance_claim",
        },
    ],
    "nextInputsRequired": [
        {
            "inputId": "external_model_assets",
            "state": "ready_for_inputs",
            "summary": "Gemma 3N E4B model assets remain external and are not loaded or referenced by path.",
            "sourceBoundary": "user_or_future_runtime_integration",
        },
        {
            "inputId": "kv260_board_environment",
            "state": "ready_for_inputs",
            "summary": "KV260 board and runtime environment evidence must arrive from lower layers before smoke status changes.",
            "sourceBoundary": "future_pccx_lab_or_core_handoff",
        },
        {
            "inputId": "timing_and_implementation_closure",
            "state": "ready_for_inputs",
            "summary": "Post-synthesis DRC, timing, implementation, and bitstream evidence must be supplied by FPGA closure work.",
            "sourceBoundary": "pccx_fpga_kv260_repo",
        },
        {
            "inputId": "kv260_smoke_evidence",
            "state": "ready_for_inputs",
            "summary": "Board smoke evidence is required before KV260 runtime status can move beyond blocked.",
            "sourceBoundary": "future_pccx_lab_or_core_handoff",
        },
        {
            "inputId": "throughput_measurement",
            "state": "ready_for_inputs",
            "summary": "Measured throughput evidence is required before any performance claim.",
            "sourceBoundary": "future_pccx_lab_or_core_handoff",
        },
    ],
    "performanceTargets": [
        {
            "metricId": "decode_throughput",
            "state": "target",
            "target": "20 tok/s",
            "measured": False,
            "achieved": False,
            "summary": "20 tok/s remains a target until measured on the Gemma 3N E4B plus KV260 path.",
        },
    ],
    "evidenceRefs": [
        {
            "evidenceId": "launcher_model_runtime_descriptor_fixture",
            "state": "evidence_present",
            "summary": "The launcher has a checked descriptor fixture for Gemma 3N E4B and the KV260 placeholder runtime.",
            "referenceKind": "repo_fixture_reference",
        },
        {
            "evidenceId": "fpga_v002_xsim_validation",
            "state": "evidence_present",
            "summary": "pccx-FPGA-NPU-LLM-kv260 v002 repo-local xsim evidence reports 11 passed and 0 failed.",
            "referenceKind": "external_repo_state_summary",
        },
        {
            "evidenceId": "fpga_v002_vivado_synth",
            "state": "evidence_present",
            "summary": "Vivado synthesis evidence exists, but this is not hardware closure.",
            "referenceKind": "external_repo_state_summary",
        },
        {
            "evidenceId": "fpga_post_synth_drc_timing",
            "state": "blocked",
            "summary": "Post-synthesis DRC and timing issues are current closure blockers.",
            "referenceKind": "external_repo_state_summary",
        },
        {
            "evidenceId": "kv260_board_smoke",
            "state": "blocked",
            "summary": "KV260 board smoke is blocked by missing board, model, bitstream, and runtime environment.",
            "referenceKind": "future_evidence_required",
        },
        {
            "evidenceId": "gemma3n_e4b_kv260_runtime",
            "state": "blocked",
            "summary": "Gemma 3N E4B KV260 hardware runtime evidence is absent.",
            "referenceKind": "future_evidence_required",
        },
        {
            "evidenceId": "gemma3n_e4b_kv260_throughput",
            "state": "target",
            "summary": "Throughput remains a target-only item until measured evidence exists.",
            "referenceKind": "future_measurement_required",
        },
    ],
    "coordinationNotes": {
        "pccxLab": "pccx-lab remains the future CLI/core diagnostics and verification backend; this launcher fixture does not invoke it.",
        "systemverilogIde": "systemverilog-ide may consume launcher or lab data later as read-only context; this fixture does not invoke or control it.",
        "launcher": "The launcher provides data contracts first and does not add runtime integration in this phase.",
    },
    "safetyFlags": {
        "dataOnly": True,
        "readOnly": True,
        "deterministic": True,
        "descriptorOnly": True,
        "writesArtifacts": False,
        "touchesHardware": False,
        "kv260Access": False,
        "runtimeExecution": False,
        "modelLoaded": False,
        "modelExecution": False,
        "modelWeightPathsIncluded": False,
        "privatePathsIncluded": False,
        "secretsIncluded": False,
        "tokensIncluded": False,
        "generatedBlobsIncluded": False,
        "hardwareDumpsIncluded": False,
        "networkCalls": False,
        "providerCalls": False,
        "telemetry": False,
        "automaticUpload": False,
        "writeBack": False,
        "executesPccxLab": False,
        "executesSystemverilogIde": False,
        "mcpServerImplemented": False,
        "lspImplemented": False,
        "marketplaceFlow": False,
        "stableApiAbiClaim": False,
    },
    "limitations": [
        "Data-only runtime readiness surface; no runtime is executed.",
        "No model assets are bundled, loaded, or referenced by path.",
        "No KV260 hardware access, board smoke, bitstream programming, or provider call is performed.",
        "xsim and Vivado synthesis evidence are recorded as evidence-aware status only, not hardware closure.",
        "Timing, implementation, bitstream, KV260 smoke, runtime, and throughput evidence remain missing for this launcher fixture.",
        "20 tok/s is a target only until measured evidence exists.",
        "This is not a release, tag, versioned compatibility commitment, MCP, LSP, IDE, marketplace, or telemetry implementation.",
    ],
    "issueRefs": [
        "pccxai/pccx-llm-launcher#3",
        "pccxai/pccx-llm-launcher#5",
        "pccxai/pccx-llm-launcher#12",
    ],
}


def create_gemma3n_e4b_kv260_runtime_readiness() -> dict:
    """Return the checked Gemma 3N E4B plus KV260 readiness fixture."""
    return copy.deepcopy(_GEMMA3N_E4B_KV260_RUNTIME_READINESS)


def readiness_json(readiness: dict | None = None) -> str:
    """Render a deterministic JSON representation."""
    return json.dumps(
        readiness
        if readiness is not None
        else create_gemma3n_e4b_kv260_runtime_readiness(),
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print data-only runtime readiness JSON.",
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
    sys.stdout.write(readiness_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
