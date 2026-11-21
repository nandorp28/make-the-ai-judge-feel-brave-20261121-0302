"""Write the competition entry: one short text that steadies its reader.

The program assembles the entry from its sentences, checks it against the
gate (UTF-8 text, 1 to 280 Unicode code points, not only whitespace), and
writes it to the output directory: the --output flag, the MAKEFUN_OUTPUT_DIR
environment variable, or /output when neither is given.

Standard library only. No network. Deterministic: the same input always
produces the same bytes.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

MAX_CHARS = 280
MIN_CHARS = 1
OUTPUT_NAME = "entry.txt"
DEFAULT_OUTPUT_DIR = "/output"

# The entry, sentence by sentence. Each sentence is one line of the text;
# the writer joins them with single spaces and ends the file there, with no
# trailing newline, so the byte count is exactly the text itself.
SENTENCES = [
    "Somewhere below you, a river is moving through the night.",
    "It carries every word you have ever read, like stones, and it does not hurry.",
    "The stones grow smooth.",
    "The water keeps going, clear and unhurried, toward a sea it has never seen \u2014 and has never needed to.",
]


def build_entry(sentences: list[str]) -> str:
    """Join the sentences into the entry text, collapsing stray space."""
    parts = [sentence.strip() for sentence in sentences]
    parts = [part for part in parts if part]
    return " ".join(parts)


def validate_entry(text: str) -> list[str]:
    """Check the text against the gate; return a list of problems found."""
    problems: list[str] = []
    if not text.strip():
        problems.append("entry is empty or only whitespace")
    count = len(text)
    if count < MIN_CHARS:
        problems.append(f"entry is {count} characters, below the {MIN_CHARS} minimum")
    if count > MAX_CHARS:
        problems.append(f"entry is {count} characters, above the {MAX_CHARS} maximum")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as exc:
        problems.append(f"entry is not valid UTF-8: {exc}")
    return problems


def resolve_output_dir(flag_value: str | None) -> Path:
    """Pick the output directory: flag, then environment, then the default."""
    if flag_value:
        return Path(flag_value)
    env_value = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_value:
        return Path(env_value)
    return Path(DEFAULT_OUTPUT_DIR)


def write_entry(text: str, output_dir: Path) -> Path:
    """Write the entry text to entry.txt inside the output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / OUTPUT_NAME
    target.write_text(text, encoding="utf-8")
    return target


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write the 'Make the AI judge feel brave' entry text."
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="output directory (default: $MAKEFUN_OUTPUT_DIR or /output)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the entry and print its length without writing",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    text = build_entry(SENTENCES)
    problems = validate_entry(text)
    if problems:
        for problem in problems:
            print(f"invalid entry: {problem}", file=sys.stderr)
        return 1
    if args.check:
        print(f"entry is valid: {len(text)} characters, {len(text.encode('utf-8'))} bytes")
        print(text)
        return 0
    target = write_entry(text, resolve_output_dir(args.output))
    print(f"wrote {len(text)} characters to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
