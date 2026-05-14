# PyGithub (GitHub) for Python

**Track:** merchant
**Category:** devops
**Slot:** `merchant.devops.pygithub`
**Source:** [https://github.com/PyGithub/PyGithub](https://github.com/PyGithub/PyGithub) (license: `LGPL-3.0`, pinned commit: `7806e7d`)
**Upstream:** GitHub (PyGithub) — https://github.com

## What it does

PyGithub

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
- Last passed: 2026-05-14T06:10:07.176753+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
