"""Build a local candidate from a clean Git commit without network access."""

import argparse
import gzip
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from importlib.metadata import version
from pathlib import Path

from packaging.requirements import Requirement


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_sdist(raw: Path, output: Path, epoch: int) -> None:
    with (
        tarfile.open(raw) as source,
        output.open("xb") as target,
        gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=epoch) as compressed,
        tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive,
    ):
        for member in sorted(source.getmembers(), key=lambda item: item.name):
            member.uid = member.gid = 0
            member.uname = member.gname = ""
            member.mtime = epoch
            member.mode = 0o755 if member.isdir() else 0o644
            member.pax_headers = {}
            content = source.extractfile(member) if member.isfile() else None
            archive.addfile(member, content)


def build(source: Path, output: Path, kind: str, env: dict[str, str]) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            f"--{kind}",
            "--no-isolation",
            "--outdir",
            str(output),
            str(source),
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"{kind} build failed; check the pinned build environment.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("dist/candidate"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if git(root, "status", "--porcelain"):
        raise RuntimeError("Commit or set aside local changes before building.")
    commit = git(root, "rev-parse", "HEAD")
    epoch = int(git(root, "show", "-s", "--format=%ct", commit))
    tools = {}
    for line in (root / "requirements/build.txt").read_text().splitlines():
        if "==" not in line:
            continue
        requirement = Requirement(line.rstrip(" \\"))
        if requirement.marker and not requirement.marker.evaluate():
            continue
        actual = version(requirement.name)
        if actual not in requirement.specifier:
            raise RuntimeError(f"Install requirements/build.txt: {requirement} is required.")
        tools[requirement.name] = actual
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("Output directory already exists; choose a new directory.")
    settings = tomllib.loads((root / "pyproject.toml").read_text())
    package_version = settings["project"]["version"]
    environment = os.environ.copy()
    environment.update(SOURCE_DATE_EPOCH=str(epoch), PYTHONHASHSEED="0", TZ="UTC")
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    with tempfile.TemporaryDirectory(prefix="agentrelease-build-") as directory:
        work = Path(directory)
        source = work / "source"
        source.mkdir()
        content = subprocess.check_output(["git", "-C", str(root), "archive", commit])
        with tarfile.open(fileobj=io.BytesIO(content)) as archive:
            archive.extractall(source, filter="data")
        raw = work / "raw"
        build(source, raw, "sdist", environment)
        staged = work / "candidate"
        staged.mkdir()
        sdist = staged / f"agentrelease-{package_version}.tar.gz"
        normalize_sdist(raw / sdist.name, sdist, epoch)
        unpacked = work / "unpacked"
        with tarfile.open(sdist) as archive:
            archive.extractall(unpacked, filter="data")
        build(unpacked / f"agentrelease-{package_version}", staged, "wheel", environment)
        shutil.copyfile(source / "docs/release-notes/0.1.0.md", staged / "RELEASE-NOTES.md")
        artifacts = {path.name: digest(path) for path in sorted(staged.iterdir())}
        metadata = {
            "schema_version": 1,
            "project": "agentrelease",
            "version": package_version,
            "source_commit": commit,
            "source_date_epoch": epoch,
            "python": platform.python_version(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "macos": platform.mac_ver()[0],
            },
            "build_tools": tools,
            "requirement_sha256": {
                path.name: digest(path) for path in sorted((root / "requirements").glob("*.txt"))
            },
            "artifacts": artifacts,
            "external_acceptance": "pending",
            "publication": "not published by this build",
        }
        metadata_path = staged / "BUILD-METADATA.json"
        metadata_path.write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
        sums = artifacts | {metadata_path.name: digest(metadata_path)}
        (staged / "SHA256SUMS").write_text(
            "".join(f"{value}  {name}\n" for name, value in sorted(sums.items()))
        )
        shutil.copytree(staged, output)
    print(f"Built AgentRelease {package_version} from {commit}")
    for name, value in sorted(artifacts.items()):
        print(f"{value}  {name}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
