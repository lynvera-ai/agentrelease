"""Check a built wheel in a clean environment outside the checkout."""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import venv
from pathlib import Path


def run(args, cwd, env):
    return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, check=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    wheel = args.wheel.resolve(strict=True)
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="agentrelease-install-") as directory:
        work = Path(directory)
        environment = work / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        binaries = environment / ("Scripts" if os.name == "nt" else "bin")
        python = binaries / ("python.exe" if os.name == "nt" else "python")
        command = binaries / ("agentrelease.exe" if os.name == "nt" else "agentrelease")
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env.pop("PYTHONHOME", None)
        env["PYTHONNOUSERSITE"] = "1"
        installation = run([str(python), "-m", "pip", "install", str(wheel)], work, env)
        if installation.returncode:
            raise RuntimeError(installation.stderr)
        dependency_check = run([str(python), "-m", "pip", "check"], work, env)
        if dependency_check.returncode:
            raise RuntimeError(dependency_check.stdout + dependency_check.stderr)
        print("Clean wheel installation and dependency check: passed")
        shutil.copytree(root / "examples", work / "examples")
        cases = [
            ("pass", 0, "PASS"),
            ("fail", 1, "FAIL"),
            ("missing", 2, "INCONCLUSIVE"),
            ("skipped", 2, "INCONCLUSIVE"),
            ("invalid", 3, "ERROR"),
        ]
        for name, exit_code, status in cases:
            result = run(
                [
                    str(command),
                    "evaluate",
                    "--policy",
                    "examples/policy.yaml",
                    "--evidence",
                    f"examples/evidence-{name}.json",
                    "--format",
                    "json",
                ],
                work,
                env,
            )
            if result.returncode != exit_code or json.loads(result.stdout)["status"] != status:
                raise RuntimeError(f"Installed CLI failed the {name} case.")
            print(f"Installed CLI {name}: {status}, exit {exit_code}")
        api = run(
            [
                str(python),
                "-I",
                "-c",
                (
                    "from pathlib import Path; import agentrelease; "
                    "from agentrelease import Status, evaluate_files; "
                    "assert 'site-packages' in str(Path(agentrelease.__file__)); "
                    "report = evaluate_files("
                    "'examples/policy.yaml', 'examples/evidence-pass.json'); "
                    "assert report.status is Status.PASS; "
                    "assert report.to_json() == evaluate_files("
                    "'examples/policy.yaml', 'examples/evidence-pass.json').to_json(); "
                    "print('Installed API and reproducibility: passed')"
                ),
            ],
            work,
            env,
        )
        if api.returncode:
            raise RuntimeError(api.stderr)
        print(api.stdout.strip())
        module = run([str(python), "-I", "-m", "agentrelease", "--version"], work, env)
        if module.returncode or module.stdout.strip() != "AgentRelease 0.1.0":
            raise RuntimeError("Installed module entry point failed.")
        print("Installed module entry point: passed")


if __name__ == "__main__":
    main()
