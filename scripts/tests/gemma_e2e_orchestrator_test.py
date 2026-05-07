#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Unit tests for the mock Gemma E2E orchestrator."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TEST_PATH = Path(__file__).resolve()

from contracts.gemma_arch_spec import GemmaArchSpec
from contracts.gemma_e2e_orchestrator import (
    ChatSession,
    GemmaE2EOrchestrator,
    RealSerialGemmaE2ENotImplemented,
    run_mock_gemma_chat,
)
from contracts.gemma_tokenizer import GemmaTokenizer
from contracts.kv260_connection_mock import KV260ConnectionMock
from contracts.token_stream_over_serial import encode_input_stream


def assert_raises(error_type, callback) -> None:
    try:
        callback()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def test_mock_orchestrator_runs_full_prompt_to_text_path() -> None:
    prompt = "hello from lane b"
    result = run_mock_gemma_chat(prompt, GemmaArchSpec())

    assert result.output_text.startswith("mock-gemma:")
    assert len(result.output_text) == len("mock-gemma:") + 16
    assert result.prompt_tokens[0] == 2
    assert result.output_tokens[-1] == 1
    assert result.serial_payload == encode_input_stream(result.prompt_tokens)
    assert result.axi_completion_count == 4
    assert result.manifest_id.startswith("gemma_weight_prep_real_w4_")
    assert len(result.manifest_sha256) == 64


def test_same_prompt_is_deterministic_and_different_prompt_changes_output() -> None:
    first = run_mock_gemma_chat("same prompt")
    second = run_mock_gemma_chat("same prompt")
    third = run_mock_gemma_chat("different prompt")

    assert first == second
    assert first.output_text != third.output_text


def test_chat_session_records_history_and_passes_context() -> None:
    spec = GemmaArchSpec()
    session = ChatSession(arch_spec=spec, seed=19)

    first_context = session.context_for("first turn")
    first = session.send("first turn")
    assert first.prompt_tokens == tuple(GemmaTokenizer(spec).encode(first_context))
    assert session.history == [("first turn", first.output_text)]

    second_context = session.context_for("second turn")
    assert "first turn" in second_context
    assert first.output_text in second_context
    assert second_context.endswith("<start_of_turn>model\n")
    assert (
        "<start_of_turn>user\n"
        "first turn<end_of_turn>\n"
        "<start_of_turn>model\n"
    ) in second_context

    second = session.send("second turn")
    assert second.prompt_tokens == tuple(GemmaTokenizer(spec).encode(second_context))
    assert session.history == [
        ("first turn", first.output_text),
        ("second turn", second.output_text),
    ]


def test_chat_session_same_seed_and_prompts_is_deterministic() -> None:
    prompts = ("alpha", "beta", "gamma")

    def run_session(seed: int) -> tuple[str, ...]:
        session = ChatSession(seed=seed)
        return tuple(session.send(prompt).output_text for prompt in prompts)

    assert run_session(7) == run_session(7)
    assert run_session(7) != run_session(8)


def test_orchestrator_uses_kv260_connection_mock_contract() -> None:
    orchestrator = GemmaE2EOrchestrator.create_mock("contract")

    assert isinstance(orchestrator.connection, KV260ConnectionMock)
    assert orchestrator.connection.is_reachable() is True
    assert orchestrator.connection.xrt_present() is True


def test_real_serial_path_is_stubbed() -> None:
    assert_raises(
        RealSerialGemmaE2ENotImplemented,
        lambda: GemmaE2EOrchestrator.create_real_serial_stub(),
    )


def test_source_has_offline_and_claim_guards() -> None:
    paths = [
        ROOT / "contracts" / "gemma_e2e_orchestrator.py",
        ROOT / "contracts" / "kv260_connection_mock.py",
        TEST_PATH,
    ]
    source = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    lowered = source.lower()

    forbidden_runtime_terms = [
        "trans" + "formers",
        "hugging" + "face_hub",
        "hf_hub_" + "download",
        "from_" + "pretrained",
        ".safe" + "tensors",
        ".g" + "guf",
        ".p" + "th",
        "req" + "uests",
        "url" + "lib",
        "sub" + "process",
        "sock" + "et",
        "/dev/" + "mem",
        "serial" + ".serial",
        "KVFPGA_PASSWORD",
        "KVFPGA_USER",
        "KVFPGA_HOST",
    ]
    for term in forbidden_runtime_terms:
        assert term not in lowered, term

    forbidden_claims = [
        "production-" + "ready",
        "marketplace-" + "ready",
        "stable " + "API",
        "stable " + "ABI",
        "KV260 inference " + "works",
        "Gemma 3N E4B " + "runs on KV260",
        "20 tok/s " + "achieved",
        "timing " + "closed",
        "bitstream " + "ready",
    ]
    for claim in forbidden_claims:
        assert claim.lower() not in lowered, claim
    assert not re.search(r"\bHF_[A-Z0-9_]+\b", source)


def test_source_headers_for_touched_python_files() -> None:
    for path in [
        ROOT / "contracts" / "gemma_e2e_orchestrator.py",
        ROOT / "contracts" / "kv260_connection_mock.py",
        TEST_PATH,
    ]:
        assert path.read_text(encoding="utf-8").splitlines()[:3] == [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ]


test_mock_orchestrator_runs_full_prompt_to_text_path()
test_same_prompt_is_deterministic_and_different_prompt_changes_output()
test_chat_session_records_history_and_passes_context()
test_chat_session_same_seed_and_prompts_is_deterministic()
test_orchestrator_uses_kv260_connection_mock_contract()
test_real_serial_path_is_stubbed()
test_source_has_offline_and_claim_guards()
test_source_headers_for_touched_python_files()

print("Gemma E2E orchestrator tests ok")
