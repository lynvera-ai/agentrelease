![Lynvera AgentRelease. Explicit policies. Reproducible reports.](assets/banner.svg)

# Lynvera AgentRelease

![Version 0.1.0](assets/badges/version.svg)
![Python 3.12 or newer](assets/badges/python.svg)
[![Apache License 2.0](assets/badges/license.svg)](LICENSE)

Experimental — under development.

AgentRelease compares supplied agent test evidence with explicit release
criteria and produces reproducible JSON and text reports. It is a local Python
library and command-line tool from Lynvera Intelligence.

Read the [Spanish quick start](docs/es/primeros-pasos.md),
[format reference](docs/formats.md), [installation guide](docs/installation.md)
and [external review steps](docs/external-review.md).

## When to use it

For developers and reviewers who already have test results and need a repeatable
release decision. For example, require a tool-boundary test to pass and an
accuracy measurement to reach 0.9. A failed test produces FAIL; missing evidence
produces INCONCLUSIVE. All bundled observations are synthetic.

PASS describes compliance with the supplied criteria only. It does not certify
general agent safety, verify evidence authenticity or guarantee agent behavior.
AgentRelease does not run agents or collect measurements.

## Install from source

Requires Python 3.12 or newer with `pip` and `venv`, plus Git for cloning.
From a new terminal on macOS or Linux:

```sh
git clone --branch v0.1.0 --single-branch https://github.com/lynvera-ai/agentrelease.git
cd agentrelease
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m pip check
agentrelease --version
```

Expected version: `AgentRelease 0.1.0`. Record `git rev-parse HEAD` to identify
the exact source used. The experimental [v0.1.0 GitHub release](https://github.com/lynvera-ai/agentrelease/releases/tag/v0.1.0)
provides the wheel, source archive and checksums. This version is not published
to PyPI; use the tagged source or a downloaded wheel rather than an unqualified
`pip install agentrelease`.

Installation may download small public build tools and PyYAML. Evaluation
requires no API key, model download, account, network connection or paid service.
PyYAML is the only runtime dependency. There are no optional integrations.
See [installation and offline use](docs/installation.md) for pinned dependencies,
wheel installation, updates, recovery and uninstalling.

## First evaluation

Run these commands from the source directory with the environment active:

```sh
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-pass.json
```

The first three output lines are:

```text
AgentRelease: PASS
Policy: synthetic-release
Evaluator version: 0.1.0
```

The remaining lines contain input fingerprints, three passing checks and the
scope statement. Exit code: `0`.

To save a JSON report, choose a new filename in a writable directory:

```sh
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-pass.json --format json --output report.json
python -c "import json; r = json.load(open('report.json')); print(r['status'], len(r['checks']))"
```

Expected output: `PASS 3`. Existing files, including previous reports, are never
overwritten. Choose another filename for a later run. `python -m agentrelease`
provides the same CLI.

## Interpret the result

| Status | Meaning | Exit code |
| --- | --- | --- |
| PASS | Every mandatory criterion has valid passing evidence | 0 |
| FAIL | Valid evidence violates a mandatory criterion | 1 |
| INCONCLUSIVE | A required test or measurement is absent, or a test was skipped | 2 |
| ERROR | Invalid input, evaluation error, file error or invalid CLI usage | 3 |

Priority: `ERROR > FAIL > INCONCLUSIVE > PASS`. Inputs are validated before
criteria are evaluated. ERROR has no partial checks. FAIL takes priority over
incomplete evidence, with both findings retained in individual checks.
Only PASS is an evaluation success; help and version commands also exit 0.

Try `evidence-fail.json`, `evidence-missing.json`, `evidence-skipped.json` and
`evidence-invalid.json` from `examples` with the same policy. Their expected
exit codes are 1, 2, 2 and 3 respectively.

Without `--output`, reports go to standard output, including input errors.
Usage and output errors go to standard error. Common errors are
`MALFORMED_INPUT`, `UNKNOWN_REFERENCE`, `INPUT_IO` and `OUTPUT_IO`.
Use `agentrelease evaluate --help` and the [format reference](docs/formats.md)
to diagnose a result without sharing private input files.

## Configure a policy

There is no global configuration, environment file or credential store.
Provide both file paths explicitly. Every policy test and metric is mandatory.
This is a complete synthetic example:

```yaml
schema_version: 1
id: synthetic-release
tests:
  - id: boundary
```

Matching JSON evidence:

```json
{"schema_version": 1, "tests": [{"id": "boundary", "status": "passed"}]}
```

Numeric rules support `>=`, `>`, `<=`, `<`, `==` and `!=`, with explicit finite
thresholds. Input files are UTF-8 and at most 5 MiB each. Unknown fields,
duplicate identifiers or keys, unknown references and invalid numbers are
errors. See [all fields and report semantics](docs/formats.md).

## Python API

```python
from agentrelease import Status, evaluate, evaluate_files

report = evaluate_files("examples/policy.yaml", "examples/evidence-pass.json")
assert report.status is Status.PASS
print(report.to_text())

policy = {"schema_version": 1, "id": "synthetic-release", "tests": [{"id": "boundary"}]}
evidence = {"schema_version": 1, "tests": [{"id": "boundary", "status": "passed"}]}
report = evaluate(policy, evidence)
data = report.to_dict()
json_report = report.to_json()
exit_code = report.status.exit_code
```

Invalid inputs return ERROR reports. Always inspect the status. Reports and
checks are immutable; input dictionaries are not modified.

## Maturity and known limits

Version 0.1.0 remains experimental, with alpha package metadata. The local test
suite exercises the supported API and CLI, but independent acceptance is
pending. This is not a beta or production-ready release.

- Local validation covers macOS Apple Silicon with Python 3.12, 3.13 and 3.14,
  and Linux ARM64 in a container with Python 3.12. Windows and other platform
  combinations remain pending. See the [exact validation matrix](docs/validation-matrix.md).
- Supplied observations are not authenticated. Test adequacy and trustworthy
  evidence collection remain the caller's responsibility.
- Numeric comparisons have no tolerance, rounding, unit conversion or
  statistical inference. Use consistent units and explicit thresholds.
- No optional criteria, framework integrations, test execution, scanners,
  dashboard, server, database, user authentication or paid APIs are included.
- A new report write is not transactional. An interrupted write can leave a
  partial new file; previous files are protected. Use a fresh filename to retry.
- File limits and restricted safe YAML parsing do not make this a hardened
  service for adversarial workloads. Public APIs and schemas may change.

See the [candidate notes](docs/release-notes/0.1.0.md) for local validation,
pending checks and the distinction between historical and current results.

## Contribute and review

[Contributing](CONTRIBUTING.md), [security reporting](SECURITY.md),
[changelog](CHANGELOG.md), [reproducible distribution](docs/distribution.md)
and [external review instructions](docs/external-review.md) describe the
project's maintenance and review workflow. No hosted automation is required.

## License and maintenance

Copyright 2026 Lynvera Intelligence. [Apache License 2.0](LICENSE); see
[NOTICE](NOTICE). PyYAML uses MIT; development and build dependencies retain
their own licenses. No dependency source is vendored into this package.

Author and principal maintainer: Dr. Felipe Castillo Rendón.
Website: [Lynvera Intelligence](https://lynvera.ai).
Organization: [lynvera-ai](https://github.com/lynvera-ai).
