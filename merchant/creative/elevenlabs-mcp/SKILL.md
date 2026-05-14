# ElevenLabs MCP

**Track:** personal + merchant
**Category:** creative
**Slot:** `both.creative.elevenlabs-mcp`
**Source:** [https://github.com/elevenlabs/elevenlabs-mcp](https://github.com/elevenlabs/elevenlabs-mcp) (license: `MIT`, pinned commit: `998b611`)
**Upstream:** ElevenLabs — https://elevenlabs.io

## What it does

The official ElevenLabs MCP server

## What it costs

- Upstream cost model: **freemium**
- Typical per-call cost: **~0.0001/char**
- Sandbox available: yes

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **pass**
- Last passed: 2026-05-14T06:10:29.110761+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
