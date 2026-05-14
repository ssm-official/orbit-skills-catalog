"""cli_crawl_aggregators.py — extract GitHub-repo URLs from MCP awesome-lists.

For each aggregator README, fetch the raw markdown, regex-extract every
github.com/owner/repo URL, dedupe, and append to _candidates_raw/discovered_from_aggregators.jsonl
as unverified rows. cli_verify.py with --extra will then verify them.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT, log, cached_fetch, write_jsonl_atomic, load_jsonl, parse_github_url

AGGREGATORS = [
    "https://raw.githubusercontent.com/punkpeye/awesome-mcp-servers/main/README.md",
    "https://raw.githubusercontent.com/wong2/awesome-mcp-servers/main/README.md",
    "https://raw.githubusercontent.com/appcypher/awesome-mcp-servers/main/README.md",
    "https://raw.githubusercontent.com/TensorBlock/awesome-mcp-servers/main/README.md",
    "https://raw.githubusercontent.com/tolkonepiu/best-of-mcp-servers/main/README.md",
]

OUT = ROOT / "_candidates_raw" / "discovered_from_aggregators.jsonl"
REPO_RE = re.compile(r"github\.com/([\w.-]+)/([\w.-]+?)(?=[)\s/#\"'>]|\.git|$)", re.IGNORECASE)

SKIP_OWNERS = {
    "modelcontextprotocol", "anthropics",
    "sponsors", "github", "raw", "user-images",
}


def main():
    seen: dict[str, dict] = {}
    for agg_url in AGGREGATORS:
        body = cached_fetch(agg_url, namespace="agg", ttl_hours=24)
        if not body:
            log(f"skip agg (no body): {agg_url}")
            continue
        for m in REPO_RE.finditer(body):
            owner = m.group(1)
            repo = m.group(2).rstrip(".")
            if owner in SKIP_OWNERS:
                continue
            url = f"https://github.com/{owner}/{repo}"
            key = url.lower()
            if key not in seen:
                seen[key] = {
                    "source_url": url,
                    "kind": "mcp_server",
                    "proposed_slot": "_uncategorized.from_aggregator",
                    "track_hint": "",
                    "notes": f"discovered_from:{agg_url.split('/')[3]}",
                }
    out_rows = list(seen.values())
    write_jsonl_atomic(OUT, out_rows)
    log(f"aggregator crawl: {len(out_rows)} unique candidates -> {OUT}")
    print(json.dumps({"unique_candidates": len(out_rows), "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
