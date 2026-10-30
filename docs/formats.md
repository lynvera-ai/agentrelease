# Policies, evidence and reports

All examples are synthetic. Version 1 accepts only the fields listed below.
Unknown fields, duplicate keys and duplicate identifiers are errors.

## Common rules

`schema_version` is integer `1`, not `true`, `1.0` or `"1"`. Identifiers are
case-sensitive and match `[A-Za-z0-9][A-Za-z0-9_.-]{0,63}`. Numeric values are
finite integers or floats; booleans, nulls and strings are not measurements.

Files are UTF-8, with a 5 MiB limit per file. JSON does not allow comments,
trailing commas, NaN or infinities. The YAML loader extends PyYAML SafeLoader
with duplicate-key and alias rejection. Custom object tags, merge keys,
multiple documents and non-string mapping keys are rejected. Quote operators
and identifiers that YAML could otherwise interpret as numbers, booleans or dates.

## Policy YAML

| Field | Required | Value |
| --- | --- | --- |
| `schema_version` | Yes | Integer 1 |
| `id` | Yes | Policy identifier |
| `tests` | Yes | Nonempty list of tests with unique IDs |

Every test has an `id` and an optional `metrics` list, which defaults to empty.
Every metric rule has `name`, `operator` and `threshold`. Names are unique
within a test. All tests and all metric rules are mandatory.

```yaml
schema_version: 1
id: synthetic-release
tests:
  - id: response-quality
    metrics:
      - name: accuracy
        operator: ">="
        threshold: 0.9
  - id: tool-boundary
```

Comparisons are `observed operator threshold`, with `>=`, `>`, `<=`, `<`, `==`
or `!=`. There is no implied metric range or unit. Floating-point equality
uses exact Python equality, with no tolerance or statistical interpretation.

## Evidence JSON

The root has `schema_version` and `tests`. The list may be empty. Each test
has a unique `id`, a `status` of `passed`, `failed` or `skipped`, and an optional
`metrics` object mapping declared metric names to finite numbers.

```json
{
  "schema_version": 1,
  "tests": [
    {"id": "response-quality", "status": "passed", "metrics": {"accuracy": 0.95}},
    {"id": "tool-boundary", "status": "passed"}
  ]
}
```

Unknown test IDs or metric names are ERROR. Missing tests or measurements are
INCONCLUSIVE. A skipped test cannot contain measurements. Executed failed
tests still have their metrics evaluated. One known failure takes priority
over missing evidence; invalid input takes priority over both.

## Report JSON

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer report version 1 |
| `evaluator_version` | Package version |
| `policy_id` | Validated policy ID; null on ERROR |
| `status` | PASS, FAIL, INCONCLUSIVE or ERROR |
| `scope` | Limits interpretation to supplied policy and evidence |
| `input_sha256` | Policy and evidence fingerprints; null on ERROR |
| `checks` | Ordered individual criteria; empty on ERROR |
| `errors` | Objects with `code` and `message`; empty on valid evaluations |

Checks contain `test_id`, `kind` (`test` or `metric`), `status`, `reason`,
`metric`, `observed`, `operator` and `threshold`. Inapplicable fields are null.
Checks are sorted by test ID, then outcome before metrics sorted by name.

Identical inputs produce identical reports, without timestamps or machine
paths. Fingerprints use SHA-256 of the validated dictionaries serialized as
compact JSON with sorted mapping keys, ASCII escaping and nonfinite values
disabled. Whitespace and mapping key order do not matter. List order, numeric
representation (`1` versus `1.0`) and explicit optional empty fields do matter.
Fingerprints do not authenticate evidence. Retain inputs and evaluator version.

## Errors and CLI output

Codes include `INVALID_INPUT`, `DUPLICATE_ID`, `DUPLICATE_KEY`,
`UNKNOWN_REFERENCE`, `MALFORMED_INPUT`, `INVALID_ENCODING`, `INPUT_TOO_LARGE`,
`INPUT_IO`, `EVALUATION_ERROR` and `OUTPUT_IO`. File errors omit machine paths
and parser dumps. Identifiers and field names can appear in validation messages;
review reports before sharing them.

CLI exit codes are PASS=0, FAIL=1, INCONCLUSIVE=2, ERROR=3. Usage errors also
exit 3; explicit help and version commands exit 0. Reports go to standard
output or `--output`; usage errors and output failures go to standard error.
Output paths must be new files in existing writable directories. Inputs and
previous reports, including symlink and hard-link aliases, are protected.

Return to the [README](../README.md).
