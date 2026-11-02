#!/usr/bin/env python3
"""Build, clean, save and register the LeaningScrub saved test site (site_spec.SAVE). LIVE ONLY.

Item LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY. Data: site_spec.py. Recipe: Utils/modcheck/biome_site.py (Cauldron's
steps, shared). The Scrub's own read-back is the Lean, by jawa/map_comp_read on RM_MapComponent_Lean:
  save    Applies True; SunBearingDegrees, then HeadingDegrees == (90 - bearing) mod 360 in [0, 360) (the wind points
          at the sun, SCRUB_WIND_BUILD_LEAN_ON_PURPOSE), and Downwind == (cos, sin) of it. Nothing is saved otherwise.
  reload  Applies True and HeadingDegrees equals the saved heading: the same tile gives the same wind, so the site
          leans one way on every load. A mismatch registers loadVerified False.

    python3    src/RimMandrake/LeaningScrub/prep_site.py --plan                       # offline: print the recipe
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build leaningscrub    # LIVE: build + save + register
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py load leaningscrub     # LIVE: load + read-back

Preconditions (the live round's, not checked here): game up on `biomes_sprint` with the composite deployed
(preflight_leaningscrub.py O-TIER / O-DEPLOY PASS), leanEnabled at its shipped default (True), bridge held.
"""
import argparse
import math
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


def _vec(text):
    """Vector2 text '(0.71, -0.71)' -> (x, z), or None when it does not parse."""
    try:
        x, z = str(text).strip().strip("()").split(",")[:2]
        return float(x), float(z)
    except (TypeError, ValueError):
        return None


def expected_heading(sun_bearing):
    """RM_LeanKernel.HeadingFromSunBearing: map x = east, z = north, bearing clockwise from north."""
    return (90.0 - sun_bearing) % 360.0


def probe(call, phase, saved=None):
    """The Lean. -> (problems, {"applies", "heading", "sunBearing"?, "downwind"?, "savedHeading"?})."""
    members = S.LEAN_LOCK_MEMBERS if phase == "save" else S.LEAN_RELOAD_MEMBERS
    v = B.comp_read(call, S.LEAN_COMP, members)
    info = {"applies": B.as_bool(v.get("Applies")), "heading": B.as_float(v.get("HeadingDegrees"))}
    P = []
    if not info["applies"]:
        P.append("lean at %s: Applies is %s (biome without RM_LeanExtension?)" % (phase, v.get("Applies")))
    h = info["heading"]
    if h is None or not 0.0 <= h < 360.0:
        P.append("lean at %s: HeadingDegrees %s is not in [0, 360)" % (phase, v.get("HeadingDegrees")))
    if phase == "save":
        sun = B.as_float(v.get("SunBearingDegrees"))
        info["sunBearing"] = sun
        info["downwind"] = v.get("Downwind")
        if sun is None:
            P.append("lean at save: SunBearingDegrees unreadable: %r" % v.get("SunBearingDegrees"))
        elif h is not None:
            want = expected_heading(sun)
            d = abs(h - want) % 360.0
            if min(d, 360.0 - d) > S.HEADING_TOL:
                P.append("lean at save: heading %s is not 90 - sun bearing %s (= %.3f): the wind does not point at the "
                         "sun" % (h, sun, want))
        dw = _vec(v.get("Downwind"))
        if dw is None:
            P.append("lean at save: Downwind unreadable: %r" % v.get("Downwind"))
        elif h is not None:
            cx, cz = math.cos(math.radians(h)), math.sin(math.radians(h))
            if abs(dw[0] - cx) > S.DOWNWIND_TOL or abs(dw[1] - cz) > S.DOWNWIND_TOL:
                P.append("lean at save: Downwind %s is not (cos, sin) of heading %s = (%.2f, %.2f)" % (dw, h, cx, cz))
    if phase == "reload":
        want = (saved or {}).get("heading")
        info["savedHeading"] = want
        if want is None or h is None or abs(h - want) > S.HEADING_TOL:
            P.append("lean at reload: heading %s, the save read %s (one tile, one wind)" % (h, want))
    return P, info


def site_problems(call, phase="save", saved=None):
    return B.site_problems(call, S, probe, phase, saved)


def build_site_save(s, work_dir, saves_dir=None, sleep=time.sleep):
    return B.build_site_save(s, S, work_dir, saves_dir=saves_dir, sleep=sleep, probe=probe)


STEPS = B.steps(S, " 8b lean: map_comp_read %s %s -> Applies True, HeadingDegrees == 90 - sun bearing, Downwind its "
                   "(cos, sin) (recorded)\n" % (S.LEAN_COMP, ",".join(S.LEAN_LOCK_MEMBERS))) + """\
   at 10, map_comp_read %s %s -> the SAME heading, within %s deg.
Then: northstar_driver run --mod LeaningScrub --plan src/RimMandrake/LeaningScrub/northstar_plan.py on the loaded
site; validation.py's lean chain (walk lines 39-41) reads that map: lean_heading_from_sun, lean_scent_upwind_flees,
lean_fire_downwind (RM_TheLeanProof).
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
