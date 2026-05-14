# _scripts — pipeline utilities

All scripts are Python (cross-platform). They share state via JSONL files
in `_candidates_raw/` and `_catalog/`, and cache external lookups in `_cache/`
so reruns are cheap.

## Order of operations

```
# Phase 1 — discover
python _scripts/cli_verify.py                   # verify seeds.py against GitHub
python _scripts/cli_crawl_aggregators.py        # extract repos from MCP awesome-lists
python _scripts/cli_verify.py --extra _candidates_raw/discovered_from_aggregators.jsonl

# Phase 2 — triage
python _scripts/cli_triage.py

# Phase 3 — safety vet
python _scripts/cli_scan.py
# (with limit/filter while iterating: --limit 5 --filter stripe)

# Phase 4 — smoke test
python _scripts/cli_smoke.py                    # per-skill smoke test

# Phase 5 — document
python _scripts/cli_document.py
```

## Files

- `orbit_pipeline.py` — shared library (no CLI). Logging, caching, GitHub
  metadata, secret/URL pattern scans, triage gates, helpers.
- `seeds.py` — the §5 starter list from the master prompt. Verified before use.
- `cli_verify.py` — verify a list of GitHub URLs via the API.
- `cli_crawl_aggregators.py` — pull MCP awesome-list READMEs and extract repo
  URLs as new candidates.
- `cli_triage.py` — license/maintenance/scope gates → shortlist.jsonl.
- `cli_scan.py` — clone shallow + static scans + verdict. Writes per-repo
  `_logs/scan/<owner>__<repo>/audit.json`.
- `cli_smoke.py` — (Phase 4) per-skill functional smoke test.
- `cli_document.py` — (Phase 5) generate per-skill folders from audits + smokes.

## Environment

The scripts use:

- Built-in: `urllib`, `subprocess`, `concurrent.futures`, `pathlib`
- External CLI: `git`, `gh` (for token), and optionally `gitleaks`, `trufflehog`,
  `osv-scanner`, `semgrep`. Each external scanner is invoked **only if it's on
  PATH**; missing scanners are noted in the audit but don't fail the pipeline.

No third-party Python packages are required.

## Conventions

- All paths are `Path` from `pathlib`, normalised with forward slashes when
  serialised to JSON.
- Atomic writes: every JSONL output goes through `write_jsonl_atomic` (`.tmp`
  → rename) so a partial run doesn't corrupt a working file.
- Every external operation `log()`s to `_logs/run/run.log`.
