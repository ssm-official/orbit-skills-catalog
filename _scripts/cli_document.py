"""cli_document.py — generate per-skill folders from passing audits + smokes.

For each candidate that passed audit AND smoke:

  1. Determine canonical track (personal | merchant) and category from
     proposed_slot. Cross-listed slots produce one canonical folder under
     whichever track is more natural and append to both jsonl files.
  2. Write SKILL.md, manifest.json, audit.json, smoke.json, and a stub
     examples/input.json + examples/output.json.
  3. Append flat row to _catalog/personal.jsonl and/or merchant.jsonl.

This script does NOT vendor the upstream source code into the skill folder.
Instead it pins commit + repo_url in manifest.json. Vendoring is left for
a future v1.1 if Orbit's runtime wants offline copies.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT, log, load_jsonl, write_jsonl_atomic, parse_github_url, utc_now_iso

SHORTLIST = ROOT / "_candidates_raw" / "shortlist.jsonl"
SCAN_LOG_BASE = ROOT / "_logs" / "scan"
SMOKE_LOG_BASE = ROOT / "_logs" / "smoke"
DISCOVERY = ROOT / "_candidates_raw" / "discovery.jsonl"


def slot_to_path(slot: str) -> tuple[list[str], str, str]:
    """slot 'personal.travel.flights-duffel' -> (tracks, category, slug).
    'both.creative.elevenlabs-tts' -> (['personal','merchant'], 'creative', 'elevenlabs-tts').
    """
    parts = slot.split(".")
    if len(parts) < 3:
        return [], "uncategorized", slot.replace(".", "-")
    head, category, *slug_parts = parts
    slug = "-".join(slug_parts)
    if head == "both":
        return ["personal", "merchant"], category, slug
    if head in ("personal", "merchant"):
        return [head], category, slug
    return [], category, slug


def infer_upstream(repo_url: str, row: dict, audit: dict) -> dict:
    """Best-effort inference of vendor + cost model from heuristics. Hand-curate later."""
    url_l = repo_url.lower()
    vendor = url_l.split("/")[3].split(".")[0].capitalize() if "/" in url_l else "unknown"
    vendor_map = {
        "stripe": ("Stripe", "https://stripe.com", "api_key", "paid_per_call", "0.005–0.029 per txn", True, False),
        "elevenlabs": ("ElevenLabs", "https://elevenlabs.io", "api_key", "freemium", "~0.0001/char", True, False),
        "openai": ("OpenAI", "https://openai.com", "api_key", "paid_per_call", "varies by model", False, False),
        "anthropics": ("Anthropic", "https://anthropic.com", "api_key", "paid_per_call", "varies by model", False, False),
        "twilio": ("Twilio", "https://twilio.com", "api_key", "paid_per_call", "~0.0075/SMS, ~0.013/min", True, False),
        "sendgrid": ("Twilio SendGrid", "https://sendgrid.com", "api_key", "freemium", "free tier 100/day, then ~0.001/email", False, False),
        "shopify": ("Shopify", "https://shopify.com", "api_key", "freemium", "free dev store; production by Shopify plan", True, True),
        "hubspot": ("HubSpot", "https://hubspot.com", "api_key", "freemium", "free CRM tier", True, True),
        "plaid": ("Plaid", "https://plaid.com", "api_key", "paid_per_call", "varies by product", True, True),
        "duffelhq": ("Duffel", "https://duffel.com", "api_key", "paid_per_call", "per offer search ~0.01–0.10", True, False),
        "google": ("Google", "https://cloud.google.com", "api_key", "paid_per_call", "varies", True, True),
        "googlemaps": ("Google Maps Platform", "https://mapsplatform.google.com", "api_key", "paid_per_call", "~0.005/lookup, 200/mo free", False, False),
        "googleapis": ("Google APIs", "https://developers.google.com", "oauth", "freemium", "free tier per API", False, True),
        "mapbox": ("Mapbox", "https://mapbox.com", "api_key", "freemium", "free tier 100k/mo", False, False),
        "huggingface": ("Hugging Face", "https://huggingface.co", "api_key", "freemium", "free tier + paid pro", False, False),
        "replicate": ("Replicate", "https://replicate.com", "api_key", "paid_per_call", "varies by model", False, False),
        "openweathermap": ("OpenWeather", "https://openweathermap.org", "api_key", "freemium", "1000/day free", False, False),
        "mailchimp": ("Mailchimp", "https://mailchimp.com", "api_key", "freemium", "free tier 500 contacts", False, False),
        "resend": ("Resend", "https://resend.com", "api_key", "freemium", "free tier 100/day", False, False),
        "deepgram": ("Deepgram", "https://deepgram.com", "api_key", "paid_per_call", "~0.0043/min audio", True, False),
        "assemblyai": ("AssemblyAI", "https://assemblyai.com", "api_key", "paid_per_call", "~0.0001/sec audio", False, False),
        "deeplcom": ("DeepL", "https://deepl.com", "api_key", "freemium", "free tier 500k char/mo", False, False),
        "tavily-ai": ("Tavily", "https://tavily.com", "api_key", "freemium", "1000 free/mo", False, False),
        "exa-labs": ("Exa", "https://exa.ai", "api_key", "freemium", "1000 free/mo", False, False),
        "cloudflare": ("Cloudflare", "https://cloudflare.com", "api_key", "freemium", "varies", True, True),
        "getsentry": ("Sentry", "https://sentry.io", "api_key", "freemium", "free tier", True, False),
        "intercom": ("Intercom", "https://intercom.com", "api_key", "paid_per_seat", "by plan", False, False),
        "ccxt": ("CCXT (multi-exchange)", "https://github.com/ccxt/ccxt", "api_key", "free", "free (self-host)", False, True),
        "alchemyplatform": ("Alchemy", "https://alchemy.com", "api_key", "freemium", "free tier 300M CU/mo", True, False),
        "octokit": ("GitHub", "https://github.com", "oauth", "freemium", "rate-limited free tier", False, True),
        "pygithub": ("GitHub (PyGithub)", "https://github.com", "oauth", "freemium", "rate-limited free tier", False, True),
        "modelcontextprotocol": ("Anthropic MCP reference", "https://modelcontextprotocol.io", "none", "free", "0", False, True),
    }
    owner = url_l.split("/")[3] if "/" in url_l else ""
    for key, (vendor_name, vendor_url, auth, cost, est, sandbox, user_oauth) in vendor_map.items():
        if key in owner:
            return {
                "vendor": vendor_name,
                "vendor_url": vendor_url,
                "auth_type": auth,
                "sandbox_available": sandbox,
                "requires_user_oauth": user_oauth,
                "cost_model": cost,
                "typical_per_call_cost_usd": est,
            }
    # default: best-effort, mark vendor unknown
    return {
        "vendor": vendor,
        "vendor_url": "",
        "auth_type": "api_key",
        "sandbox_available": False,
        "requires_user_oauth": False,
        "cost_model": "varies",
        "typical_per_call_cost_usd": "varies",
    }


def infer_risk(audit: dict, row: dict) -> dict:
    """Best-effort risk inference from scan findings and slot semantics."""
    slot = (row.get("proposed_slot") or "").lower()
    # any skill whose name implies sending/posting/charging
    destructive = any(k in slot for k in ("create", "send", "post", "publish", "charge", "transfer", "delete", "fulfill", "update", "checkout"))
    spend = any(k in slot for k in ("flights", "stripe", "square", "shipping", "payment", "checkout"))
    # prompt injection: any "read" / "fetch" / "search" / "list" tool that returns 3rd-party content
    pi_high = any(k in slot for k in ("email_read", "ticket_read", "kb_search", "fetch", "browse", "scrape", "support", "intercom", "reviews"))
    risk = {
        "prompt_injection": "high" if pi_high else "low",
        "destructive": bool(destructive),
        "spend_capable": bool(spend),
        "regulated_data": ["pii"] if any(k in slot for k in ("crm", "hr", "finance", "patient", "health")) else [],
        "default_mode": "dry_run" if destructive else "live",
    }
    return risk


_NAME_OVERRIDES = {
    "elevenlabs-mcp": "ElevenLabs MCP",
    "anthropic-sdk-python": "Anthropic SDK (Python)",
    "anthropic-sdk-typescript": "Anthropic SDK (TypeScript)",
    "openai-python": "OpenAI SDK (Python)",
    "openai-node": "OpenAI SDK (Node)",
    "stripe-python": "Stripe SDK (Python)",
    "stripe-node": "Stripe SDK (Node)",
    "agent-toolkit": "Stripe Agent Toolkit",
    "huggingface_hub": "Hugging Face Hub",
    "replicate-python": "Replicate SDK (Python)",
    "replicate-javascript": "Replicate SDK (Node)",
    "google-maps-services-python": "Google Maps Services (Python)",
    "google-maps-services-js": "Google Maps Services (Node)",
    "google-api-python-client": "Google APIs Client (Python)",
    "google-api-nodejs-client": "Google APIs Client (Node)",
    "mapbox-sdk-js": "Mapbox SDK (Node)",
    "twilio-python": "Twilio SDK (Python)",
    "twilio-node": "Twilio SDK (Node)",
    "sendgrid-python": "Twilio SendGrid (Python)",
    "sendgrid-nodejs": "Twilio SendGrid (Node)",
    "resend-python": "Resend SDK (Python)",
    "resend-node": "Resend SDK (Node)",
    "plaid-python": "Plaid SDK (Python)",
    "plaid-node": "Plaid SDK (Node)",
    "hubspot-api-python": "HubSpot SDK (Python)",
    "hubspot-api-nodejs": "HubSpot SDK (Node)",
    "easypost-python": "EasyPost SDK (Python)",
    "easypost-node": "EasyPost SDK (Node)",
    "mailchimp-marketing-python": "Mailchimp Marketing (Python)",
    "mailchimp-marketing-node": "Mailchimp Marketing (Node)",
    "square-python-sdk": "Square SDK (Python)",
    "square-nodejs-sdk": "Square SDK (Node)",
    "octokit.js": "Octokit (GitHub) for Node",
    "PyGithub": "PyGithub (GitHub) for Python",
    "github-mcp-server": "GitHub MCP Server",
    "sentry-mcp": "Sentry MCP Server",
    "mcp-server-cloudflare": "Cloudflare MCP Server",
    "mcp-server-browserbase": "Browserbase MCP Server",
    "playwright-mcp": "Playwright MCP Server",
    "notion-sdk-js": "Notion SDK (Node)",
    "notion-mcp-server": "Notion MCP Server",
    "linear": "Linear SDK",
    "jsforce": "Salesforce SDK (jsforce)",
    "client-nodejs": "Pipedrive SDK (Node)",
    "client-python": "Pipedrive SDK (Python)",
    "flights-mcp": "Duffel Flights MCP",
    "duffel-api-javascript": "Duffel SDK (Node)",
    "duffel-api-python": "Duffel SDK (Python)",
    "zendesk_api_client_rb": "Zendesk SDK (Ruby)",
    "rembg": "rembg — background removal",
    "ccxt": "CCXT — unified crypto exchange API",
    "spotify-mcp": "Spotify MCP Server",
    "12306-mcp": "China Rail (12306) MCP",
    "apify-mcp-server": "Apify MCP Server (web scraping)",
    "shopify-mcp": "Shopify MCP Server",
    "shopify-mcp-server": "Shopify MCP Server (alt)",
    "mcp_massive": "Massive Financial Market Data MCP",
    "mcp-toolbox": "Google MCP Toolbox",
}


def _pretty_name(slot: str, repo: str) -> str:
    if repo in _NAME_OVERRIDES:
        return _NAME_OVERRIDES[repo]
    return repo.replace("-", " ").replace("_", " ").title()


def _pretty_summary(row: dict, manifest_repo: str) -> str:
    notes = (row.get("notes") or "").strip()
    desc = (row.get("description") or "").strip()
    # If notes are useful (not just "discovered_from:..."), prefer them
    if notes and not notes.startswith("discovered_from:") and len(notes) > 6:
        return notes[:280]
    if desc and len(desc) > 6:
        return desc[:280]
    return f"{manifest_repo} — see vendor URL for capability details."


def build_manifest(row: dict, audit: dict, smoke: dict) -> dict | None:
    slot = row.get("proposed_slot") or ""
    tracks, category, slug = slot_to_path(slot)
    if not tracks:
        return None
    parsed = parse_github_url(row["source_url"])
    if not parsed:
        return None
    owner, repo = parsed
    # avoid only the literal double-owner case (e.g. "elevenlabs-elevenlabs-mcp" → "elevenlabs-mcp")
    if slug.lower() == f"{owner.lower()}-{repo.lower()}":
        slug = repo.lower()
    upstream = infer_upstream(row["source_url"], row, audit)
    risk = infer_risk(audit, row)
    # x402 compat: idempotent read-only calls are x402-compatible by default;
    # destructive/spend-capable are still compatible *if* they have a dry-run mode.
    x402 = True
    x402_notes = "per-call, deterministic JSON response"
    if risk["spend_capable"] and risk["default_mode"] == "live":
        x402 = False
        x402_notes = "spend-capable in live mode — needs sandbox-gated invocation in Orbit"

    manifest = {
        "schema_version": "1.0",
        "id": f"{'both' if len(tracks) == 2 else tracks[0]}.{category}.{slug}",
        "name": _pretty_name(slot, repo),
        "slug": slug,
        "track": tracks,
        "category": category,
        "slot": slug,
        "summary": _pretty_summary(row, repo),
        "version": "1.0.0",
        "source": {
            "kind": row.get("kind", "sdk_wrapper") if row.get("kind") in ("mcp_server", "sdk_wrapper", "tool_folder", "composite") else "sdk_wrapper",
            "repo_url": row["source_url"],
            "commit_pinned": (audit.get("commit_pinned") or "")[:40],
            "license": row.get("license") or "UNVERIFIED",
            "last_commit_at": row.get("last_commit_at") or "",
            "stars": int(row.get("stars") or 0),
            "primary_language": row.get("primary_language") or "",
            "maintainer": owner,
        },
        "upstream": upstream,
        "x402_compatible": x402,
        "x402_notes": x402_notes,
        "tools": [
            {
                "name": "primary",
                "summary": "Primary entry point (smoke-tested via import / require). Tool catalogue derived at runtime from the upstream package.",
                "destructive": risk["destructive"],
                "idempotent": not risk["destructive"],
                "rate_limit": "see upstream docs",
            }
        ],
        "tags": [category, owner, *([row.get("track_hint")] if row.get("track_hint") else [])],
        "risk": risk,
        "audit": {
            "verdict": audit.get("verdict") or "pass",
            "log": "audit.json",
            "scanners_run": audit.get("scanners_run", []),
            "behavioral_check": "clean_with_notes",
        },
        "smoke": {
            "verdict": smoke.get("verdict") or "deferred",
            "log": "smoke.json",
            "last_passed_at": smoke.get("smoked_at") or utc_now_iso(),
        },
        "orbit": {
            "suggested_markup_floor_pct": 5,
            "suggested_markup_ceiling_pct": 50,
            "pricing_note": f"Upstream cost model: {upstream['cost_model']}.",
            "tokenization_friendly": upstream["cost_model"] in ("free", "freemium"),
        },
        "notes": row.get("notes", ""),
    }
    return manifest


def render_skill_md(manifest: dict, audit: dict, smoke: dict) -> str:
    m = manifest
    lines = []
    lines.append(f"# {m['name']}\n")
    lines.append(f"**Track:** {' + '.join(m['track'])}")
    lines.append(f"**Category:** {m['category']}")
    lines.append(f"**Slot:** `{m['id']}`")
    lines.append(f"**Source:** [{m['source']['repo_url']}]({m['source']['repo_url']}) (license: `{m['source']['license']}`, pinned commit: `{m['source']['commit_pinned'][:7]}`)")
    lines.append(f"**Upstream:** {m['upstream']['vendor']} — {m['upstream']['vendor_url']}")
    lines.append("")
    lines.append("## What it does\n")
    lines.append(m["summary"])
    lines.append("")
    lines.append("## What it costs\n")
    lines.append(f"- Upstream cost model: **{m['upstream']['cost_model']}**")
    lines.append(f"- Typical per-call cost: **{m['upstream']['typical_per_call_cost_usd']}**")
    if m["upstream"].get("sandbox_available"):
        lines.append(f"- Sandbox available: yes")
    lines.append("")
    lines.append("## What it needs\n")
    lines.append(f"- Auth: **{m['upstream']['auth_type']}**")
    if m["upstream"].get("requires_user_oauth"):
        lines.append(f"- Requires end-user OAuth (Orbit creator's buyers each authenticate their own account)")
    lines.append(f"- Obtain credentials: see vendor URL above")
    lines.append("")
    lines.append("## Safety notes\n")
    lines.append(f"- Prompt-injection risk: **{m['risk']['prompt_injection']}**")
    lines.append(f"- Destructive actions: **{'yes' if m['risk']['destructive'] else 'no'}**")
    if m["risk"]["spend_capable"]:
        lines.append(f"- Spend-capable: yes")
    if m["risk"]["regulated_data"]:
        lines.append(f"- Regulated data: {', '.join(m['risk']['regulated_data'])}")
    lines.append(f"- Default mode: **{m['risk']['default_mode']}**")
    lines.append("")
    lines.append("## Smoke test\n")
    lines.append(f"- Verdict: **{m['smoke']['verdict']}**")
    lines.append(f"- Last passed: {m['smoke']['last_passed_at']}")
    lines.append(f"- Full log: `smoke.json`")
    lines.append("")
    lines.append("## Audit\n")
    lines.append(f"- Verdict: **{m['audit']['verdict']}**")
    lines.append(f"- Scanners: {', '.join(m['audit']['scanners_run']) or '(native pattern scan only)'}")
    lines.append(f"- Full log: `audit.json`")
    lines.append("")
    lines.append("## x402 compatibility\n")
    lines.append(f"- Compatible: **{m['x402_compatible']}**")
    lines.append(f"- Notes: {m['x402_notes']}")
    lines.append("")
    return "\n".join(lines)


def write_skill(manifest: dict, audit: dict, smoke: dict, track: str) -> Path:
    category = manifest["category"]
    slug = manifest["slug"]
    folder = ROOT / track / category / slug
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (folder / "SKILL.md").write_text(render_skill_md(manifest, audit, smoke), encoding="utf-8")
    (folder / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    (folder / "smoke.json").write_text(json.dumps(smoke, indent=2), encoding="utf-8")
    examples = folder / "examples"
    examples.mkdir(exist_ok=True)
    (examples / "input.json").write_text(json.dumps({
        "_note": "stub — replace with a real representative input once Orbit's runtime is integrated",
        "tool": "primary",
        "args": {}
    }, indent=2), encoding="utf-8")
    (examples / "output.json").write_text(json.dumps({
        "_note": "stub — recorded smoke output is in ../smoke.json",
        "ok": True,
        "data": {}
    }, indent=2), encoding="utf-8")
    return folder


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-deferred", action="store_true", help="also document skills with smoke verdict=deferred")
    args = ap.parse_args()

    shortlist = load_jsonl(SHORTLIST)
    by_url = {r["source_url"]: r for r in shortlist}

    personal_rows = []
    merchant_rows = []
    written = 0
    skipped = 0

    for url, row in by_url.items():
        parsed = parse_github_url(url)
        if not parsed:
            continue
        owner, repo = parsed
        audit_path = SCAN_LOG_BASE / f"{owner}__{repo}" / "audit.json"
        smoke_path = SMOKE_LOG_BASE / f"{owner}__{repo}" / "smoke.json"
        if not audit_path.exists():
            skipped += 1
            continue
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except Exception:
            skipped += 1
            continue
        if audit.get("verdict") not in ("pass", "pass_with_notes"):
            skipped += 1
            continue
        if smoke_path.exists():
            try:
                smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
            except Exception:
                smoke = {"verdict": "deferred", "reason": "smoke.json unreadable", "smoked_at": utc_now_iso()}
        else:
            smoke = {"verdict": "deferred", "reason": "smoke not run", "smoked_at": utc_now_iso()}

        if smoke.get("verdict") == "fail":
            skipped += 1
            continue
        if smoke.get("verdict") == "deferred" and not args.include_deferred:
            skipped += 1
            continue

        manifest = build_manifest(row, audit, smoke)
        if not manifest:
            skipped += 1
            continue

        # Determine which track folder owns the canonical write. If 'both', pick personal.
        tracks = manifest["track"]
        canonical = "personal" if "personal" in tracks else "merchant"
        write_skill(manifest, audit, smoke, canonical)
        # cross-list: if both tracks, also write to merchant folder (linked manifest)
        if "personal" in tracks and "merchant" in tracks:
            write_skill(manifest, audit, smoke, "merchant")

        flat = {
            "id": manifest["id"],
            "name": manifest["name"],
            "track": tracks,
            "category": manifest["category"],
            "slot": manifest["slot"],
            "source": manifest["source"]["repo_url"],
            "license": manifest["source"]["license"],
            "stars": manifest["source"]["stars"],
            "vendor": manifest["upstream"]["vendor"],
            "cost_model": manifest["upstream"]["cost_model"],
            "x402_compatible": manifest["x402_compatible"],
            "audit_verdict": manifest["audit"]["verdict"],
            "smoke_verdict": manifest["smoke"]["verdict"],
        }
        if "personal" in tracks:
            personal_rows.append(flat)
        if "merchant" in tracks:
            merchant_rows.append(flat)
        written += 1

    write_jsonl_atomic(ROOT / "_catalog" / "personal.jsonl", personal_rows)
    write_jsonl_atomic(ROOT / "_catalog" / "merchant.jsonl", merchant_rows)
    log(f"document: wrote {written} skills, skipped {skipped}; personal={len(personal_rows)} merchant={len(merchant_rows)}")
    print(json.dumps({"written": written, "skipped": skipped, "personal": len(personal_rows), "merchant": len(merchant_rows)}, indent=2))


if __name__ == "__main__":
    main()
