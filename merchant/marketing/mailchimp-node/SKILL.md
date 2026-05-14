# Mailchimp Marketing (Node)

**Track:** merchant
**Category:** marketing
**Slot:** `merchant.marketing.mailchimp-node`
**Source:** [https://github.com/mailchimp/mailchimp-marketing-node](https://github.com/mailchimp/mailchimp-marketing-node) (license: `NOASSERTION`, pinned commit: `7c1edd2`)
**Upstream:** Mailchimp — https://mailchimp.com

## What it does

Mailchimp Node SDK

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

- Verdict: **pass**
- Last passed: 2026-05-14T06:09:14.332564+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
