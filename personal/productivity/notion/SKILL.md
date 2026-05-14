# Notion SDK (Node)

**Track:** personal + merchant
**Category:** productivity
**Slot:** `both.productivity.notion`
**Source:** [https://github.com/makenotion/notion-sdk-js](https://github.com/makenotion/notion-sdk-js) (license: `MIT`, pinned commit: `ece663b`)
**Upstream:** Makenotion — 

## What it does

Official Notion JS SDK

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

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:07:52.260428+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
