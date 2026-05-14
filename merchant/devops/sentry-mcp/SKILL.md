# Sentry MCP Server

**Track:** merchant
**Category:** devops
**Slot:** `merchant.devops.sentry-mcp`
**Source:** [https://github.com/getsentry/sentry-mcp](https://github.com/getsentry/sentry-mcp) (license: `NOASSERTION`, pinned commit: `42f1442`)
**Upstream:** Sentry — https://sentry.io

## What it does

An MCP server for interacting with Sentry via LLMs.

## What it costs

- Upstream cost model: **freemium**
- Typical per-call cost: **free tier**
- Sandbox available: yes

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **deferred**
- Last passed: 2026-05-14T06:10:27.519254+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
