import subprocess
import sys
from pathlib import Path

import pytest

import quantize_labels as ql


def test_parse_args_minimal():
    ns = ql.parse_args(["ref.txt", "tgt.txt"])
    assert ns.reference_file == "ref.txt"
    assert ns.target_file == "tgt.txt"
    assert ns.inplace is False
    assert ns.verbose is False


def test_parse_args_inplace_short():
    ns = ql.parse_args(["ref.txt", "tgt.txt", "-i"])
    assert ns.inplace is True


def test_parse_args_inplace_long():
    ns = ql.parse_args(["ref.txt", "tgt.txt", "--inplace"])
    assert ns.inplace is True


def test_parse_args_verbose_short():
    ns = ql.parse_args(["ref.txt", "tgt.txt", "-v"])
    assert ns.verbose is True


def test_parse_args_missing_required():
    with pytest.raises(SystemExit):
        ql.parse_args([])


def test_module_does_not_import_typer():
    import importlib
    import sys as _sys

    _sys.modules.pop("quantize_labels", None)
    mod = importlib.import_module("quantize_labels")
    assert "typer" not in _sys.modules or mod.__dict__.get("typer") is None


def test_end_to_end_single_column(tmp_path: Path):
    ref = tmp_path / "ref.txt"
    tgt = tmp_path / "tgt.txt"
    ref.write_text("0.0\n1.0\n2.0\n")
    tgt.write_text("0.1\n0.9\n2.2\n")
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).parent / "quantize_labels.py"),
            str(ref),
            str(tgt),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = result.stdout.strip().splitlines()
    assert lines == ["0.0", "1.0", "2.0"]
