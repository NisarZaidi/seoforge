# Security policy

## Reporting a vulnerability

Please use [GitHub private vulnerability reporting](https://github.com/NisarZaidi/seoforge/security/advisories/new) when available, or open a private security advisory against this repository. Include the affected version, a minimal reproduction, and impact. Do **not** post credentials or exploitable private-site details in a public issue.

## Safety model (high level)

SeoForge:

- Validates destination addresses and TLS for fetches
- Limits response sizes and crawl frontiers
- Respects `robots.txt` by default (`--robots ignore` is an explicit, recorded override)
- Treats crawled HTML/text/JSON-LD as untrusted data (evidence, not instructions)

`--allow-private` intentionally relaxes public-IP checks for local/staging audits only.

Keep crawl output, credentials, and client reports out of version control. Connection examples use environment-variable names — never commit real secrets.

See [docs/operations.md](docs/operations.md) for staging/apply/rollback of reviewed content edits.
