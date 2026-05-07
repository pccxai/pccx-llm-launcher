#!/usr/bin/env python3
"""Unit tests for the offline Gemma tokenizer adapter."""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "gemma_tokenizer.py"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "tokenizer" / "gemma3n-e4b.tokenizer.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_placeholder_round_trip_hello_world() -> None:
    module = load_module(MODULE_PATH, "gemma_tokenizer")
    tokenizer = module.GemmaTokenizer(FIXTURE_PATH)

    ids = tokenizer.encode("hello world")

    assert ids == [4, 5]
    assert tokenizer.decode(ids).split() == ["hello", "world"]
    assert tokenizer.decode(ids) == "hello world"


def test_default_path_uses_placeholder_fixture() -> None:
    module = load_module(MODULE_PATH, "gemma_tokenizer_default")
    tokenizer = module.load_default_gemma_tokenizer()

    assert tokenizer.config_path == FIXTURE_PATH
    assert tokenizer.decode(tokenizer.encode("hello world")) == "hello world"


def test_fixture_is_miniature_placeholder_vocab() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert fixture["source"] == "miniature_placeholder_fixture"
    assert "real Gemma tokenizer data" in fixture["contentPolicy"]
    assert len(fixture["vocab"]) == 50
    assert fixture["vocab"]["hello"] == 4
    assert fixture["vocab"]["world"] == 5


def test_local_bpe_shape_round_trip() -> None:
    module = load_module(MODULE_PATH, "gemma_tokenizer_bpe")
    config = {
        "tokenizerType": "sentencepiece_bpe",
        "unknownId": 0,
        "model": {
            "type": "BPE",
            "vocab": {
                "<unk>": 0,
                "▁hello": 1,
                "▁world": 2,
            },
            "merges": [
                "▁ h",
                "▁h e",
                "▁he l",
                "▁hel l",
                "▁hell o",
                "▁ w",
                "▁w o",
                "▁wo r",
                "▁wor l",
                "▁worl d",
            ],
        },
    }

    with tempfile.TemporaryDirectory() as directory:
        config_path = Path(directory) / "local-bpe-tokenizer.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        tokenizer = module.GemmaTokenizer(config_path)

        assert tokenizer.encode("hello world") == [1, 2]
        assert tokenizer.decode([1, 2]) == "hello world"


if __name__ == "__main__":
    test_placeholder_round_trip_hello_world()
    test_default_path_uses_placeholder_fixture()
    test_fixture_is_miniature_placeholder_vocab()
    test_local_bpe_shape_round_trip()
