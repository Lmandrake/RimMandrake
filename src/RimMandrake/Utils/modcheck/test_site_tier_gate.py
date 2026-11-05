#!/usr/bin/env python3
"""test_site_tier_gate -- LIVE read-only precondition: is the RUNNING game the site's fixture tier at all?
(RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS A1/A2.)

A site save records the list it was made on, so `test_site_saves.py prove river` refuses to build or load on a game that
is not SITES[site]["tier"]. On 2026-11-03 the live round ran it on another item's 28-mod game (sarg.alphabiomes, HAR,
OuterRim ...): prove said NOT CLEAN, the round wrote FAIL, and a FAIL stands for the build. That reading measured the
game, not the item. This gate runs first in each live line and turns "wrong game" into UNMEASURED (exit 2), which the
round restages, instead of a FAIL.

Fits (exit 0) when the running packageIds hold no retired donor, no mod beyond the resolved tier, every member of the
resolved tier (not only the ones it `want`s: a 13-mod subset is not the 14-mod list), and all five DLC. Exit 2 = wrong game (restage on the tier); exit 3 = the instrument could not read. It never
exits 1: it judges the game, never the item.

    python.exe src/RimMandrake/Utils/modcheck/test_site_tier_gate.py river
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_UTILS = os.path.dirname(_HERE)
_NORTHSTAR = os.path.join(os.path.dirname(_UTILS), "FlowWorks", "northstar")
for _p in (_HERE, _UTILS, _NORTHSTAR):
    if _p not in sys.path:
        sys.path.append(_p)

import test_site_saves as T  # noqa: E402

FITS, WRONG_GAME, BLIND = 0, 2, 3


def tier_want(tier):
    """The packageIds the tier must load (modset_builder TIERS[tier]['want'], lowercased)."""
    import modset_builder as MB
    return [str(i).lower() for i in MB.TIERS[tier].get("want") or ()]


def tier_gaps(running, site, tier_list=None, want=None, tier=None):
    """running packageIds -> problems (empty = the game is the site's tier). tier_list/want default to the resolved
    tier; the selftest passes its own. `tier` names the tier directly for a site that is not in T.SITES (the FlowWorks
    golden trial site: FlowWorks/northstar/trial_site.py gate)."""
    from retired_mods import is_retired
    from biome_site import missing_dlc
    tier = tier or T.SITES[site].get("tier")
    if not tier:
        return ["site %s names no fixture tier" % site]
    run = [str(i).strip().lower() for i in running or () if str(i).strip()]
    if not run:
        return ["running mod list unreadable (empty)"]
    tl = set(tier_list if tier_list is not None else T.tier_ids(tier))
    want = want if want is not None else tier_want(tier)
    P = []
    bad = [i for i in run if is_retired(i)]
    if bad:
        P.append("running list holds retired donor(s) %s" % bad)
    beyond = [i for i in run if i not in tl]
    if beyond:
        P.append("running list has mod(s) beyond tier %s %s" % (tier, beyond))
    lack = [i for i in want if i not in run]
    if lack:
        P.append("running list lacks tier %s mod(s) %s" % (tier, lack))
    short = sorted(i for i in tl if i not in run and i not in lack)   # the tier is the WHOLE list (14 mods), not its want
    if short:
        P.append("running list lacks tier %s member(s) %s" % (tier, short))
    dlc = missing_dlc(run)
    if dlc:
        P.append("running list lacks DLC %s" % dlc)
    return P


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("site", choices=sorted(k for k, v in T.SITES.items() if v.get("tier")))
    a = ap.parse_args(argv)
    try:
        from rimbridge_client import RimBridge, resolve_endpoint
        from biome_site import running_retired
        h, p, t = resolve_endpoint()
        with RimBridge(h, p, t, timeout=60.0) as rb:
            running, _ = running_retired(lambda tool, **kw: rb.call(tool, kw))
        P = tier_gaps(running, a.site)          # an unresolvable tier raises here: BLIND too, never a traceback's exit 1
    except Exception as ex:  # noqa: BLE001 - a blind read is UNMEASURED, never a verdict
        print("tier gate %s: BLIND %s: %s" % (a.site, type(ex).__name__, str(ex)[:300]))
        return BLIND
    tier = T.SITES[a.site]["tier"]
    if P:
        print("tier gate %s: WRONG GAME (UNMEASURED; restage on tier %s: modlist_swap.py / modset_builder) %s"
              % (a.site, tier, json.dumps({"problems": P, "running": running})))
        return WRONG_GAME
    print("tier gate %s: FITS tier %s (%d mods)" % (a.site, tier, len(running)))
    return FITS


if __name__ == "__main__":
    sys.exit(main())
