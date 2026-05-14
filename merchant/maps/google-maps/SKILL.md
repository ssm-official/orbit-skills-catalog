# Google Maps Services (Node)

**Track:** personal + merchant
**Category:** maps
**Slot:** `both.maps.google-maps`
**Source:** [https://github.com/googlemaps/google-maps-services-js](https://github.com/googlemaps/google-maps-services-js) (license: `Apache-2.0`, pinned commit: `9ef8a41`)
**Upstream:** Google — https://cloud.google.com

## What it does

Official Google Maps JS client

## What it costs

- Upstream cost model: **paid_per_call**
- Typical per-call cost: **varies**
- Sandbox available: yes

## What it needs

- Auth: **api_key**
- Requires end-user OAuth (Orbit creator's buyers each authenticate their own account)
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:07:13.289548+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
