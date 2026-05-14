# Google Maps Services (Python)

**Track:** personal + merchant
**Category:** maps
**Slot:** `both.maps.google-maps-py`
**Source:** [https://github.com/googlemaps/google-maps-services-python](https://github.com/googlemaps/google-maps-services-python) (license: `Apache-2.0`, pinned commit: `9ec69cb`)
**Upstream:** Google — https://cloud.google.com

## What it does

Official Google Maps Python client

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

- Verdict: **pass**
- Last passed: 2026-05-14T06:07:20.706151+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
