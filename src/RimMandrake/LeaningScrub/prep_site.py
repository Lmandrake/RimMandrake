#!/usr/bin/env python3
"""Build, clean, save and register the LeaningScrub saved test site (RM_TestSite_leaningscrub_v1). LIVE ONLY.

Item LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY. Data: site_spec.py. Recipe: Utils/modcheck/biome_site.py (Cauldron's
steps, shared). The Scrub's own read-back is the Lean, by jawa/map_comp_read on RM_MapComponent_Lean:
  save    Applies True; reading Downwind LOCKS the heading (its getter rolls it once per map); headingDegrees then
          reads in [0, 360). Nothing is saved otherwise -- a site with no locked heading would roll a fresh one per
          load and could never show "leans one way".
  reload  Applies True and headingDegrees -- read BEFORE anything asks Downwind -- equals the saved heading. A save
          that dropped it reads -1 (the field's default) and the site is registered loadVerified False.

    python3    src/RimMandrake/LeaningScrub/prep_site.py --plan                       # offline: print the recipe
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build leaningscrub    # LIVE: build + save + register
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py load leaningscrub     # LIVE: load + read-back

Preconditions (the live round's, not checked here): game up on `biomes_sprint` with the composite deployed
(preflight_leaningscrub.py O-TIER / O-DEPLOY PASS), leanEnabled at its shipped default (True), bridge held.
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

S = B.load_spec(os.path.join(HERE, "site_spec.py"), "leaningscrub_site_spec")
SiteError = B.SiteError


def probe(call, phase, saved=None):
    """The Lean. -> (problems, {"applies", "heading", "downwind"?, "savedHeading"?})."""
    members = S.LEAN_LOCK_MEMBERS if phase == "save" else S.LEAN_RELOAD_MEMBERS
    v = B.comp_read(call, S.LEAN_COMP, members)
    info = {"applies": B.as_bool(v.get("Applies")), "heading": B.as_float(v.get("headingDegrees"))}
    if "Downwind" in v:
        info["downwind"] = v["Downwind"]
    P = []
    if not info["applies"]:
        P.append("lean at %s: Applies is %s (biome without RM_LeanExtension?)" % (phase, v.get("Applies")))
    h = info["heading"]
    if h is None or not 0.0 <= h < 360.0:
        P.append("lean at %s: heading %s is not locked in [0, 360)" % (phase, v.get("headingDegrees")))
    if phase == "reload":
        want = (saved or {}).get("heading")
        info["savedHeading"] = want
        if want is None or h is None or abs(h - want) > S.HEADING_TOL:
            P.append("lean at reload: heading %s, the save locked %s (the save must carry ONE heading)" % (h, want))
    return P, info


def site_problems(call, phase="save", saved=None):
    return B.site_problems(call, S, probe, phase, saved)


def build_site_save(s, work_dir, saves_dir=None, sleep=time.sleep):
    return B.build_site_save(s, S, work_dir, saves_dir=saves_dir, sleep=sleep, probe=probe)


STEPS = B.steps(S, " 8b lean: map_comp_read %s %s -> Applies True, heading locked in [0,360) (recorded)\n"
                   % (S.LEAN_COMP, ",".join(S.LEAN_LOCK_MEMBERS))) + """\
   at 10, map_comp_read %s %s (no Downwind first) -> the SAME heading, within %s deg.
Then: northstar_driver run --mod LeaningScrub --plan src/RimMandrake/LeaningScrub/northstar_plan.py on the loaded
site, once the Lean components exist in validation.py (FOUNDRY; walk lines 39-41) -- the site gives them a map that
leans one known way: heading-lock, scent flee upwind within leanScentRange, fire downwind leanFireBias of the time.
""" % (S.LEAN_COMP, ",".join(S.LEAN_RELOAD_MEMBERS), S.HEADING_TOL)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true", help="print the recipe; touch nothing (the default)")
    ap.parse_args(argv)
    print(STEPS)
    print("Build it with: python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build leaningscrub")
    return 0


if __name__ == "__main__":
    sys.exit(main())
