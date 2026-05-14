# Plaid SDK (Node)

**Track:** personal + merchant
**Category:** finance
**Slot:** `both.finance.plaid-node`
**Source:** [https://github.com/plaid/plaid-node](https://github.com/plaid/plaid-node) (license: `MIT`, pinned commit: `49270ba`)
**Upstream:** Plaid — https://plaid.com

## What it does

Plaid official Node SDK

## What it costs

- Upstream cost model: **paid_per_call**
- Typical per-call cost: **varies by product**
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

- Verdict: **pass**
- Last passed: 2026-05-14T06:07:35.167117+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
