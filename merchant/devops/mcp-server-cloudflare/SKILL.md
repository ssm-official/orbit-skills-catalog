# Cloudflare MCP Server

**Track:** merchant
**Category:** devops
**Slot:** `merchant.devops.mcp-server-cloudflare`
**Source:** [https://github.com/cloudflare/mcp-server-cloudflare](https://github.com/cloudflare/mcp-server-cloudflare) (license: `Apache-2.0`, pinned commit: `10a4755`)
**Upstream:** Cloudflare — https://cloudflare.com

## What it does

mcp-server-cloudflare — see vendor URL for capability details.

## What it costs

- Upstream cost model: **freemium**
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
- Last passed: 2026-05-14T06:10:41.103499+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
