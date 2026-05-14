# Google APIs Client (Python)

**Track:** personal + merchant
**Category:** productivity
**Slot:** `both.productivity.google-apis-py`
**Source:** [https://github.com/googleapis/google-api-python-client](https://github.com/googleapis/google-api-python-client) (license: `Apache-2.0`, pinned commit: `91ccdbe`)
**Upstream:** Google — https://cloud.google.com

## What it does

Official Google APIs Python client

## What it costs

- Upstream cost model: **paid_per_call**
- Typical per-call cost: **varies**
- Sandbox available: yes

## What it needs

- Auth: **api_key**
- Requires end-user OAuth (Orbit creator's buyers each authenticate their own account)
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:07:41.324237+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
