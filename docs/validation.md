# Validation results

Validation date: 2026-10-28.

Environment: macOS on Apple Silicon, Python 3.12.9.
Runtime dependency: PyYAML 6.0.3.
Tools: pytest 9.2.0, Ruff 0.17.3, build 1.6.1; isolated build backend:
setuptools 82.0.1.

## Checks

| Check | Result |
| --- | --- |
| `pytest -q` | 147 passed |
| `ruff check .` | Passed |
| `ruff format --check .` | Passed |
| `git diff --check` | Passed |
| `python -m build` | Source distribution and wheel built successfully |
| Clean wheel installation | Passed in a fresh virtual environment outside the checkout |
| Installed dependency consistency (`pip check`) | Passed |
| Installed CLI and module entry points | Passed |
| Installed API and repeat evaluation | Passed with identical JSON output |

## Required evaluation cases

| Case | Verified result |
| --- | --- |
| All mandatory criteria satisfied | PASS, exit 0 |
| Mandatory test failed | FAIL, exit 1 |
| Mandatory test missing | INCONCLUSIVE, exit 2 |
| Mandatory test skipped | INCONCLUSIVE, exit 2 |
| Metric violates threshold | FAIL, exit 1 |
| Malformed input | ERROR, exit 3 |
| Duplicate identifiers or mapping keys | ERROR, exit 3 |
| Unknown test or metric reference | ERROR, exit 3 |
| Identical inputs evaluated repeatedly | Identical result and report |
| Failure combined with missing evidence | FAIL; individual missing checks remain visible |
| Invalid input combined with failure | ERROR; no partial checks |

Additional tests cover all six numeric operators and their boundaries, booleans
and nonfinite numbers, schema versions, unknown fields, missing measurements,
empty evidence, unsafe YAML tags, aliases, encoding, file size, I/O errors,
unexpected evaluation errors, immutable reports and input preservation.
CLI tests cover text and JSON reports, output files, usage errors, help,
version, reproducibility and refusal to overwrite inputs through direct paths,
symlinks or hard links.

The clean installation check uses `scripts/check_install.py`. It creates an
empty virtual environment in a temporary directory, installs the wheel and
its runtime dependency, runs `pip check`, and checks all five synthetic CLI
examples and the Python API. The API check runs with isolated imports and
confirms the package is loaded from the installed environment. It does not
import the checkout's source tree.

## Reproduce

From a checkout with Python 3.12 or newer:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest -q
ruff check .
ruff format --check .
git diff --check
python -m build
python scripts/check_install.py dist/agentrelease-0.1.0-py3-none-any.whl
```

Dependency installation and isolated builds may need network access. Evaluation
itself runs locally. This validation does not establish test coverage for other
operating systems or Python versions, real agents, evidence authenticity,
external integrations or general agent safety. No hosted CI, paid service,
PyPI publication or release is part of these checks.
