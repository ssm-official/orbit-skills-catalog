# Salesforce SDK (jsforce)

**Track:** merchant
**Category:** crm
**Slot:** `merchant.crm.salesforce-jsforce`
**Source:** [https://github.com/jsforce/jsforce](https://github.com/jsforce/jsforce) (license: `MIT`, pinned commit: `8ab4831`)
**Upstream:** Jsforce — 

## What it does

Salesforce community SDK

## What it costs

- Upstream cost model: **varies**
- Typical per-call cost: **varies**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Regulated data: pii
- Default mode: **live**

## Smoke test

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:08:57.496731+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
