# Approval checklist

## Customer content approval

Record affirmative confirmation for:

- business name and contact details
- services, copy, prices, hours, and claims
- logo, photography, and other media rights
- forms, analytics, cookies, and privacy text
- final domain and public visibility

An interested lead is not an approved customer site.

## Private hosted demo gate

Before uploading, show:

1. The named hosting service and account/project.
2. The exact directory or files to upload.
3. The proposed URL and who can access it.
4. The noindex and visible demo-label behavior.
5. How to remove the preview.

Obtain confirmation immediately before the upload action.

## Domain and DNS gate

Before any registrar or DNS mutation, show:

1. Exact domain spelling and registrant account.
2. Purchase/renewal price and renewal behavior, when applicable.
3. Records to add, change, or remove with TTL values.
4. Expected propagation and service impact.
5. A rollback or recovery plan.

Domain purchase and DNS changes require their own confirmations; neither is implied by site-deployment approval.

## Public deployment gate

Before deployment, show:

1. Exact production account, project, branch/build, and public URL.
2. Files and data leaving the local machine.
3. Tests completed and known limitations.
4. Whether preview-only disclaimers/noindex will change.
5. Rollback procedure.

Obtain confirmation immediately before publishing. Afterward, verify the public result and report the observed state rather than assuming success.

## Maintenance gate

Local edits and tests may proceed within the requested repository. Updating production is a new external mutation and needs a fresh confirmation that identifies the target and diff, even when the user approved an earlier launch.
