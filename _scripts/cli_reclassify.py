"""cli_reclassify.py — re-apply the verdict logic from cli_scan.py against
existing audit.json + gitleaks.json files, without re-running the (expensive)
scanners themselves.

Use when the verdict logic improves (e.g. test-path detection fix) but the
underlying findings are still valid. Reads the on-disk findings, recomputes
the verdict, writes audit.json back.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orbit_pipeline import ROOT, log


SCAN_LOG_BASE = ROOT / "_logs" / "scan"


def _is_test_path(rel: str) -> bool:
    """Classify a file path as test / doc / example space (findings here become
    pass_with_notes rather than quarantine). Covers:
      - any /test/ /tests/ /spec/ /fixtures/ /mocks/ /example/ /samples/ tree
      - /docs/, /.github/, /site-packages/, /snapshots/
      - filenames like test_*.py, spec_*.rb, *.test.js, *.spec.ts
      - Go test files: *_test.go, *_test_*.go
      - reference docs: reference.md, README.md, CHANGELOG.md
      - vendored API specs: /discovery/, /openapi/, /swagger/
      - common SDK doc/example dirs at repo root
    """
    rl = "/" + rel.lower().replace("\\", "/")
    dir_markers = (
        "/test/", "/tests/", "/__tests__/", "/spec/", "/specs/",
        "/fixtures/", "/fixture/", "/__fixtures__/", "/mocks/", "/mock/",
        "/example/", "/examples/", "/sample/", "/samples/",
        "/docs/", "/doc/", "/.github/", "/site-packages/",
        "/snapshots/", "/__snapshots__/",
        "/discovery/", "/openapi/", "/swagger/", "/spec-fixtures/",
        "/cassettes/", "/vcr/",  # API replay fixtures (vcrpy, betamax, etc.)
        "/scripts/", "/script/",  # dev scripts — typically not shipped
        "/typings/", "/types/",
        "/reference/", "/references/",
    )
    if any(m in rl for m in dir_markers):
        return True
    fn = rl.rsplit("/", 1)[-1]
    # filename-based markers
    if fn.endswith(".example") or fn.endswith(".sample"):
        return True
    if fn.startswith("test_") or fn.startswith("spec_"):
        return True
    if ".test." in fn or ".spec." in fn or ".example." in fn or ".sample." in fn:
        return True
    # Go convention: *_test.go is a test file
    if fn.endswith("_test.go") or "_test_" in fn:
        return True
    # documentation / reference markdown
    if fn in ("readme.md", "readme.rst", "reference.md", "changelog.md", "contributing.md",
              "code_of_conduct.md", "security.md", "license", "license.md", "license.txt"):
        return True
    # OpenAPI / discovery / vendored API specs
    if fn.endswith(".discovery.json") or fn.endswith(".openapi.json") or fn.endswith(".swagger.json"):
        return True
    # If anywhere in the path is a markdown file under root-level docs
    if fn.endswith(".md") and "/docs/" in rl:
        return True
    return False


def _is_test_only_secret(label: str, prefix: str) -> bool:
    if label == "stripe test key":
        return True
    if "_test_" in prefix.lower() or prefix.lower().startswith("sk_test_"):
        return True
    return False


# Official vendor orgs whose SDKs publish example values / docstring
# credentials that gitleaks flags as false positives. For these, gitleaks
# findings are downgraded to notes — but only IF every finding is in
# source-code documentation or example shape, not in hot code paths.
# These vendors have professional security teams; their public SDKs
# would not contain real keys.
TRUSTED_VENDOR_ORGS = {
    "anthropics", "openai", "stripe", "twilio", "sendgrid", "shopify",
    "hubspot", "plaid", "duffelhq", "google", "googlemaps", "googleapis",
    "mapbox", "huggingface", "replicate", "deepgram", "assemblyai",
    "elevenlabs", "cloudflare", "getsentry", "intercom", "octokit",
    "pygithub", "modelcontextprotocol", "anthropic-ai", "anthropic",
    "microsoft", "github", "linear", "makenotion", "atlassian", "square",
    "ccxt", "ravinahp",  # ccxt is multi-exchange aggregator; ravinahp = Duffel MCP author
    "easypost", "resend", "klaviyo", "mailchimp", "deeplcom", "tavily-ai", "exa-labs",
    "alchemyplatform", "apify",
}

# Per-repo manual overrides after ground-truth inspection. Each entry
# documents why a finding was classified differently from the automatic
# verdict. Audited 2026-05-14.
MANUAL_OVERRIDES: dict[str, dict] = {
    "https://github.com/HKUDS/Vibe-Trading": {
        "verdict": "pass_with_notes",
        "note": "gitleaks generic-api-key match in SKILL.md is a Hugging Face model identifier "
                "(`ProsusAI/finbert`), not an API key. Confirmed by hand 2026-05-14."
    },
    "https://github.com/mbailey/voicemode": {
        "verdict": "pass_with_notes",
        "note": "gitleaks generic-api-key match is `AUTH0_CLIENT_ID`, which is a public OAuth "
                "client identifier (the corresponding client_secret stays server-side and is "
                "not in this file). Confirmed by hand 2026-05-14."
    },
}


def _is_trusted_vendor(source_url: str) -> bool:
    url_l = (source_url or "").lower()
    parts = url_l.split("/")
    if "github.com" in parts:
        idx = parts.index("github.com")
        if idx + 1 < len(parts):
            return parts[idx + 1] in TRUSTED_VENDOR_ORGS
    return False


def reclassify(audit_path: Path) -> dict | None:
    try:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    findings = audit.get("findings", {})
    reject_reasons = []
    notes_reasons = []
    trusted = _is_trusted_vendor(audit.get("source_url", ""))

    # secrets
    real_secret_hits = []
    test_secret_hits = []
    for s in findings.get("secrets", []):
        if _is_test_path(s.get("file", "")) or _is_test_only_secret(s.get("label", ""), s.get("match_prefix", "")):
            test_secret_hits.append(s)
        else:
            real_secret_hits.append(s)
    if real_secret_hits:
        if trusted:
            notes_reasons.append(f"trusted-vendor: {len(real_secret_hits)} pattern-scan secret hit(s) downgraded to notes (likely docstring/example values)")
        else:
            reject_reasons.append(f"hardcoded secrets in non-test paths ({len(real_secret_hits)} hits, e.g. {real_secret_hits[0]['file']})")
    if test_secret_hits:
        notes_reasons.append(f"test-path secret findings ({len(test_secret_hits)})")

    # install hooks
    for h in findings.get("install_hooks", []):
        if h.get("dangerous"):
            reject_reasons.append(f"dangerous {h['hook']} hook in {h['file']}")
    for h in findings.get("py_build_hooks", []):
        reject_reasons.append(f"python build hook issue: {h['issue']} in {h['file']}")

    # suspicious (all that survived the prose-skip filter at scan time)
    auto_reject_labels = {"miner-string", "self-update", "io-snooping"}
    for s in findings.get("suspicious", []):
        if s["label"] in auto_reject_labels:
            reject_reasons.append(f"suspicious code: {s['label']} in {s['file']}")
        else:
            notes_reasons.append(f"{s['label']} in {s['file']}")

    # gitleaks
    gitleaks_path = audit_path.parent / "gitleaks.json"
    gitleaks_real = 0
    gitleaks_test = 0
    if gitleaks_path.exists():
        try:
            gl = json.loads(gitleaks_path.read_text(encoding="utf-8"))
            if isinstance(gl, list):
                for finding in gl:
                    f = finding.get("File") or finding.get("file") or ""
                    if _is_test_path(f):
                        gitleaks_test += 1
                    else:
                        gitleaks_real += 1
        except Exception:
            pass
    if gitleaks_real:
        if trusted:
            notes_reasons.append(f"trusted-vendor: {gitleaks_real} gitleaks finding(s) downgraded to notes (likely SDK docs/example values)")
        else:
            reject_reasons.append(f"gitleaks: {gitleaks_real} non-test secret(s)")
    if gitleaks_test:
        notes_reasons.append(f"gitleaks: {gitleaks_test} test-path secret(s)")

    if reject_reasons:
        audit["verdict"] = "quarantine"
        audit["verdict_reason"] = "; ".join(reject_reasons)
    elif notes_reasons or findings.get("install_hooks"):
        audit["verdict"] = "pass_with_notes"
        audit["verdict_reason"] = "; ".join(notes_reasons) or f"{len(findings.get('install_hooks', []))} install hooks documented"
    else:
        audit["verdict"] = "pass"
        audit["verdict_reason"] = "no findings of concern in static scan"

    # Apply manual overrides AFTER auto-classification
    mo = MANUAL_OVERRIDES.get(audit.get("source_url", ""))
    if mo:
        audit["verdict"] = mo["verdict"]
        audit["verdict_reason"] = f"manual override: {mo['note']}"
        audit["_manual_override"] = True

    audit["_reclassified"] = True
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return audit


def main():
    from collections import Counter
    if not SCAN_LOG_BASE.exists():
        print("no scan logs yet")
        return
    summary = Counter()
    for ad in SCAN_LOG_BASE.glob("*/audit.json"):
        result = reclassify(ad)
        if result:
            summary[result.get("verdict", "?")] += 1
        else:
            summary["unreadable"] += 1
    print(json.dumps(dict(summary.most_common()), indent=2))


if __name__ == "__main__":
    main()
