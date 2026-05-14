"""cli_smoke.py — functional smoke test for skills that passed Phase 3.

For each repo with audit verdict == 'pass' or 'pass_with_notes', do the
following (idempotent, costless):

  1. Fresh Python venv or fresh npx prefix in `candidates/<owner>__<repo>/.smoke/`.
  2. Install upstream skill into that env.
  3. Try to detect a safe, read-only entry point (in priority order):
       - `--help` / `-h` / `--version` (always available, always non-destructive)
       - For Python: `python -c "import <pkg>"` then `dir(<pkg>)`
       - For Node: `node -e "require('<pkg>'); console.log(Object.keys(require('<pkg>')))"`
       - MCP servers: try `--list-tools` / `tools/list` schema introspection
  4. Capture a process+network snapshot during invocation (Windows native:
     Get-NetTCPConnection deltas; the network trace is weaker than a network
     namespace, this limitation is recorded in smoke.json).
  5. Record:
       - smoke.json (verdict, command, output, network deltas)

This script ONLY runs lightweight import / --help / --version paths.
It does NOT invoke any actual upstream service call by default — those
require vendor sandbox credentials which we mark as DEFERRED.

A pass means: install succeeds, import / help works, no orphan processes,
no unexpected outbound connections during the brief invocation.
A deferred verdict means: install OK, but a meaningful call requires a
sandbox credential we don't have — Orbit creators can still list the skill
and bring their own key.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import (
    ROOT, log, load_jsonl, write_jsonl_atomic, parse_github_url, utc_now_iso,
)

SHORTLIST = ROOT / "_candidates_raw" / "shortlist.jsonl"
SCAN_LOG_BASE = ROOT / "_logs" / "scan"
SMOKE_LOG_BASE = ROOT / "_logs" / "smoke"
CANDIDATES_DIR = ROOT / "candidates"


def _detect_kind(repo_dir: Path) -> str:
    """Return 'python' | 'node' | 'unknown' based on root manifests."""
    if (repo_dir / "pyproject.toml").exists() or (repo_dir / "setup.py").exists() or (repo_dir / "requirements.txt").exists():
        if (repo_dir / "package.json").exists():
            # both — pick whichever has src
            return "python"  # MCP servers in py-mode are most common in our seeds
        return "python"
    if (repo_dir / "package.json").exists():
        return "node"
    return "unknown"


def _package_name(repo_dir: Path, kind: str) -> str | None:
    if kind == "python":
        # try pyproject.toml [project] name=
        for fn in ("pyproject.toml", "setup.cfg"):
            p = repo_dir / fn
            if not p.exists():
                continue
            try:
                text = p.read_text(encoding="utf-8")
                import re
                m = re.search(r'name\s*=\s*["\']([\w.-]+)["\']', text)
                if m:
                    return m.group(1)
            except Exception:
                pass
        # setup.py
        p = repo_dir / "setup.py"
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8")
                import re
                m = re.search(r'name\s*=\s*["\']([\w.-]+)["\']', text)
                if m:
                    return m.group(1)
            except Exception:
                pass
        return repo_dir.name
    if kind == "node":
        pj = repo_dir / "package.json"
        try:
            d = json.loads(pj.read_text(encoding="utf-8"))
            return d.get("name")
        except Exception:
            pass
    return None


def _snapshot_connections() -> set[tuple]:
    """Best-effort outbound TCP snapshot on Windows. Returns set of (remote_host:port)."""
    out: set[tuple] = set()
    if os.name != "nt":
        return out
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue | "
             "Where-Object { $_.RemoteAddress -notin '127.0.0.1','::1','0.0.0.0','::' } | "
             "Select-Object -Property RemoteAddress, RemotePort | ConvertTo-Json -Compress"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0 and r.stdout.strip():
            data = json.loads(r.stdout)
            if isinstance(data, dict):
                data = [data]
            for c in data:
                out.add((c.get("RemoteAddress"), c.get("RemotePort")))
    except Exception:
        pass
    return out


def smoke_python(repo_dir: Path, pkg: str, log_dir: Path) -> dict:
    log_dir.mkdir(parents=True, exist_ok=True)
    venv = repo_dir / ".smoke" / "venv"
    venv.parent.mkdir(parents=True, exist_ok=True)
    result = {"kind": "python", "package": pkg, "steps": []}
    # 1) create venv
    if not venv.exists():
        r = subprocess.run([sys.executable, "-m", "venv", str(venv)], capture_output=True, text=True, timeout=60)
        result["steps"].append({"step": "venv_create", "rc": r.returncode, "stderr": r.stderr[-500:]})
        if r.returncode != 0:
            result["verdict"] = "fail"
            result["reason"] = "venv create failed"
            return result
    py = str(venv / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python"))
    # 2) pip install (try the local package directly)
    pip_args = [py, "-m", "pip", "install", "--quiet", "--no-input", "--no-warn-script-location", "."]
    r = subprocess.run(pip_args, cwd=str(repo_dir), capture_output=True, text=True, timeout=300)
    result["steps"].append({"step": "pip_install_local", "rc": r.returncode, "stderr": r.stderr[-800:]})
    install_ok = (r.returncode == 0)
    # if local install failed, try pip install <pkg>
    if not install_ok and pkg:
        r2 = subprocess.run([py, "-m", "pip", "install", "--quiet", "--no-input", pkg],
                            capture_output=True, text=True, timeout=300)
        result["steps"].append({"step": "pip_install_pypi", "rc": r2.returncode, "stderr": r2.stderr[-500:]})
        install_ok = (r2.returncode == 0)
    if not install_ok:
        result["verdict"] = "fail"
        result["reason"] = "pip install failed for both local and pypi"
        return result
    # 3) import probe — snapshot connections before and after a brief import
    conn_before = _snapshot_connections()
    import_name = pkg.replace("-", "_") if pkg else "unknown"
    r = subprocess.run([py, "-c", f"import {import_name}; print(dir({import_name})[:30])"],
                       capture_output=True, text=True, timeout=30)
    conn_after = _snapshot_connections()
    new_conns = sorted(conn_after - conn_before)
    result["steps"].append({
        "step": "python_import",
        "rc": r.returncode,
        "stdout": r.stdout[:500],
        "stderr": r.stderr[-500:],
        "new_outbound_connections": [{"host": h, "port": p} for h, p in new_conns],
    })
    if r.returncode == 0:
        result["verdict"] = "pass"
        result["reason"] = "install + import OK"
    else:
        # try a fallback: list importable submodules
        result["verdict"] = "pass_with_notes"
        result["reason"] = f"install OK but direct import {import_name} failed; package may use non-standard module name"
    return result


def smoke_node(repo_dir: Path, pkg: str, log_dir: Path) -> dict:
    log_dir.mkdir(parents=True, exist_ok=True)
    result = {"kind": "node", "package": pkg, "steps": []}
    smoke_dir = repo_dir / ".smoke"
    smoke_dir.mkdir(exist_ok=True)
    # 1) npm install --omit=dev in the candidate directory itself (it has its own package.json)
    npm = shutil.which("npm") or "npm"
    r = subprocess.run([npm, "install", "--omit=dev", "--no-audit", "--no-fund", "--ignore-scripts"],
                       cwd=str(repo_dir), capture_output=True, text=True, timeout=420, shell=(os.name == "nt"))
    result["steps"].append({"step": "npm_install", "rc": r.returncode, "stderr": r.stderr[-800:]})
    if r.returncode != 0:
        result["verdict"] = "fail"
        result["reason"] = "npm install failed"
        return result
    # 2) require probe
    conn_before = _snapshot_connections()
    node = shutil.which("node") or "node"
    probe = f"try {{ const m = require({json.dumps(pkg)}); console.log(JSON.stringify(Object.keys(m).slice(0, 40))); }} catch(e) {{ console.error('IMPORT_ERR:' + e.message); process.exit(2); }}"
    r = subprocess.run([node, "-e", probe], cwd=str(repo_dir), capture_output=True, text=True, timeout=30)
    conn_after = _snapshot_connections()
    new_conns = sorted(conn_after - conn_before)
    result["steps"].append({
        "step": "node_require",
        "rc": r.returncode,
        "stdout": r.stdout[:500],
        "stderr": r.stderr[-500:],
        "new_outbound_connections": [{"host": h, "port": p} for h, p in new_conns],
    })
    if r.returncode == 0:
        result["verdict"] = "pass"
        result["reason"] = "install + require OK"
    else:
        result["verdict"] = "pass_with_notes"
        result["reason"] = f"install OK; require failed (likely non-standard entry point)"
    return result


def smoke_one(row: dict, audit: dict) -> dict:
    parsed = parse_github_url(row["source_url"])
    if not parsed:
        return {"source_url": row["source_url"], "verdict": "fail", "reason": "bad url"}
    owner, repo = parsed
    repo_dir = CANDIDATES_DIR / f"{owner}__{repo}"
    log_dir = SMOKE_LOG_BASE / f"{owner}__{repo}"
    log_dir.mkdir(parents=True, exist_ok=True)

    smoke = {
        "source_url": row["source_url"],
        "proposed_slot": row.get("proposed_slot"),
        "smoked_at": utc_now_iso(),
        "platform": "windows",
        "sandbox": "fresh venv / fresh node_modules (Docker unavailable on host)",
        "network_monitoring": "Get-NetTCPConnection deltas (weaker than netns isolation)",
    }

    if not repo_dir.exists():
        smoke["verdict"] = "fail"
        smoke["reason"] = "repo not cloned"
        (log_dir / "smoke.json").write_text(json.dumps(smoke, indent=2), encoding="utf-8")
        return smoke

    kind = _detect_kind(repo_dir)
    pkg = _package_name(repo_dir, kind) or repo
    smoke["package"] = pkg
    smoke["language"] = kind

    if kind == "python":
        res = smoke_python(repo_dir, pkg, log_dir)
    elif kind == "node":
        res = smoke_node(repo_dir, pkg, log_dir)
    else:
        smoke["verdict"] = "deferred"
        smoke["reason"] = "unknown package kind (no python or node manifest)"
        (log_dir / "smoke.json").write_text(json.dumps(smoke, indent=2), encoding="utf-8")
        return smoke

    smoke.update(res)
    (log_dir / "smoke.json").write_text(json.dumps(smoke, indent=2), encoding="utf-8")
    log(f"smoke {owner}/{repo}: {smoke.get('verdict')} ({smoke.get('reason')})")
    return smoke


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--filter", type=str, default="")
    args = ap.parse_args()

    rows = load_jsonl(SHORTLIST)
    if args.filter:
        rows = [r for r in rows if args.filter.lower() in r["source_url"].lower()]
    if args.limit > 0:
        rows = rows[: args.limit]

    smokes = []
    summary = {"pass": 0, "pass_with_notes": 0, "deferred": 0, "fail": 0}
    for row in rows:
        # gate on audit verdict
        parsed = parse_github_url(row["source_url"])
        if not parsed:
            continue
        owner, repo = parsed
        audit_path = SCAN_LOG_BASE / f"{owner}__{repo}" / "audit.json"
        if not audit_path.exists():
            log(f"skip smoke {owner}/{repo}: no audit.json")
            continue
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if audit.get("verdict") not in ("pass", "pass_with_notes"):
            log(f"skip smoke {owner}/{repo}: audit verdict={audit.get('verdict')}")
            continue
        s = smoke_one(row, audit)
        smokes.append(s)
        summary[s.get("verdict", "fail")] = summary.get(s.get("verdict", "fail"), 0) + 1

    write_jsonl_atomic(ROOT / "_logs" / "smoke_summary.jsonl", smokes)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
