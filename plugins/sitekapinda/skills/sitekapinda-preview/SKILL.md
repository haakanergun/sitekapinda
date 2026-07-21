---
name: sitekapinda-preview
description: Review, regenerate, and safely refine SiteKapında's business-specific local website previews and image-prompt manifests. Use when Codex needs to inspect a selected lead's demo, verify noindex/disclaimers, or plan rights-safe visual improvements without publishing an official customer site.
---

# SiteKapında Preview

Turn a reviewed candidate into a tangible local first version while preserving its demo status.

## Workflow

1. Read [references/preview-contract.md](references/preview-contract.md).
2. Confirm the selected lead and evidence source. Do not invent services, prices, awards, testimonials, operating hours, credentials, or customer claims.
3. Locate the generated package under `runtime/generated/demos/<slug>/`. If it does not exist, run one bounded mock pipeline cycle or explain why a real run needs separate permission.
4. Inspect `index.html`, `brand-kit.json`, `image-prompts.json`, `page-manifest.json`, and local assets together.
5. Verify `noindex,nofollow`, the preview disclaimer, owner-approval language, absence of review text, and working local asset paths.
6. Refine files locally when requested, then rerun relevant tests or validation and show the exact preview path.
7. Label the result as a proposal, never as an official site.

## Visual evidence boundary

- Prefer synthetic fixtures, customer-supplied media with confirmed rights, or explicitly permitted public business context.
- Do not copy social-media photos, logos, or review content merely because they are publicly viewable.
- The packaged runtime creates deterministic SVG assets and an image-generation-ready prompt manifest. Do not claim it called GPT Image.
- If the user explicitly invokes an image-generation tool, record the source/rights basis, keep the output labeled as a demo, and review visible text and business claims before use.

## Publishing boundary

Keep this skill local. Uploading even a private preview to Codex Sites, Cloudflare, or another host is an external publish action and belongs to `$sitekapinda-launch-maintain`. Require a new confirmation that names the destination and files to be uploaded.
