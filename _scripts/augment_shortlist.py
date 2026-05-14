"""Augment the shortlist with high-value aggregator-discovered candidates.

The basic triage collapses all `_uncategorized.from_aggregator` rows into a
single dedup bucket, which is too coarse. This script:

  1. Reads discovery.jsonl.
  2. Filters aggregator-discovered rows by:
       - exists, not archived
       - permissive license
       - last_commit_at within 12 months
       - stars >= AGGREGATOR_STAR_FLOOR
  3. Heuristically re-slots them based on owner + description keywords.
  4. Appends to shortlist.jsonl, deduping by source_url.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT, log, load_jsonl, write_jsonl_atomic, EXCLUDED_LICENSES

DISCOVERY = ROOT / "_candidates_raw" / "discovery.jsonl"
SHORTLIST = ROOT / "_candidates_raw" / "shortlist.jsonl"

AGGREGATOR_STAR_FLOOR = 200  # only pull aggregator finds with at least this many stars

# Owner -> (track, category) when owner alone is sufficient signal
OWNER_HINTS = {
    "microsoft": ("merchant", "devops"),
    "anthropic": ("both", "creative"),
    "anthropics": ("both", "creative"),
    "openai": ("both", "creative"),
    "google": ("both", "productivity"),
    "googlemaps": ("both", "maps"),
    "googleapis": ("both", "productivity"),
    "mapbox": ("both", "maps"),
    "stripe": ("merchant", "finance"),
    "twilio": ("both", "comms"),
    "sendgrid": ("merchant", "marketing"),
    "shopify": ("merchant", "ecommerce"),
    "hubspot": ("merchant", "crm"),
    "atlassian": ("merchant", "ops"),
    "cloudflare": ("merchant", "devops"),
    "supabase": ("merchant", "devops"),
    "getsentry": ("merchant", "devops"),
    "elevenlabs": ("both", "creative"),
    "duffelhq": ("personal", "travel"),
    "plaid": ("both", "finance"),
    "replicate": ("both", "creative"),
    "huggingface": ("both", "creative"),
    "deepgram": ("both", "creative"),
    "assemblyai": ("both", "creative"),
    "tavily-ai": ("both", "search"),
    "exa-labs": ("both", "search"),
    "ccxt": ("personal", "finance"),
    "playwright": ("merchant", "devops"),
    "browserbase": ("merchant", "devops"),
}

# Keyword -> (track, category) for description-based slotting
KW_HINTS = [
    (r"\b(flight|airline|airfare)\b", ("personal", "travel")),
    (r"\b(hotel|booking|airbnb)\b", ("personal", "travel")),
    (r"\b(weather|forecast|meteo)\b", ("personal", "home")),
    (r"\b(recipe|cooking|meal)\b", ("personal", "home")),
    (r"\b(map|maps|geocod|navigation|directions)\b", ("both", "maps")),
    (r"\b(payment|invoice|billing|stripe|square|paypal)\b", ("merchant", "finance")),
    (r"\b(crm|hubspot|salesforce|pipedrive)\b", ("merchant", "crm")),
    (r"\b(email|mail|gmail|smtp|imap)\b", ("both", "productivity")),
    (r"\b(calendar|schedul|meeting)\b", ("both", "productivity")),
    (r"\b(notion|obsidian|note-taking)\b", ("both", "productivity")),
    (r"\b(linear|jira|asana|trello|monday|clickup)\b", ("merchant", "ops")),
    (r"\b(slack|discord|teams|whatsapp|telegram)\b", ("both", "comms")),
    (r"\b(github|gitlab|bitbucket|pull request)\b", ("merchant", "devops")),
    (r"\b(sentry|datadog|grafana|prometheus|new relic|pagerduty)\b", ("merchant", "devops")),
    (r"\b(aws|s3|ec2|lambda|google cloud|azure)\b", ("merchant", "devops")),
    (r"\b(playwright|puppeteer|selenium|browser)\b", ("merchant", "devops")),
    (r"\b(database|sql|postgres|mysql|sqlite|mongo|redis)\b", ("merchant", "analytics")),
    (r"\b(zendesk|intercom|freshdesk|helpscout|customer support)\b", ("merchant", "support")),
    (r"\b(seo|keyword|serp|google ads|meta ads|advertising)\b", ("merchant", "marketing")),
    (r"\b(shopify|woocommerce|magento|bigcommerce|ecommerce)\b", ("merchant", "ecommerce")),
    (r"\b(stock|crypto|market|trading|portfolio|finance)\b", ("personal", "finance")),
    (r"\b(arxiv|wikipedia|wikidata|pubmed|scholar|research)\b", ("both", "learning")),
    (r"\b(news|reuters|bloomberg|reddit|hackernews)\b", ("personal", "news")),
    (r"\b(image|video|audio|tts|stt|transcrib|voice|music)\b", ("both", "creative")),
    (r"\b(translat|deepl|nllb)\b", ("both", "creative")),
    (r"\b(search|tavily|exa|brave|serp)\b", ("both", "search")),
    (r"\b(scrape|fetch|browser|web)\b", ("both", "search")),
    (r"\b(spotify|apple music|tidal|youtube)\b", ("personal", "entertainment")),
    (r"\b(movie|film|tmdb|netflix|streaming)\b", ("personal", "entertainment")),
    (r"\b(fitness|workout|strava|fitbit|garmin)\b", ("personal", "health")),
    (r"\b(home assistant|hue|smart home|matter|thread)\b", ("personal", "home")),
    (r"\b(blockchain|ethereum|solana|wallet|nft)\b", ("personal", "finance")),
]


def categorize(row: dict) -> tuple[str, str, str] | None:
    """Return (track, category, slug) or None if can't categorize confidently."""
    url_l = (row.get("source_url") or "").lower()
    owner = url_l.split("/")[3] if "/" in url_l else ""
    repo = url_l.split("/")[-1] if "/" in url_l else ""
    desc = (row.get("description") or "").lower()
    haystack = " ".join([owner, repo, desc])
    # 1) owner hint
    for o, (track, category) in OWNER_HINTS.items():
        if owner == o or owner.startswith(o + "-") or owner.endswith("-" + o):
            return track, category, f"{owner}-{repo}"
    # 2) keyword hints
    for pat, (track, category) in KW_HINTS:
        if re.search(pat, haystack):
            return track, category, f"{owner}-{repo}"
    return None


