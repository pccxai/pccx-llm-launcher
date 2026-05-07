#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Unit tests for Gemma mock tokenizer and architecture spec."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TEST_PATH = Path(__file__).resolve()

from contracts.gemma_arch_spec import GemmaArchSpec
from contracts.gemma_tokenizer import GemmaTokenizer


def assert_raises(error_type, callback) -> None:
    try:
        callback()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def test_arch_spec_validates_token_ranges() -> None:
    spec = GemmaArchSpec(vocab_size=1024, byte_token_offset=512)

    assert spec.model_id == "gemma3n-e4b"
    assert spec.target == "kv260"
    assert spec.w4_group_size == 64
    assert_raises(ValueError, lambda: GemmaArchSpec(vocab_size=300))
    assert_raises(ValueError, lambda: GemmaArchSpec(eos_token_id=2))


def test_tokenizer_round_trips_prompt_and_generated_text() -> None:
    tokenizer = GemmaTokenizer(GemmaArchSpec())

    prompt_tokens = tokenizer.encode("hello kv260")
    generated_tokens = tokenizer.encode_generated_text("mock-gemma:abcd")

    assert prompt_tokens[0] == tokenizer.arch_spec.bos_token_id
    assert prompt_tokens[-1] == tokenizer.arch_spec.eos_token_id
    assert tokenizer.decode(prompt_tokens) == "hello kv260"
    assert tokenizer.decode(generated_tokens) == "mock-gemma:abcd"


def test_source_has_offline_and_claim_guards() -> None:
    paths = [
        ROOT / "contracts" / "gemma_arch_spec.py",
        ROOT / "contracts" / "gemma_tokenizer.py",
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
        "req" + "uests",
        "url" + "lib",
        "sub" + "process",
        "sock" + "et",
        "/dev/" + "mem",
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
        ROOT / "contracts" / "gemma_arch_spec.py",
        ROOT / "contracts" / "gemma_tokenizer.py",
        TEST_PATH,
    ]:
        assert path.read_text(encoding="utf-8").splitlines()[:3] == [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ]


test_arch_spec_validates_token_ranges()
test_tokenizer_round_trips_prompt_and_generated_text()
test_source_has_offline_and_claim_guards()
test_source_headers_for_touched_python_files()

print("Gemma tokenizer and arch spec tests ok")
