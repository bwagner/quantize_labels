# quantize_labels

Quantizes Audacity labels according to a reference label track.

```console
usage: quantize_labels.py [-h] [-i] [-v] reference_file target_file

Quantize labels in the target file to the reference file.

positional arguments:
  reference_file  Path to the reference label file.
  target_file     Path to the target label file.

options:
  -h, --help      show this help message and exit
  -i, --inplace   Apply quantizations directly to the TARGET_FILE.
  -v, --verbose   Enable verbose output.
```

## Behavior

The reference file defines a grid of time points. Each target boundary snaps
to the nearest point on that grid.

- **Single-column reference** — each line is one time point.
- **Audacity reference** (`start\tend\tlabel`) — both `start` and `end` of
  every reference row contribute to the grid, so a target end near a reference
  end will snap to that end rather than to a distant reference start.

## Install

The script uses a [uv](https://docs.astral.sh/uv/) shebang with PEP 723 inline
metadata. Only the standard library is required; uv still provisions a suitable
Python interpreter automatically on first run.

Install `uv`:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Run directly:
```bash
./quantize_labels.py REFERENCE_FILE TARGET_FILE
```

## TODO
- more generators
- simplify

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
