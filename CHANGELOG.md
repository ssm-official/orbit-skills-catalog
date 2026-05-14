# Changelog

## v1.0 — 2026-05-14

First public release. 50 vetted x402-compatible skills across Personal and Merchant tracks.

### Phase 0 — Scaffold
- Directory tree, schema, pipeline scripts (Python, cross-platform).
- Workspace at `C:\Users\ssmca\orbit-skills-catalog`; remote at `github.com/ssm-official/orbit-skills-catalog`.

### Phase 1 — Discover
- Verified 82 §5 hand-curated vendor seeds (5 missing → documented in `_logs/source_corrections.md`).
- Added 38 supplemental seeds (renamed Duffel JS SDK, weather/search/STT vendors, AWS/GCP/Azure SDKs).
- Crawled 5 MCP awesome-lists (punkpeye, wong2, appcypher, TensorBlock, tolkonepiu best-of) → 3670 unique repo URLs.
- Final discovery feed: **3727 candidates**, 3540 verified, 55 archived, 187 missing.

### Phase 2 — Triage
- 47 vendor seeds survived per-slot top-2 dedup.
- `augment_shortlist.py` categorised 86 high-star aggregator finds via owner+keyword heuristics → **133-candidate shortlist**.
- Drops: 661 no-license, 187 missing, 56 GPL-3.0, 55 archived, 35 AGPL-3.0, 7 meta/aggregator.

### Phase 3 — Safety vet
- Focused to 52 hand-curated vendor candidates for v1.0 (86 aggregator augments deferred to v1.1).
- Static scanners: native pattern scan + install-hook audit + gitleaks + osv-scanner + pip-audit when applicable.
- `_is_test_path` recognises `/tests/`, `/fixtures/`, `/.github/`, `/docs/`, Go `*_test.go`, `test_*.py`, `*.spec.ts`, reference docs.
- `TRUSTED_VENDOR_ORGS` downgrades gitleaks findings to pass_with_notes for 30+ official vendor orgs (their SDK docstrings and example values are reliably false positives).
- 2 manual ground-truth overrides: HKUDS/Vibe-Trading (HF model id) and mbailey/voicemode (public OAuth client id).
- **Final audit verdicts:** 22 pass · 41 pass_with_notes · **1 quarantine** (skarlekar/mcp_travelassistant ships a real 64-char SerpAPI key in `env_template_visible.sh`).

### Phase 4 — Smoke
- `uv` (Astral) installed for fast `uv pip install --dry-run` + `uv run --with .` Python probes.
- Node: `npm install --omit=dev --ignore-scripts` + `node --check <main>` (no execution).
- Windows TCP-connection-delta network monitoring (Docker unavailable on host; substituted Get-NetTCPConnection snapshots).
- **Final smoke verdicts:** 16 pass · 21 pass_with_notes · 14 deferred · 0 fail.

### Phase 5 — Document
- Per-skill folder: `SKILL.md` + `manifest.json` (schema v1.0) + `audit.json` (sanitised) + `smoke.json` + `examples/`.
- Manifest.json schema requires: pinned commit SHA, license, vendor cost model, x402 compatibility, audit + smoke verdicts, risk fields.
- **50 skills written** (2 skipped for unresolvable slot). 28 personal · 47 merchant · 25 cross-listed.

### Phase 6 — Final delivery
- `_catalog/INDEX.md` — browseable table grouped by track + category.
- `_catalog/RECOMMENDATIONS.md` — top 10 launch picks per track.
- `_catalog/GAPS.md` — slots still without a survivor (with near-misses).
- `_catalog/SUMMARY.md` — operator-facing one-pager.
- `_logs/status_final.md` — totals and methodology notes.

### Operational notes
- **GitHub push-protection sanitisation** (`_scripts/sanitize_audits.py`): redacts any string in audit.json findings that matches `sk_(live|test)_*`, `AKIA*`, `AIza*`, `gh[pous]_*`, `xox[baprs]-*`, JWT shape, BEGIN PRIVATE KEY blocks, 40+ char hex, or 30+ char alnum. Raw scanner output (gitleaks.json, osv.json, etc.) is gitignored entirely.
- Docker unavailable on the build host → §3.4 containerised behavioural check substituted with Windows-native `Get-NetTCPConnection` snapshots before/after invocation. Limitation documented in every audit.
