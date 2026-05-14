# EasyPost SDK (Node)

**Track:** personal + merchant
**Category:** shipping
**Slot:** `both.shipping.easypost`
**Source:** [https://github.com/easypost/easypost-node](https://github.com/easypost/easypost-node) (license: `MIT`, pinned commit: `ac2a732`)
**Upstream:** Easypost — 

## What it does

EasyPost Node SDK

## What it costs

- Upstream cost model: **varies**
- Typical per-call cost: **varies**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **yes**
- Spend-capable: yes
- Default mode: **dry_run**

## Smoke test

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:07:21.059027+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
