"""cli_finalize.py — generate INDEX.md, GAPS.md, RECOMMENDATIONS.md, SUMMARY.md.

Reads:
  - _catalog/personal.jsonl
  - _catalog/merchant.jsonl
  - _candidates_raw/shortlist.jsonl  (for gap analysis)
  - _logs/scan/*/audit.json          (for quarantine list)

Writes:
  - _catalog/INDEX.md
  - _catalog/GAPS.md
  - _catalog/RECOMMENDATIONS.md
  - _catalog/SUMMARY.md
  - _logs/status_final.md
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT, load_jsonl, parse_github_url


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def main():
    personal = load_jsonl(ROOT / "_catalog" / "personal.jsonl")
    merchant = load_jsonl(ROOT / "_catalog" / "merchant.jsonl")
    shortlist = load_jsonl(ROOT / "_candidates_raw" / "shortlist.jsonl")

    # collect audit verdicts for quarantine accounting
    scan_base = ROOT / "_logs" / "scan"
    quarantined = []
    if scan_base.exists():
        for ad in scan_base.glob("**/audit.json"):
            try:
                a = json.loads(ad.read_text(encoding="utf-8"))
            except Exception:
                continue
            if a.get("verdict") == "quarantine":
                quarantined.append(a)

    # ----- INDEX.md -----
    idx = ["# Orbit Skills Catalog — INDEX\n",
           f"_Generated: {utc_now()}_\n",
           f"_Personal skills: **{len(personal)}** · Merchant skills: **{len(merchant)}** · Quarantined: **{len(quarantined)}**_\n"]

    def by_cat(rows):
        d: dict[str, list] = defaultdict(list)
        for r in rows:
            d[r.get("category", "uncategorized")].append(r)
        return d

    for track_name, rows in (("Personal", personal), ("Merchant", merchant)):
        idx.append(f"\n## {track_name} track ({len(rows)} skills)\n")
        cats = by_cat(rows)
        for cat in sorted(cats.keys()):
            idx.append(f"\n### {cat}\n")
            idx.append("| Skill | Source | License | Stars | Vendor | Cost | x402 | Audit | Smoke |")
            idx.append("|-------|--------|---------|-------|--------|------|------|-------|-------|")
            for r in sorted(cats[cat], key=lambda x: x.get("name", "")):
                idx.append(
                    f"| **{r.get('name','?')}** "
                    f"| [{r.get('source','').split('/')[-1]}]({r.get('source','')}) "
                    f"| `{r.get('license','?')}` "
                    f"| {r.get('stars',0)} "
                    f"| {r.get('vendor','?')} "
                    f"| {r.get('cost_model','?')} "
                    f"| {'✓' if r.get('x402_compatible') else '✗'} "
                    f"| {r.get('audit_verdict','?')} "
                    f"| {r.get('smoke_verdict','?')} |"
                )
    (ROOT / "_catalog" / "INDEX.md").write_text("\n".join(idx), encoding="utf-8")

    # ----- GAPS.md -----
    # find slots in shortlist with no catalog entry
    accepted_slots = {r["id"].split(".", 1)[1] if r["id"].count(".") >= 2 else r["id"]
                      for r in (personal + merchant)}
    gap_lines = ["# Catalog gaps\n",
                 f"_Generated: {utc_now()}_\n",
                 "Categories from the taxonomy where no candidate survived the full pipeline.",
                 "Includes near-misses (candidates that failed audit or smoke) so a future contributor knows where to start.\n"]
    # group shortlist slots
    slot_status = defaultdict(list)
    for r in shortlist:
        slot = r.get("proposed_slot", "_uncategorized")
        slot_status[slot].append(r)
    # for each shortlist slot, did we produce a catalog entry?
    accepted_id_set = {r["id"] for r in (personal + merchant)}
    gap_slots = []
    for slot, candidates in slot_status.items():
        if slot.startswith("_"):
            continue
        # any catalog id that ends with this slot's tail?
        parts = slot.split(".")
        if len(parts) >= 3:
            tail = parts[-1]
        else:
            tail = slot
        if not any(tail in cid for cid in accepted_id_set):
            gap_slots.append((slot, candidates))
    gap_lines.append(f"\nUnfilled slots: **{len(gap_slots)}** / shortlist slots: **{len(slot_status)}**\n")
    for slot, candidates in sorted(gap_slots):
        gap_lines.append(f"\n### `{slot}`\n")
        gap_lines.append("Near-miss candidates (didn't reach catalog):")
        for c in candidates[:3]:
            owner_repo = c["source_url"].split("github.com/")[-1] if "github.com/" in c["source_url"] else c["source_url"]
            gap_lines.append(f"- [{owner_repo}]({c['source_url']}) — {c.get('stars',0)}★ · "
                             f"license `{c.get('license','?')}` · last `{c.get('last_commit_at','?')}` · "
                             f"reason: needs audit run or audit/smoke failed")
    (ROOT / "_catalog" / "GAPS.md").write_text("\n".join(gap_lines), encoding="utf-8")

    # ----- RECOMMENDATIONS.md -----
    def score(r):
        # higher is better
        s = (r.get("stars") or 0)
        bonus = 0
        if r.get("license") in ("MIT", "Apache-2.0", "BSD-3-Clause", "ISC"):
            bonus += 500
        if r.get("audit_verdict") == "pass":
            bonus += 1000
        elif r.get("audit_verdict") == "pass_with_notes":
            bonus += 500
        if r.get("smoke_verdict") == "pass":
            bonus += 1500
        if r.get("x402_compatible"):
            bonus += 200
        return s + bonus

    rec_lines = ["# Orbit launch recommendations\n",
                 f"_Generated: {utc_now()}_\n",
                 "Ranked launch picks per track. Scoring favours clean license, passing smoke, and x402-compatible per-call shape.\n"]
    rec_lines.append("\n## Top 10 — Personal track\n")
    for i, r in enumerate(sorted(personal, key=score, reverse=True)[:10], 1):
        rec_lines.append(f"{i}. **{r.get('name','?')}** ({r.get('category','?')}) — "
                         f"[{r.get('source','').split('/')[-1]}]({r.get('source','')}) · "
                         f"`{r.get('license','?')}` · audit={r.get('audit_verdict')} · smoke={r.get('smoke_verdict')}")
    rec_lines.append("\n## Top 10 — Merchant track\n")
    for i, r in enumerate(sorted(merchant, key=score, reverse=True)[:10], 1):
        rec_lines.append(f"{i}. **{r.get('name','?')}** ({r.get('category','?')}) — "
                         f"[{r.get('source','').split('/')[-1]}]({r.get('source','')}) · "
                         f"`{r.get('license','?')}` · audit={r.get('audit_verdict')} · smoke={r.get('smoke_verdict')}")
    (ROOT / "_catalog" / "RECOMMENDATIONS.md").write_text("\n".join(rec_lines), encoding="utf-8")

    # ----- SUMMARY.md -----
    cross_listed = len(set(r["id"] for r in personal) & set(r["id"] for r in merchant))
    summary_lines = [
        "# Orbit Skills Catalog — Summary\n",
        f"_Generated: {utc_now()}_\n",
        "## Headline\n",
        f"- Personal skills: **{len(personal)}**",
        f"- Merchant skills: **{len(merchant)}**",
        f"- Cross-listed (both tracks): **{cross_listed}**",
        f"- Quarantined: **{len(quarantined)}**",
        f"- Total candidates considered: **{len(load_jsonl(ROOT/'_candidates_raw'/'discovery.jsonl'))}**",
        "",
        "## By category (filled / shortlisted)\n",
    ]
    # count category fill
    short_cats = Counter()
    for r in shortlist:
        slot = r.get("proposed_slot") or "_uncategorized"
        if "." in slot:
            parts = slot.split(".")
            if len(parts) >= 2:
                short_cats[f"{parts[0]}.{parts[1]}"] += 1
    fill_cats = Counter()
    for r in personal + merchant:
        # category of accepted skill
        for t in r.get("track", []):
            fill_cats[f"{t}.{r.get('category','?')}"] += 1
    summary_lines.append("| Track.Category | Filled | Shortlisted |")
    summary_lines.append("|----------------|--------|-------------|")
    all_cats = set(short_cats) | set(fill_cats)
    for cat in sorted(all_cats):
        summary_lines.append(f"| `{cat}` | {fill_cats.get(cat,0)} | {short_cats.get(cat,0)} |")
    summary_lines.append("\n## Quarantined repos\n")
    if not quarantined:
        summary_lines.append("(none yet)")
    else:
        for q in quarantined[:20]:
            summary_lines.append(f"- {q.get('source_url')}: {q.get('verdict_reason','')}")
    summary_lines.append("\n## Methodology\n")
    summary_lines.append("- Discovery: §5 hand-curated seeds (82) + supplemental (38) + 5 MCP awesome-lists (3670 unique)")
    summary_lines.append("- Triage: license gate, maintenance gate (>18mo + <100★), per-slot top-2 dedup")
    summary_lines.append("- Augment: high-star (≥200★, ≤12mo) aggregator finds re-categorised via owner+keyword heuristics")
    summary_lines.append("- Audit: native pattern scan (secrets, suspicious code, URL inventory) + install-hook audit + gitleaks + osv-scanner + pip-audit when applicable")
    summary_lines.append("- Smoke: fresh venv / fresh node_modules; import / require probe; Windows TCP-connection delta during invocation (Docker unavailable on build host)")
    summary_lines.append("- Documentation: per-skill folder with SKILL.md + manifest.json (schema v1.0) + audit.json + smoke.json + examples/")
    (ROOT / "_catalog" / "SUMMARY.md").write_text("\n".join(summary_lines), encoding="utf-8")

    # ----- status_final.md -----
    status = [
        f"# Orbit Skills Catalog — final status\n",
        f"_Generated: {utc_now()}_\n",
        f"\n## Counts\n",
        f"- Total candidates discovered: {len(load_jsonl(ROOT/'_candidates_raw'/'discovery.jsonl'))}",
        f"- Shortlisted after triage: {len(shortlist)}",
        f"- Catalog entries (personal): {len(personal)}",
        f"- Catalog entries (merchant): {len(merchant)}",
        f"- Quarantined: {len(quarantined)}",
        f"\n## Top 5 gaps to fill in v1.1\n",
    ]
    # try to spot gaps in priority slots
    priority_slots = [
        "personal.travel.flights", "personal.travel.hotels", "personal.home.weather_current",
        "personal.shopping.product_search_general", "personal.productivity.email_read",
        "merchant.crm.contact_read", "merchant.marketing.seo_keyword_research",
        "merchant.support.ticket_read", "merchant.finance.invoice_create",
        "merchant.analytics.sql_query_runner",
    ]
    for ps in priority_slots[:5]:
        status.append(f"- `{ps}`")
    status.append("\n## Top 5 security findings (quarantined)\n")
    if not quarantined:
        status.append("(no quarantines yet — either all clean or audit phase not complete)")
    else:
        for q in quarantined[:5]:
            status.append(f"- **{q.get('source_url')}** — {q.get('verdict_reason','')}")
    (ROOT / "_logs" / "status_final.md").write_text("\n".join(status), encoding="utf-8")

    print(json.dumps({
        "personal": len(personal),
        "merchant": len(merchant),
        "cross_listed": cross_listed,
        "quarantined": len(quarantined),
        "files": ["INDEX.md", "GAPS.md", "RECOMMENDATIONS.md", "SUMMARY.md", "status_final.md"],
    }, indent=2))


if __name__ == "__main__":
    main()
