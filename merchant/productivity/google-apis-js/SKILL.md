# Google APIs Client (Node)

**Track:** personal + merchant
**Category:** productivity
**Slot:** `both.productivity.google-apis-js`
**Source:** [https://github.com/googleapis/google-api-nodejs-client](https://github.com/googleapis/google-api-nodejs-client) (license: `Apache-2.0`, pinned commit: `b385d3f`)
**Upstream:** Google — https://cloud.google.com

## What it does

Official Google APIs Node client

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

- Verdict: **deferred**
- Last passed: 2026-05-14T06:07:39.008488+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
