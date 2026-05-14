# Duffel Flights MCP

**Track:** personal
**Category:** travel
**Slot:** `personal.travel.flights-duffel`
**Source:** [https://github.com/ravinahp/flights-mcp](https://github.com/ravinahp/flights-mcp) (license: `MIT`, pinned commit: `749d7ad`)
**Upstream:** Ravinahp — 

## What it does

Duffel flight search MCP

## What it costs

- Upstream cost model: **varies**
- Typical per-call cost: **varies**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Spend-capable: yes
- Default mode: **live**

## Smoke test

- Verdict: **pass_with_notes**
- Last passed: 2026-05-14T06:07:54.114298+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **False**
- Notes: spend-capable in live mode — needs sandbox-gated invocation in Orbit
