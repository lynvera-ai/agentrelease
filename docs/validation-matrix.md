# Validation matrix and remaining review

Local validation date: 2026-10-29. The project remains experimental.
These are local engineering checks, not independent acceptance or a support
commitment for every operating system that can install the wheel.

## Executed checks

| System | Architecture | Python | Test suite | Scope |
| --- | --- | --- | --- | --- |
| macOS | Apple Silicon ARM64 | 3.12.9 | 149 passed | Local virtual environment |
| macOS | Apple Silicon ARM64 | 3.13.6 | 149 passed | Separate local virtual environment |
| macOS | Apple Silicon ARM64 | 3.14.4 | 149 passed | Separate local virtual environment |
| Debian GNU/Linux 13 container | ARM64 | 3.12.16 | 149 passed | Local Linux VM; root and non-root runs |

The tests cover validation, all four outcomes, priority, numeric boundaries,
reproducibility, API behavior, CLI exit codes, report output and input/report
protection. A local virtual environment is not evidence of another operating
system. The Linux container uses a real Linux kernel in a local VM; it is not
a native Windows or Linux x86-64 test.

Strict mypy 2.4.1 analysis passes for the package and both maintenance tools,
targeting Python 3.12. PyYAML stubs and type-checker dependencies are pinned in
`requirements/typing.txt`. No global missing-import ignore, disabled error
codes or untyped module exclusions are used. File data is still validated at
runtime; typing does not verify evidence truth or general safety.

Ruff, dependency consistency and compilation checks run locally. Artifact
installation receipts and exact build identity accompany the local candidate
as JSON files. They do not contain personal paths or raw execution logs.

## Pending checks

| Check | Status | What is needed |
| --- | --- | --- |
| Windows | Not executed | A real Windows machine with Python 3.12 or newer |
| Linux x86-64 | Not executed | A matching local machine or container host |
| Linux Python 3.13 and 3.14 | Not executed | Separate interpreter environments on Linux |
| Other Python versions and implementations | Not executed | An explicitly chosen target and real run |
| Independent acceptance | Pending | Another person installs and reviews the exact candidate |
| Upgrade across published versions | Not applicable yet | Distinct published versions and retained artifacts |

No Windows machine or independent reviewer is currently available. Their
absence is recorded rather than replaced by simulated results, a forged
receipt or a paid execution service. Version 0.1.0 and the alpha classification
remain unchanged.

## Ready-to-run review

From an extracted candidate source archive, with the wheel, source archive,
SHA256SUMS and BUILD-METADATA.json in the parent directory:

```sh
python3.12 tools/check_candidate.py --artifacts .. --output local-review.json
```

On Windows in PowerShell, after extracting the same source archive:

```powershell
py -3.12 tools\check_candidate.py --artifacts .. --output windows-review.json
```

The checker creates a fresh temporary virtual environment outside the source
tree, checks artifact hashes, installs the pinned runtime and wheel, exercises
the API and CLI, and writes a sanitized JSON result. Online installation uses
the public package index; no API key or paid service is needed. For offline
use, add `--wheelhouse` with a directory containing the matching PyYAML wheel.
The result path must be new. Exit 0 means these automated checks passed; exit
1 means the review failed or could not complete. CLI usage errors exit 2.

The JSON always leaves `independent_acceptance` as `pending`. To establish an
independent result, another person must execute the steps and supply their
actual findings tied to the source commit and hashes, using the
[review form](external-review.md#report-findings). Automation is evidence for
that review, not acceptance by itself. Do not send personal paths, credentials,
private input files or full console logs.
