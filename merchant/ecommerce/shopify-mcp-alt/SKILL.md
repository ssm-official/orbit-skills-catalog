# Shopify MCP Server (alt)

**Track:** merchant
**Category:** ecommerce
**Slot:** `merchant.ecommerce.shopify-mcp-alt`
**Source:** [https://github.com/amir-bengherbi/shopify-mcp-server](https://github.com/amir-bengherbi/shopify-mcp-server) (license: `MIT`, pinned commit: `ef60720`)
**Upstream:** Amir-bengherbi — 

## What it does

Alt community Shopify MCP

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
- Last passed: 2026-05-14T06:10:20.335901+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
