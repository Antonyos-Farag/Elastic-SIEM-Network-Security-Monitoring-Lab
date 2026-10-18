# Security & responsible use

## Lab-only scope

Attack simulations require explicit authorization and an isolated environment. Do not connect intentionally exposed services or offensive tests to production or shared networks. Use disposable accounts, bounded attempts, snapshots, and rollback plans.

## Never publish secrets

Do not commit:

- Elasticsearch passwords, API keys, Fleet enrollment tokens, or service tokens.
- Private keys, keystores, `.env` files, credential lists, or shell history.
- Raw reports, packet captures, or screenshots containing credentials or personal information.
- VM disks, memory dumps, or unreviewed log exports.

Before publishing a screenshot, inspect the entire image—including terminals, URLs, browser tabs, sidebars, and command history. Flatten redactions so hidden text/layers cannot be recovered. Do not rely on `.gitignore` as a secret scanner.

The supplied source report is not redistributed because setup screenshots may contain sensitive information. If any captured credential or token remains active, revoke or rotate it before sharing further—even if the lab is no longer in use.

## Safer deployment defaults

Use trusted TLS, restricted management access, least-privilege ingestion users, protected secret storage, synchronized clocks, bounded retention, and tested recovery. Disabled certificate verification and superuser pipeline credentials in historical screenshots are not recommended configurations.

## Reporting a concern

Do not open a public issue containing a secret or a working exploit against a live host. If the repository has private vulnerability reporting enabled, use its private security-reporting flow; otherwise contact the maintainer through an available private channel. If a credential was exposed, revoke/rotate it immediately. Deleting a file alone does not remove it from Git history or existing copies.
