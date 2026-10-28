# Experimental scope and limitations

AgentRelease compares supplied test outcomes and numeric measurements with
explicit policy rules. It does not run tests, decide whether a test suite is
adequate, inspect an agent, validate the truth of supplied observations or
establish general safety or reliability. PASS means only that the supplied
evidence meets every declared criterion.

The caller is responsible for test design, trustworthy evidence collection,
units, appropriate thresholds and retaining original inputs. Input fingerprints
are content identifiers, not signatures or attestations.

The initial rule set requires all declared tests to pass and all declared
measurements to satisfy their comparisons. Optional criteria, weighted scores,
aggregations, confidence intervals, statistical significance, floating-point
tolerances, policy inheritance and custom executable rules are outside scope.
Unknown evidence test IDs and metric names are rejected rather than ignored.

YAML is loaded with SafeLoader restrictions plus duplicate-key and alias
rejection. No configuration-supplied code, commands or network requests are
executed. The 5 MiB input limit bounds file size, but this local experimental
tool is not a hardened service for adversarial workloads. Dictionary inputs
are intended for ordinary in-process JSON-compatible data.

Reports have stable ordering and no timestamps or machine paths. Report files
are written locally and can replace an existing report, but cannot overwrite
input files. Writes are not transactional; retain a previous report separately
if it must survive an interrupted write.

No framework integrations, real agent execution, external scanners, dashboard,
cloud service, database, user authentication, model APIs, subscriptions or paid
services are included. The project does not publish to PyPI or create releases
as part of this implementation. No hosted CI or billing changes are configured.
Validation is performed locally and its environment is recorded separately.

Python 3.12 is the minimum supported version. The public API and schema may
change during experimental development. Compatibility across future versions
is not guaranteed; record the evaluator version with each report.
