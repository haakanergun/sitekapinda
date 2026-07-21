# Discovery policy

## Synthetic mode

`--mode mock` reads only `data/mock_places.json`, writes local artifacts under `runtime/`, and makes no discovery network request. It is the required mode for an uncomplicated judge run.

## Real mode

`--mode real` uses the official Google Places Text Search API and requires `SITEKAPINDA_GOOGLE_PLACES_API_KEY` in the process environment. It can incur provider cost and writes discovered public business fields to the configured local SQLite database.

The provider requests a bounded field mask containing the stable place ID, business name/type, address, coordinates, public phone, website URL, aggregate rating, rating count, and business status. Review bodies are excluded. The runtime does not retain a raw provider response.

Before a real run, confirm all of the following:

1. The user explicitly requested real discovery now.
2. The locations, categories, `--max-per-run`, and `--min-score` are visible to the user.
3. The official API key is already configured in the environment and will not be printed.
4. The user understands public business contact fields will be stored locally.
5. The intended use complies with provider terms and applicable law.

## Screening behavior

The pipeline deduplicates by stable place ID, skips previously processed or suppressed records, rejects categories outside the initial target set, rejects regulated or sensitive keywords, classifies website presence, and applies a suitability threshold. These are qualification signals, not proof that outreach is appropriate.

## Scheduling

`python -m sitekapinda worker --mode mock --interval-seconds 3600` is a foreground loop, not a Codex automation and not a production service. Do not start it during a judge walkthrough. Create a recurring Codex task only after the user approves its source, frequency, output location, and review process. Keep outreach and publishing outside that task.
