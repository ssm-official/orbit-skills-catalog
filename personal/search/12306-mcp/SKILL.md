# China Rail (12306) MCP

**Track:** personal + merchant
**Category:** search
**Slot:** `both.search.12306-mcp`
**Source:** [https://github.com/Joooook/12306-mcp](https://github.com/Joooook/12306-mcp) (license: `MIT`, pinned commit: `2c8e01c`)
**Upstream:** Joooook — 

## What it does

This is a 12306 ticket search server based on the Model Context Protocol (MCP).

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

- Verdict: **pass**
- Last passed: 2026-05-14T06:10:24.284899+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
