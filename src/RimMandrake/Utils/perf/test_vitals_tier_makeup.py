#!/usr/bin/env python3
"""Is the RUNNING game on the 23-mod tier? (VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL, live clause A1)

The item measures vitals overhead "on the 23-mod tier and the full list". The 23-mod tier is ratchet_pilot
(+ mandrake.rm.patches), design/RimMandrake/ratchet_workflow_and_token_burst_design_2026-10-11.md section H, whose
makeup is modset_builder.TIERS["ratchet_pilot"]. vitals_overhead.py --tier minimal only bounds the COUNT (10..80),
so a 13-mod minimal list or a 70-mod list would pass it; this check pins the tier by what it holds:
  every `want` id (bar retired donors), all five DLC + Core, no `forbid` id, no `forbid_substr` match,
  and COUNT_LO..COUNT_HI running mods (22 and 23 measured on that tier; zoom/harmony may move it by a few).
Exit 0 = TIER_OK, 1 = WRONG_TIER, 2 = BLIND (no running list read). Reads jawa/running_mods, never ModsConfig.xml.
`--ids FILE` judges a saved list (one packageId per line, or a JSON list) offline.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)
sys.path.insert(0, UTILS)
import modset_builder as MB

TIER = "ratchet_pilot"
COUNT_LO, COUNT_HI = 20, 26


def makeup(ids, tier=TIER):
    """-> (code, word, why) for a list of running packageIds against the tier's makeup."""
    if not isinstance(ids, list) or not ids or not all(isinstance(x, str) and x.strip() for x in ids):
        return 2, "BLIND", "no usable running packageIds: %r" % (str(ids)[:200],)
    got = [x.strip().lower() for x in ids]
    have = set(got)
    t = MB.TIERS[tier]
    bad = []
    want = [w.lower() for w in t["want"] if not MB._is_retired_donor(w)]
    miss = [w for w in want if w not in have]
    if miss:
        bad.append("missing tier mods %s" % miss)
    dlc = [d for d in (MB.CORE,) + MB.DLC_IDS if d not in have]
    if dlc:
        bad.append("missing Core/DLC %s" % dlc)
    forb = [f for f in t.get("forbid", []) if f.lower() in have]
    forb += [p for p in got for s in t.get("forbid_substr", []) if s.lower() in p]
    if forb:
        bad.append("forbidden mods running %s" % sorted(set(forb)))
    if not (COUNT_LO <= len(got) <= COUNT_HI):
        bad.append("%d running mods, the %s tier holds %d..%d" % (len(got), tier, COUNT_LO, COUNT_HI))
    if bad:
        return 1, "WRONG_TIER", "; ".join(bad)
    return 0, "TIER_OK", "%d running mods hold the %s tier makeup" % (len(got), tier)


def _read_ids(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        v = json.loads(text)
        return v.get("packageIds") if isinstance(v, dict) else v
    except ValueError:
        return [l.strip() for l in text.splitlines() if l.strip()]


def _live_ids():
    from rimbridge_client import RimBridge, resolve_endpoint
    h, p, t = resolve_endpoint()
    with RimBridge(h, p, t, timeout=120.0) as B:
        r = B.call("jawa/running_mods", {"assembly": "", "details": False}, check=False) or {}
        if isinstance(r, dict) and r.get("content"):
            try:
                r = json.loads(r["content"][0]["text"])
            except Exception:
                pass
    return r.get("packageIds") if isinstance(r, dict) else None


def main(argv):
    ids = _read_ids(argv[argv.index("--ids") + 1]) if "--ids" in argv else _live_ids()
    code, word, why = makeup(ids)
    print("%s %s" % (word, why), flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
