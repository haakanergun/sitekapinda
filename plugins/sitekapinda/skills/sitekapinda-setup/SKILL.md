---
name: sitekapinda-setup
description: Set up, verify, and run the SiteKapında submission in its safe synthetic mode. Use when Codex needs to install the local Python package, run the judge demo, diagnose prerequisites, or explain the generated artifacts without enabling real discovery, outreach, automation, or deployment.
---

# SiteKapında Setup

Prepare a reproducible local demonstration while keeping every external action disabled.

## Workflow

1. Work from the repository root that contains `pyproject.toml`, `src/sitekapinda/`, and `data/mock_places.json`.
2. Read [references/judge-runbook.md](references/judge-runbook.md) before running commands.
3. Inspect prerequisites and existing files. Preserve an existing virtual environment and `runtime/`; never delete or overwrite user data to obtain a clean run.
4. Use the repository bootstrap for the current platform. It creates or reuses a workspace-local virtual environment, runs without package downloads, forces synthetic paths for its process, and executes the tests plus exactly one mock pipeline cycle.
5. If bootstrap cannot run, use only the manual `PYTHONPATH=src` fallback in the runbook; do not turn an offline setup problem into a package-registry install.
6. Show the local English Sales Ops workspace, generated demo paths, and run report. Explain which outputs are synthetic and which capabilities are intentionally not exercised.
7. Report failures with the command, error, and the smallest safe remediation. Do not silently switch to real mode.

## Mandatory boundaries

- Default to `--mode mock`. Never run `--mode real` from this skill.
- Never start `worker`, create a scheduled task, or install an hourly automation unless the user separately requests it.
- Never contact a business, send a message, upload a preview, buy a domain, change DNS, or publish a site.
- Keep credentials out of the repository. Do not ask the user to paste secrets into tracked files or chat output.
- Describe this submission truthfully: the packaged runtime is deterministic and produces image-generation-ready prompts; it does not itself call GPT Image or provide an MCP server.
- Treat local fixture data as fictional. Stop and warn if the expected synthetic fixture is missing or appears to contain real personal data.

## Handoff

Recommend `$sitekapinda-discover` for discovery analysis, `$sitekapinda-preview` for preview review, and `$sitekapinda-sales` for local lifecycle updates. Use `$sitekapinda-launch-maintain` only for an explicitly approved deployment or maintenance request.
