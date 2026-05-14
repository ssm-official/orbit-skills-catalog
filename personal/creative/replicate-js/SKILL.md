# Replicate SDK (Node)

**Track:** personal + merchant
**Category:** creative
**Slot:** `both.creative.replicate-js`
**Source:** [https://github.com/replicate/replicate-javascript](https://github.com/replicate/replicate-javascript) (license: `Apache-2.0`, pinned commit: `2fd6f39`)
**Upstream:** Replicate — https://replicate.com

## What it does

Replicate JS SDK

## What it costs

- Upstream cost model: **paid_per_call**
- Typical per-call cost: **varies by model**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **pass**
- Last passed: 2026-05-14T06:07:58.670222+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
