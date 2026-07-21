---
name: sitekapinda-launch-maintain
description: Plan and execute customer-approved SiteKapında preview hosting, public launch, domain, DNS, and maintenance work with explicit action-time confirmations. Use only after a user requests deployment or customer-site changes; default to planning and local validation without publishing.
---

# SiteKapında Launch & Maintain

Move a reviewed preview toward production without treating earlier interest or setup permission as deployment consent.

## Default behavior

Plan and validate locally. Read [references/approval-checklist.md](references/approval-checklist.md) before any external action. This skills-only plugin does not bundle Codex Sites, Cloudflare, registrar, or messaging integrations; use an installed capability only when the user explicitly requests it.

## Workflow

1. Identify the customer, repository, target environment, current URL, requested change, and rollback path.
2. Verify that content, brand assets, contact details, and the intended domain have documented customer approval.
3. Inspect and test the exact local files to be uploaded. Preserve preview disclaimers until public launch approval is complete.
4. For a private hosted demo, show the host, visibility, noindex behavior, uploaded files, and resulting URL; obtain confirmation immediately before upload.
5. For a public launch, show the account, project, domain, DNS changes, expected cost, public exposure, and rollback plan; obtain confirmation immediately before deployment.
6. Treat domain purchase, DNS mutation, and public deployment as separate external actions with separate confirmations.
7. Verify the resulting URL, TLS, responsive layout, forms/links, robots policy, and ownership labeling. Record what changed without printing credentials.
8. For maintenance, reproduce the issue, implement locally, test, preview the diff, and confirm again before updating production.

## Mandatory boundaries

- Never infer customer approval from `interested`, a salesperson note, or a prior demo review. `approved` must be backed by explicit customer confirmation.
- Never purchase a domain, accept a charge, change nameservers/DNS, upload files, or publish a site without action-time user confirmation.
- Never reuse account IDs, tokens, deployment IDs, or credentials found in examples or another customer's workspace.
- Do not transfer another customer's data or chat history. Give each customer only their own repository, approved assets, and decision records.
- Do not claim a private hosted demo is an official site. Keep it noindex and visibly labeled until public-launch approval.
- If the selected integration is unavailable, stop after producing an exact manual handoff; do not invent a successful deployment.
