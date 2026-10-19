#!/usr/bin/env python3
"""Build, clean, save and register the Contagion saved test site (RM_TestSite_contagion_v1). LIVE ONLY, bridge holder.

BIOME_SPRINT_PROVE_SCRUB_SETS_PACE (kickoff packet §1.2). Data: site_spec.py. Recipe: Utils/modcheck/biome_site.py
(Cauldron's steps, shared). Contagion's own read-back: no Burn may be active at the save or after the reload (a site
that loads into a Burn is not a calm baseline), read off RM_MapComponent_ContagionSky with jawa/map_comp_read.

    python3    src/RimMandrake/Contagion/prep_site.py --plan                      # offline: print the recipe
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build contagion  # LIVE: build + save + register
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py load contagion   # LIVE: load + read-back

Preconditions (the live round's, not checked here): the game is up on the `biomes_sprint` tier with the composite
deployed (preflight_contagion.py O-TIER / O-DEPLOY PASS), the bridge held by the running seat.
Nothing is saved unless the clean read-back is clean; a save is never overwritten (bump SAVE in site_spec.py).
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
_MODCHECK = os.path.join(HERE, "..", "Utils", "modcheck")
if _MODCHECK not in sys.path:
    sys.path.insert(0, _MODCHECK)
import biome_site as B  # noqa: E402

S = B.load_spec(os.path.join(HERE, "site_spec.py"), "contagion_site_spec")
SiteError = B.SiteError


def probe(call, phase, saved=None):
    """The sky: BurnActive must read False. -> (problems, {member: text})."""
    v = B.comp_read(call, S.SKY_COMP, S.SKY_MEMBERS)
    P = []
    if "BurnActive" not in v or B.as_bool(v.get("BurnActive")):
        P.append("sky at %s: a Burn is active (%s)" % (phase, v))
    return P, v


def site_problems(call, phase="save", saved=None):
    return B.site_problems(call, S, probe, phase, saved)


def build_site_save(s, work_dir, saves_dir=None, sleep=time.sleep):
    return B.build_site_save(s, S, work_dir, saves_dir=saves_dir, sleep=sleep, probe=probe)


STEPS = B.steps(S, " 8b sky: map_comp_read %s %s -> BurnActive False (recorded with NextBurnTick)\n"
                   % (S.SKY_COMP, ",".join(S.SKY_MEMBERS))) + """\
Then: northstar_driver run --mod Contagion --plan src/RimMandrake/Contagion/northstar_plan.py. The whole suite runs
on this already-sick site (validation.py TWO STARTS): northstar_site.preflight accepts an RM_Contagion map, and the two
stock-map components take it off the biome themselves and put it back.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true", help="print the recipe; touch nothing (the default)")
    ap.parse_args(argv)
    print(STEPS)
    print("Build it with: python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build contagion")
    return 0


if __name__ == "__main__":
    sys.exit(main())
