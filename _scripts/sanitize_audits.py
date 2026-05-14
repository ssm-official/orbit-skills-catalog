"""Sanitize audit.json files so they don't trip GitHub's secret-scanning push
protection. Redacts match prefixes and any snippet that looks like it could
contain real-or-real-looking key material.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT

SCAN_BASE = ROOT / "_logs" / "scan"

# Patterns of strings that GitHub treats as suspicious — match them so we
# can replace with `<redacted>` to stay below push-protection thresholds.
REDACT_PATTERNS = [
    re.compile(r"sk_(?:live|test)_[A-Za-z0-9]{16,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    re.compile(r"gh[pous]_[A-Za-z0-9]{36,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]+"),
    re.compile(r"eyJ[A-Za-z0-9_=-]{20,}\.[A-Za-z0-9_=-]{20,}\.[A-Za-z0-9_=.-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[^-]{20,}-----END[^-]{0,30}-----", re.DOTALL),
    re.compile(r"[a-f0-9]{40,}"),  # 40+ hex chars (sha-ish, would catch SerpAPI 64-char)
    re.compile(r"[A-Za-z0-9]{30,}"),  # very-long alnum tokens
]


def redact(s: str) -> str:
    if not s:
        return s
    out = s
    for rx in REDACT_PATTERNS:
        out = rx.sub("<redacted>", out)
    return out


def sanitize_audit(audit: dict) -> dict:
    # secrets: keep file + label + a short shape hint, drop match content
    new_secrets = []
    for s in audit.get("findings", {}).get("secrets", []):
        new_secrets.append({
            "file": s.get("file", ""),
            "label": s.get("label", ""),
            "match_redacted": True,
        })
    audit.setdefault("findings", {})["secrets"] = new_secrets

    # suspicious: keep file + label, redact snippet
    new_susp = []
    for s in audit.get("findings", {}).get("suspicious", []):
        new_susp.append({
            "file": s.get("file", ""),
            "label": s.get("label", ""),
            "snippet": redact(s.get("snippet", ""))[:120],
        })
    audit["findings"]["suspicious"] = new_susp

    # install hooks: keep file + hook + dangerous flag, redact command
    for h in audit.get("findings", {}).get("install_hooks", []):
        h["command"] = redact(h.get("command", ""))[:160]

    # verdict_reason: redact any matchy substrings
    audit["verdict_reason"] = redact(audit.get("verdict_reason", ""))

    audit["_sanitized"] = True
    return audit


def main():
    n = 0
    for ad in SCAN_BASE.glob("*/audit.json"):
        try:
            data = json.loads(ad.read_text(encoding="utf-8"))
        except Exception:
            continue
        sanitize_audit(data)
        ad.write_text(json.dumps(data, indent=2), encoding="utf-8")
        n += 1
    print(f"sanitized {n} audit.json files")


if __name__ == "__main__":
    main()
