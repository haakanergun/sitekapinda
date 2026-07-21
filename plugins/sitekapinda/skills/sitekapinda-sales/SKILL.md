---
name: sitekapinda-sales
description: Review SiteKapında lead exports and Sales Ops workspace data, and update the local lead lifecycle with auditable notes. Use for synthetic sales-panel demonstrations or user-directed record maintenance; it never sends calls, email, WhatsApp, or other outreach.
---

# SiteKapında Sales

Operate the local review queue without conflating a database state with a real-world interaction.

## Workflow

1. Read [references/lead-lifecycle.md](references/lead-lifecycle.md).
2. Confirm whether the workspace uses synthetic or real data. Default all judge demonstrations to `--mode mock`.
3. Regenerate the Sales Ops workspace or export only the minimum fields needed for the task.
4. Before changing a record, show its place ID, current status, proposed status, note, and next action.
5. Apply only the user-requested local change, regenerate the Sales Ops workspace, and verify the persisted result.
6. Report that the command updated local state only and sent no message.

## Truthful status rules

- Set `contacted` only when the user confirms contact actually occurred.
- Set `interested` only from an affirmative customer signal supplied by the user.
- Set `approved` only when explicit customer approval is documented; interest is not approval.
- Set `rejected` when the user records a refusal.
- Set `do_not_contact` immediately when requested, and preserve the suppression boundary.
- Never fabricate notes, contact timestamps, outcomes, or conversion statistics to make a demo look successful. Use clearly fictional records for judge demonstrations.

## Mandatory boundaries

- This plugin has no outbound connector. Never claim a CLI status command sent a call, email, WhatsApp, or preview.
- Draft outreach only when requested. Show the complete recipient, channel, and message for review; do not send without a separate action-time confirmation and an authorized connector.
- Minimize exposure of phone numbers and notes in logs or shared artifacts.
- Do not weaken or remove a `do_not_contact` or suppression record without an explicit, documented user instruction and a lawful basis.
- Do not publish a preview or deploy a site from this skill.
