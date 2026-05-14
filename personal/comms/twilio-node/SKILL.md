# Twilio SDK (Node)

**Track:** personal + merchant
**Category:** comms
**Slot:** `both.comms.twilio-node`
**Source:** [https://github.com/twilio/twilio-node](https://github.com/twilio/twilio-node) (license: `MIT`, pinned commit: `e9e5469`)
**Upstream:** Twilio — https://twilio.com

## What it does

Twilio Node SDK

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

- Verdict: **deferred**
- Last passed: 2026-05-14T06:09:46.330668+00:00
- Full log: `smoke.json`

## Audit

- Verdict: **pass_with_notes**
- Scanners: orbit_pattern_scan, install_hook_audit, gitleaks, osv-scanner
- Full log: `audit.json`

## x402 compatibility

- Compatible: **True**
- Notes: per-call, deterministic JSON response
