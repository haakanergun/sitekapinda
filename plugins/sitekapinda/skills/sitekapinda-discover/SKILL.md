---
name: sitekapinda-discover
description: Run and inspect SiteKapında business discovery with source, compliance, scoring, deduplication, and data-minimization controls. Use for a synthetic discovery cycle, discovery report review, or an explicitly requested real Google Places run; never use it for outreach or publishing.
---

# SiteKapında Discover

Find qualified missing-site opportunities while preserving evidence and consent boundaries.

## Choose the mode

- Use `mock` unless the user explicitly asks for real discovery.
- Before any real run, read [references/discovery-policy.md](references/discovery-policy.md), explain the network request and local data written, verify an official API credential is already supplied through the environment, and obtain action-specific confirmation.
- Never infer permission to run real discovery from permission to run the synthetic judge demo.

## Run one cycle

1. Inspect the configured mode, search locations, score threshold, and maximum results.
2. Run one bounded cycle. Prefer `python -m sitekapinda run --mode mock` for judging.
3. Review the report rather than relying only on terminal totals. Distinguish selected, already seen, compliance-rejected, low-score, generated, and failed candidates.
4. Verify generated candidates have a stable `place_id`, an allowed initial category, and no suppression record.
5. Summarize evidence, score reasons, output paths, and errors without exposing unnecessary contact data.

## Mandatory boundaries

- Use permitted public business fields only. Never scrape social networks, bypass access controls, or ingest private sources.
- Do not collect or quote review text. The real provider deliberately excludes reviews and raw response storage.
- Do not contact discovered businesses or change their sales status from this skill.
- Do not start an infinite worker or create an hourly Codex task without a separate user request. Show its exact frequency, scope, data source, and stop mechanism before asking for approval.
- Do not claim every missing-site signal is correct. Treat results as candidates for human review.
- Respect `do_not_contact` and suppression records without override.

## Handoff

Use `$sitekapinda-preview` only after a candidate has passed review. Use `$sitekapinda-sales` for local lifecycle changes; discovery itself sends nothing.
