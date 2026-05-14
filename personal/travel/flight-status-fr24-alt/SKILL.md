# Flightradar24 Mcp Server

**Track:** personal
**Category:** travel
**Slot:** `personal.travel.flight-status-fr24-alt`
**Source:** [https://github.com/sunsetcoder/flightradar24-mcp-server](https://github.com/sunsetcoder/flightradar24-mcp-server) (license: `MIT`, pinned commit: `97d3e99`)
**Upstream:** Sunsetcoder — 

## What it does

FlightRadar24 MCP alt — check ToS

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
- Last passed: 2026-05-14T06:07:13.288956+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
