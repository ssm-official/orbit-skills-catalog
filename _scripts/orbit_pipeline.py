"""Core utilities for the Orbit Skills Catalog pipeline.

Cross-platform (Python 3.9+). Uses only stdlib + optional gh CLI / git CLI.
Network calls go through a cache so reruns are free.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "_cache"
LOG_DIR = ROOT / "_logs"
RUN_LOG = LOG_DIR / "run" / "run.log"

# Auto-prepend bundled scanner binaries to PATH (gitleaks, osv-scanner live in _tools/)
_TOOLS_DIR = ROOT / "_tools"
if _TOOLS_DIR.exists():
    _path_sep = ";" if os.name == "nt" else ":"
    if str(_TOOLS_DIR) not in os.environ.get("PATH", ""):
        os.environ["PATH"] = str(_TOOLS_DIR) + _path_sep + os.environ.get("PATH", "")


# ---------- logging ----------

def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    """Append a line to the central run log and stderr."""
    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"[{_ts()}] {msg}\n"
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    sys.stderr.write(line)
    sys.stderr.flush()


# ---------- caching ----------

def _cache_key(url: str, namespace: str) -> Path:
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    day = datetime.utcnow().strftime("%Y%m%d")
    return CACHE_DIR / namespace / day / f"{h}.json"


def cached_fetch(url: str, namespace: str = "http", headers: Optional[dict] = None, ttl_hours: int = 24) -> Optional[str]:
    """HTTP GET with on-disk day-bucketed cache. Returns text or None on error."""
    key = _cache_key(url, namespace)
    if key.exists():
        age_hours = (time.time() - key.stat().st_mtime) / 3600
        if age_hours < ttl_hours:
            try:
                return json.loads(key.read_text(encoding="utf-8"))["body"]
            except Exception:
                pass
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "orbit-catalog/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        log(f"HTTP {e.code} for {url}")
        return None
    except Exception as e:
        log(f"fetch error {url}: {e}")
        return None
    key.parent.mkdir(parents=True, exist_ok=True)
    key.write_text(json.dumps({"url": url, "status": status, "body": body, "fetched_at": _ts()}), encoding="utf-8")
    return body


# ---------- gh / github ----------

GH_TOKEN: Optional[str] = None


def _gh_token() -> Optional[str]:
    global GH_TOKEN
    if GH_TOKEN is not None:
        return GH_TOKEN
    # try env
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if tok:
        GH_TOKEN = tok
        return tok
    # try gh CLI
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10)
        if out.returncode == 0:
            GH_TOKEN = out.stdout.strip()
            return GH_TOKEN
    except FileNotFoundError:
        pass
    return None


def gh_api(path: str) -> Optional[dict]:
    """Call GitHub API with token auth + caching."""
    url = f"https://api.github.com{path}" if path.startswith("/") else f"https://api.github.com/{path}"
    headers = {"User-Agent": "orbit-catalog/1.0", "Accept": "application/vnd.github+json"}
    tok = _gh_token()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    body = cached_fetch(url, namespace="ghapi", headers=headers, ttl_hours=24)
    if body is None:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


# ---------- repo verification ----------

@dataclass
class RepoMeta:
    repo_url: str
    owner: str = ""
    repo: str = ""
    exists: bool = False
    archived: bool = False
    private: bool = False
    fork: bool = False
    stars: int = 0
    forks: int = 0
    license: str = ""
    primary_language: str = ""
    default_branch: str = ""
    last_commit_at: str = ""
    description: str = ""
    pushed_at: str = ""
    error: str = ""

    def asdict(self) -> dict:
        return asdict(self)


_GITHUB_URL_RE = re.compile(r"github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?(?:/|$|#)")


def parse_github_url(url: str) -> Optional[tuple[str, str]]:
    m = _GITHUB_URL_RE.search(url)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    return owner, repo


def verify_repo(url: str) -> RepoMeta:
    """Look up GitHub repo metadata via API. Returns RepoMeta with exists=False on failure."""
    parsed = parse_github_url(url)
    if not parsed:
        return RepoMeta(repo_url=url, error="not a github url")
    owner, repo = parsed
    meta = RepoMeta(repo_url=url, owner=owner, repo=repo)
    data = gh_api(f"/repos/{owner}/{repo}")
    if not data:
        meta.error = "api not found or rate-limited"
        return meta
    if data.get("message") == "Not Found":
        meta.error = "404"
        return meta
    meta.exists = True
    meta.archived = bool(data.get("archived"))
    meta.private = bool(data.get("private"))
    meta.fork = bool(data.get("fork"))
    meta.stars = int(data.get("stargazers_count") or 0)
    meta.forks = int(data.get("forks_count") or 0)
    lic = data.get("license") or {}
    meta.license = lic.get("spdx_id") or lic.get("key") or ""
    meta.primary_language = data.get("language") or ""
    meta.default_branch = data.get("default_branch") or ""
    meta.pushed_at = data.get("pushed_at") or ""
    meta.last_commit_at = (data.get("pushed_at") or "")[:10]
    meta.description = (data.get("description") or "")[:300]
    return meta


# ---------- discovery row schema ----------

@dataclass
class Candidate:
    source_url: str
    kind: str = "unknown"  # mcp_server | sdk_wrapper | tool_folder | unknown
    proposed_slot: str = ""
    track_hint: str = ""  # personal | merchant | both
    discovered_via: str = ""
    notes: str = ""
    # filled in by verify
    exists: bool = False
    archived: bool = False
    stars: int = 0
    license: str = ""
    last_commit_at: str = ""
    primary_language: str = ""
    description: str = ""
    error: str = ""

    def to_jsonl(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, separators=(",", ":"))


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def append_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")))
            f.write("\n")


def write_jsonl_atomic(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")))
            f.write("\n")
    tmp.replace(path)


# ---------- git ops ----------

def clone_shallow(url: str, target: Path) -> bool:
    """git clone --depth=1 --filter=blob:none."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return True
    try:
        r = subprocess.run(
            ["git", "clone", "--depth=1", "--filter=blob:none", "--no-tags", url, str(target)],
            capture_output=True, text=True, timeout=180,
        )
        if r.returncode != 0:
            log(f"clone failed {url}: {r.stderr[:200]}")
            return False
        return True
    except Exception as e:
        log(f"clone exception {url}: {e}")
        return False