def main():
    discovery = load_jsonl(DISCOVERY)
    shortlist = load_jsonl(SHORTLIST)
    existing_urls = {r["source_url"].lower() for r in shortlist}

    cutoff_date = datetime(2025, 5, 14)  # 12 months back from 2026-05-14
    added = []
    seen_slots: dict[str, int] = Counter()
    for r in discovery:
        if r["source_url"].lower() in existing_urls:
            continue
        if not r.get("exists") or r.get("archived"):
            continue
        if r.get("license") in EXCLUDED_LICENSES:
            continue
        if not r.get("license"):
            continue
        stars = int(r.get("stars") or 0)
        if stars < AGGREGATOR_STAR_FLOOR:
            continue
        # maintenance
        last = r.get("last_commit_at") or ""
        try:
            d = datetime.fromisoformat(last)
            if d < cutoff_date:
                continue
        except Exception:
            continue
        # only aggregator-sourced (proposed_slot will start with _uncategorized when
        # the row came from the awesome-list crawl rather than the curated seed list)
        if r.get("proposed_slot", "").startswith("_uncategorized"):
            cat = categorize(r)
            if not cat:
                continue
            track, category, slug = cat
            slot = f"{track}.{category}.{slug}"
            # cap per category at 12 to keep audit phase tractable
            cat_key = f"{track}.{category}"
            if seen_slots[cat_key] >= 12:
                continue
            seen_slots[cat_key] += 1
            r2 = dict(r)
            r2["proposed_slot"] = slot
            r2["track_hint"] = track
            r2["_triage_decision"] = "keep"
            r2["_triage_reason"] = f"aggregator-augment: {stars}★ last={last} category={track}.{category}"
            added.append(r2)
            existing_urls.add(r["source_url"].lower())

    out = shortlist + added
    write_jsonl_atomic(SHORTLIST, out)
    print(json.dumps({
        "shortlist_before": len(shortlist),
        "augment_added": len(added),
        "shortlist_after": len(out),
        "by_category": {k: v for k, v in seen_slots.most_common()},
    }, indent=2))


if __name__ == "__main__":
    main()
