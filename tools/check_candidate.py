"""Check a local candidate in a fresh environment and write a sanitized result."""

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import tarfile
import tempfile
import venv
from pathlib import Path


class ReviewFailure(RuntimeError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(
    arguments: list[str | Path],
    cwd: Path,
    environment: dict[str, str],
    label: str,
    expected: int = 0,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(value) for value in arguments],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != expected:
        raise ReviewFailure(label)
    return result


def check_candidate(artifacts: Path, wheelhouse: Path | None) -> dict[str, object]:
    checks: list[dict[str, str]] = []
    report: dict[str, object] = {
        "schema_version": 1,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "python": platform.python_version(),
        "checks": checks,
        "automated_review": "failed",
        "independent_acceptance": "pending",
        "manual_review_required": True,
    }

    def record(label: str, passed: bool = True) -> None:
        checks.append({"check": label, "result": "passed" if passed else "failed"})
        if not passed:
            raise ReviewFailure(label)

    try:
        verified = {}
        for line in (artifacts / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
            expected, name = line.split("  ", 1)
            if Path(name).name != name or not re.fullmatch(r"[a-f0-9]{64}", expected):
                raise ReviewFailure("Checksum manifest format")
            if digest(artifacts / name) != expected:
                raise ReviewFailure("Artifact integrity")
            verified[name] = expected
        metadata = json.loads((artifacts / "BUILD-METADATA.json").read_text(encoding="utf-8"))
        package_version = metadata["version"]
        commit = metadata["source_commit"]
        if not isinstance(package_version, str) or not re.fullmatch(
            r"[0-9][0-9A-Za-z.+-]*",
            package_version,
        ):
            raise ReviewFailure("Candidate version")
        if not isinstance(commit, str) or not re.fullmatch(r"[a-f0-9]{40}", commit):
            raise ReviewFailure("Candidate source identity")
        archive_name = f"agentrelease-{package_version}.tar.gz"
        wheel_name = f"agentrelease-{package_version}-py3-none-any.whl"
        if not {archive_name, wheel_name, "BUILD-METADATA.json"}.issubset(verified):
            raise ReviewFailure("Required candidate artifacts")
        report.update(
            version=package_version,
            source_commit=commit,
            artifact_sha256={name: verified[name] for name in (archive_name, wheel_name)},
        )
        record("Artifact integrity")
        environment = os.environ.copy()
        for name in (
            "PYTHONPATH",
            "PYTHONHOME",
            "PYTHONOPTIMIZE",
            "PIP_INDEX_URL",
            "PIP_EXTRA_INDEX_URL",
            "PIP_TRUSTED_HOST",
        ):
            environment.pop(name, None)
        environment.update(
            PYTHONNOUSERSITE="1", PIP_CONFIG_FILE=os.devnull, PIP_DISABLE_PIP_VERSION_CHECK="1"
        )
        with tempfile.TemporaryDirectory(prefix="agentrelease-review-") as directory:
            work = Path(directory)
            with tarfile.open(artifacts / archive_name) as archive:
                archive.extractall(work, filter="data")
            source = work / f"agentrelease-{package_version}"
            isolated = work / "environment"
            venv.EnvBuilder(with_pip=True).create(isolated)
            python = isolated / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            index = (
                ["--no-index", "--find-links", str(wheelhouse)]
                if wheelhouse
                else ["--index-url", "https://pypi.org/simple"]
            )
            run(
                [
                    python,
                    "-m",
                    "pip",
                    "install",
                    *index,
                    "--require-hashes",
                    "-r",
                    source / "requirements/runtime.txt",
                ],
                source,
                environment,
                "Runtime installation",
            )
            run(
                [python, "-m", "pip", "install", "--no-index", "--no-deps", artifacts / wheel_name],
                source,
                environment,
                "Wheel installation",
            )
            run([python, "-m", "pip", "check"], source, environment, "Dependency consistency")
            record("Clean installation and dependency consistency")
            cli: list[str | Path] = [python, "-I", "-m", "agentrelease"]
            version_result = run([*cli, "--version"], source, environment, "CLI version")
            record(
                "CLI version", version_result.stdout.strip() == f"AgentRelease {package_version}"
            )
            base: list[str | Path] = [
                *cli,
                "evaluate",
                "--policy",
                "examples/policy.yaml",
                "--evidence",
            ]
            for name, exit_code, status in [
                ("pass", 0, "PASS"),
                ("fail", 1, "FAIL"),
                ("missing", 2, "INCONCLUSIVE"),
                ("skipped", 2, "INCONCLUSIVE"),
                ("invalid", 3, "ERROR"),
            ]:
                result = run(
                    [*base, f"examples/evidence-{name}.json", "--format", "json"],
                    source,
                    environment,
                    f"Synthetic example: {name}",
                    exit_code,
                )
                record(f"Synthetic example: {name}", json.loads(result.stdout)["status"] == status)
            text = [*base, "examples/evidence-pass.json"]
            first = run(text, source, environment, "Text report")
            second = run(text, source, environment, "Repeat text report")
            record("Report reproducibility", first.stdout == second.stdout)
            output = source / "review-report.json"
            output_command = [*text, "--format", "json", "--output", str(output)]
            run(output_command, source, environment, "JSON report output")
            before = output.read_bytes()
            record("JSON report checks", len(json.loads(before)["checks"]) == 3)
            result = run(output_command, source, environment, "Existing report protection", 3)
            record(
                "Existing report protection",
                output.read_bytes() == before
                and json.loads(result.stderr)["errors"][0]["code"] == "OUTPUT_IO",
            )
            policy = source / "examples/policy.yaml"
            original = policy.read_bytes()
            run([*text, "--output", str(policy)], source, environment, "Input protection", 3)
            record("Input protection", policy.read_bytes() == original)
            (source / "malformed.json").write_text("{", encoding="utf-8")
            result = run(
                [*base, "malformed.json", "--format", "json"],
                source,
                environment,
                "Malformed input",
                3,
            )
            record(
                "Malformed input",
                json.loads(result.stdout)["errors"][0]["code"] == "MALFORMED_INPUT",
            )
            api = run(
                [
                    python,
                    "-I",
                    "-c",
                    (
                        "from pathlib import Path; import agentrelease; "
                        "from agentrelease import Status, evaluate_files; "
                        "assert 'site-packages' in str(Path(agentrelease.__file__)); "
                        "r = evaluate_files("
                        "'examples/policy.yaml', 'examples/evidence-pass.json'); "
                        "assert r.status is Status.PASS; print(r.status)"
                    ),
                ],
                source,
                environment,
                "Installed Python API",
            )
            record("Installed Python API", api.stdout.strip() == "PASS")
        report["automated_review"] = "passed"
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        tarfile.TarError,
        subprocess.SubprocessError,
        ReviewFailure,
    ) as error:
        report["failure"] = (
            str(error) if isinstance(error, ReviewFailure) else "Review could not complete"
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--wheelhouse", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output filename.")
    report = check_candidate(
        args.artifacts.resolve(), args.wheelhouse.resolve() if args.wheelhouse else None
    )
    try:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(report, sort_keys=True, indent=2) + "\n")
    except OSError:
        parser.exit(1, "Cannot write review result; choose a new writable filename.\n")
    print(f"Automated review: {report['automated_review']}. Independent acceptance: pending.")
    return 0 if report["automated_review"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
