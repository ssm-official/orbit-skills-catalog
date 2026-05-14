# Stripe SDK (Python)

**Track:** merchant
**Category:** finance
**Slot:** `merchant.finance.stripe-py`
**Source:** [https://github.com/stripe/stripe-python](https://github.com/stripe/stripe-python) (license: `MIT`, pinned commit: `41a2ece`)
**Upstream:** Stripe — https://stripe.com

## What it does

Official Stripe Python SDK

## What it costs

- Upstream cost model: **paid_per_call**
- Typical per-call cost: **0.005–0.029 per txn**
- Sandbox available: yes

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

- Verdict: **pass**
- Last passed: 2026-05-14T06:09:54.482428+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **False**
- Notes: spend-capable in live mode — needs sandbox-gated invocation in Orbit
