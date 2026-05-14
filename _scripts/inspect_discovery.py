"""Quick inspector for discovery.jsonl — categorize rows that need attention."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT

rows = []
for line in (ROOT / "_candidates_raw" / "discovery.jsonl").read_text(encoding="utf-8").splitlines():
    if line.strip():
        rows.append(json.loads(line))

print(f"=== TOTAL: {len(rows)} ===\n")

print("=== MISSING (need source corrections) ===")
for r in rows:
    if not r["exists"]:
        print(f"  {r['source_url']}  -> {r['error']}")

print("\n=== ARCHIVED ===")
arch = [r for r in rows if r["exists"] and r["archived"]]
for r in arch:
    print(f"  {r['source_url']}")
print(f"  (count: {len(arch)})")

print("\n=== NOASSERTION license ===")
for r in rows:
    if r.get("license") == "NOASSERTION":
        print(f"  {r['source_url']}  | stars={r['stars']} | last={r['last_commit_at']}")

print("\n=== empty license ===")
for r in rows:
    if r["exists"] and not r.get("license"):
        print(f"  {r['source_url']}  | stars={r['stars']} | last={r['last_commit_at']}")

print("\n=== GPL-family ===")
for r in rows:
    if "GPL" in (r.get("license") or ""):
        print(f"  {r['source_url']}  ({r['license']})  stars={r['stars']}")

# license distribution
print("\n=== LICENSE DISTRIBUTION ===")
from collections import Counter
c = Counter(r.get("license") or "(none)" for r in rows if r["exists"])
for lic, n in c.most_common():
    print(f"  {lic}: {n}")
