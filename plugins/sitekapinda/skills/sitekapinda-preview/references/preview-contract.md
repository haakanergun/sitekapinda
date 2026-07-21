# Preview contract

## Package layout

Each generated preview is expected to contain:

```text
runtime/generated/demos/<slug>/
├── index.html
├── brand-kit.json
├── image-prompts.json
├── page-manifest.json
└── assets/
    ├── hero-desktop.png
    └── hero-mobile.png
```

Desktop and mobile hero assets are separate compositions. They must remain clearly synthetic or rights-safe creative inputs and must not be represented as verified photographs of the business.

## Required checks

- The page contains a robots directive with `noindex` and `nofollow`.
- The page clearly states that it is a SiteKapında preview and is not official without owner approval.
- No customer review text, fabricated testimonial, award, guarantee, price, or regulated claim appears.
- Phone, name, category, and location match the selected record or are visibly marked as placeholders.
- Mobile and desktop layouts remain usable, and mobile uses its dedicated asset rather than a desktop crop.
- All assets resolve locally and no third-party tracker is introduced.

## GPT Image handoff

`image-prompts.json` records the intended art direction and safety constraints. It is not evidence of an API call. If a user requests generated imagery, use the available image-generation capability separately, retain the prompt/output provenance, and never imply the resulting scene is a documentary photograph of the business unless a rights-cleared source and transformation request support that claim.

## Approval levels

1. **Local proposal:** no external upload; suitable for the synthetic judge demo.
2. **Private hosted demo:** requires explicit approval to upload to the named host and must remain noindex with an unambiguous demo label.
3. **Public customer site:** requires documented customer content approval plus a separate action-time deployment confirmation.
