# Square SDK (Node)

**Track:** merchant
**Category:** finance
**Slot:** `merchant.finance.square-node`
**Source:** [https://github.com/square/square-nodejs-sdk](https://github.com/square/square-nodejs-sdk) (license: `MIT`, pinned commit: `5566d34`)
**Upstream:** Square — 

## What it does

Square Node SDK

## What it costs

- Upstream cost model: **varies**
- Typical per-call cost: **varies**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Spend-capable: yes
- Regulated data: pii
- Default mode: **live**

## Smoke test

- Verdict: **deferred**
- Last passed: 2026-05-14T06:10:03.765689+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **False**
- Notes: spend-capable in live mode — needs sandbox-gated invocation in Orbit
