# Changelog

No version has been released as part of this preparation. Dates below identify
development work, not published tags or packages.

## 0.1.0 - Unreleased

### Supported experimental behavior

- Local Python API and CLI for supplied JSON evidence and YAML release policies.
- Mandatory tests, passing or failed outcomes, skipped or missing evidence,
  and six explicit numeric threshold comparisons.
- PASS, FAIL, INCONCLUSIVE and ERROR with documented priority and exit codes.
- Strict validation, safe YAML loading, reproducible JSON and text reports,
  evaluator version and content fingerprints.

### Distribution preparation, 2026-10-29

- English documentation, Spanish quick start, original local SVG header and
  factual version, Python requirement and license badges.
- Contribution, security, issue reporting and independent review guidance.
- Pinned dependency requirements with distribution hashes, a local candidate
  build process, artifact checksums and sanitized build metadata.
- Existing report files now produce OUTPUT_IO instead of being replaced.
  Use a new output filename; input protection remains in place.

### Known limits

- Experimental alpha metadata, with independent acceptance pending.
- Only macOS Apple Silicon and Python 3.12 have been checked locally for this
  candidate; other platforms and Python versions remain pending.
- No evidence authentication, agent execution, integrations, optional rules,
  statistical inference, cloud service or transactional report writes.
- Version 0.1.0 is retained because this is preparation of an unpublished
  experimental candidate, not a new published release. Identify candidates
  by source commit and artifact hashes until a version is published.
