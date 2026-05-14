# Zendesk SDK (Ruby)

**Track:** merchant
**Category:** support
**Slot:** `merchant.support.zendesk-rb`
**Source:** [https://github.com/zendesk/zendesk_api_client_rb](https://github.com/zendesk/zendesk_api_client_rb) (license: `Apache-2.0`, pinned commit: `7f573a8`)
**Upstream:** Zendesk — 

## What it does

Zendesk Ruby SDK — note Ruby

## What it costs

- Upstream cost model: **varies**
- Typical per-call cost: **varies**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **high**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **deferred**
- Last passed: 2026-05-14T06:09:46.329429+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
