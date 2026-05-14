# Orbit Skills Catalog — Summary

_Generated: 2026-05-14 06:13 UTC_

## Headline

- Personal skills: **28**
- Merchant skills: **47**
- Cross-listed (both tracks): **25**
- Quarantined: **1**
- Total candidates considered: **3727**

## By category (filled / shortlisted)

| Track.Category | Filled | Shortlisted |
|----------------|--------|-------------|
| `_uncategorized.from_aggregator` | 0 | 1 |
| `both.comms` | 0 | 2 |
| `both.creative` | 0 | 9 |
| `both.finance` | 0 | 2 |
| `both.maps` | 0 | 3 |
| `both.marketing` | 0 | 2 |
| `both.productivity` | 0 | 4 |
| `both.search` | 0 | 1 |
| `both.shipping` | 0 | 2 |
| `merchant.comms` | 4 | 0 |
| `merchant.creative` | 18 | 0 |
| `merchant.crm` | 4 | 4 |
| `merchant.devops` | 6 | 6 |
| `merchant.ecommerce` | 2 | 2 |
| `merchant.finance` | 9 | 5 |
| `merchant.maps` | 6 | 0 |
| `merchant.marketing` | 8 | 4 |
| `merchant.productivity` | 8 | 0 |
| `merchant.search` | 2 | 0 |
| `merchant.shipping` | 4 | 0 |
| `merchant.support` | 1 | 1 |
| `personal.comms` | 4 | 0 |
| `personal.creative` | 18 | 0 |
| `personal.finance` | 5 | 1 |
| `personal.maps` | 6 | 0 |
| `personal.marketing` | 4 | 0 |
| `personal.productivity` | 8 | 0 |
| `personal.search` | 2 | 0 |
| `personal.shipping` | 4 | 0 |
| `personal.travel` | 2 | 3 |

## Quarantined repos

- https://github.com/skarlekar/mcp_travelassistant: gitleaks: 1 non-test secret(s)

## Methodology

- Discovery: §5 hand-curated seeds (82) + supplemental (38) + 5 MCP awesome-lists (3670 unique)
- Triage: license gate, maintenance gate (>18mo + <100★), per-slot top-2 dedup
- Augment: high-star (≥200★, ≤12mo) aggregator finds re-categorised via owner+keyword heuristics
- Audit: native pattern scan (secrets, suspicious code, URL inventory) + install-hook audit + gitleaks + osv-scanner + pip-audit when applicable
- Smoke: fresh venv / fresh node_modules; import / require probe; Windows TCP-connection delta during invocation (Docker unavailable on build host)
- Documentation: per-skill folder with SKILL.md + manifest.json (schema v1.0) + audit.json + smoke.json + examples/