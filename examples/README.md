# Synthetic examples

All names, test outcomes and measurements in this directory are synthetic.
They do not describe a real agent, a real test run or an empirical safety result.

Use every evidence file with `policy.yaml`:

| Evidence | Expected status | Exit code |
| --- | --- | --- |
| `evidence-pass.json` | PASS | 0 |
| `evidence-fail.json` | FAIL | 1 |
| `evidence-missing.json` | INCONCLUSIVE | 2 |
| `evidence-skipped.json` | INCONCLUSIVE | 2 |
| `evidence-invalid.json` | ERROR | 3 |

The invalid example is valid JSON with an unknown test reference. Malformed
JSON is a separate input error, covered by the automated tests.
