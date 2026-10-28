"""Command-line evaluation and report output."""

import argparse
import sys
from pathlib import Path

from .engine import evaluate_files
from .models import VERSION, error_report


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(3, f"{self.prog}: error: {message}\n")


def main(argv: list[str] | None = None) -> int:
    parser = Parser(prog="agentrelease", description="Evaluate supplied release test evidence.")
    parser.add_argument("--version", action="version", version=f"AgentRelease {VERSION}")
    commands = parser.add_subparsers(dest="command", required=True)
    evaluation = commands.add_parser("evaluate", help="Evaluate evidence against a policy.")
    evaluation.add_argument("--policy", required=True, type=Path, help="YAML policy file.")
    evaluation.add_argument("--evidence", required=True, type=Path, help="JSON evidence file.")
    evaluation.add_argument("--format", choices=("text", "json"), default="text")
    evaluation.add_argument("--output", type=Path, help="Save the report to a file.")
    args = parser.parse_args(argv)
    report = evaluate_files(args.policy, args.evidence)
    content = report.to_json() if args.format == "json" else report.to_text()
    try:
        if args.output:
            inputs = {args.policy.resolve(), args.evidence.resolve()}
            if args.output.resolve() in inputs or any(
                args.output.exists() and args.output.samefile(path)
                for path in inputs
                if path.exists()
            ):
                raise OSError("Output must not overwrite an input file.")
            args.output.write_text(content, encoding="utf-8")
        else:
            sys.stdout.write(content)
    except (OSError, UnicodeError, ValueError):
        error = error_report("OUTPUT_IO", "Cannot write report; input files cannot be overwritten.")
        sys.stderr.write(error.to_json() if args.format == "json" else error.to_text())
        return 3
    return report.status.exit_code