def pinned_commit(repo_path: Path) -> str:
    try:
        r = subprocess.run(["git", "-C", str(repo_path), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip()[:40] if r.returncode == 0 else ""
    except Exception:
        return ""


# ---------- triage filters ----------

EXCLUDED_LICENSES = {"GPL-3.0", "GPL-2.0", "AGPL-3.0", "AGPL-1.0", "GPL-3.0-or-later", "GPL-2.0-or-later", "AGPL-3.0-or-later"}
PERMISSIVE_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "Unlicense", "0BSD", "MPL-2.0", "LGPL-2.1", "LGPL-3.0"}


def triage_decision(c: dict, allow_unmaintained_for_official: bool = True) -> tuple[str, str]:
    """Return (decision, reason). decision is keep | drop | needs_review."""
    if not c.get("exists"):
        return "drop", f"repo not verified: {c.get('error','unknown')}"
    if c.get("archived"):
        # archived can still be valid if it's an Anthropic reference server
        owner = (c.get("source_url") or "").lower()
        if "modelcontextprotocol/servers" in owner or "anthropics/" in owner:
            return "keep", "archived but canonical reference server"
        return "drop", "archived without successor"
    lic = c.get("license") or ""
    if lic in EXCLUDED_LICENSES:
        return "drop", f"license excluded ({lic})"
    if not lic:
        # no license = all rights reserved; reject unless it's an official vendor SDK
        owner_l = (c.get("source_url") or "").lower()
        if any(o in owner_l for o in ("github.com/stripe/", "github.com/github/", "github.com/elevenlabs/", "github.com/openai/", "github.com/anthropics/", "github.com/cloudflare/", "github.com/getsentry/")):
            return "needs_review", "no license but official vendor org"
        return "drop", "no license"
    # maintenance gate
    last = c.get("last_commit_at") or ""
    stars = int(c.get("stars") or 0)
    if last:
        try:
            d = datetime.fromisoformat(last)
            months = (datetime.utcnow() - d).days / 30.4
            if months > 18 and stars < 100:
                # exception for official vendor SDKs
                owner_l = (c.get("source_url") or "").lower()
                if allow_unmaintained_for_official and any(o in owner_l for o in ("github.com/stripe/", "github.com/twilio/", "github.com/sendgrid/", "github.com/hubspot/", "github.com/shopify/", "github.com/plaid/", "github.com/duffelhq/", "github.com/google", "github.com/microsoft/", "github.com/openai/", "github.com/anthropics/", "github.com/elevenlabs/")):
                    return "keep", f"stale ({months:.0f}mo) but official vendor SDK"
                return "drop", f"stale {months:.0f}mo and stars<100"
        except Exception:
            pass
    return "keep", "passes triage"


# ---------- secret / pattern heuristics ----------

SECRET_PATTERNS = [
    (re.compile(r"sk_live_[A-Za-z0-9]{16,}"), "stripe live key"),
    (re.compile(r"sk_test_[A-Za-z0-9]{16,}"), "stripe test key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws access key"),
    (re.compile(r"AIza[0-9A-Za-z_-]{35}"), "google api key"),
    (re.compile(r"ghp_[A-Za-z0-9]{36,}"), "github personal token"),
    (re.compile(r"gho_[A-Za-z0-9]{36,}"), "github oauth token"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]+"), "slack token"),
    (re.compile(r"eyJ[A-Za-z0-9_=-]{20,}\.[A-Za-z0-9_=-]{20,}\.[A-Za-z0-9_=.-]{20,}"), "jwt-like"),
    (re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "private key"),
]

SUSPICIOUS_PATTERNS = [
    (re.compile(r"\beval\s*\("), "eval-call"),
    (re.compile(r"\bexec\s*\("), "exec-call"),
    (re.compile(r"Function\s*\("), "Function-constructor"),
    (re.compile(r"child_process|subprocess\.(Popen|run|call|check_output)|spawn\s*\("), "process-spawn"),
    (re.compile(r"\.discord\.com|\.discordapp\.com|pastebin\.|ngrok\."), "suspicious-host"),
    (re.compile(r"download_and_run|self_update|auto_update"), "self-update"),
    (re.compile(r"keylog|clipboard\.read|screencap|screenshot"), "io-snooping"),
    (re.compile(r"xmrig|stratum\+tcp|coinhive|monero"), "miner-string"),
    (re.compile(r"window\.location\s*="), "location-redirect"),
    (re.compile(r"document\.cookie"), "cookie-access"),
]

URL_RE = re.compile(r"https?://[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+", re.IGNORECASE)


def scan_tree_for_patterns(repo_path: Path, max_file_bytes: int = 5_000_000) -> dict:
    """Walk the repo, grep for secrets/suspicious/URLs. Light static analysis."""
    findings = {"secrets": [], "suspicious": [], "urls": {}, "files_scanned": 0, "files_skipped": 0}
    skip_dirs = {".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build", ".next", ".turbo", "target"}
    binary_exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".tar", ".gz", ".woff", ".woff2", ".ttf", ".eot", ".ico", ".mp3", ".mp4", ".wav", ".mov", ".bin", ".so", ".dll", ".dylib", ".pyc"}
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fn in files:
            p = Path(root) / fn
            if p.suffix.lower() in binary_exts:
                continue
            try:
                if p.stat().st_size > max_file_bytes:
                    findings["files_skipped"] += 1
                    continue
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                findings["files_skipped"] += 1
                continue
            findings["files_scanned"] += 1
            rel = str(p.relative_to(repo_path)).replace("\\", "/")
            for rx, label in SECRET_PATTERNS:
                for m in rx.finditer(text):
                    findings["secrets"].append({"file": rel, "label": label, "match_prefix": m.group(0)[:24]})
            for rx, label in SUSPICIOUS_PATTERNS:
                for m in rx.finditer(text):
                    snippet = text[max(0, m.start()-30):m.end()+30].replace("\n", " ")
                    findings["suspicious"].append({"file": rel, "label": label, "snippet": snippet[:200]})
            for m in URL_RE.finditer(text):
                u = m.group(0).rstrip(".,;:)\"'")
                try:
                    host = urllib.parse.urlparse(u).netloc.lower()
                except Exception:
                    continue
                if not host or host.startswith("localhost") or host.startswith("127.") or host.startswith("0.0.0.0") or host == "example.com":
                    continue
                findings["urls"].setdefault(host, []).append(rel)
    # dedupe url file lists
    for host, files in findings["urls"].items():
        findings["urls"][host] = sorted(set(files))[:5]
    return findings


