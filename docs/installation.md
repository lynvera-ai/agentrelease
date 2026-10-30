# Installation and maintenance

The main requirements are Python 3.12 or newer, `venv` and `pip`. Git is needed
only to clone source. PyYAML is the only runtime dependency. No integrations,
models, accounts, API keys, databases, background services or ports are needed.

Local validation covers macOS Apple Silicon with Python 3.12.9, 3.13.6 and
3.14.4, and a Linux ARM64 Debian container with Python 3.12.16. Windows commands
below are provided for review, not as evidence of a tested platform. See the
[validation matrix](validation-matrix.md) for scope and pending combinations.

## Source installation

Use the [README quick start](../README.md#install-from-source). On Windows,
use `py -3.12 -m venv .venv` and `.venv\Scripts\Activate.ps1` instead of the
macOS/Linux environment commands. If Python lacks `venv` or `pip`, install
those components through the operating system's Python distribution first.

For a source archive supplied for review:

```sh
tar -xzf agentrelease-0.1.0.tar.gz
cd agentrelease-0.1.0
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements/runtime.txt
python -m pip install --no-deps .
python -m pip check
agentrelease --version
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-pass.json
```

This installs the pinned runtime dependency before installing the source. Source
installation can still download the build backend. To avoid build-time network
access, prefer the supplied wheel and the offline instructions below.

## Wheel installation outside the checkout

From an extracted source archive with the wheel alongside it:

```sh
python3.12 -m venv .review-venv
source .review-venv/bin/activate
python -m pip install --require-hashes -r requirements/runtime.txt
python -m pip install --no-deps ../agentrelease-0.1.0-py3-none-any.whl
python -m pip check
agentrelease --version
agentrelease evaluate --policy examples/policy.yaml --evidence examples/evidence-pass.json --format json --output review-report.json
```

The wheel contains the library and CLI, not the examples or documentation.
Those are included in the source archive. Retain both when sharing a candidate.
Always verify `SHA256SUMS` before installing, as described in the
[external review guide](external-review.md).

## Offline installation

On a connected machine with the same target Python and platform, extract the
source archive. From the directory containing that archive and its extracted
`agentrelease-0.1.0` directory, download only the pinned runtime wheel:

```sh
python -m pip download --only-binary=:all: --require-hashes -r agentrelease-0.1.0/requirements/runtime.txt --dest wheelhouse
```

Transfer the source archive, AgentRelease wheel, checksum file and wheelhouse
to the review machine. From the extracted source directory:

```sh
python -m pip install --no-index --find-links ../wheelhouse --require-hashes -r requirements/runtime.txt
python -m pip install --no-index --no-deps ../agentrelease-0.1.0-py3-none-any.whl
python -m pip check
```

Evaluation makes no network requests. The offline commands do not contact a
package index. A missing cached dependency fails installation; do not disable
hash checks to work around it. Download it on the connected machine and retry.

## Updating and recovery

There is no global configuration or automatic update. Record the installed
version with `agentrelease --version`, the source commit from build metadata,
and dependency versions with `python -m pip list`. Keep these records private
until reviewed for sensitive data.

Create a fresh virtual environment for a reviewed update. Install its pinned
runtime requirements and wheel, run `pip check` and the synthetic examples,
then use that environment for new evaluations. Keep the previous environment,
inputs and reports until the update is accepted. The `v0.1.0` release identifies
one exact source commit and set of artifact hashes. Local candidates also need
their source commit and hashes recorded; later published changes need a new
version rather than replacing the existing tag or files.

To recover, reactivate the previous environment or reinstall the retained wheel
and its matching requirements into a new one. AgentRelease does not migrate
inputs, alter policies or delete report files. Retry a failed evaluation with
a new report filename; an interrupted new write may leave a partial file.

## Uninstall

With the environment active:

```sh
python -m pip uninstall agentrelease
```

This leaves PyYAML installed because it may be shared by other packages. An
entire disposable virtual environment can be removed separately after checking
its location. Uninstalling does not remove policies, evidence or reports.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| `agentrelease` is not found | Activate the intended environment; try `python -m agentrelease --version` |
| `ModuleNotFoundError: yaml` | Run `python -m pip check`, then reinstall the matching runtime requirements |
| Network or certificate failure during installation | Check connectivity or use the offline wheelhouse; do not disable TLS checks |
| Unsupported Python version | Use Python 3.12 or newer; no compatibility below 3.12 is promised |
| INPUT_IO | Verify both explicit paths and read permissions locally |
| OUTPUT_IO | Choose a new filename in an existing writable directory |
| MALFORMED_INPUT or INVALID_INPUT | Check UTF-8, schema version, types and the [format reference](formats.md) |
| FAIL or INCONCLUSIVE | Inspect individual checks; these are evaluation findings, not installation failures |

Do not include credential files, private evidence, personal paths, full
environment dumps or execution logs in public issues.
