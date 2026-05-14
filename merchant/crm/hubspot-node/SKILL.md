# HubSpot SDK (Node)

**Track:** merchant
**Category:** crm
**Slot:** `merchant.crm.hubspot-node`
**Source:** [https://github.com/HubSpot/hubspot-api-nodejs](https://github.com/HubSpot/hubspot-api-nodejs) (license: `Apache-2.0`, pinned commit: `77ae0dd`)
**Upstream:** HubSpot — https://hubspot.com

## What it does

Official HubSpot Node SDK

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
- Last passed: 2026-05-14T06:08:43.325365+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
