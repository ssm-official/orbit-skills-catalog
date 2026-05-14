"""cli_verify.py — verify the seed list and any additional candidate URLs.

Reads candidates from:
  - _scripts/seeds.py (SEEDS constant)
  - --extra <jsonl path> (optional; rows with at least source_url)

Writes verified rows (with stars/license/last_commit/etc) to:
  _candidates_raw/discovery.jsonl

Verification is via GitHub API (cached). Failures are kept with error=<reason>
so phase 2 can drop them.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT, Candidate, log, verify_repo, write_jsonl_atomic, load_jsonl
from seeds import SEEDS

OUT = ROOT / "_candidates_raw" / "discovery.jsonl"


def verify_one(seed_row: tuple) -> dict:
    url, kind, slot, track, notes = seed_row
    meta = verify_repo(url)
    c = Candidate(
        source_url=url,
        kind=kind,
        proposed_slot=slot,
        track_hint=track,
        discovered_via="seed_list",
        notes=notes,
        exists=meta.exists,
        archived=meta.archived,
        stars=meta.stars,
        license=meta.license,
        last_commit_at=meta.last_commit_at,
        primary_language=meta.primary_language,
        description=meta.description,
        error=meta.error,
    )
    log(f"verify {url} -> exists={meta.exists} stars={meta.stars} license={meta.license} last={meta.last_commit_at} err={meta.error}")
    return asdict(c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", type=str, default=None, help="optional JSONL of extra candidates (objects with source_url)")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    rows = list(SEEDS)
    if args.extra:
        extra = load_jsonl(Path(args.extra))
        for e in extra:
            rows.append((
                e["source_url"],
                e.get("kind", "unknown"),
                e.get("proposed_slot", ""),
                e.get("track_hint", ""),
                e.get("notes", "extra"),
            ))

    log(f"verifying {len(rows)} candidates with {args.workers} workers")
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(verify_one, r): r for r in rows}
        for f in as_completed(futures):
            results.append(f.result())

    # dedupe by source_url
    by_url = {}
    for r in results:
        by_url[r["source_url"].rstrip("/").lower()] = r
    dedup = list(by_url.values())

    write_jsonl_atomic(OUT, dedup)
    n_ok = sum(1 for r in dedup if r["exists"])
    n_archived = sum(1 for r in dedup if r["exists"] and r["archived"])
    log(f"wrote {len(dedup)} rows to {OUT} ({n_ok} verified, {n_archived} archived)")
    print(json.dumps({
        "total": len(dedup),
        "verified": n_ok,
        "archived": n_archived,
        "missing": len(dedup) - n_ok,
        "out": str(OUT),
    }, indent=2))


if __name__ == "__main__":
    main()
