# How Codex was used

## Short answer

Codex is the development and operating environment around SiteKapında, not a hidden dependency inside the Python program.

During Build Week, Codex tasks helped inspect a large existing workspace, separate real runtime behavior from aspirational agent language, parallelize implementation and review, improve prompt and visual direction, validate browser flows, create the demonstration video, and package a clean synthetic repository. GPT Image / `imagegen` supported rights-safe visual exploration. Codex Sites demonstrated how an owner can see a live private first version before public launch.

The local program that judges run remains deterministic, offline, and independently testable.

## Capability ledger

| Capability | Used during authoring | Runs in local bootstrap | Requires separate human authorization |
|---|---:|---:|---:|
| Codebase research and architecture audit with Codex | Yes | No | No external action |
| Parallel Codex implementation, documentation, and review tasks | Yes | No | No external action |
| Python discovery/compliance/scoring/generation pipeline | Yes | Yes | No in mock mode |
| GPT Image creative exploration and asset transformation | Yes | No | Source rights must be confirmed |
| Codex Sites private-demo workflow | Yes | No | Yes for upload/hosting changes |
| Browser validation and submission assistance | Yes | No | Yes for uploads, saves, or submission |
| Hourly Codex scheduled discovery experiments in the authoring environment | Yes | No | Yes; account-local and not transferred |
| Local deterministic hourly worker | Available | Not enabled by default | User starts and stops it |
| Outreach to a business | Human workflow only | No | Always |
| Domain purchase or public deployment | Human workflow only | No | Always |

## Model disclosure

The authoring workflow used GPT-5.6-class Codex models, primarily the `gpt-5.6-sol` profile where it was available. The demonstration shows an hourly, high-reasoning discovery configuration as an example of the creator's Codex workspace.

That configuration is **not** an application runtime claim:

- `pyproject.toml` has no OpenAI SDK dependency.
- `src/sitekapinda/` does not call an OpenAI endpoint.
- The Python pipeline does not silently fall back to a model.
- The bundled plugin does not force a private or account-specific model identifier.
- A judge may use whatever Codex model is available in their own environment.

This distinction is intentional. Deterministic policy, suppression, state, and publication gates should not depend on a probabilistic creative model.

## Build Week Codex workflow

### 1. Research and truth audit

Codex mapped the existing runtime, generated artifacts, sales panel, Cloudflare code, Sites demo, and Remotion project. It compared claims in the narrative with executable code and identified the central truth boundary: the core was a deterministic pipeline, while the strongest design work lived in Codex and image-generation sessions. The judge build reuses the video's English Sales Ops interface without copying production records, connectors, or contact actions.

The submission therefore describes:

- **deterministic runtime** for discovery, compliance, scoring, persistence, and safe first-version packages
- **Codex-assisted workflow** for research, creative direction, implementation, QA, private review, and maintenance
- **future production architecture** only as a roadmap, never as a finished API service

### 2. Parallel implementation and review

Focused Codex tasks were used for independent scopes such as runtime packaging, plugin authoring, safety boundary review, documentation, video copy, Remotion adjustments, and candidate-demo inspection. Work was reconciled in one shared workspace and validated against the same safety and accuracy requirements.

This is where multi-agent operation added the most value: research-heavy and implementation-heavy work could progress together, while the final repository retained one consistent runtime truth.

### 3. Creative production

GPT Image / `imagegen` was used to explore rights-safe visual direction and to produce twenty-four complete website UI mockups for the judge fixture: an independent desktop and mobile composition for each of twelve fictional businesses. The designs deliberately vary by sector—editorial restaurant, booking-first beauty, vertical-navigation cafe, diagnostic-console auto service, textile conservation, modular education, and other distinct systems. Rights-safe sector photography supplied visual context; the checked-in offline runtime simply presents the resulting local PNGs and makes no model call.

Image-model outputs were treated as creative artifacts:

- no exact business fact was inferred from an image
- no generated text was treated as verified customer copy
- conceptual imagery was not presented as a verified photograph of real premises
- HTML structure, disclaimers, and publication state remained deterministic/human-controlled
- GPT Image hero assets are labelled as synthetic authoring inputs and are never presented as verified premises or owner-approved truth
- earlier packaged concepts are labelled as visual-reference fallbacks and are never presented as live websites

### 4. Private review through Codex Sites

