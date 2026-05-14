# Octokit (GitHub) for Node

**Track:** merchant
**Category:** devops
**Slot:** `merchant.devops.octokit-js`
**Source:** [https://github.com/octokit/octokit.js](https://github.com/octokit/octokit.js) (license: `MIT`, pinned commit: `fd76973`)
**Upstream:** GitHub — https://github.com

## What it does

Octokit (GitHub) JS

## What it costs

- Upstream cost model: **freemium**
- Typical per-call cost: **rate-limited free tier**

## What it needs

- Auth: **oauth**
- Requires end-user OAuth (Orbit creator's buyers each authenticate their own account)
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:10:02.887115+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
