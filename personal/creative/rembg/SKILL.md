# rembg — background removal

**Track:** personal + merchant
**Category:** creative
**Slot:** `both.creative.rembg`
**Source:** [https://github.com/danielgatis/rembg](https://github.com/danielgatis/rembg) (license: `MIT`, pinned commit: `7b8de60`)
**Upstream:** Danielgatis — 

## What it does

Background removal (self-host)

## What it costs

- Upstream cost model: **varies**
- Typical per-call cost: **varies**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:08:59.734043+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
