# Lead lifecycle

## States

- `not_lead`: retained record that is not currently qualified
- `ready`: qualified preview is available for human review
- `contacted`: a human confirmed that contact occurred
- `interested`: a human recorded an affirmative customer signal
- `approved`: explicit customer approval is documented
- `rejected`: the customer declined or the opportunity was closed
- `do_not_contact`: outreach is prohibited and suppression must be respected

## Local commands

Generate the Sales Ops workspace:

```bash
python -m sitekapinda dashboard --mode mock
```

Export reviewed records:

```bash
python -m sitekapinda export --mode mock --format csv
python -m sitekapinda export --mode mock --format json
```

Update one lifecycle state:

```bash
python -m sitekapinda lead-status --mode mock --place-id <id> --status <state> --note "<fact supplied by user>"
```

Add a suppression entry:

```bash
python -m sitekapinda suppress --mode mock --place-id <id> --reason "<reason supplied by user>"
```

Use the active virtual environment's Python executable when one exists.

## Audit rule

A status change is a local record mutation, not an external communication. Keep notes factual, attributable to user-provided evidence, and free of unnecessary sensitive data. For a synthetic demo, label any test outcome as fictional rather than presenting it as real traction.