The hosted [Codex Sites demo](https://sedirra-sites-demo.haakanergun.chatgpt.site) shows the intended private-review step: give an owner a live link, collect concrete revision requests, and obtain approval before any public domain launch.

The local CLI does not deploy to Sites. Hosting remains an explicit separate operation.

### 5. Persistent customer development context

A continuing Codex task can preserve the design decisions, bug history, and maintenance discussion for one customer. This makes the same task useful after initial delivery.

For a portable production version, customer context should also be written to versioned files (evidence, decisions, approvals, deployments, and tests). Chat history is helpful context but should not be the only source of truth, and one customer's context must never be exposed to another.

## Bundled SiteKapında skills

The repository packages five reusable skills under `plugins/sitekapinda/skills/`.

| Skill | Purpose | Required stop condition |
|---|---|---|
| `$sitekapinda-setup` | Verify prerequisites and run the synthetic local demo | Never enable real mode or external actions automatically |
| `$sitekapinda-discover` | Run/review compliant discovery and explain decisions | Reject unsupported sources and stop on policy ambiguity |
| `$sitekapinda-preview` | Inspect or refine a private, noindex first version | Never present it as official or publish it |
| `$sitekapinda-sales` | Review leads and operate local synthetic status changes | Never contact a business on the user's behalf without explicit instruction |
| `$sitekapinda-launch-maintain` | Plan revisions, launch readiness, and ongoing maintenance | Require explicit owner and user approval before deployment or account changes |

Skills are instructions that Codex loads when invoked. They can call repository scripts and apply consistent checks, but they do not provide credentials, authority, or a hosted agent service.

## Open this package in Codex

### Path A — no plugin installation required

1. Open the repository root as the Codex project.
2. Start a new task from the repository root so `AGENTS.md` is discovered.
3. Send:

```text
Read README.md and AGENTS.md. Run the safe synthetic judge path, verify the
tests, and explain the generated English Sales Ops workspace and one preview. Do not use real
provider mode, contact anyone, upload data, or publish anything.
```

This path proves that the project is Codex-friendly even when local plugin installation is unavailable.

### Path B — use the bundled plugin

The submission includes a local marketplace descriptor and an installable plugin under `plugins/sitekapinda/`. On a Codex surface that supports local plugins:

1. Open the Plugins directory from Codex or Work mode.
2. Add/select this repository's local marketplace file at `.agents/plugins/marketplace.json`.
3. Install **SiteKapında**.
4. Start a new Codex task so the bundled skills are available.
5. Invoke `$sitekapinda-setup` with the safe prompt below.

Plugin availability and UI can depend on the user's Codex surface and workspace policy. If the local marketplace is unavailable, use Path A; the runtime evidence is identical.

Official Codex concepts used by this package:

- [`AGENTS.md` project guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Build plugins](https://learn.chatgpt.com/docs/build-plugins)
- [Scheduled tasks](https://learn.chatgpt.com/docs/automations.md)

## Copy-ready judge prompts

Safe setup:

```text
Use $sitekapinda-setup to run the synthetic demonstration. Verify the doctor
checks and unit tests, then show me the English Sales Ops workspace and one generated preview.
Do not enable real discovery or take any external action.
```

Architecture review:

```text
Explain this repository's actual data flow from BusinessCandidate to the
generated noindex preview. Separate deterministic runtime behavior, Codex-
assisted authoring, and future roadmap claims.
```

Safety review:

```text
Audit the synthetic judge run for personal data, secrets, network calls,
invented business claims, copied reviews, missing noindex tags, and paths that
could contact or publish externally. Report evidence by file.
```

Synthetic sales-state demonstration:

```text
Use $sitekapinda-sales to list the fictional leads, choose one generated lead,
and explain the local status transition you recommend. Ask before changing the
status. Do not send a message or open an external account.
```

Launch planning without launch:

```text
Use $sitekapinda-launch-maintain to produce a launch-readiness checklist for a
synthetic approved lead. Do not deploy, register a domain, change DNS, or use
any account credential.
```

## Hourly operation boundary

The product story includes hourly discovery. There are two different mechanisms:

- In the creator's environment, scheduled Codex tasks were used for recurring experiments with task history and model-assisted follow-up.
- In this portable repository, `scripts/run_hourly.ps1` and `scripts/run_hourly.sh` start a transparent foreground Python loop at a 3,600-second interval.

Bootstrap starts neither. Codex scheduled tasks are account-local and are not silently copied to a judge's machine. A user should test the prompt in a normal task, choose the model/permissions themselves, inspect early runs, and keep the narrowest required access before creating any schedule.

## Why this design matters

Codex contributes most when it carries rich project context across research, design, implementation, QA, and maintenance. Deterministic code contributes most where repeatability, policy enforcement, suppression, and publication safety matter.

SiteKapında combines those strengths without claiming that a prompt alone is a production system.
