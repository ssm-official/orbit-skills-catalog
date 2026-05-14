# Square SDK (Python)

**Track:** merchant
**Category:** finance
**Slot:** `merchant.finance.square-py`
**Source:** [https://github.com/square/square-python-sdk](https://github.com/square/square-python-sdk) (license: `MIT`, pinned commit: `813313d`)
**Upstream:** Square — 

## What it does

Square Python SDK

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

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:10:11.464082+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **False**
- Notes: spend-capable in live mode — needs sandbox-gated invocation in Orbit
