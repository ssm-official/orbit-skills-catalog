# Twilio SDK (Python)

**Track:** personal + merchant
**Category:** comms
**Slot:** `both.comms.twilio-py`
**Source:** [https://github.com/twilio/twilio-python](https://github.com/twilio/twilio-python) (license: `MIT`, pinned commit: `82adf8f`)
**Upstream:** Twilio — https://twilio.com

## What it does

Twilio Python SDK

## What it costs

- Upstream cost model: **paid_per_call**
- Typical per-call cost: **~0.0075/SMS, ~0.013/min**
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
- Last passed: 2026-05-14T06:09:46.572804+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner, pip-audit
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
