# HubSpot SDK (Python)

**Track:** merchant
**Category:** crm
**Slot:** `merchant.crm.hubspot-py`
**Source:** [https://github.com/HubSpot/hubspot-api-python](https://github.com/HubSpot/hubspot-api-python) (license: `Apache-2.0`, pinned commit: `a2a528a`)
**Upstream:** HubSpot — https://hubspot.com

## What it does

Official HubSpot Python SDK

## What it costs

- Upstream cost model: **freemium**
- Typical per-call cost: **free CRM tier**
- Sandbox available: yes

## What it needs

- Auth: **api_key**
- Requires end-user OAuth (Orbit creator's buyers each authenticate their own account)
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Regulated data: pii
- Default mode: **live**

## Smoke test

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:08:38.028571+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
