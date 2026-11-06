#!/usr/bin/env python3
"""tier_load.py - is the RUNNING game exactly a modset_builder tier? (LANE_TIER_WIRE_A_WHOLE_LIST_LOAD)

Owner by card 2026-11-05: SteveDesktop is the exact-tier host. A testq job of profile tier:<name> loads that tier as the
whole list there and runs an item's live-proof lines; this tool is the worker's tier-exact load check, before the proofs
run and as the job's record of what actually ran.

  python.exe src/RimMandrake/Utils/testq/tier_load.py check --tier gizkastowaway

prints ONE JSON line, {"tier", "want", "running", "extra", "missing", "exact", "why"}: want is resolve_tier's packageIds
(all five DLC with the tier's dependency closure), running what jawa/running_mods says the game loaded. Exit 0 exact, 1 the
load is another list, 2 it could not measure (no game, no bridge, a tier that does not resolve). Run under Windows
Python: the bridge binds Windows loopback. The worker reads exit 1 and 2 alike as UNMEASURED, never a verdict.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.dirname(HERE)


def compare(want, running, alias=None):
    """-> (extra, missing): packageIds the running load holds beyond the tier, and the tier's ids it lacks. Case-blind;
    alias maps an id to the id it loads as (live_def_check.aliases), so a renamed mod is not a false gap."""
    alias = {k.lower(): v.lower() for k, v in (alias or {}).items()}
    run = {p.lower() for p in running}
    norm = {alias.get(p.lower(), p.lower()) for p in want}
    missing = sorted(p for p in want if p.lower() not in run and alias.get(p.lower(), "") not in run)
    extra = sorted(p for p in run if p not in norm and p not in {w.lower() for w in want})
    return extra, missing


def reading(tier, want, running, why=None, alias=None):
    out = {"tier": tier, "want": list(want or []), "running": None if running is None else sorted(running),
           "extra": [], "missing": [], "exact": False, "why": why}
    if running is None or why:
        out["why"] = why or "running mod list unread"
        return out
    out["extra"], out["missing"] = compare(want, running, alias)
    out["exact"] = not out["extra"] and not out["missing"]
    if not out["exact"]:
        out["why"] = "WRONG_TIER: the running load is not tier %s (%d running, %d wanted; extra %s; missing %s)" % (
            tier, len(running), len(want), out["extra"][:8], out["missing"][:8])
    return out


def measure(tier):
    """-> the reading of the live game (Windows Python, the bridge up)."""
    sys.path.insert(0, UTILS)
    sys.path.insert(0, os.path.join(UTILS, "modcheck"))
    import modset_builder as mb
    if mb.tier_def(tier) is None:
        return reading(tier, [], None, "tier %s is no modset_builder.py tier" % tier)
    try:
        pids, missing, refusals = mb.resolve_tier(tier, mb.scan())
    except ValueError as e:     # a mods__ token two installed packageIds spell (modset_builder.tier_def)
        return reading(tier, [], None, "tier %s does not resolve here: %s" % (tier, e))
    if missing or refusals:
        return reading(tier, pids, None, "tier %s does not resolve here: missing %s, refused %s"
                       % (tier, list(missing)[:8], list(refusals)[:4]))
    try:
        import live_def_check
        import rimbridge_client as rb
        import runner
        host, port, token = rb.resolve_endpoint()
        c = rb.RimBridge(host=host, port=port, token=token, timeout=60.0)
        c.connect()
        running = live_def_check.running_ids(runner._rb_call(c, "jawa/running_mods", {"details": False, "assembly": ""}))
        alias = live_def_check.aliases()
    except Exception as e:  # noqa: BLE001 - no game or no bridge is a reading of its own, never "exact"
        return reading(tier, pids, None, "jawa/running_mods raised (%s: %s)" % (type(e).__name__, str(e)[:200]))
    return reading(tier, pids, running, alias=alias)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--tier", required=True)
    a = ap.parse_args(argv)
    r = measure(a.tier)
    print(json.dumps(r, sort_keys=True))
    return 0 if r["exact"] else 1 if r["running"] is not None else 2


if __name__ == "__main__":
    sys.exit(main())
