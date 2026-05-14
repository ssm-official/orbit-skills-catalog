# Hugging Face Hub

**Track:** personal + merchant
**Category:** creative
**Slot:** `both.creative.huggingface`
**Source:** [https://github.com/huggingface/huggingface_hub](https://github.com/huggingface/huggingface_hub) (license: `Apache-2.0`, pinned commit: `9c05199`)
**Upstream:** Hugging Face — https://huggingface.co

## What it does

Hugging Face hub client

## What it costs

- Upstream cost model: **freemium**
- Typical per-call cost: **free tier + paid pro**

## What it needs

- Auth: **api_key**
- Obtain credentials: see vendor URL above

## Safety notes

- Prompt-injection risk: **low**
- Destructive actions: **no**
- Default mode: **live**

## Smoke test

- Verdict: **pass**
- Last passed: 2026-05-14T06:08:04.164524+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
