# Contributing

AgentRelease 0.1.0 is experimental. Small, reviewable fixes to the supported
evaluation behavior, documentation and distribution are welcome. Discuss changes
to policy semantics or scope in an issue before starting a large contribution.
There is no promised review or support response time.

## Local setup

Requires Python 3.12 or newer. From a source checkout:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements/development.txt
python -m pip install --no-build-isolation --no-deps -e .
pytest -q
ruff check .
ruff format --check .
mypy
```

No hosted workflow, paid API or external agent is required. Mypy runs in strict
mode over the package and maintenance tools, targeting the Python 3.12 minimum.
Its version and PyYAML definitions are pinned in `requirements/typing.txt`.
Do not add broad ignores or disable checks to make failures disappear. Dynamic
file inputs remain subject to runtime validation; static analysis does not
replace the tests or independent review.

## Changes

- Use a branch outside `main` and keep unrelated edits separate.
- Preserve the documented state priority and strict validation. Do not loosen
  criteria to make failing evidence pass.
- Add a regression test for a relevant behavior fix. Avoid tests that simply
  duplicate implementation details.
- Keep comments short, public documentation and commit messages in English,
  and examples synthetic. Update the changelog for user-visible behavior.
- Retain the existing Apache-2.0 license and notices. Do not add private data,
  credentials, personal paths, runtime logs, caches or environments.
- Include actual local checks, platform, limitations and pending work in a
  review description. Keep external acceptance pending without independent evidence.

For installation review, use [the external guide](docs/external-review.md).
For candidate builds and checksums, use [distribution instructions](docs/distribution.md).
Dependency locks should be updated from original distribution SHA-256 digests
and revalidated locally. A hash match verifies bytes, not general package safety.

## Reporting problems

Use the repository issue template with version, environment, minimal synthetic
steps, expected outcome and observed outcome. Include exit codes and error
codes rather than a full private execution log. Review attachments before
posting. See [SECURITY.md](SECURITY.md) for sensitive reports.

Contributions remain subject to the project's existing Apache-2.0 license.
