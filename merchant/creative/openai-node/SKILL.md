# OpenAI SDK (Node)

**Track:** personal + merchant
**Category:** creative
**Slot:** `both.creative.openai-node`
**Source:** [https://github.com/openai/openai-node](https://github.com/openai/openai-node) (license: `Apache-2.0`, pinned commit: `b0e89cd`)
**Upstream:** OpenAI — https://openai.com

## What it does

OpenAI Node SDK

## What it costs

- Upstream cost model: **paid_per_call**
- Typical per-call cost: **varies by model**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **deferred**
- Last passed: 2026-05-14T06:08:28.549528+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
