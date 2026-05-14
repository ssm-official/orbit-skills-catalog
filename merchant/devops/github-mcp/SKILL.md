# GitHub MCP Server

**Track:** merchant
**Category:** devops
**Slot:** `merchant.devops.github-mcp`
**Source:** [https://github.com/github/github-mcp-server](https://github.com/github/github-mcp-server) (license: `MIT`, pinned commit: `3a4bc26`)
**Upstream:** Github — 

## What it does

Official GitHub MCP

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

- Verdict: **deferred**
- Last passed: 2026-05-14T06:07:58.668036+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
