# Mapbox SDK (Node)

**Track:** personal + merchant
**Category:** maps
**Slot:** `both.maps.mapbox`
**Source:** [https://github.com/mapbox/mapbox-sdk-js](https://github.com/mapbox/mapbox-sdk-js) (license: `NOASSERTION`, pinned commit: `314e747`)
**Upstream:** Mapbox — https://mapbox.com

## What it does

Official Mapbox JS SDK

## What it costs

- Upstream cost model: **freemium**
- Typical per-call cost: **free tier 100k/mo**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **pass**
- Last passed: 2026-05-14T06:07:20.715590+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
