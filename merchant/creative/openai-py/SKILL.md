# OpenAI SDK (Python)

**Track:** personal + merchant
**Category:** creative
**Slot:** `both.creative.openai-py`
**Source:** [https://github.com/openai/openai-python](https://github.com/openai/openai-python) (license: `Apache-2.0`, pinned commit: `38d75d7`)
**Upstream:** OpenAI — https://openai.com

## What it does

OpenAI Python SDK

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

- Verdict: **pass**
- Last passed: 2026-05-14T06:08:05.440753+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
