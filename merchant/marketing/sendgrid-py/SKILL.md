# Twilio SendGrid (Python)

**Track:** merchant
**Category:** marketing
**Slot:** `merchant.marketing.sendgrid-py`
**Source:** [https://github.com/sendgrid/sendgrid-python](https://github.com/sendgrid/sendgrid-python) (license: `MIT`, pinned commit: `76788e7`)
**Upstream:** Twilio SendGrid — https://sendgrid.com

## What it does

Twilio SendGrid Python SDK

## What it costs

- Upstream cost model: **freemium**
- Typical per-call cost: **free tier 100/day, then ~0.001/email**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **yes**
- Default mode: **dry_run**

## Smoke test

- Verdict: **pass**
- Last passed: 2026-05-14T06:09:10.959629+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
