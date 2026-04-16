# quantize_labels

Quantizes Audacity labels according to a reference label track.

```console

 Usage: quantize_labels.py [OPTIONS] REFERENCE_FILE TARGET_FILE

 Quantize labels in the target file to the reference file.

╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────╮
│ *    reference_file      TEXT  Path to the reference label file. [default: None] [required]   │
│ *    target_file         TEXT  Path to the target label file. [default: None] [required]      │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────╮
│ --inplace  -i        Apply quantizations directly to the TARGET_FILE.                         │
│ --verbose  -v        Enable verbose output.                                                   │
│ --help               Show this message and exit.                                              │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯

```

## Install

The script uses a [uv](https://docs.astral.sh/uv/) shebang with PEP 723 inline
metadata, so dependencies (e.g. `typer`) are resolved automatically on first run.

Install `uv`:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Run directly:
```bash
./quantize_labels.py REFERENCE_FILE TARGET_FILE
```

## TODO
- tests
- more generators
- simplify
- notify when there were no changes.

## Contribute
```console
pre-commit install
```
if this fails
```
pip install pre-commit
```
(see [pre-commit](https://pre-commit.com/))

## See also
- [rebuildap](https://github.com/bwagner/rebuildap)
- [audacity_click_label](https://github.com/bwagner/audacity_click_label)
- [beats2bars](https://github.com/bwagner/beats2bars)
- [shift_labels](https://github.com/bwagner/shift_labels)
- [audacity_legatize](https://github.com/bwagner/audacity_legatize)
- [pyaudacity](https://github.com/bwagner/pyaudacity)
