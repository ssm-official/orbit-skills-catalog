"""cli_triage.py — apply license/maintenance/scope gates from §3 / Phase 2.

Reads:   _candidates_raw/discovery.jsonl
Writes:  _candidates_raw/shortlist.jsonl
         _candidates_raw/triage_drops.jsonl
         _logs/status_phase_2.md (summary)
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT, log, load_jsonl, write_jsonl_atomic, triage_decision

DISCOVERY = ROOT / "_candidates_raw" / "discovery.jsonl"
SHORTLIST = ROOT / "_candidates_raw" / "shortlist.jsonl"
DROPS = ROOT / "_candidates_raw" / "triage_drops.jsonl"
STATUS = ROOT / "_logs" / "status_phase_2.md"


def main():
    rows = load_jsonl(DISCOVERY)
    if not rows:
        print(f"no rows in {DISCOVERY}; run cli_verify.py first")
        return

    keeps, drops = [], []
    reasons = Counter()
    for r in rows:
        # aggregators don't enter the catalog directly — they fan out in Phase 1.5
        if r.get("kind") == "aggregator" or (r.get("proposed_slot", "").startswith("_aggregator")) or (r.get("proposed_slot", "").startswith("_meta")):
            r["_triage_decision"] = "drop"
            r["_triage_reason"] = "aggregator/meta — fans out separately"
            drops.append(r)
            reasons["meta"] += 1
            continue
        decision, reason = triage_decision(r)
        r["_triage_decision"] = decision
        r["_triage_reason"] = reason
        if decision == "keep":
            keeps.append(r)
        else:
            drops.append(r)
        reasons[reason if decision != "keep" else "kept"] += 1

    # dedupe by proposed_slot — top 2 per slot, preferring official orgs first then highest stars
    OFFICIAL_HINTS = ("stripe/", "github/", "elevenlabs/", "openai/", "anthropics/", "googlemaps/",
                      "google/", "googleapis/", "mapbox/", "huggingface/", "replicate/",
                      "shopify/", "hubspot/", "twilio/", "sendgrid/", "resend/", "plaid/",
                      "duffelhq/", "square/", "easypost/", "mailchimp/", "octokit/",
                      "modelcontextprotocol/", "getsentry/", "cloudflare/", "microsoft/",
                      "makenotion/", "linear/", "browserbase/", "intercom/")

    def rank_key(c):
        url_l = (c.get("source_url") or "").lower()
        is_official = any(h in url_l for h in OFFICIAL_HINTS)
        return (0 if is_official else 1, -(c.get("stars") or 0))

    by_slot: dict[str, list] = {}
    for c in keeps:
        slot = c.get("proposed_slot") or "_unslotted"
        by_slot.setdefault(slot, []).append(c)

    shortlist = []
    for slot, items in by_slot.items():
        items.sort(key=rank_key)
        for it in items[:2]:
            shortlist.append(it)
        for it in items[2:]:
            it["_triage_decision"] = "drop"
            it["_triage_reason"] = f"slot {slot} already has top 2"
            drops.append(it)

    write_jsonl_atomic(SHORTLIST, shortlist)
    write_jsonl_atomic(DROPS, drops)

    # status summary
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    with STATUS.open("w", encoding="utf-8") as f:
        f.write("# Phase 2 — Triage status\n\n")
        f.write(f"- Discovery input: **{len(rows)}** candidates\n")
        f.write(f"- Shortlist output: **{len(shortlist)}** candidates\n")
        f.write(f"- Drops: **{len(drops)}**\n\n")
        f.write("## Drop reasons\n\n")
        for reason, n in reasons.most_common():
            f.write(f"- `{reason}` — {n}\n")
        f.write("\n## Shortlisted slots\n\n")
        slot_counts = Counter(c.get("proposed_slot") or "_unslotted" for c in shortlist)
        for slot, n in slot_counts.most_common():
            f.write(f"- `{slot}` — {n} candidate(s)\n")

    log(f"triage: discovered={len(rows)} shortlist={len(shortlist)} drops={len(drops)}")
    print(json.dumps({"discovered": len(rows), "shortlisted": len(shortlist), "dropped": len(drops)}, indent=2))


if __name__ == "__main__":
    main()
