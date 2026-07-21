# Hourly Discovery Automation Template

This is a reviewable template, not an installed automation. Scheduled tasks are account- and machine-specific and must be created from the Codex desktop app after the user confirms the project path, model, sources, and cadence.

Suggested cadence: hourly while the local machine and Codex app are running.

Suggested prompt:

> Use `$sitekapinda-discover` in this repository. Inspect only the configured permitted sources, qualify at most five new candidates, persist evidence and rejection reasons, and stop. Do not contact businesses, generate public pages, buy domains, or deploy. If real-mode credentials or source permissions are missing, report the blocker instead of falling back to scraping.

Recommended first run: paused or one-time dry run with the synthetic fixture.

