#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 pccxai
"""Type-only tests for the KV260 readiness scaffold."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "contracts" / "kv260_readiness_scaffold.py"
DOC_PATH = ROOT / "docs" / "KV260_DATA_ONLY_READINESS_SCAFFOLD.md"
TEST_PATH = Path(__file__).resolve()


def load_module():
    spec = importlib.util.spec_from_file_location(
        "kv260_readiness_scaffold",
        MODULE_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_raises_not_implemented(func) -> None:
    try:
        func()
    except NotImplementedError:
        return
    raise AssertionError("expected NotImplementedError")


def test_connection_env_presence_only_and_skip_if_unset() -> None:
    module = load_module()
    env_names = ("KVFPGA_HOST", "KVFPGA_USER", "KVFPGA_PASSWORD")
    if not all(os.environ.get(name) for name in env_names):
        print("skip: KVFPGA_* env unset")

    fake_env = {
        "KVFPGA_HOST": "kv260.example.invalid",
        "KVFPGA_USER": "kvuser",
        "KVFPGA_PASSWORD": "redacted-test-password",
    }
    connection = module.KV260Connection.from_env(fake_env)
    rendered = repr(connection)

    assert connection.is_configured() is True
    assert connection.host_configured is True
    assert connection.user_configured is True
    assert connection.password_configured is True
    for value in fake_env.values():
        assert value not in rendered

    assert_raises_not_implemented(connection.is_reachable)
    assert_raises_not_implemented(connection.kernel_uname)
    assert_raises_not_implemented(connection.xrt_present)
    assert_raises_not_implemented(connection.xmutil_listapps)


def test_status_manifest_and_pipeline_shapes() -> None:
    module = load_module()
    status = module.NPUStatus(
        bitstream_loaded=False,
        bitstream_uuid=None,
        axi_base_addr=None,
        axi_stat_register_value=None,
        last_error=None,
    )
    source = module.HFWeightSource(model_id="gemma3n-e4b", revision=None)
    manifest = module.GemmaWeightManifest(
        schema_version="pccx.gemmaWeightManifest.v0",
        model_id=source.model_id,
        source_revision=source.revision,
        weight_format="W4",
        activation_format="A8",
        tensor_count=0,
        artifact_paths=(),
        checksums={},
        evidence_refs=("future_weight_prep_evidence",),
        limitations=("data_only_scaffold",),
    )

    assert status.bitstream_loaded is False
    assert manifest.weight_format == "W4"
    assert manifest.activation_format == "A8"

    prep = module.GemmaWeightPrep()
    assert_raises_not_implemented(lambda: prep.load_hf(source))
    assert_raises_not_implemented(
        lambda: prep.quantize_W4(module.LoadedHFWeights(source=source)),
    )
    assert_raises_not_implemented(
        lambda: prep.quantize_A8(module.QuantizedW4Weights(source=source)),
    )
    assert_raises_not_implemented(
        lambda: prep.emit_manifest(module.QuantizedA8Weights(source=source)),
    )


def test_axi_shapes_and_result_stream_are_typed_only() -> None:
    module = load_module()
    cmd = module.NpuCmd(0x4000000000000001)
    busy = module.NpuStat(module.UCA_STAT_BUSY)
    done = module.NpuStat(module.UCA_STAT_DONE)
    empty = module.EmptyResultStream()

    assert cmd.lo32 == 0x00000001
    assert cmd.hi32 == 0x40000000
    assert busy.busy is True
    assert busy.done is False
    assert done.busy is False
    assert done.done is True
    assert done.reserved == 0
    assert list(empty) == []

    try:
        module.NpuCmd(0x1_0000_0000_0000_0000)
    except ValueError:
        pass
    else:
        raise AssertionError("expected NpuCmd width guard")

    try:
        module.NpuStat(0x1_0000_0000)
    except ValueError:
        pass
    else:
        raise AssertionError("expected NpuStat width guard")


def test_source_does_not_contain_board_or_model_actions() -> None:
    source = read_text(MODULE_PATH)
    doc = read_text(DOC_PATH)
    scan_text = "\n".join([source, doc])
    forbidden_terms = [
        "subprocess",
        "os.system",
        "popen",
        "socket",
        "paramiko",
        "requests",
        "urllib",
        "transformers",
        "huggingface_hub",
        "mmap",
        "/dev/mem",
        "ssh ",
        "scp ",
    ]
    for term in forbidden_terms:
        assert term not in source.lower(), term

    assert "print(" not in source
    assert "logging." not in source
    assert "redacted-test-password" not in scan_text

    forbidden_claims = [
        "production-ready",
        "marketplace-ready",
        "stable API",
        "stable ABI",
        "KV260 inference works",
        "Gemma 3N E4B runs on KV260",
        "20 tok/s achieved",
        "timing closed",
        "bitstream ready",
    ]
    lowered = scan_text.lower()
    for claim in forbidden_claims:
        assert claim.lower() not in lowered, claim


def test_source_headers_for_touched_code_files() -> None:
    expected_headers = {
        MODULE_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
        TEST_PATH: [
            "#!/usr/bin/env python3",
            "# SPDX-License-Identifier: Apache-2.0",
            "# Copyright 2026 pccxai",
        ],
    }
    for path, header in expected_headers.items():
        assert read_text(path).splitlines()[: len(header)] == header, path


test_connection_env_presence_only_and_skip_if_unset()
test_status_manifest_and_pipeline_shapes()
test_axi_shapes_and_result_stream_are_typed_only()
test_source_does_not_contain_board_or_model_actions()
test_source_headers_for_touched_code_files()

print("kv260 readiness scaffold tests ok")
