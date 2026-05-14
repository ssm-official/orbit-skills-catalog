# Stripe SDK (Node)

**Track:** merchant
**Category:** finance
**Slot:** `merchant.finance.stripe-node`
**Source:** [https://github.com/stripe/stripe-node](https://github.com/stripe/stripe-node) (license: `MIT`, pinned commit: `185f336`)
**Upstream:** Stripe — https://stripe.com

## What it does

Official Stripe Node SDK

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

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:10:09.404384+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **False**
- Notes: spend-capable in live mode — needs sandbox-gated invocation in Orbit
