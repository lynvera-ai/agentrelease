# Independent installation review

Acceptance status: pending. Local checks and historical test results are not
independent acceptance. Do not mark this candidate accepted without actual
review evidence tied to its source commit and artifact hashes.

## Receive and verify

Use a new directory outside the original checkout. Obtain the wheel, source
archive, SHA256SUMS and BUILD-METADATA.json from the maintainer. This preparation
does not upload them. Check the source commit and reported platform in the
metadata. No credentials or paid services are needed.

On macOS, from the directory containing the four files:

```sh
shasum -a 256 -c SHA256SUMS
tar -xzf agentrelease-0.1.0.tar.gz
cd agentrelease-0.1.0
python3.12 -m venv .review-venv
source .review-venv/bin/activate
python -m pip install --require-hashes -r requirements/runtime.txt
python -m pip install --no-deps ../agentrelease-0.1.0-py3-none-any.whl
python -m pip check
agentrelease --version
```

`shasum` and `tar` must be available. On Linux, `sha256sum -c SHA256SUMS`
is an alternative. Windows and unlisted environments remain pending; see
[installation](installation.md) for environment commands. Checksums verify
received bytes against the supplied manifest, not who supplied them.

## First use

For a repeatable automated walkthrough, run the portable checker from this
extracted source directory:

```sh
python3.12 tools/check_candidate.py --artifacts .. --output local-review.json
```

On Windows with Python 3.12 installed:

```powershell
py -3.12 tools\check_candidate.py --artifacts .. --output windows-review.json
```

The checker creates its own clean temporary environment and writes a sanitized
result; it does not upload anything or grant acceptance. Use `--wheelhouse`
for offline dependency installation. An existing result file is protected.
See the [validation matrix](validation-matrix.md) for what has actually run.
The following manual steps remain useful for reviewing behavior personally.

```sh
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-pass.json
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-pass.json --format json --output review-report.json
python -c "import json; r = json.load(open('review-report.json')); print(r['status'], len(r['checks']))"
```

Expected: version `AgentRelease 0.1.0`, PASS, three checks and exit code 0.
The last command prints `PASS 3`. Reports include the evaluator version and
input fingerprints. Repeat the text command and compare the output if desired.

Use the same policy with the other bundled synthetic evidence files:

| Evidence file | Status | Exit code |
| --- | --- | --- |
| `evidence-fail.json` | FAIL | 1 |
| `evidence-missing.json` | INCONCLUSIVE | 2 |
| `evidence-skipped.json` | INCONCLUSIVE | 2 |
| `evidence-invalid.json` | ERROR | 3 |

An expected nonzero evaluation exit is not a broken installation. In a shell,
inspect `$?` immediately after a command, or `$LASTEXITCODE` in PowerShell.
An invalid CLI command also exits 3. Help and version commands exit 0.

## Protection, recovery and API

Repeat the JSON command with the existing `review-report.json`: it must exit 3
with OUTPUT_IO and leave that file unchanged. Choose `review-report-2.json` to
recover. Never use private policy or evidence files for this review.

```sh
python -c "from agentrelease import Status, evaluate_files; r = evaluate_files('examples/policy.yaml', 'examples/evidence-pass.json'); assert r.status is Status.PASS; print(r.status)"
```

Expected: `PASS`. To review offline installation or update recovery, follow
[the corresponding instructions](installation.md). Record separately which
steps were actually run and which remain pending.

## Report findings

Use the issue template or copy this short form:

```text
Version and source commit or artifact SHA-256:
Operating system, architecture and Python version:
Installation method:
Minimal synthetic steps:
Expected result:
Observed result, exit code and error code:
Checks performed:
Checks not performed:
Review outcome and remaining concerns:
```

Do not include usernames, machine names, personal paths, credentials, private
inputs or full execution logs. Review screenshots and reports before sharing.
Do not use a public issue for a sensitive vulnerability; see [security reporting](../SECURITY.md).
There is no promised response time. Acceptance requires the maintainer to
evaluate real review evidence, not merely an issue or checklist being created.