def scan_package_json_install_hooks(repo_path: Path) -> list[dict]:
    """Detect dangerous npm install hooks (network+exec at install time)."""
    findings = []
    for pj in repo_path.rglob("package.json"):
        # ignore vendored node_modules
        if "node_modules" in pj.parts:
            continue
        try:
            data = json.loads(pj.read_text(encoding="utf-8"))
        except Exception:
            continue
        scripts = data.get("scripts") or {}
        for hook in ("preinstall", "install", "postinstall"):
            cmd = scripts.get(hook)
            if not cmd:
                continue
            danger = any(s in cmd for s in ("curl", "wget", "node -e", "python -c", "eval", "fetch", "http://", "https://"))
            findings.append({
                "file": str(pj.relative_to(repo_path)).replace("\\", "/"),
                "hook": hook,
                "command": cmd[:300],
                "dangerous": danger,
            })
    return findings


def scan_pyproject_hooks(repo_path: Path) -> list[dict]:
    """Detect dangerous Python build hooks."""
    findings = []
    for fn in ("setup.py", "pyproject.toml"):
        for p in repo_path.rglob(fn):
            if "venv" in p.parts or ".venv" in p.parts:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if re.search(r"(?:urlopen|urlretrieve|requests\.get|httpx\.get)\s*\(", text) and "setup.py" in p.name:
                findings.append({"file": str(p.relative_to(repo_path)).replace("\\", "/"), "issue": "network-call-in-setup"})
            if re.search(r"\bos\.system\s*\(|\bsubprocess\.(call|run|Popen|check_output)\s*\(", text) and "setup.py" in p.name:
                findings.append({"file": str(p.relative_to(repo_path)).replace("\\", "/"), "issue": "shell-call-in-setup"})
    return findings


# ---------- entry helpers ----------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    print("orbit_pipeline core utilities (not a CLI). use _scripts/cli_*.py wrappers.")
