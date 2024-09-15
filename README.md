# quantize_labels

Quantizes Audacity labels according to a reference label track.

```console

 Usage: quantize_labels.py [OPTIONS] REFERENCE_FILE TARGET_FILE

 Quantize labels in the target file to the reference file.

╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    reference_file      TEXT  Path to the reference label file. [default: None] [required]                                                               │
│ *    target_file         TEXT  Path to the target label file. [default: None] [required]                                                                  │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --verbose  -v        Enable verbose output.                                                                                                               │
│ --help               Show this message and exit.                                                                                                          │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

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
[rebuildap](https://github.com/bwagner/rebuildap), [shift_labels](https://github.com/bwagner/shift_labels), [pyaudacity](https://github.com/bwagner/pyaudacity)
