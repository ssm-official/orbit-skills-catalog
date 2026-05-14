# Anthropic SDK (TypeScript)

**Track:** personal + merchant
**Category:** creative
**Slot:** `both.creative.anthropic-ts`
**Source:** [https://github.com/anthropics/anthropic-sdk-typescript](https://github.com/anthropics/anthropic-sdk-typescript) (license: `MIT`, pinned commit: `a53f60d`)
**Upstream:** Anthropic — https://anthropic.com

## What it does

Anthropic TS SDK

## What it costs

- Upstream cost model: **paid_per_call**
- Typical per-call cost: **varies by model**

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
- Last passed: 2026-05-14T06:08:45.593324+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
