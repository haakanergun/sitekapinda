# Build Week changes and prior-work disclosure

## Why this disclosure exists

SiteKapında did not begin as an empty repository during OpenAI Build Week. It was an existing product concept and working prototype. Build Week was used to clarify the architecture, strengthen the Codex-centered workflow, produce a judgeable demonstration, and turn a large private workspace into a clean, reproducible, safety-bounded submission.

This document distinguishes the prior foundation, Build Week contribution, and future roadmap. It should be read with the executable evidence rather than as a substitute for commit history.

## Prior foundation

Before the final submission effort, the broader SiteKapında workspace already contained substantial exploration and product work:

- the SiteKapında name, value proposition, and Turkish product direction
- a deterministic Python/SQLite lead-to-preview pipeline
- mock and official Google Places provider boundaries
- rule-based compliance, scoring, and suppression logic
- generated demo pages, manifests, SVG assets, reports, and a Sales Ops workspace
- a public SiteKapında marketing site and Cloudflare experiments
- a library of visual preview experiments produced across Codex/image-generation tasks
- sales lifecycle exploration and early manual customer outreach
- a real customer website implementation represented by [cagrikarakas.com](https://cagrikarakas.com)

The private workspace also contained limitations inappropriate for direct publication: local caches and runtime artifacts, real operational data, environment-specific Cloudflare values, historic generated assets, mixed status vocabularies, and narrative language that sometimes described a future agent architecture more strongly than the code supported.

## Build Week contribution

### 1. Runtime and claim audit

Codex was used to inspect the project end to end and answer a crucial question: what is executable today, and what belongs to the operating workflow or roadmap?

The resulting submission makes the boundary explicit:

- discovery, compliance, scoring, preview packaging, SQLite, Sales Ops workspace generation, and exports are deterministic code
- Codex tasks and GPT Image assisted research, design, implementation, QA, demo creation, and continued development
- there is no OpenAI SDK or autonomous GPT-5.6 API runtime hidden inside the Python package
- private review, outreach, domain work, and deployment remain distinct, human-approved operations

This accuracy work is a substantive part of the submission: it turns a compelling concept into a system judges can evaluate without relying on unverifiable agent language.

### 2. Safe distributable package

The private working directory was not copied wholesale. A new allowlisted package was assembled under `submission/sitekapinda-build-week/` with:

- only the deterministic application source needed for the demonstration
- a completely fictional and non-routable 12-business fixture
- the same English Sales Ops master-detail interface shown in the video, with production records and connectors removed and every judge record supplied by the synthetic local pipeline
- offline tests that enforce fixture safety and run the end-to-end mock pipeline
- zero-third-party-dependency bootstrap scripts for Windows, macOS, and Linux
- doctor scripts and local start helpers
- safe `.env.example` defaults
- runtime/caches/secrets/customer-data exclusions
- English README, architecture, test, safety, security, and disclosure documents
- an MIT license

The bootstrap forces mock paths for its own process and removes any inherited Google Places key before the demo. It neither starts the hourly worker nor deploys anything.

### 3. Codex-ready operating layer

Repeated SiteKapında workflows were converted into a repository-local Codex plugin with five validated skills:

- setup
- discovery
- private preview
- sales-state operations
- launch and maintenance planning

The plugin includes no MCP server, connector, app, credential, or automatic deployment capability. It uses the model selected in the user's Codex task and preserves explicit approval gates.

The repository also includes:

- `AGENTS.md` with durable project truth, commands, safety rules, and definition of done
- versioned example prompts for discovery, site building, preview, and QA
- an example hourly-automation prompt that is not installed or scheduled automatically
- a model-routing note that separates authoring choices from runtime dependencies

### 4. Demonstration and product communication

Build Week production work turned the internal workflow into a concise public story:

- [2:40 English product video](https://youtu.be/ktev7Dng_jk)
- a Build Week YouTube thumbnail and visual system
- [Codex Sites private-demo example](https://sedirra-sites-demo.haakanergun.chatgpt.site)
- a clear ending flow from discovery to human-approved launch
- restaurant, beauty, and dental visual directions to show category specificity
- the independent [Çağrı Karakaş customer implementation](https://cagrikarakas.com) as a compact delivery example
- [sitekapinda.com](https://sitekapinda.com) as the product home

The video and hosted artifacts show the broader operating vision. The local repository remains the authoritative evidence for executable behavior.

### 5. Creative workflow refinement

The project narrative was refined from “generate a generic site” into a business-specific evidence-to-first-version process:

- preserve verified identity and facts
- use rights-safe or permissioned visual context
- use GPT Image for stronger web-ready creative direction, not for inventing business truth
- package twenty-four complete fictional website UI mockups—independent desktop and mobile compositions—spanning restaurant, beauty, cafe, grooming, services, education, fitness, floral, pet, automotive, and textile categories
- give every sector a different information architecture, art direction, typography, and conversion path rather than recoloring one template
- render the paired GPT Image mockups as static local assets inside Sales Ops; there are no iframes and the mobile designs are not desktop crops
- keep visible UI, compliance disclaimers, state, and publication gates deterministic
- show a live private version before asking the owner to commit
- keep revisions in a continuing Codex development context

This establishes a practical division of labor between creative models and auditable application code.

## Change matrix

| Area | Earlier prototype state | Build Week submission state |
|---|---|---|
| Runtime description | agent vision and deterministic implementation could be conflated | executable Python core and Codex-assisted workflow are explicitly separated |
| Distribution | multi-gigabyte private workspace with local/runtime material | allowlisted judge package with synthetic data and no secrets |
| Setup | manual commands and environment knowledge | idempotent one-command bootstrap plus doctor |
| Judge evidence | distributed across internal artifacts | five-minute offline test guide and linked hosted evidence |
| Codex workflow | valuable but task/chat-specific | repo guidance plus a five-skill local plugin |
| Model claims | GPT-5.6 could sound like an application dependency | authoring model use disclosed; no runtime API claim |
| Image workflow | many visual experiments, inconsistent provenance language | rights-safe/permissioned boundary and explicit conceptual-vs-verified distinction |
| Safety | noindex, compliance, and suppression existed in code | controls documented, tested with synthetic data, and made part of Codex guidance |
| Automation | account-local experiments and local worker | no schedule is transferred; foreground hourly example remains opt-in |
| Publication | Cloudflare/Sites work existed elsewhere | public action excluded from bootstrap and gated by explicit approval |

## Founder-reported early validation

The product story references a small manual test of ten businesses: four reportedly liked the tailored designs but the conversations did not close, five said they were not interested, and one — Çağrı Karakaş — became the first customer.

This is directional founder-reported evidence, not a statistically meaningful conversion benchmark. The underlying contact records are intentionally excluded from the public repository. Judges should use [cagrikarakas.com](https://cagrikarakas.com) as the public implementation evidence and should not infer performance guarantees from the ten-business sample.

## What was deliberately not claimed as complete

The following are not Build Week runtime features in this repository:

- autonomous GPT-5.6 API agents inside the Python application
- automatic collection of social-media images
- unattended outreach or sales messaging
- owner-consent verification service
- automatic Codex Sites publication
- domain purchase, DNS mutation, or Cloudflare deployment
- production authentication and multi-tenant data isolation
- durable model-call telemetry, prompt registry, and structured-output orchestration
- fully automatic visual QA and repair loops
- customer chat-history export as a portable developer agent

The concept and video explain how some of these pieces can work together with Codex and extensions. The repository presents them as human-supervised workflow steps or future hardening, not completed autonomous infrastructure.

## Reproduce the Build Week evidence

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1
```

or:

```bash
bash ./scripts/bootstrap.sh
```

Then follow [JUDGE_TEST_GUIDE.md](JUDGE_TEST_GUIDE.md). The clean local result, source code, tests, and documented limitations are the reproducible evidence for this submission.
