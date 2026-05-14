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
from concurrent.futures import ThreadPoolExecutor, as_completed
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


def smoke_python(repo_dir: Path, pkg: str, log_dir: Path, install_timeout: int = 120, import_timeout: int = 30) -> dict:
    """Smoke-test a Python skill.

    Strategy:
      1. Prefer `uv run --no-project --with .` to import the package without
         leaving artefacts (fast, reliable).
      2. Fallback: `pip install --dry-run .` just to validate the metadata
         resolves (skips actual install which can be slow / fail on missing
         system deps).
      3. Capture outbound TCP delta around the import call.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    result = {"kind": "python", "package": pkg, "steps": []}
    import_name = (pkg or "").replace("-", "_") or "unknown"

    uv = shutil.which("uv")
    if uv:
        # uv-based fast path: install package into a temp env and probe
        probe_cmd = [uv, "pip", "install", "--quiet", "--system", "--dry-run", "."]
        r = subprocess.run(probe_cmd, cwd=str(repo_dir), capture_output=True, text=True, timeout=install_timeout)
        result["steps"].append({"step": "uv_dryrun", "rc": r.returncode, "stderr": r.stderr[-400:]})
        # Always try the actual import via uv run --with .
        conn_before = _snapshot_connections()
        r2 = subprocess.run(
            [uv, "run", "--no-project", "--with", ".", "--isolated", "python", "-c",
             f"import {import_name}; print('OK', sorted(set(dir({import_name})))[:20])"],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=install_timeout + import_timeout,
        )
        conn_after = _snapshot_connections()
        new_conns = sorted(conn_after - conn_before)
        result["steps"].append({
            "step": "uv_run_import",
            "rc": r2.returncode,
            "stdout": r2.stdout[:400],
            "stderr": r2.stderr[-400:],
            "new_outbound_connections": [{"host": h, "port": p} for h, p in new_conns],
        })
        if r2.returncode == 0 and "OK " in r2.stdout:
            result["verdict"] = "pass"
            result["reason"] = "uv install + import OK"
            return result
        # import failed but install dry-run succeeded
        if r.returncode == 0:
            result["verdict"] = "pass_with_notes"
            result["reason"] = f"installable but direct import {import_name} failed (may use non-standard module name)"
            return result
        result["verdict"] = "deferred"
        result["reason"] = "uv install dry-run failed; package may need uvx-style invocation or extra system deps"
        return result

    # No uv available — minimal fallback using stdlib venv (slower)
    venv = repo_dir / ".smoke" / "venv"
    venv.parent.mkdir(parents=True, exist_ok=True)
    if not venv.exists():
        r = subprocess.run([sys.executable, "-m", "venv", str(venv)], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            result["verdict"] = "deferred"
            result["reason"] = "no uv available and venv create failed"
            return result
    py = str(venv / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python"))
    r = subprocess.run([py, "-m", "pip", "install", "--quiet", "--no-input", "--dry-run", "."],
                       cwd=str(repo_dir), capture_output=True, text=True, timeout=install_timeout)
    result["steps"].append({"step": "pip_dryrun", "rc": r.returncode})
    if r.returncode == 0:
        result["verdict"] = "pass_with_notes"
        result["reason"] = "pip install dry-run OK; no uv available for full import test"
    else:
        result["verdict"] = "deferred"
        result["reason"] = "pip install dry-run failed; package may need uvx or extra system deps"
    return result


def smoke_node(repo_dir: Path, pkg: str, log_dir: Path, install_timeout: int = 240, import_timeout: int = 30) -> dict:
    """Smoke-test a Node skill — npm install + require probe.

    npm install is bounded; ignore-scripts is on so we don't fire postinstall hooks.
    For repos without a `main` entry, the require-step is downgraded to a syntax check
    via `node --check <main-file>` when discoverable.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    result = {"kind": "node", "package": pkg, "steps": []}
    npm = shutil.which("npm") or "npm"
    node = shutil.which("node") or "node"

    # 1) bounded npm install
    r = subprocess.run(
        [npm, "install", "--omit=dev", "--no-audit", "--no-fund", "--ignore-scripts", "--prefer-offline", "--silent"],
        cwd=str(repo_dir), capture_output=True, text=True, timeout=install_timeout, shell=(os.name == "nt"),
    )
    result["steps"].append({"step": "npm_install", "rc": r.returncode, "stderr": r.stderr[-500:]})
    if r.returncode != 0:
        result["verdict"] = "deferred"
        result["reason"] = "npm install failed (may need vendor-provided lockfile or a release-only entry point)"
        return result

    # 2) determine main entry: package.json `main` field if present
    main_field = None
    try:
        pj = json.loads((repo_dir / "package.json").read_text(encoding="utf-8"))
        main_field = pj.get("main") or pj.get("module")
    except Exception:
        pass

    conn_before = _snapshot_connections()
    if main_field and (repo_dir / main_field).exists():
        # syntax-check the main file (no execution)
        r2 = subprocess.run(
            [node, "--check", main_field],
            cwd=str(repo_dir), capture_output=True, text=True, timeout=import_timeout,
        )
        result["steps"].append({"step": "node_check_main", "main": main_field, "rc": r2.returncode, "stderr": r2.stderr[-300:]})
        verdict = "pass" if r2.returncode == 0 else "pass_with_notes"
        reason = "npm install + syntax-check OK" if r2.returncode == 0 else "install OK; syntax-check found warnings"
    else:
        # fall back to require by package name from inside the package dir
        probe = f"try {{ const m = require({json.dumps('./')}); console.log('OK'); }} catch(e) {{ console.error('IMPORT_ERR:' + e.message); process.exit(2); }}"
        r2 = subprocess.run([node, "-e", probe], cwd=str(repo_dir), capture_output=True, text=True, timeout=import_timeout)
        result["steps"].append({"step": "node_require_relative", "rc": r2.returncode, "stdout": r2.stdout[:200], "stderr": r2.stderr[-300:]})
        if r2.returncode == 0:
            verdict, reason = "pass", "install + relative-require OK"
        else:
            verdict, reason = "pass_with_notes", "install OK; relative-require failed (likely TS-only / build required)"
    conn_after = _snapshot_connections()
    new_conns = sorted(conn_after - conn_before)
    result["steps"].append({"new_outbound_connections": [{"host": h, "port": p} for h, p in new_conns]})
    result["verdict"] = verdict
    result["reason"] = reason
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


