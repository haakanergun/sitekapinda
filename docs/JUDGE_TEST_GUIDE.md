# Judge test guide

## Goal

In about five minutes, verify that SiteKapında can take fictional business candidates through discovery, deterministic safety checks, transparent scoring, private-preview generation, persistence, and the same English Sales Ops master-detail interface shown in the video — using only synthetic local data and without credentials, network access, outreach, or publication.

## Evidence links

- Product video: [https://youtu.be/ktev7Dng_jk](https://youtu.be/ktev7Dng_jk)
- Codex Sites demo: [https://sedirra-sites-demo.haakanergun.chatgpt.site](https://sedirra-sites-demo.haakanergun.chatgpt.site)
- Product site: [https://sitekapinda.com](https://sitekapinda.com)
- Customer implementation example: [https://cagrikarakas.com](https://cagrikarakas.com)

External links are optional supporting evidence. The test below is local and self-contained.

## Prerequisites

- Python 3.10 or newer
- Windows PowerShell, or Bash on macOS/Linux
- permission to create files inside this repository

Not required:

- OpenAI API key
- Google Places API key
- Node.js
- Docker
- cloud account
- internet access

## Test 1 — one-command clean run

From the repository root:

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1
```

macOS/Linux:

```bash
bash ./scripts/bootstrap.sh
```

Bootstrap is idempotent and performs four operations:

1. creates a local `.venv` without downloading third-party packages
2. creates `.env` from safe mock defaults only when `.env` is absent
3. runs doctor checks and the offline test suite
4. runs one synthetic pipeline cycle

Expected result:

- doctor reports a compatible Python interpreter and required files
- all twelve offline tests pass
- the run reports fictional candidates found and one or more generated previews
- no browser login, API prompt, upload, outreach, or deployment occurs
- `runtime/` contains the database, generated artifacts, and reports

If bootstrap fails, copy the complete doctor/test output into the issue report; do not add an API key as a workaround.

## Test 2 — inspect the evidence

Expected output tree:

```text
runtime/
├── sitekapinda.sqlite3
├── generated/
│   ├── index.html
│   ├── admin.css
│   ├── admin.js
│   ├── panel-data.js
│   ├── sitekapinda-logo.svg
│   ├── mockups/
│   │   ├── <fictional-place-id>-desktop.png
│   │   └── <fictional-place-id>-mobile.png
│   └── demos/
│       └── <fictional-business-slug>/
│           ├── index.html
│           ├── brand-kit.json
│           ├── image-prompts.json
│           ├── page-manifest.json
│           └── assets/
│               ├── hero-desktop.png
│               └── hero-mobile.png
└── reports/
    ├── leads.csv
    ├── leads.json
    └── <run reports>
```

Open `runtime/generated/index.html` directly in a browser. It should be the English Sales Ops master-detail interface: a searchable and filterable fictional lead list on the left, with the selected lead's status, synthetic evidence, rationale, and two full GPT Image website designs on the right. The large frame shows the dedicated desktop mockup and the phone frame shows an independently composed mobile mockup—not a crop. The preview surface contains no iframe or generated page execution. Every record comes from `data/mock_places.json` through the local pipeline; no production customer data is bundled.

For the primary Sales Ops surface, confirm:

- every lead loads separate `<place-id>-desktop.png` and `<place-id>-mobile.png` assets
- mobile is independently composed rather than cropped from desktop
- sector layouts differ across restaurant, beauty, cafe, grooming, service, fitness, learning, floral, pet, automotive, and textile examples
- the panel contains no iframe, executable generated-page script, form submission, or external preview navigation
- synthetic call and WhatsApp controls stay local/inert and contain no `tel:` or `wa.me` target
- the mockups contain no copied reviews, invented prices, awards, credentials, or outcome guarantees
- the business name and contact fields match the fictional fixture rather than a real customer

Twenty-four complete GPT Image UI mockups are packaged under `src/sitekapinda/panel_assets/mockups/`: an independently composed desktop and mobile website design for every fictional fixture. The local pipeline copies those assets into `runtime/generated/mockups/` and records only safe local paths in `panel-data.js`; it does not claim that it called GPT Image at runtime. Supplementary deterministic HTML packages remain under `runtime/generated/demos/` as evidence of the later implementation stage, but they are not embedded in the Sales Ops preview surface.

## Test 3 — repeat the offline checks

Windows:

```powershell
.\scripts\doctor.ps1
$env:PYTHONPATH = (Resolve-Path .\src)
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
powershell -ExecutionPolicy Bypass -File .\scripts\run_once.ps1
```

macOS/Linux:

```bash
bash ./scripts/doctor.sh
PYTHONPATH=src ./.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
bash ./scripts/run_once.sh
```

Because the database remembers stable fixture identifiers, a second run should skip candidates already processed or suppressed instead of creating duplicate leads. That behavior is an intentional idempotency check.

## Test 4 — serve the static Sales Ops workspace locally

This is optional; opening the files directly is sufficient.

Windows:

```powershell
.\.venv\Scripts\python.exe -m http.server 8000 --directory runtime/generated
```

macOS/Linux:

```bash
./.venv/bin/python -m http.server 8000 --directory runtime/generated
```

Then open:

```text
http://127.0.0.1:8000/
```

Stop the server with `Ctrl+C`. This server binds for local inspection only; it is not a deployment step.

## Test 5 — demonstrate a synthetic sales-state update

Choose an ID from `runtime/reports/leads.json`; do not substitute a real business.

Windows PowerShell:

```powershell
$lead = (Get-Content -Raw .\runtime\reports\leads.json | ConvertFrom-Json)[0]
$env:PYTHONPATH = (Resolve-Path .\src)
.\.venv\Scripts\python.exe -m sitekapinda mark-contacted `
  --mode mock `
  --place-id $lead.place_id `
  --note "Synthetic judge test — no message was sent"
```

macOS/Linux:

```bash
PLACE_ID="$(./.venv/bin/python -c "import json; print(json.load(open('runtime/reports/leads.json', encoding='utf-8'))[0]['place_id'])")"
PYTHONPATH=src ./.venv/bin/python -m sitekapinda mark-contacted \
  --mode mock \
  --place-id "$PLACE_ID" \
  --note "Synthetic judge test — no message was sent"
```

Refresh the workspace and verify the status. The CLI updates SQLite and regenerates `panel-data.js`; “contacted” is a lifecycle label and does not send a message. The panel's **Save locally** action writes only to this browser's `localStorage` and sends nothing. Use **Reset view** before checking a CLI change if a browser-only override exists.

Optional suppression test: repeat the same platform-specific CLI pattern with `mark-do-not-contact` instead of `mark-contacted`, using only a fictional fixture ID. The status should become `do_not_contact`, and a suppression record should prevent future reprocessing.

## Test 6 — use Codex as the judge assistant

Open the repository root in Codex and start a new task. `AGENTS.md` supplies the durable project commands and safety boundary.

No plugin installation is required for this prompt:

```text
Read README.md and AGENTS.md. Run the synthetic judge path, verify the tests,
and explain one generated preview from input evidence through compliance,
scoring, persistence, and HTML output. Do not use real provider mode, contact
anyone, upload data, or publish anything.
```

If the Codex surface supports repo-local plugin marketplaces, install the SiteKapında plugin from `.agents/plugins/marketplace.json`, start a new task, and run:

```text
Use $sitekapinda-setup to install and run the synthetic local demo.
```

The plugin is a bundle of five workflow skills and no MCP server or app. It uses the model already selected in the judge's Codex environment. If local plugin installation is unavailable, the no-plugin path above demonstrates the same runtime.

## Optional — reproduce the Sites companion

The hosted Sedirra demonstration source lives at `apps/sites-demo/`. It is separate from the Python core and requires Node.js 22.13+, npm, and package-registry access:

```bash
cd apps/sites-demo
npm ci
npm test
npm run lint
```

The app is fictional, contains `noindex,nofollow` metadata, and has no working address, phone, booking, or customer record. Skip this optional path when judging offline; the hosted link and Python evidence are sufficient.

## What each test proves

| Check | Evidence |
|---|---|
| Reproducibility | zero-dependency bootstrap and nineteen offline core/fixture/panel tests |
| Real executable product | twenty-four distinct desktop/mobile GPT Image website UI mockups, twelve supplementary deterministic site packages, SQLite, reports, and the English Sales Ops master-detail workspace |
| Explainability | deterministic compliance reasons and visible score inputs |
| Data discipline | fictional fixture, normalized provider contract, no raw response/review storage |
| Safe iteration | `noindex,nofollow`, preview disclaimer, owner-approval disclaimer |
| Respect for rejection | durable `do_not_contact` suppression |
| Codex integration | `AGENTS.md`, installable five-skill plugin, copy-ready judge tasks |
| Honest AI boundary | GPT Image/Codex authoring outputs are packaged and labelled; no Python API runtime call is implied |
| Market proof | independent customer implementation link, separate from synthetic evidence |

## Do not use for judging

The following are not necessary and may create avoidable external effects:

- `--mode real`
- a Google Places API key
- a live business identifier
- the hourly worker
- outreach commands outside the local status CLI
- Cloudflare credentials
- domain registration or DNS tools
- publishing through Sites or another host

## Known result boundary

The test proves the local lead-to-private-preview foundation and the Codex-ready operating package. It does not prove unattended outreach, autonomous domain purchase, production multi-tenancy, or an OpenAI model call inside the Python application. Those capabilities are intentionally excluded or separately human-controlled.
