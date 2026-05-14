# CCXT — unified crypto exchange API

**Track:** personal
**Category:** finance
**Slot:** `personal.finance.crypto-ccxt`
**Source:** [https://github.com/ccxt/ccxt](https://github.com/ccxt/ccxt) (license: `MIT`, pinned commit: `77fb795`)
**Upstream:** CCXT (multi-exchange) — https://github.com/ccxt/ccxt

## What it does

Unified crypto exchange API

## What it costs

- Upstream cost model: **free**
- Typical per-call cost: **free (self-host)**

## What it needs

- Auth: **api_key**
- Requires end-user OAuth (Orbit creator's buyers each authenticate their own account)
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Regulated data: pii
- Default mode: **live**

## Smoke test

- Verdict: **deferred**
- Last passed: 2026-05-14T06:07:27.532569+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
