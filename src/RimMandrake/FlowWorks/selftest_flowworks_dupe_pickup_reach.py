#!/usr/bin/env python3
"""Offline guard: vanilla's duplicate pickup asks FlowWorks' full reach before it retargets a haul.

RIMMANDRAKE_VETO_DUPLICATE_PICKUP_ACROSS_SEALED_PIT_DROPS_HAUL (live 2026-11-16, the hauler's job log): after picking a stack up,
Toils_Haul.CheckForGetOpportunityDuplicate looks for a same-def stack within 8 cells with GenClosest.ClosestThingReachable's
REGION search, which never calls Reachability.CanReach, so FlowWorks' pit vetoes (a raised ladder seals a pit) are never asked.
The haul was retargeted into a sealed pit 6 cells off, the path errored, the stack was dropped on the ladder cell, all day.
The fix (Superdeep/RM_PitAccess.cs, RM_Patch_HaulDupeReach) adds to the duplicate search's validator the same
Reachability.CanReach that the search's own TraverseParms would pass, from the carrier's cell. This guard reads the shape of
that patch; the behaviour is decided live by northstar/live_haul_dupe_sealed_pit.py.

Cases: the patch class exists and targets CheckForGetOpportunityDuplicate; it wraps extraValidator (keeps the caller's
validator); it asks map.reachability.CanReach with TraverseParms.For(actor) and ClosestTouch (the search's own parameters); the
actor is set for the duration of the toil's initAction and cleared after (a finally), so no stale actor leaks to another toil;
it carries a [PatchFeature]. Planted: each case is checked on a copy with that part removed, and must go red.
Exit 0 all pass, 1 a case failed.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source", "Superdeep", "RM_PitAccess.cs")


def patch_body(text):
    m = re.search(r"\[HarmonyPatch\(typeof\(Toils_Haul\),\s*nameof\(Toils_Haul\.CheckForGetOpportunityDuplicate\)\)\]", text)
    if not m:
        return None
    end = text.find("\n\t}\n", m.end())
    return text[max(0, m.start() - 600): end if end > 0 else len(text)]


CASES = [
    ("targets CheckForGetOpportunityDuplicate", lambda b: b is not None),
    ("keeps the caller's validator", lambda b: b is not None and re.search(r"ref\s+(?:System\.)?Predicate<Thing>\s+extraValidator", b)
     and re.search(r"orig\s*==\s*null\s*\|\|\s*orig\(\s*t\s*\)", b)),
    ("asks the full reach with the search's own parameters", lambda b: b is not None and re.search(
        r"reachability\.CanReach\(\s*\w+\.Position\s*,\s*t\s*,\s*PathEndMode\.ClosestTouch\s*,\s*TraverseParms\.For\(\s*\w+\s*\)\s*\)", b)),
    ("sets the actor only for the initAction", lambda b: b is not None and re.search(r"finally\s*\{[^}]*=\s*prev", b)
     and "initAction" in b),
    ("carries a PatchFeature", lambda b: b is not None and "PatchFeature(" in b),
]

PLANTS = {
    "targets CheckForGetOpportunityDuplicate": lambda t: t.replace("nameof(Toils_Haul.CheckForGetOpportunityDuplicate)", "nameof(Toils_Haul.X)"),
    "keeps the caller's validator": lambda t: t.replace("orig == null || orig(t)", "true"),
    "asks the full reach with the search's own parameters": lambda t: t.replace("TraverseParms.For(a)", "TraverseParms.For(TraverseMode.PassAllDestroyableThings)"),
    "sets the actor only for the initAction": lambda t: re.sub(r"finally\s*\{[^}]*\}", "", t),
    "carries a PatchFeature": lambda t: re.sub(r"(\[RimMandrake\.Shared\.PatchFeature\(\"Hauling picks up only stacks it can reach\"\)\])", "", t),
}


def run(text):
    b = patch_body(text)
    return {name: bool(fn(b)) for name, fn in CASES}


def main():
    text = open(SRC, encoding="utf-8").read()
    real = run(text)
    bad = 0
    for name, ok in real.items():
        print("%-6s %s" % ("ok" if ok else "FAIL", name))
        bad += not ok
    if not bad:
        for name, plant in PLANTS.items():
            planted = run(plant(text))
            caught = not planted[name]
            print("%-6s planted fault caught: %s" % ("ok" if caught else "FAIL", name))
            bad += not caught
    print("DUPE PICKUP REACH: %d cases, %d failed" % (len(CASES) + (len(PLANTS) if not any(not v for v in real.values()) else 0), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