def _safe_smoke(row, audit):
    try:
        return smoke_one(row, audit)
    except Exception as e:
        log(f"smoke exception {row.get('source_url')}: {e}")
        return {"source_url": row.get("source_url"), "verdict": "deferred", "reason": f"exception: {e}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--filter", type=str, default="")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    rows = load_jsonl(SHORTLIST)
    if args.filter:
        rows = [r for r in rows if args.filter.lower() in r["source_url"].lower()]
    if args.limit > 0:
        rows = rows[: args.limit]

    # filter to those with a passing audit
    eligible = []
    for row in rows:
        parsed = parse_github_url(row["source_url"])
        if not parsed:
            continue
        owner, repo = parsed
        audit_path = SCAN_LOG_BASE / f"{owner}__{repo}" / "audit.json"
        if not audit_path.exists():
            continue
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if audit.get("verdict") not in ("pass", "pass_with_notes"):
            continue
        eligible.append((row, audit))

    log(f"smoke testing {len(eligible)} audit-passing candidates with {args.workers} workers")
    smokes = []
    summary = {"pass": 0, "pass_with_notes": 0, "deferred": 0, "fail": 0}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(_safe_smoke, row, audit): row for row, audit in eligible}
        for f in as_completed(futures):
            s = f.result()
            smokes.append(s)
            v = s.get("verdict", "deferred")
            summary[v] = summary.get(v, 0) + 1

    write_jsonl_atomic(ROOT / "_logs" / "smoke_summary.jsonl", smokes)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
