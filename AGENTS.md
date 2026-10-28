# Repository instructions

## Scope and style

- Keep the experimental scope documented in `docs/specification.md`.
- Public documentation and commit messages must be in English.
- Communicate with the maintainer in Spanish.
- Use short comments and plain formatting. Do not add assistant attribution,
  tool branding, decorative symbols or generated-by signatures.
- Use branches such as `feature/experimental-mvp`; never work on `main`.
- Preserve existing work. Open pull requests against `main`; do not merge them.
- Keep examples synthetic. Do not include workplace, university or third-party
  private data, documents or code.
- Do not enable paid services, change zero-dollar budgets, publish to PyPI or
  create releases.

## Required Git identity

- Authorized personal GitHub account: `fcastillorendon`.
- Author and committer name: `Dr. Felipe Castillo Rendón`.
- Author and committer email: `fcastillorendon@gmail.com`.
- Configure `user.name` and `user.email` locally in this repository only.
  Never change global or academic repository configuration.
- Never use the institutional Tec account or its credentials for commits,
  pushes or pull requests. Do not use `felipe.castillo@lynvera.ai` for commits;
  it is a business contact address.
- Before the first commit, verify the effective author and committer,
  including environment overrides. Both emails must match the personal email.
- Verify that the destination is `https://github.com/lynvera-ai/agentrelease`.
- Before every push or pull request, verify the authenticated login is exactly
  `fcastillorendon` and inspect the actual Git authentication mechanism
  (HTTPS credential helper or SSH). Browser and command-line sessions can
  differ. Commit email is not proof of authentication identity.
- Never fall back to institutional credentials. Never print tokens, passwords
  or private keys. If identity cannot be guaranteed, continue local work but
  stop before the affected commit or publication and report what is missing.
- After every commit, verify both author and committer names and emails.
  Review every new commit before pushing. Do not rewrite existing history or
  force push.

## Verification

Use Python 3.12 or newer. Run `pytest`, `ruff check .`, `ruff format --check .`,
`python -m build`, then install the wheel and run the CLI and API outside the
checkout in a clean virtual environment. Record actual results and limitations.
