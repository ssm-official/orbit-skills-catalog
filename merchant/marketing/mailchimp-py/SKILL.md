# Mailchimp Marketing (Python)

**Track:** merchant
**Category:** marketing
**Slot:** `merchant.marketing.mailchimp-py`
**Source:** [https://github.com/mailchimp/mailchimp-marketing-python](https://github.com/mailchimp/mailchimp-marketing-python) (license: `NOASSERTION`, pinned commit: `3305fa4`)
**Upstream:** Mailchimp — https://mailchimp.com

## What it does

Mailchimp Python SDK

## What it costs

- Upstream cost model: **freemium**
- Typical per-call cost: **free tier 500 contacts**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:08:59.868126+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
