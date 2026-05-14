# Resend SDK (Node)

**Track:** personal + merchant
**Category:** marketing
**Slot:** `both.marketing.resend-node`
**Source:** [https://github.com/resend/resend-node](https://github.com/resend/resend-node) (license: `MIT`, pinned commit: `6cf8c66`)
**Upstream:** Resend — https://resend.com

## What it does

Resend Node SDK

## What it costs

- Upstream cost model: **freemium**
- Typical per-call cost: **free tier 100/day**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **yes**
- Default mode: **dry_run**

## Smoke test

- Verdict: **deferred**
- Last passed: 2026-05-14T06:09:32.805206+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
