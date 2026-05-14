"""Build a v1.0-focus shortlist from the §5 hand-curated seeds only.

Aggregator augments are deferred to v1.1 — they're real candidates but
need more curatorial attention before being safe to vet en masse.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT, load_jsonl, write_jsonl_atomic
from seeds import SEEDS

# Seed-supplied URLs (the curated §5 list)
seed_urls = {s[0].lower() for s in SEEDS}
# Supplemental seed URLs
supp = load_jsonl(ROOT / "_candidates_raw" / "supplemental_seeds.jsonl")
seed_urls |= {s["source_url"].lower() for s in supp}

shortlist = load_jsonl(ROOT / "_candidates_raw" / "shortlist.jsonl")
focused = [r for r in shortlist if r["source_url"].lower() in seed_urls]

write_jsonl_atomic(ROOT / "_candidates_raw" / "shortlist.jsonl", focused)
print(json.dumps({"focused_count": len(focused), "from": len(shortlist)}, indent=2))
