# Lynvera AgentRelease

Experimental — under development.

AgentRelease is a local Python library and command-line tool from Lynvera
Intelligence. It compares supplied test evidence with explicit release criteria
and produces reproducible JSON or text reports.

An evaluation describes only the supplied policy and evidence. It is not a
certification of general agent safety or a guarantee that an agent will work.
AgentRelease does not run agents or independently verify supplied measurements.

## Install

Requires Python 3.12 or newer. From a checkout of this repository:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

No model API, API key, paid service or network access is needed for evaluation.
Installation downloads the build tools and the PyYAML dependency unless they
are already available locally. No PyPI release has been published by this project.

## Command line

The bundled examples contain synthetic data only:

```sh
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-pass.json
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-fail.json --format json
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-pass.json --format json --output report.json
```

`python -m agentrelease` provides the same interface. `--output` writes to an
existing directory and refuses to overwrite an input. Without it, the report
goes to standard output. Input errors are returned as reports. Usage errors and
output write errors go to standard error.

| Result | Meaning | Exit code |
| --- | --- | --- |
| PASS | All mandatory criteria have valid passing evidence | 0 |
| FAIL | Valid evidence violates at least one mandatory criterion | 1 |
| INCONCLUSIVE | A required test or measurement is missing, or a test was skipped | 2 |
| ERROR | Invalid input or an evaluation, file or usage error | 3 |

Priority is `ERROR > FAIL > INCONCLUSIVE > PASS`. Validation happens before
evaluation; invalid input yields no partial checks. A failure takes priority
over incomplete evidence, while individual checks retain both findings.
Only PASS exits successfully. Help and version commands also exit 0.

## Python API

```python
from agentrelease import Status, evaluate, evaluate_files

report = evaluate_files("examples/policy.yaml", "examples/evidence-pass.json")
print(report.to_text())
assert report.status is Status.PASS

policy = {
    "schema_version": 1,
    "id": "synthetic-release",
    "tests": [{"id": "boundary"}],
}
evidence = {
    "schema_version": 1,
    "tests": [{"id": "boundary", "status": "passed"}],
}
report = evaluate(policy, evidence)
data = report.to_dict()
json_report = report.to_json()
exit_code = report.status.exit_code
```

Reports and checks are immutable. The API returns ERROR reports for invalid
inputs; callers should always inspect `report.status`. File inputs are UTF-8,
limited to 5 MiB each. Dictionary inputs use the same schema validation.

## Input formats

Policy (`YAML`):

```yaml
schema_version: 1
id: synthetic-release
tests:
  - id: quality
    metrics:
      - name: accuracy
        operator: ">="
        threshold: 0.9
  - id: boundary
```

Evidence (`JSON`):

```json
{
  "schema_version": 1,
  "tests": [
    {"id": "quality", "status": "passed", "metrics": {"accuracy": 0.95}},
    {"id": "boundary", "status": "passed"}
  ]
}
```

All declared tests and metrics are mandatory. Supported comparisons are `>=`,
`>`, `<=`, `<`, `==`, `!=`. Evidence statuses are `passed`, `failed`, `skipped`.
Missing required tests or measurements are INCONCLUSIVE. Unknown test IDs or
metric names, duplicate identifiers or keys, and malformed inputs are ERROR.

`schema_version` must be integer `1`. A policy needs an `id` and a nonempty
`tests` list. Test IDs, policy IDs and metric names match
`[A-Za-z0-9][A-Za-z0-9_.-]{0,63}` and are case-sensitive. Metric rules require
`name`, `operator` and a finite numeric `threshold`. Evidence requires a
`tests` list, which may be empty. Every evidence test needs `id` and `status`;
its optional `metrics` object maps declared names to finite numbers.

Unknown fields, numeric strings, booleans used as numbers and nonfinite values
are invalid. A skipped test cannot contain measurements. YAML aliases, merge
keys, custom object tags and multiple documents are rejected. Quote operators
and identifiers that YAML could interpret as another type.

The synthetic files in `examples` cover passing, failed, missing, skipped and
invalid evidence. Use each JSON file with `examples/policy.yaml`.

## Reproducibility and limits

The same inputs produce the same evaluation and serialized report. Reports
include input fingerprints and evaluator version; they omit timestamps and
machine paths. Fingerprints identify content and do not authenticate evidence.
They use SHA-256 of validated inputs serialized as compact JSON with sorted
mapping keys and ASCII escaping. Whitespace and mapping key order do not
affect fingerprints; list order and numeric representation do.

JSON reports contain `schema_version`, `evaluator_version`, `policy_id`,
`status`, `scope`, `input_sha256`, `checks` and `errors`. Checks are sorted by
test ID, with the outcome before metric checks sorted by name. Each check
includes its status, reason, observation and applicable comparison. Invalid
inputs produce ERROR reports with no checks and an error code and message.

Comparisons use Python numeric semantics without tolerance, rounding, unit
conversion or statistical inference. Choose explicit thresholds and consistent
units. This version has no optional criteria, custom rules, framework
integrations, real agent execution, external scanners, dashboard, cloud service,
database, user authentication or paid APIs. The caller remains responsible
for trustworthy evidence collection, appropriate tests and consistent units.

## Development

```sh
python -m pip install -e '.[dev]'
pytest
ruff check .
ruff format --check .
python -m build
```

Tests cover all four states, priority, missing and skipped evidence, numeric
boundaries, strict input validation, safe YAML loading, reproducibility, report
output and CLI exit codes.

PyYAML (MIT) is the sole runtime dependency, for safe YAML parsing. Python's
standard library provides validation, the CLI, comparisons and reports.
Development tools are pytest (MIT), Ruff (MIT) and build (MIT); setuptools (MIT)
is the build backend. These licenses are compatible with Apache-2.0.
The loader uses a restricted [PyYAML SafeLoader](https://pyyaml.org/wiki/PyYAMLDocumentation),
with additional duplicate-key and alias rejection. Packaging follows the
[Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

## License and maintenance

Copyright 2026 Lynvera Intelligence. Licensed under
[Apache License 2.0](LICENSE). See [NOTICE](NOTICE).

Author and principal maintainer: Dr. Felipe Castillo Rendón.
Website: [Lynvera Intelligence](https://lynvera.ai).
Organization: [lynvera-ai](https://github.com/lynvera-ai).
