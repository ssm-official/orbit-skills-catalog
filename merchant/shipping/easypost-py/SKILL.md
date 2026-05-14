# EasyPost SDK (Python)

**Track:** personal + merchant
**Category:** shipping
**Slot:** `both.shipping.easypost-py`
**Source:** [https://github.com/easypost/easypost-python](https://github.com/easypost/easypost-python) (license: `MIT`, pinned commit: `655796d`)
**Upstream:** Easypost — 

## What it does

EasyPost Python SDK

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

- Verdict: **pass**
- Last passed: 2026-05-14T06:07:29.149609+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
