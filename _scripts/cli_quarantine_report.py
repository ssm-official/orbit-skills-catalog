"""cli_quarantine_report.py — produce per-quarantine memos under _quarantine/.

Reads:  _logs/scan/<owner>__<repo>/audit.json
Writes: _quarantine/<owner>__<repo>/MEMO.md + audit.json (copy)

Each memo summarises:
  - what the repo claimed to do
  - what the static scan found
  - why it was quarantined
  - whether a successor exists to slot in

A repo only ends up here if its audit verdict is 'quarantine'. Quarantine is
the audit trail — these aren't catalog entries, but the catalog has to be
able to explain why a popular repo was *not* included.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT, load_jsonl

SCAN_LOG_BASE = ROOT / "_logs" / "scan"
QUARANTINE_BASE = ROOT / "_quarantine"
SHORTLIST = ROOT / "_candidates_raw" / "shortlist.jsonl"


def main():
    shortlist = load_jsonl(SHORTLIST)
    by_url = {r["source_url"]: r for r in shortlist}
    if not SCAN_LOG_BASE.exists():
        print("no scan logs yet")
        return
    n = 0
    for ad in SCAN_LOG_BASE.glob("*/audit.json"):
        try:
            a = json.loads(ad.read_text(encoding="utf-8"))
        except Exception:
            continue
        if a.get("verdict") != "quarantine":
            continue
        owner_repo = ad.parent.name
        row = by_url.get(a["source_url"], {})
        q_dir = QUARANTINE_BASE / owner_repo
        q_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ad, q_dir / "audit.json")
        memo = []
        memo.append(f"# Quarantine memo — {owner_repo}\n")
        memo.append(f"**Source:** [{a['source_url']}]({a['source_url']})\n")
        memo.append(f"**Proposed slot:** `{row.get('proposed_slot', a.get('proposed_slot', '?'))}`\n")
        memo.append(f"**License:** `{row.get('license', '?')}` · **Stars:** {row.get('stars', '?')} · **Last commit:** {row.get('last_commit_at', '?')}\n")
        memo.append(f"**Pinned commit at scan time:** `{a.get('commit_pinned', '?')[:12]}`\n")
        memo.append(f"\n## Why quarantined\n")
        memo.append(f"> {a.get('verdict_reason', '(none recorded)')}\n")
        memo.append(f"\n## What the repo claims to do\n")
        memo.append(f"{row.get('notes', row.get('description', '(no description)'))}\n")
        memo.append(f"\n## Detailed findings\n")
        if a["findings"]["secrets"]:
            memo.append(f"### Secrets ({len(a['findings']['secrets'])})\n")
            for s in a["findings"]["secrets"][:10]:
                memo.append(f"- `{s['file']}` — {s['label']} (prefix `{s['match_prefix']}`)")
        if a["findings"]["suspicious"]:
            memo.append(f"\n### Suspicious code ({len(a['findings']['suspicious'])})\n")
            for s in a["findings"]["suspicious"][:10]:
                memo.append(f"- `{s['file']}` — {s['label']}")
        if a["findings"]["install_hooks"]:
            memo.append(f"\n### Install hooks\n")
            for h in a["findings"]["install_hooks"]:
                if h.get("dangerous"):
                    memo.append(f"- `{h['file']}` — `{h['hook']}`: `{h['command']}`")
        memo.append(f"\n## Network endpoints found in source\n")
        for host in sorted((a['findings']['urls'] or {}).keys()):
            memo.append(f"- `{host}`")
        memo.append(f"\n## Audit log\n")
        memo.append(f"Full scan output: `_logs/scan/{owner_repo}/`\n")
        (q_dir / "MEMO.md").write_text("\n".join(memo), encoding="utf-8")
        n += 1
    print(f"wrote {n} quarantine memos to {QUARANTINE_BASE}")


if __name__ == "__main__":
    main()
