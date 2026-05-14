# Browserbase MCP Server

**Track:** merchant
**Category:** devops
**Slot:** `merchant.devops.mcp-server-browserbase`
**Source:** [https://github.com/browserbase/mcp-server-browserbase](https://github.com/browserbase/mcp-server-browserbase) (license: `Apache-2.0`, pinned commit: `1e196b3`)
**Upstream:** Browserbase — 

## What it does

Allow LLMs to control a browser with Browserbase and Stagehand

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
- Last passed: 2026-05-14T06:10:31.654089+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
