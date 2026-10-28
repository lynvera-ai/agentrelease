# Format reference

The authoritative runtime validation is implemented in the package. Version 1
accepts only the fields below. All examples and names here are synthetic.

## Shared rules

- `schema_version` is integer `1`; `true`, `1.0` and `"1"` are invalid.
- Identifiers match `[A-Za-z0-9][A-Za-z0-9_.-]{0,63}` and are case-sensitive.
- Lists retain their supplied content for fingerprints. Evaluation checks are
  sorted by test ID and then metric name, independently of list order.
- Unknown fields and duplicate identifiers or mapping keys are errors.
- A number is a finite Python/JSON integer or floating-point value. Booleans,
  nulls, numeric strings, NaN and infinities are invalid.
- Files must be UTF-8 and at most 5 MiB each. No comments or trailing commas
  are allowed in JSON. YAML uses a restricted safe loader: custom object tags,
  aliases, merge keys, non-string mapping keys and multiple documents are
  rejected. Quote YAML operators and string values that YAML could interpret
  as booleans, dates or numbers.

## Policy YAML

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `schema_version` | integer | yes | Exactly 1 |
| `id` | identifier | yes | Policy identifier |
| `tests` | list of test objects | yes | Nonempty; unique test IDs |

Every policy test is mandatory:

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `id` | identifier | yes | Unique within policy |
| `metrics` | list of metric rules | no | Defaults to empty; unique names within test |

Every metric rule is mandatory:

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `name` | identifier | yes | Unique within test |
| `operator` | string | yes | `>=`, `>`, `<=`, `<`, `==`, `!=` |
| `threshold` | finite number | yes | Comparison target |

The comparison is `observed operator threshold`. Use metric names to document
units, for example `latency_ms`, and keep measurements in the same units.
There are no implied ranges: an accuracy range of 0–1 is a convention of the
example, not a built-in rule. Floating-point equality is exact Python equality;
no tolerance is applied.

## Evidence JSON

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `schema_version` | integer | yes | Exactly 1 |
| `tests` | list of evidence objects | yes | May be empty; unique test IDs |

Evidence test:

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `id` | identifier | yes | Must reference a policy test |
| `status` | string | yes | `passed`, `failed`, `skipped` |
| `metrics` | object | no | Maps declared metric names to finite numbers |

Missing tests and absent declared metric measurements produce INCONCLUSIVE,
not ERROR. A skipped test may omit `metrics` or supply `{}`, but cannot report
measurements. For an executed test, metrics are checked even if its outcome
is `failed`. Unknown metric names are errors; add them to the policy before
including them in evidence.

## Report JSON

The report schema is integer version 1. Every report contains:

| Field | Meaning |
| --- | --- |
| `schema_version` | Report schema version |
| `evaluator_version` | Package version |
| `policy_id` | Validated policy ID; null for ERROR reports |
| `status` | PASS, FAIL, INCONCLUSIVE or ERROR |
| `scope` | Statement limiting interpretation to supplied evidence and policy |
| `input_sha256` | Policy and evidence content fingerprints; null on ERROR |
| `checks` | Ordered list of individual test and metric checks |
| `errors` | Error objects with `code` and `message`; empty for valid evaluations |

Each check contains `test_id`, `kind` (`test` or `metric`), `status`, `reason`,
`metric`, `observed`, `operator`, `threshold`. Fields not applicable to a check
are null. Test check observations are `passed`, `failed`, `skipped` or null
for a missing test. Missing measurements have null observations.

Error codes include `INVALID_INPUT`, `DUPLICATE_ID`, `DUPLICATE_KEY`,
`UNKNOWN_REFERENCE`, `MALFORMED_INPUT`, `INVALID_ENCODING`, `INPUT_TOO_LARGE`,
`INPUT_IO`, `EVALUATION_ERROR`, and `OUTPUT_IO`. File errors omit machine paths
and parser dumps. CLI usage errors are plain messages with exit code 3.

Content fingerprints use SHA-256 of each validated input dictionary serialized
as compact JSON with sorted mapping keys, ASCII escaping and nonfinite numbers
disabled. Whitespace and mapping key order do not affect fingerprints; list
order, numeric representation (`1` versus `1.0`) and explicit empty optional
fields do. Retain the original inputs and evaluator version to reproduce a run.

Example PASS report excerpt:

```json
{
  "schema_version": 1,
  "evaluator_version": "0.1.0",
  "policy_id": "synthetic-release",
  "status": "PASS",
  "checks": [
    {
      "test_id": "boundary",
      "kind": "test",
      "status": "PASS",
      "reason": "Required test passed.",
      "metric": null,
      "observed": "passed",
      "operator": null,
      "threshold": null
    }
  ]
}
```

This excerpt omits scope, fingerprints and errors for readability.
