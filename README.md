# Orbit Skills Catalog

Vetted, x402-compatible agent skills for [Orbit](https://orbit.xona-agent.com), Xona's agent marketplace.

## What this is

A curated catalog of single-callable agent capabilities — MCP servers, official SDK wrappers, and small tool folders — that an Orbit agent owner can attach to their agent. Every skill in this catalog has:

- A pinned upstream commit and a verified license
- A static safety scan (secrets, vulns, network endpoints, install-hook audit)
- A behavioral check (one real invocation, network trace recorded)
- A functional smoke test against a sandbox / read-only endpoint
- A documented credential surface and cost model

Skills that fail any step are quarantined or rejected. The catalog never contains an un-vetted entry.

## Layout

```
orbit-skills-catalog/
├── personal/              # skills aimed at individuals (track: personal)
│   └── <service>/
├── merchant/              # skills aimed at businesses/teams (track: merchant)
│   └── <service>/
├── _quarantine/           # rejected skills + memos (audit trail)
├── _candidates_raw/       # pre-triage discovery dumps
├── _logs/                 # scans, smoke tests, command traces
├── _scripts/              # Python pipeline scripts
└── _catalog/
    ├── personal.jsonl     # flat row per accepted personal skill
    ├── merchant.jsonl     # flat row per accepted merchant skill
    ├── INDEX.md           # human-browsable index
    ├── GAPS.md            # documented holes for future runs
    └── schema.json        # manifest schema
```

A skill cross-listed to both tracks has one canonical folder under whichever track is more natural and is appended to both jsonl files.

## Per-skill folder

```
<track>/<service>/
├── SKILL.md          # human-readable
├── manifest.json     # machine-readable (see _catalog/schema.json)
├── audit.json        # safety findings
├── smoke.json        # functional test result
└── examples/
    ├── input.json
    └── output.json
```

## Pipeline

Six phases — see `_scripts/` and `_logs/status_phase_*.md` for progress.

1. **Setup** — scaffold + scripts (Phase 0).
2. **Discover** — crawl MCP aggregators and vendor seed list, capture metadata.
3. **Triage** — license / maintenance / scope gates; dedupe per slot.
4. **Safety vet** — scanners + behavioral check; classify PASS / PASS_WITH_NOTES / QUARANTINE / REJECT.
5. **Smoke test** — one read-only call per survivor.
6. **Document & catalog** — generate per-skill folders; update INDEX / GAPS.

## Environment

Built on Windows 11 (PowerShell). All scripts in `_scripts/` are Python and platform-neutral. Scanners used:

- `gitleaks` (secrets)
- `trufflehog` (secrets, deeper)
- `osv-scanner` (vulnerable deps, all ecosystems)
- `semgrep` (SAST)
- `pip-audit` / `npm audit` (language-specific)

Docker is **not** available on the build host. The §3.4 "containerized behavioral check" from the master prompt is substituted with a fresh-Python-venv / fresh-npx-prefix sandbox plus Windows-native process + outbound-TCP monitoring (`Get-NetTCPConnection` snapshots before / during / after the invocation). This is weaker than network namespace isolation and is documented as such in every `audit.json`.

## How to read this catalog (operator)

- `_catalog/INDEX.md` — start here for a browse.
- `_catalog/personal.jsonl` / `merchant.jsonl` — machine ingestion source of truth.
- For any single skill, `manifest.json` is canonical metadata; `SKILL.md` is the prose description.

## How to extend

To propose a new skill: drop a row into `_candidates_raw/manual_proposals.jsonl` (one JSON object per line, fields `source_url`, `proposed_slot`, `notes`) and run `_scripts/run_pipeline.py --candidates _candidates_raw/manual_proposals.jsonl`.

## License

Catalog metadata (everything *outside* `personal/*/source/` and `merchant/*/source/`) is MIT, see `LICENSE`. Each individual skill's source is governed by its upstream repository's license, recorded in `manifest.json`.

## Status

See `_logs/status_phase_*.md` for phase-by-phase progress, and `_logs/status_final.md` once `v1.0` is tagged.
