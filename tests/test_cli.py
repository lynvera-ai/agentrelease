import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run(
        [sys.executable, "-m", "agentrelease", *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("example", "code", "status"),
    [
        ("pass", 0, "PASS"),
        ("fail", 1, "FAIL"),
        ("missing", 2, "INCONCLUSIVE"),
        ("skipped", 2, "INCONCLUSIVE"),
        ("invalid", 3, "ERROR"),
    ],
)
@pytest.mark.parametrize("format", ["text", "json"])
def test_cli_exit_codes(example, code, status, format):
    result = run(
        "evaluate",
        "--policy",
        ROOT / "examples/policy.yaml",
        "--evidence",
        ROOT / f"examples/evidence-{example}.json",
        "--format",
        format,
    )
    assert result.returncode == code
    assert result.stderr == ""
    if format == "json":
        assert json.loads(result.stdout)["status"] == status
    else:
        assert result.stdout.startswith(f"AgentRelease: {status}\n")


def test_malformed_json_exit_code(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    result = run(
        "evaluate", "--policy", ROOT / "examples/policy.yaml", "--evidence", bad, "--format", "json"
    )
    assert result.returncode == 3
    assert json.loads(result.stdout)["errors"][0]["code"] == "MALFORMED_INPUT"


@pytest.mark.parametrize("args", [[], ["unknown"], ["evaluate"], ["evaluate", "--format", "other"]])
def test_usage_errors_exit_three(args):
    result = run(*args)
    assert result.returncode == 3
    assert "error:" in result.stderr


@pytest.mark.parametrize("args", [["--help"], ["evaluate", "--help"], ["--version"]])
def test_help_and_version_exit_zero(args):
    assert run(*args).returncode == 0


def test_report_saved_to_file(tmp_path):
    output = tmp_path / "report.json"
    result = run(
        "evaluate",
        "--policy",
        ROOT / "examples/policy.yaml",
        "--evidence",
        ROOT / "examples/evidence-pass.json",
        "--format",
        "json",
        "--output",
        output,
    )
    assert result.returncode == 0
    assert result.stdout == ""
    assert json.loads(output.read_text())["status"] == "PASS"


def test_output_failure_exit_three(tmp_path):
    result = run(
        "evaluate",
        "--policy",
        ROOT / "examples/policy.yaml",
        "--evidence",
        ROOT / "examples/evidence-pass.json",
        "--format",
        "json",
        "--output",
        tmp_path,
    )
    assert result.returncode == 3
    assert result.stdout == ""
    assert json.loads(result.stderr)["errors"][0]["code"] == "OUTPUT_IO"


@pytest.mark.parametrize("alias", ["same", "symlink", "hardlink"])
def test_output_cannot_overwrite_input(tmp_path, alias):
    policy = tmp_path / "policy.yaml"
    original = (ROOT / "examples/policy.yaml").read_bytes()
    policy.write_bytes(original)
    output = policy
    if alias != "same":
        output = tmp_path / "report.json"
        if alias == "symlink":
            output.symlink_to(policy)
        else:
            os.link(policy, output)
    result = run(
        "evaluate",
        "--policy",
        policy,
        "--evidence",
        ROOT / "examples/evidence-pass.json",
        "--output",
        output,
    )
    assert result.returncode == 3
    assert policy.read_bytes() == original


def test_cli_report_is_byte_reproducible():
    args = (
        "evaluate",
        "--policy",
        ROOT / "examples/policy.yaml",
        "--evidence",
        ROOT / "examples/evidence-pass.json",
        "--format",
        "json",
    )
    first, second = run(*args), run(*args)
    assert first.returncode == second.returncode == 0
    assert first.stdout == second.stdout
