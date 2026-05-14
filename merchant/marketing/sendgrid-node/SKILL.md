# Twilio SendGrid (Node)

**Track:** merchant
**Category:** marketing
**Slot:** `merchant.marketing.sendgrid-node`
**Source:** [https://github.com/sendgrid/sendgrid-nodejs](https://github.com/sendgrid/sendgrid-nodejs) (license: `MIT`, pinned commit: `498e232`)
**Upstream:** Twilio SendGrid — https://sendgrid.com

## What it does

Twilio SendGrid Node SDK

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

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:09:26.743569+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
