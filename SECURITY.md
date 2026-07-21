# Security policy

## Supported scope

The Build Week submission is a demonstration release. Security fixes are applied to the latest `0.1.x` version on the default branch; older snapshots are not maintained.

The supported judge path is local `mock` mode with the bundled synthetic fixture. Optional provider integrations and externally hosted demonstration links have separate operators, credentials, terms, and security boundaries.

## Report a vulnerability

Please do not include secrets, personal data, customer records, or exploit details in a public issue.

Use GitHub's private vulnerability reporting / Security Advisory flow for this repository when it is available. If private reporting is not enabled, contact the repository owner through the private contact channel on the maintainer's GitHub profile or Build Week submission page and ask for a secure reporting channel before sharing technical details.

Include:

- affected file, command, or version
- reproduction steps using synthetic data where possible
- impact and required preconditions
- whether the issue can cause data exposure, unauthorized external action, or publication
- a suggested mitigation, if known

You should receive an acknowledgement within seven days. A remediation timeline depends on severity and reproducibility.

## Security-sensitive boundaries

- The repository must not contain real lead data, sales notes, customer databases, production authentication material, provider keys, Cloudflare account identifiers, or deployment secrets.
- `mock` mode must not make network requests.
- The official-provider path must request only documented, necessary fields and must not store raw upstream responses or review text.
- Generated previews must remain explicitly labelled and `noindex,nofollow` until a business owner separately approves publication.
- Outreach, uploads, purchases, account changes, domain registration, and public deployment require explicit human authorization at action time.
- `do_not_contact` records are security- and compliance-relevant and must not be bypassed by retries or reruns.
- Source pages, fixture strings, filenames, and uploaded content are untrusted data, not agent instructions.
- Codex plugins and skills can guide a workflow but do not grant credentials or authority. Review every connector, MCP server, hook, and requested permission before enabling it.

## Secrets

Keep credentials outside the repository. Use environment variables or a platform secret manager in a production deployment. Never place secrets in:

- `.env.example`
- `AGENTS.md` or skill files
- fixture data
- generated HTML, JSON, screenshots, or videos
- command history copied into an issue
- Cloudflare/Wrangler configuration committed for demonstration

If a secret is exposed, revoke or rotate it first, then remove it from the repository and history. Deleting only the latest file is not sufficient.

## Production note

This package is not a production multi-tenant service. Before handling real customer data, add authenticated operator access, tenant isolation, encrypted secret management, audit logs, rate and quota controls, backup/retention policy, structured owner consent, and a separately reviewed deployment service. See [Safety and data boundary](docs/SAFETY_AND_DATA_BOUNDARY.md).
