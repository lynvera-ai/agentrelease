# Experimental MVP specification

Status: Experimental — under development.

AgentRelease evaluates supplied test evidence against explicit release criteria.
It does not run agents or certify their general safety or reliability.

## Inputs

Both formats use integer `schema_version: 1`. Unknown fields, duplicate keys,
duplicate identifiers, invalid values and unknown test references are errors.
Identifiers use 1–64 ASCII letters, digits, underscores, periods or hyphens,
starting with a letter or digit. Each input file is UTF-8 and at most 5 MiB.

A YAML policy declares an `id` and a nonempty `tests` list. Every declared test
is mandatory and must have a `passed` outcome. Each test has an `id` and an
optional `metrics` list with unique `name`, `operator` and numeric `threshold`.
Supported operators are `>=`, `>`, `<=`, `<`, `==` and `!=`.

JSON evidence declares a `tests` list, which may be empty. Every entry has an
`id`, a `status` (`passed`, `failed` or `skipped`) and an optional `metrics`
object mapping declared metric names to finite numbers. Booleans, strings,
nulls, NaN and infinities are not numeric measurements. A skipped test must
have no measurements. Evidence may omit mandatory tests or measurements;
those omissions are incomplete evidence, not malformed input.

## Evaluation

Validate both complete inputs before checking criteria. Evidence test IDs must
exist in the policy; evidence metric names must exist in that policy test.
For each policy test, emit one outcome check and one check per metric rule:

| Condition | Outcome |
| --- | --- |
| Required test passed | PASS |
| Required test failed | FAIL |
| Required test missing or skipped | INCONCLUSIVE |
| Executed test has a missing required metric | INCONCLUSIVE |
| Observed metric satisfies its comparison | PASS |
| Observed metric violates its comparison | FAIL |
| Malformed input, unknown reference, I/O or evaluation error | ERROR |

Metrics on executed failed tests are still evaluated. Skipped or missing tests
make all their metric checks inconclusive. Aggregation priority is
`ERROR > FAIL > INCONCLUSIVE > PASS`; a known failure remains visible even when
other evidence is missing. Any invalid input produces ERROR with no partial
criterion results. Empty policies are invalid, so an empty policy cannot pass.

## Outputs and API

`evaluate(policy, evidence)` accepts Python dictionaries and returns a frozen
report. `evaluate_files(policy_path, evidence_path)` loads safe YAML and strict
JSON and returns the same report type. Expected input and file errors are
returned as ERROR reports. Inputs are never mutated.

Reports expose `to_dict()`, `to_json()` and `to_text()`. They contain the
schema and evaluator versions, policy ID, overall status, ordered checks,
input fingerprints and errors. Check order is lexical by test ID and metric
name, with the test outcome before its metrics. Fingerprints are SHA-256 of
the validated input dictionaries serialized with sorted keys, compact
separators, ASCII escaping and no nonfinite numbers. They identify supplied
content; they do not establish authenticity. No timestamps, absolute paths,
random IDs or network requests affect evaluation output.

`agentrelease evaluate --policy POLICY.yaml --evidence EVIDENCE.json`
prints text by default; `--format json` prints JSON. `--output PATH` saves
the report. Exit codes are PASS=0, FAIL=1, INCONCLUSIVE=2, ERROR=3. Invalid CLI
usage also exits 3; explicit help and version commands exit 0. An output write
failure emits an ERROR report to standard error and exits 3.

## Acceptance criteria

Tests must cover passing evidence, failed mandatory tests, missing and skipped
tests, threshold failures, malformed inputs, duplicate identifiers and keys,
unknown references, deterministic output, state priority and CLI exit codes.
Ruff checks, package construction, and installation and execution from a clean
environment must pass. Examples contain synthetic data only.

## Exclusions

No framework integrations, real agent execution, external scanners, dashboard,
cloud services, database, user authentication, paid APIs, PyPI publishing or
releases. No hosted automation or billing settings are enabled by this MVP.
