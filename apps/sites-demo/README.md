# Sedirra — Synthetic Codex Sites Demo

This is a fictional restaurant website used to demonstrate the private-preview stage of SiteKapında. It contains no real booking channel, address, telephone number, review, or customer record.

## Run locally

Requires Node.js 22.13 or newer.

```bash
npm ci
npm run dev
```

Validate the production build:

```bash
npm test
npm run lint
```

## Codex Sites

The live Build Week demonstration is available at <https://sedirra-sites-demo.haakanergun.chatgpt.site>.

The checked-in `.openai/hosting.example.json` deliberately omits the original Sites project identifier. To deploy a copy, create a new Codex Sites project in the judge's own workspace and let Sites generate a new `.openai/hosting.json`.

The private demo is not the final public customer website. SiteKapında collects revisions and requires explicit public-publish approval before a domain is attached.

