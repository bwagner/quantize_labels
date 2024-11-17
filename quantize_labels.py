#!/usr/bin/env python

import sys
from typing import Generator, Tuple, Union

import typer


def file_line_generator(file_path: str) -> Generator[str, None, None]:
    """
    Generator that yields lines from a file, ensuring the file handle stays open during iteration.
    """
    with open(file_path, "r") as file:
        for line in file:
            yield line


def read_labels(
    lines: Generator[str, None, None],
) -> Generator[Union[float, Tuple[float, float, str]], None, None]:
    """
    Generator to parse label times from lines of a file.
    Supports:
    - Single-column format: A single timestamp per line.
    - Audacity label format: 'start_time end_time label' (tab-separated).
    """
    for line in lines:
        parts = line.strip().split("\t")
        if len(parts) == 1:
            # Single-column format
            yield float(parts[0])
        elif len(parts) >= 2:
            # Audacity label format, include label if present
            start_time = float(parts[0])
            end_time = float(parts[1])
            label = parts[2] if len(parts) > 2 else ""
            yield (start_time, end_time, label)


def quantize_labels(
    reference_gen: Generator[Union[float, Tuple[float, float, str]], None, None],
    target_gen: Generator[Union[float, Tuple[float, float, str]], None, None],
) -> Generator[
    Union[Tuple[float, float, str, float, float], Tuple[float, float]], None, None
]:
    """
    Quantize target labels to the nearest reference label.
    Supports both single-column and Audacity label formats for reference and target labels.
    Yields the adjusted labels along with the adjustments made for further processing.
    """
    # Extract start times from reference labels for quantization
    reference_list = [
        (
            ref if isinstance(ref, float) else ref[0]
        )  # Use start time if it's an Audacity label
        for ref in reference_gen
    ]

    for target_label in target_gen:
        if isinstance(target_label, tuple):
            # Audacity label format
            start_time = target_label[0]
            end_time = target_label[1]

            # Quantize both start and end times independently
            nearest_start = min(reference_list, key=lambda ref: abs(ref - start_time))
            nearest_end = min(reference_list, key=lambda ref: abs(ref - end_time))

            start_adjustment = nearest_start - start_time
            end_adjustment = nearest_end - end_time

            # Yield the adjusted label and adjustments
            yield (
                nearest_start,
                nearest_end,
                target_label[2],
                start_adjustment,
                end_adjustment,
            )

        else:
            # Single-column format
            nearest_reference = min(
                reference_list, key=lambda ref: abs(ref - target_label)
            )
            adjustment = nearest_reference - target_label

            # Yield the adjusted label and adjustment
            yield (nearest_reference, adjustment)


def main(
    reference_file: str = typer.Argument(..., help="Path to the reference label file."),
    target_file: str = typer.Argument(..., help="Path to the target label file."),
    inplace: bool = typer.Option(
        False,
        "--inplace",
        "-i",
        help="Apply quantizations directly to the TARGET_FILE.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output."
    ),
):
    """Quantize labels in the target file to the reference file."""
    # Use file_line_generator within the context of the main function to keep the file handle open
    reference_lines = file_line_generator(reference_file)
    target_lines = file_line_generator(target_file)

    reference_gen = read_labels(reference_lines)
    target_gen = read_labels(target_lines)

    output_lines = []

    # Initialize totals for summary statistics
    total_adjustment = 0
    count = 0

    # Iterate over the quantized labels and process results
    for result in quantize_labels(reference_gen, target_gen):
        if isinstance(result, tuple) and len(result) == 5:
            # Audacity label format
            nearest_start, nearest_end, label, start_adjustment, end_adjustment = result
            line = f"{nearest_start}\t{nearest_end}\t{label}"
            output_lines.append(line)

            # Verbose output
            if verbose:
                print(
                    f"Adjusted start {nearest_start} {'->' if start_adjustment > 0 else '<-'} {abs(start_adjustment):.6f}",
                    file=sys.stderr,
                )
                print(
                    f"Adjusted end {nearest_end} {'->' if end_adjustment > 0 else '<-'} {abs(end_adjustment):.6f}",
                    file=sys.stderr,
                )

            # Update total adjustments and count
            total_adjustment += abs(start_adjustment) + abs(end_adjustment)
            count += 2

        elif isinstance(result, tuple) and len(result) == 2:
            # Single-column format
            nearest_reference, adjustment = result
            line = f"{nearest_reference}"
            output_lines.append(line)

            # Verbose output
            if verbose:
                print(f"Adjusted -> {abs(adjustment):.6f}", file=sys.stderr)

            # Update total adjustments and count
            total_adjustment += abs(adjustment)
            count += 1

    # Output to file or stdout
    if inplace:
        with open(target_file, "w") as f:
            f.write("\n".join(output_lines) + "\n")
    else:
        print("\n".join(output_lines))

    # Calculate summary statistics
    if count > 0:
        avg_adjustment = total_adjustment / count
    else:
        avg_adjustment = 0

    # Print summary to stderr
    summary_message = (
        f"\nTotal adjustment: {total_adjustment:.6f} seconds\n"
        f"Average adjustment: {avg_adjustment:.6f} seconds\n"
    )
    print(summary_message, file=sys.stderr)


if __name__ == "__main__":
    typer.run(main)
