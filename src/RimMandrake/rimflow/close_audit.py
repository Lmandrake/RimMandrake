#!/usr/bin/env python3
"""close_audit.py - AU4, unverified closes (rimflow_v3_responsibilities_2026-10-26.md; RO3 of
operating_requirements_2026-11-01.md): closes with no level-tagged verify event of that item before the close.

The window is close_gate_rules.json `since`, when the gate landed; the 2026-10-19 window, the baseline's (813 of 823),
is printed beside it. A --no-code close has no code to check, so it is counted apart, under its own limit.
Exit 0 in range, 1 out of range, 2 UNMEASURED (no close in the window, or the ledger reads empty).

    python3 src/RimMandrake/rimflow/close_audit.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import model                                       # noqa: E402

RULES = os.path.join(HERE, "close_gate_rules.json")


def unverified(events, since):
    """Pure. -> (closes in the window, those with no level-tagged verify before them), the baseline's formula (M8)."""
    levelled = {}
    for e in events:
        if e.get("event") == "verify" and e.get("level"):
            levelled.setdefault(e.get("id"), []).append(e["ts"])
    closes = [e for e in events if e.get("event") == "close" and e["ts"] >= since]
    return closes, [e for e in closes if not any(t <= e["ts"] for t in levelled.get(e.get("id"), ()))]


def main():
    with open(RULES, encoding="utf-8") as f:
        r = json.load(f)
    events = model.read()
    base, base_bad = unverified(events, "2026-10-19")
    print("ledger: %d events" % len(events))
    print("AU4 since 2026-10-19 (the baseline's window): %d of %d" % (len(base_bad), len(base)))
    closes, bad = unverified(events, r["since"])
    code = [e for e in closes if not e.get("noCode")]
    code_bad = [e for e in bad if not e.get("noCode")]
    print("AU4 since the gate landed (%s): %d of %d; code closes %d of %d; --no-code %d" % (
        r["since"], len(bad), len(closes), len(code_bad), len(code), len(closes) - len(code)))
    for e in code_bad[:10]:
        print("  unverified: %s at %s" % (e.get("id"), e.get("sha")))
    if not events or not closes:
        print("UNMEASURED: no close in the window")
        return 2
    high = [bool(code) and len(code_bad) / len(code) > r["code_unverified_max_share"],
            (len(closes) - len(code)) / len(closes) > r["no_code_max_share"]]
    print("AU4 %s (code unverified <= %.2f, --no-code <= %.2f of closes)" % (
        "OUT OF RANGE" if any(high) else "IN RANGE", r["code_unverified_max_share"], r["no_code_max_share"]))
    return 1 if any(high) else 0


if __name__ == "__main__":
    sys.exit(main())
