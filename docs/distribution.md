# Local distribution and reproducible builds

Version 0.1.0 is distributed as an experimental GitHub prerelease, tagged
`v0.1.0`. The local build command below does not upload tags, releases or packages.

## Distribution choice

The project is a Python library and CLI using a `src` layout and setuptools.
Build a source distribution (`.tar.gz`) and a pure Python wheel
(`py3-none-any.whl`). The wheel is the preferred installation artifact because
it avoids a build step for the user. The source distribution includes examples,
documentation, tests, SVG assets and dependency requirements for inspection.
The platform-independent wheel tag describes its contents, not tested platform
coverage. PyYAML is a separate dependency with platform-specific wheels.

Tagged source and release downloads are available on
[GitHub](https://github.com/lynvera-ai/agentrelease/releases/tag/v0.1.0).
Publishing to PyPI is a separate decision and is not part of this release.
Keep local candidate builds separate from the published files; do not move
the tag or overwrite release artifacts when making later changes.

## Pinned environment

From a clean Git checkout with Python 3.12 or newer:

```sh
python3.12 -m venv .build-venv
.build-venv/bin/python -m pip install --require-hashes -r requirements/build.txt
.build-venv/bin/python tools/build_distribution.py --output dist/candidate
```

The build command requires a clean committed source tree and exact build tool
versions from `requirements/build.txt`. Bootstrapping the build environment
needs public package downloads unless dependencies are cached. The build
itself uses no network: it invokes `build --no-isolation` with those installed
tools and builds a wheel from the source distribution.

No tracked or untracked local edits are included: source comes from `git archive`
of the recorded commit. Git metadata, ignored environments, caches, logs and
reports are excluded. The manifest includes only the intended package and
review material; the issue template stays in the repository, not in packages.

`tools/build_distribution.py` sets `SOURCE_DATE_EPOCH` to the source commit
timestamp, fixes the Python hash seed, normalizes source archive ordering,
timestamps, ownership and permissions, and removes gzip filename metadata.
This addresses archive metadata that would otherwise vary between builds.
Do not infer byte reproducibility across other platforms or toolchains without
repeating the comparison there.

## Artifacts and provenance

`dist/candidate` contains:

- `agentrelease-0.1.0-py3-none-any.whl`
- `agentrelease-0.1.0.tar.gz`
- `SHA256SUMS`
- `BUILD-METADATA.json`
- `RELEASE-NOTES.md`

The metadata records the exact source commit, source timestamp, Python,
operating system and architecture, build tool versions, dependency-requirement
hashes and artifact hashes. It excludes hostnames, usernames, personal paths,
environment variables, credentials and execution logs. Acceptance is pending.
SHA256SUMS covers the package artifacts, candidate notes and metadata. Neither file
is a digital signature or independent attestation.

Build again from the same clean commit into a separate directory:

```sh
.build-venv/bin/python tools/build_distribution.py --output dist/rebuild
cmp dist/candidate/agentrelease-0.1.0.tar.gz dist/rebuild/agentrelease-0.1.0.tar.gz
cmp dist/candidate/agentrelease-0.1.0-py3-none-any.whl dist/rebuild/agentrelease-0.1.0-py3-none-any.whl
```

Successful `cmp` commands produce no output and exit 0. The builder refuses an
existing output directory; choose another location for additional candidates.
Generated files stay ignored locally. Do not commit build logs or virtual
environments. Keep the candidate hashes with review evidence.

## Dependency integrity

`requirements/runtime.txt`, `build.txt`, `typing.txt` and `development.txt` pin the candidate
environment and include SHA-256 hashes from original package distributions.
The project's install metadata retains bounded dependency ranges; the locks
identify the exact environment reviewed here. They include distribution hashes
for other platforms without claiming those platforms have been validated.

For an offline review, download the runtime wheelhouse as described in
[installation](installation.md#offline-installation). Run `pip check` after
installation and the [external review steps](external-review.md). Do not upload
the wheelhouse as if it were original AgentRelease code; dependencies retain
their own notices and licenses.

The workflow uses the [Python packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/),
[setuptools distribution controls](https://setuptools.pypa.io/en/latest/userguide/miscellaneous.html)
and [pip hash checking](https://pip.pypa.io/en/stable/topics/secure-installs/).
