# Security reporting

This experimental project has no stable support window or guaranteed response
time. The only current candidate line is 0.1.0. No production-readiness or
general agent-safety certification is claimed.

Do not post credentials, private evidence, exploit details, personal paths or
execution logs in a public issue. If the repository offers **Security** then
**Report a vulnerability**, use that private channel. Its availability depends
on repository settings; this document does not enable it.

If no private reporting option is available, open a minimal public issue asking
the maintainer for a private reporting channel. Do not include the sensitive
details until a channel is confirmed. No security contact address or response
commitment is implied by this fallback.

For a private report, include the source commit or artifact hash, Python and
package versions, affected behavior, impact and minimal synthetic reproduction.
Do not send secrets even through a private channel. Rotate any credentials that
were exposed through your own workflow.

AgentRelease uses restricted safe YAML parsing, validates JSON-compatible
inputs, limits file size and does not execute configured commands. These are
specific controls, not proof that all malicious inputs are safe. Reports can
contain supplied identifiers and field names. Inspect them before sharing.

Existing input and report files are protected from overwrite. Writes of new
reports are not transactional and may leave a partial file after interruption.

Report ordinary bugs through [repository issues](https://github.com/lynvera-ai/agentrelease/issues),
using the short form in the [external review guide](docs/external-review.md#report-findings).
