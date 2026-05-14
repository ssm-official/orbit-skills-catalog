"""cli_scan.py — clone shortlisted repos shallowly and run static scans.

For each shortlisted row, do all of the following and persist to
_logs/scan/<owner>__<repo>/:

  - clone shallow into candidates/<owner>__<repo>/
  - native python pattern scan (secrets, suspicious code, URL inventory)
  - npm install-hook audit (if package.json)
  - python setup.py / pyproject hook audit
  - external scanners if installed on PATH:
      * gitleaks
      * trufflehog
      * osv-scanner
      * semgrep --config=auto
  - record audit.json with a preliminary verdict

The preliminary verdict is one of:
    pass | pass_with_notes | quarantine

Quarantine is reserved for §3.1 automatic-reject hits (hardcoded secrets,
dangerous install hooks, miner strings, etc). Pass_with_notes covers the
yellow-flag category. Pass means no findings of concern.

This script DOES NOT run code from the cloned repos. It only reads files.
The behavioral check (§3.4) is a separate phase.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import (
    ROOT, log, load_jsonl, write_jsonl_atomic, clone_shallow, pinned_commit,
    scan_tree_for_patterns, scan_package_json_install_hooks, scan_pyproject_hooks,
    parse_github_url, utc_now_iso,
)

SHORTLIST = ROOT / "_candidates_raw" / "shortlist.jsonl"
CANDIDATES_DIR = ROOT / "candidates"
SCAN_LOG_BASE = ROOT / "_logs" / "scan"


def _tool_available(name: str) -> bool:
    return shutil.which(name) is not None


def _run_tool(cmd: list[str], cwd: Path, output_file: Path, timeout: int = 240) -> dict:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        output_file.write_text(r.stdout if r.stdout else r.stderr, encoding="utf-8", errors="replace")
        return {"command": " ".join(cmd), "exit_code": r.returncode, "output_path": str(output_file.relative_to(ROOT)).replace("\\", "/")}
    except subprocess.TimeoutExpired:
        return {"command": " ".join(cmd), "exit_code": -1, "output_path": None, "error": "timeout"}
    except Exception as e:
        return {"command": " ".join(cmd), "exit_code": -1, "output_path": None, "error": str(e)}


def scan_one(row: dict) -> dict:
    parsed = parse_github_url(row["source_url"])
    if not parsed:
        return {"source_url": row["source_url"], "error": "not a github url"}
    owner, repo = parsed
    repo_dir = CANDIDATES_DIR / f"{owner}__{repo}"
    log_dir = SCAN_LOG_BASE / f"{owner}__{repo}"
    log_dir.mkdir(parents=True, exist_ok=True)

    audit = {
        "source_url": row["source_url"],
        "proposed_slot": row.get("proposed_slot", ""),
        "scanned_at": utc_now_iso(),
        "clone_ok": False,
        "commit_pinned": "",
        "scanners_run": [],
        "findings": {
            "secrets": [],
            "suspicious": [],
            "install_hooks": [],
            "py_build_hooks": [],
            "urls_found": {},
        },
        "external_scanners": {},
        "verdict": "needs_review",
        "verdict_reason": "",
    }

    # clone
    ok = clone_shallow(row["source_url"], repo_dir)
    if not ok or not repo_dir.exists():
        audit["verdict"] = "drop"
        audit["verdict_reason"] = "clone failed"
        (log_dir / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        return audit
    audit["clone_ok"] = True
    audit["commit_pinned"] = pinned_commit(repo_dir)

    # native pattern scan
    audit["scanners_run"].append("orbit_pattern_scan")
    fp = scan_tree_for_patterns(repo_dir)
    audit["findings"]["secrets"] = fp["secrets"][:50]
    audit["findings"]["suspicious"] = fp["suspicious"][:100]
    audit["findings"]["urls_found"] = fp["urls"]
    audit["files_scanned"] = fp["files_scanned"]
    audit["files_skipped"] = fp["files_skipped"]

    # install hooks
    audit["scanners_run"].append("install_hook_audit")
    audit["findings"]["install_hooks"] = scan_package_json_install_hooks(repo_dir)
    audit["findings"]["py_build_hooks"] = scan_pyproject_hooks(repo_dir)

    # external scanners
    if _tool_available("gitleaks"):
        audit["scanners_run"].append("gitleaks")
        audit["external_scanners"]["gitleaks"] = _run_tool(
            ["gitleaks", "detect", "--no-banner", "--no-git", "--source", ".", "--report-format", "json", "--report-path", str(log_dir / "gitleaks.json")],
            cwd=repo_dir, output_file=log_dir / "gitleaks.stdout.txt", timeout=120,
        )
    if _tool_available("trufflehog"):
        audit["scanners_run"].append("trufflehog")
        audit["external_scanners"]["trufflehog"] = _run_tool(
            ["trufflehog", "filesystem", ".", "--json", "--no-update", "--fail"],
            cwd=repo_dir, output_file=log_dir / "trufflehog.json", timeout=180,
        )
    if _tool_available("osv-scanner"):
        audit["scanners_run"].append("osv-scanner")
        audit["external_scanners"]["osv"] = _run_tool(
            ["osv-scanner", "--recursive", "--format=json", "."],
            cwd=repo_dir, output_file=log_dir / "osv.json", timeout=180,
        )
    if _tool_available("semgrep"):
        audit["scanners_run"].append("semgrep")
        audit["external_scanners"]["semgrep"] = _run_tool(
            ["semgrep", "--config=auto", "--json", "--output", str(log_dir / "semgrep.json"), "."],
            cwd=repo_dir, output_file=log_dir / "semgrep.stdout.txt", timeout=300,
        )

    # pip-audit (Python deps) — invoke as module since user-installed scripts dir may not be on PATH
    if any(p.exists() for p in [repo_dir / "requirements.txt", repo_dir / "pyproject.toml", repo_dir / "setup.py"]):
        try:
            r = subprocess.run([sys.executable, "-m", "pip_audit", "--format=json", "--strict", "."],
                               cwd=str(repo_dir), capture_output=True, text=True, timeout=180)
            (log_dir / "pip-audit.json").write_text(r.stdout or "[]", encoding="utf-8")
            audit["scanners_run"].append("pip-audit")
            audit["external_scanners"]["pip_audit"] = {
                "exit_code": r.returncode,
                "output_path": f"_logs/scan/{owner}__{repo}/pip-audit.json",
            }
        except Exception as e:
            audit["external_scanners"]["pip_audit"] = {"error": str(e)}

    # ---- verdict logic ----
    # Tests / fixtures / examples often legitimately include placeholder secrets
    # (Stripe sk_test_*, example keys in `.env.example`, etc.). A finding inside
    # these paths is documented as a note, not an automatic quarantine.
    def _is_test_path(rel: str) -> bool:
        rl = rel.lower().replace("\\", "/")
        markers = ("/test/", "/tests/", "/__tests__/", "/spec/", "/specs/",
                   "/fixtures/", "/fixture/", "/__fixtures__/", "/mocks/", "/mock/",
                   ".example", ".sample", ".test.", ".spec.", "/example/", "/examples/",
                   "/docs/", "/doc/", "/.github/")
        return any(m in rl for m in markers) or rl.endswith(".example") or rl.endswith(".sample")

    def _is_test_only_secret(label: str, prefix: str) -> bool:
        # Stripe test keys are intentionally public.
        if label == "stripe test key":
            return True
        if "_test_" in prefix.lower() or prefix.lower().startswith("sk_test_"):
            return True
        return False

    reject_reasons = []
    notes_reasons = []

    # secrets — split into real vs test-path findings
    real_secret_hits = []
    test_secret_hits = []
    for s in audit["findings"]["secrets"]:
        if _is_test_path(s["file"]) or _is_test_only_secret(s.get("label", ""), s.get("match_prefix", "")):
            test_secret_hits.append(s)
        else:
            real_secret_hits.append(s)
    if real_secret_hits:
        reject_reasons.append(f"hardcoded secrets in non-test paths ({len(real_secret_hits)} hits, e.g. {real_secret_hits[0]['file']})")
    if test_secret_hits:
        notes_reasons.append(f"test-path secret findings ({len(test_secret_hits)})")

    # dangerous install hooks
    for h in audit["findings"]["install_hooks"]:
        if h.get("dangerous"):
            reject_reasons.append(f"dangerous {h['hook']} hook in {h['file']}")
    for h in audit["findings"]["py_build_hooks"]:
        reject_reasons.append(f"python build hook issue: {h['issue']} in {h['file']}")

    # miner / self-update / io-snooping in source (we already filter out
    # markdown/yaml/.github paths upstream — any hit here is real)
    auto_reject_labels = {"miner-string", "self-update", "io-snooping"}
    for s in audit["findings"]["suspicious"]:
        if s["label"] in auto_reject_labels:
            reject_reasons.append(f"suspicious code: {s['label']} in {s['file']}")
        else:
            notes_reasons.append(f"{s['label']} in {s['file']}")

    # gitleaks: parse output; ignore findings in test paths
    gitleaks_path = log_dir / "gitleaks.json"
    gitleaks_real = 0
    gitleaks_test = 0
    if gitleaks_path.exists():
        try:
            gl = json.loads(gitleaks_path.read_text(encoding="utf-8"))
            if isinstance(gl, list):
                for finding in gl:
                    f = (finding.get("File") or finding.get("file") or "")
                    if _is_test_path(f):
                        gitleaks_test += 1
                    else:
                        gitleaks_real += 1
        except Exception:
            pass
    if gitleaks_real:
        reject_reasons.append(f"gitleaks: {gitleaks_real} non-test secret(s)")
    if gitleaks_test:
        notes_reasons.append(f"gitleaks: {gitleaks_test} test-path secret(s)")

    if reject_reasons:
        audit["verdict"] = "quarantine"
        audit["verdict_reason"] = "; ".join(reject_reasons)
    elif notes_reasons or audit["findings"]["install_hooks"]:
        audit["verdict"] = "pass_with_notes"
        audit["verdict_reason"] = "; ".join(notes_reasons) or f"{len(audit['findings']['install_hooks'])} install hooks documented"
    else:
        audit["verdict"] = "pass"
        audit["verdict_reason"] = "no findings of concern in static scan"

    (log_dir / "audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    log(f"scan {owner}/{repo}: verdict={audit['verdict']} ({audit['verdict_reason']})")
    return audit


def _safe_scan(row):
    try:
        return scan_one(row)
    except Exception as e:
        log(f"scan exception {row.get('source_url')}: {e}")
        return {"source_url": row.get("source_url"), "verdict": "errors", "error": str(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="limit number of repos to scan (0 = all)")
    ap.add_argument("--filter", type=str, default="", help="only process rows whose source_url contains this substring")
    ap.add_argument("--workers", type=int, default=4, help="parallel clone+scan workers")
    ap.add_argument("--skip-existing", action="store_true", help="skip repos that already have an audit.json")
    args = ap.parse_args()

    rows = load_jsonl(SHORTLIST)
    if args.filter:
        rows = [r for r in rows if args.filter.lower() in r["source_url"].lower()]
    if args.skip_existing:
        from orbit_pipeline import parse_github_url as _pg
        kept = []
        for r in rows:
            p = _pg(r["source_url"])
            if not p:
                continue
            owner, repo = p
            if not (SCAN_LOG_BASE / f"{owner}__{repo}" / "audit.json").exists():
                kept.append(r)
        rows = kept
    if args.limit > 0:
        rows = rows[: args.limit]

    log(f"scanning {len(rows)} shortlisted repos with {args.workers} workers")
    summary = {"pass": 0, "pass_with_notes": 0, "quarantine": 0, "drop": 0, "errors": 0}
    audits = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(_safe_scan, row): row for row in rows}
        for f in as_completed(futures):
            a = f.result()
            audits.append(a)
            v = a.get("verdict", "errors")
            summary[v] = summary.get(v, 0) + 1

    summary_path = ROOT / "_logs" / "scan_summary.jsonl"
    write_jsonl_atomic(summary_path, audits)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
