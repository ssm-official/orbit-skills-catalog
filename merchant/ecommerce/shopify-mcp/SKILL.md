# Shopify MCP Server

**Track:** merchant
**Category:** ecommerce
**Slot:** `merchant.ecommerce.shopify-mcp`
**Source:** [https://github.com/GeLi2001/shopify-mcp](https://github.com/GeLi2001/shopify-mcp) (license: `MIT`, pinned commit: `c90faaf`)
**Upstream:** Geli2001 — 

## What it does

Community Shopify MCP — vet carefully

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
- Last passed: 2026-05-14T06:09:59.005521+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
