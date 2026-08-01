"""CLI entry point of the application."""

from __future__ import annotations

import argparse
import sys

from app import __version__
from app.calculator import add, divide, multiply, power, subtract

OPERATIONS = {
    "add": add,
    "sub": subtract,
    "mul": multiply,
    "div": divide,
    "pow": power,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="calc",
        description="Simple calculator used in the CI/CD lab.",
    )
    parser.add_argument("--version", action="version", version=f"calc {__version__}")
    parser.add_argument("operation", choices=OPERATIONS.keys(), help="Operation to run")
    parser.add_argument("a", type=float, help="First operand")
    parser.add_argument("b", type=float, help="Second operand")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = OPERATIONS[args.operation](args.a, args.b)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
