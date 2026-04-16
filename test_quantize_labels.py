import subprocess
import sys
from pathlib import Path

import pytest

import quantize_labels as ql

SCRIPT = Path(__file__).parent / "quantize_labels.py"


def _run(*args, check=True):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=check,
    )


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


def test_already_quantized_notification(tmp_path: Path):
    ref = tmp_path / "ref.txt"
    tgt = tmp_path / "tgt.txt"
    ref.write_text("0.0\n1.0\n2.0\n")
    tgt.write_text("0.0\n1.0\n2.0\n")
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
    assert "already quantized" in result.stderr.lower()


def test_changes_no_already_quantized_notification(tmp_path: Path):
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
    assert "already quantized" not in result.stderr.lower()


# ---- unit: read_labels ----


def test_read_labels_single_column():
    result = list(ql.read_labels(iter(["0.0\n", "1.5\n", "2.75\n"])))
    assert result == [0.0, 1.5, 2.75]


def test_read_labels_audacity_format():
    result = list(ql.read_labels(iter(["0.0\t1.0\tfoo\n", "1.0\t2.5\tbar\n"])))
    assert result == [(0.0, 1.0, "foo"), (1.0, 2.5, "bar")]


def test_read_labels_audacity_no_label():
    result = list(ql.read_labels(iter(["0.0\t1.0\n"])))
    assert result == [(0.0, 1.0, "")]


# ---- unit: quantize_labels ----


def test_quantize_single_column_snaps_to_nearest():
    ref = iter([0.0, 1.0, 2.0])
    tgt = iter([0.1, 0.9, 2.2])
    result = list(ql.quantize_labels(ref, tgt))
    assert [r[0] for r in result] == [0.0, 1.0, 2.0]


def test_quantize_audacity_snaps_start_and_end_independently():
    ref = iter([0.0, 1.0, 2.0])
    tgt = iter([(0.1, 0.9, "x")])
    ((nearest_start, nearest_end, label, ds, de),) = ql.quantize_labels(ref, tgt)
    assert (nearest_start, nearest_end, label) == (0.0, 1.0, "x")
    assert ds == pytest.approx(-0.1)
    assert de == pytest.approx(0.1)


# ---- e2e: audacity format ----


def test_end_to_end_audacity(tmp_path: Path):
    # Flat-grid semantics: target boundaries snap to the union of all
    # reference start and end times.
    ref = tmp_path / "ref.txt"
    tgt = tmp_path / "tgt.txt"
    ref.write_text("0.0\t0.5\t\n1.0\t1.5\t\n2.0\t2.5\t\n")
    tgt.write_text("0.1\t0.4\tA\n1.1\t1.4\tB\n")
    result = _run(str(ref), str(tgt))
    lines = result.stdout.strip().splitlines()
    assert lines == ["0.0\t0.5\tA", "1.0\t1.5\tB"]


def test_audacity_end_snaps_to_reference_end(tmp_path: Path):
    # Target end near a reference END should snap to that end, not to a
    # distant reference START.
    ref = tmp_path / "ref.txt"
    tgt = tmp_path / "tgt.txt"
    ref.write_text("0.0\t0.5\t\n1.0\t1.5\t\n")
    tgt.write_text("0.1\t0.6\tA\n")
    result = _run(str(ref), str(tgt))
    assert result.stdout.strip().splitlines() == ["0.0\t0.5\tA"]


def test_quantize_audacity_end_snaps_to_reference_end():
    ref = iter([(0.0, 0.5, ""), (1.0, 1.5, "")])
    tgt = iter([(0.1, 0.6, "A")])
    ((ns, ne, lbl, _, _),) = ql.quantize_labels(ref, tgt)
    assert (ns, ne, lbl) == (0.0, 0.5, "A")


# ---- e2e: --inplace ----


def test_inplace_rewrites_target_and_empties_stdout(tmp_path: Path):
    ref = tmp_path / "ref.txt"
    tgt = tmp_path / "tgt.txt"
    ref.write_text("0.0\n1.0\n2.0\n")
    tgt.write_text("0.1\n0.9\n2.2\n")
    result = _run(str(ref), str(tgt), "-i")
    assert result.stdout == ""
    assert tgt.read_text().strip().splitlines() == ["0.0", "1.0", "2.0"]


# ---- e2e: --verbose ----


def test_verbose_emits_per_label_stderr(tmp_path: Path):
    ref = tmp_path / "ref.txt"
    tgt = tmp_path / "tgt.txt"
    ref.write_text("0.0\n1.0\n")
    tgt.write_text("0.1\n0.9\n")
    result = _run(str(ref), str(tgt), "-v")
    assert "Adjusted" in result.stderr


# ---- edge cases ----


def test_empty_target_does_not_crash(tmp_path: Path):
    ref = tmp_path / "ref.txt"
    tgt = tmp_path / "tgt.txt"
    ref.write_text("0.0\n1.0\n")
    tgt.write_text("")
    result = _run(str(ref), str(tgt))
    assert result.stdout.strip() == ""
    assert "already quantized" not in result.stderr.lower()


def test_malformed_input_exits_nonzero(tmp_path: Path):
    ref = tmp_path / "ref.txt"
    tgt = tmp_path / "tgt.txt"
    ref.write_text("0.0\n1.0\n")
    tgt.write_text("not-a-number\n")
    result = _run(str(ref), str(tgt), check=False)
    assert result.returncode != 0
