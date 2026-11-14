#!/usr/bin/env python3
"""tier_cut_creature_check.py: does any modset_builder test tier load a creature the owner's full list cuts?

Acceptance test of RIMMANDRAKE_KEEP_CUT_BEASTS_OFF_TEST_TIERS (owner 2026-11-13, on the Explosive Knockback proof
scene: "WTF is that Thrumbo creature?! We shouldn't have anything called a Thrumbo in the game anymore").

The full list removes vanilla beasts with Cherry Picker (VANILLA_BEAST_EXCISION_1). A test tier without Cherry
Picker loads every one of them again: Thrumbo stands up in a proof scene with whatever picture a mod puts at its
texPath. A tier passes when it carries Cherry Picker, or when none of the mods it loads defines a cut creature.

Inputs, all read, none guessed:
  cut list   infrastructure/state/cherrypicker/CherryPicker.SHIP.xml (ThingDef/<name> keys; --cuts overrides)
  creatures  the newest DefDump capture's animals.json (defName -> packageId; captured before Cherry Picker runs,
             so cut creatures are in it)
  tiers      modset_builder.TIERS resolved against the installed mods, the exact list --apply would write

Exit 0: every tier clean. 1: a tier loads a cut creature (listed). 2: UNMEASURED (an input is unreadable, a tier
would not resolve, or the sanity probe failed: no cut creature mapped to any mod means the instrument is blind).

    python3 src/RimMandrake/Utils/tier_cut_creature_check.py [--tier NAME ...] [--cuts PATH] [--animals PATH]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cherrypicker as CP          # noqa: E402
import game_paths as GP            # noqa: E402
import modset_builder as MB        # noqa: E402

SHIP = os.path.join(CP.REPO, "infrastructure", "state", "cherrypicker", "CherryPicker.SHIP.xml")
CHERRY = "owlchemist.cherrypicker"


def cut_creatures(cuts_path, animals_path):
    """-> {defName: packageId} for every creature the cut list removes; raises on an unreadable input."""
    keys = CP._parse_settings(cuts_path)
    cut_things = {k.split("/", 1)[1] for k in keys if k.startswith("ThingDef/")}
    with open(animals_path, encoding="utf-8") as fh:
        rows = json.load(fh)["animals"]
    if len(rows) < 50 or not cut_things:
        raise ValueError("sanity: %d creature rows, %d cut ThingDefs: the instrument cannot see" % (len(rows),
                                                                                                   len(cut_things)))
    return {r["defName"]: (r.get("packageId") or "").lower() for r in rows if r["defName"] in cut_things}


def check(tiers, cut, installed):
    """-> (fails {tier: [creature (mod)]}, unmeasured {tier: reason})."""
    fails, unmeasured = {}, {}
    for name in tiers:
        try:
            pids, missing, _refusals = MB.resolve_tier(name, installed)
        except Exception as exc:                       # a tier that will not resolve is not a pass
            unmeasured[name] = "%s: %s" % (type(exc).__name__, exc)
            continue
        low = {p.lower() for p in pids}
        if CHERRY in low:
            continue
        hit = sorted("%s (%s)" % (d, p) for d, p in cut.items() if p in low)
        if hit:
            fails[name] = hit
    return fails, unmeasured


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tier", action="append", help="check only these tiers (default: every TIERS entry)")
    ap.add_argument("--cuts", default=SHIP)
    ap.add_argument("--animals", default=None, help="animals.json (default: newest DefDump capture)")
    a = ap.parse_args(argv)
    animals = a.animals or os.path.join(GP.newest_capture() or "", "animals.json")
    try:
        cut = cut_creatures(a.cuts, animals)
    except (OSError, ValueError, KeyError) as exc:
        print("UNMEASURED: %s" % exc)
        return 2
    if not cut:
        print("UNMEASURED: no cut creature found in %s: the dump cannot see the cut list" % animals)
        return 2
    installed = MB.scan()
    if not installed:
        print("UNMEASURED: no installed mods found, so no tier can be resolved")
        return 2
    tiers = a.tier or sorted(MB.TIERS)
    fails, unmeasured = check(tiers, cut, installed)
    print("cut list %s: %d cut creatures defined by %d mods; %d tiers checked"
          % (a.cuts, len(cut), len(set(cut.values())), len(tiers)))
    for t in sorted(fails):
        print("FAIL %s loads %d cut creatures, no Cherry Picker: %s%s"
              % (t, len(fails[t]), ", ".join(fails[t][:8]), " ..." if len(fails[t]) > 8 else ""))
    for t in sorted(unmeasured):
        print("UNMEASURED %s: %s" % (t, unmeasured[t]))
    print("%d FAIL, %d UNMEASURED, %d clean" % (len(fails), len(unmeasured), len(tiers) - len(fails) - len(unmeasured)))
    return 1 if fails else (2 if unmeasured else 0)


if __name__ == "__main__":
    sys.exit(main())
