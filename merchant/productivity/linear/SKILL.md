# Linear SDK

**Track:** personal + merchant
**Category:** productivity
**Slot:** `both.productivity.linear`
**Source:** [https://github.com/linear/linear](https://github.com/linear/linear) (license: `MIT`, pinned commit: `bfb8a93`)
**Upstream:** Linear — 

## What it does

Linear SDK monorepo

## What it costs

- Upstream cost model: **varies**
- Typical per-call cost: **varies**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **deferred**
- Last passed: 2026-05-14T06:07:52.310514+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
