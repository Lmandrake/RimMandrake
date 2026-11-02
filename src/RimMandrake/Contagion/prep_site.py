#!/usr/bin/env python3
"""Build, clean, save and register the Contagion saved test site (RM_TestSite_contagion_v2). LIVE ONLY, bridge holder.

BIOME_SPRINT_PROVE_SCRUB_SETS_PACE (kickoff packet §1.2). Data: site_spec.py. Recipe: Utils/modcheck/biome_site.py
(Cauldron's steps, shared). Contagion's own read-back: no Burn may be active at the save or after the reload (a site
that loads into a Burn is not a calm baseline), read off RM_MapComponent_ContagionSky with jawa/map_comp_read.

    python3    src/RimMandrake/Contagion/prep_site.py --plan                      # offline: print the recipe
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build contagion  # LIVE: build + save + register
    python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py load contagion   # LIVE: load + read-back
    python.exe src/RimMandrake/Contagion/prep_site.py --prove [--build-if-missing]  # LIVE: the item's proof (exit 0/1)

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


def header_problems(path):
    """The saved file's own mod header (<meta><modIds>) -> problems: missing file, unreadable header, a retired donor
    (CONTAGION_SITE_BUILD_SKY_STAYS_CALM: v1 carried sarg.alphabiomes + vfe.insectoid2 and was a dead fixture)."""
    import re
    from retired_mods import is_retired
    if not os.path.isfile(path):
        return ["no save file %s" % path], []
    with open(path, encoding="utf-8", errors="replace") as f:
        head = f.read(65536)
    m = re.search(r"<modIds>(.*?)</modIds>", head, re.S)
    ids = [x.strip().lower() for x in re.findall(r"<li>(.*?)</li>", m.group(1))] if m else []
    if not ids:
        return ["save header unreadable: no <modIds> in the first 64 KiB of %s" % path], []
    bad = [i for i in ids if is_retired(i)]
    return (["save header holds retired donor(s) %s" % bad] if bad else []), ids


def prove(build_if_missing=False, saves_dir=None):
    """LIVE, bridge holder, game up on a donor-free tier. A1: the site save exists (built now if missing and asked)
    with a donor-free header. A2: a load from the main menu reads verified, biome RM_Contagion, a native alive, no Burn.
    -> (exit code, receipt)."""
    import test_site_saves as TS
    if saves_dir is None:
        from game_paths import SAVES as saves_dir
    rec = {"save": S.SAVE, "utc": TS._now()}
    path = os.path.join(saves_dir, S.SAVE + ".rws")
    from northstar_driver.session import FastSession
    with FastSession(strict=False) as s:
        if build_if_missing and not os.path.isfile(path):
            work = os.path.join(B.ROOT, "Transient", "test_site_saves")
            os.makedirs(work, exist_ok=True)
            rec["build"] = {"verified": build_site_save(s, work).get("verified")}
        rec["A1"], rec["mods"] = header_problems(path)
        if not rec["A1"]:
            ld = TS.load_site(s.call, S.SITE)
            extra, rec["census"] = site_problems(s.call, "reload")
            rec["A2"] = list(ld.get("problems") or []) + extra
        else:
            rec["A2"] = ["not loaded: A1 failed"]
    return (0 if not rec["A1"] and not rec["A2"] else 1), rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plan", action="store_true", help="print the recipe; touch nothing (the default)")
    ap.add_argument("--prove", action="store_true", help="LIVE: A1 donor-free save on disk + A2 verified calm reload")
    ap.add_argument("--build-if-missing", action="store_true", help="with --prove: build the site first if no save")
    a = ap.parse_args(argv)
    if a.prove:
        import json
        code, rec = prove(a.build_if_missing)
        print(json.dumps({k: rec.get(k) for k in ("save", "build", "A1", "A2", "census")}, default=str)[:2000])
        print("%s %s" % ("PROVEN" if code == 0 else "NOT PROVEN", S.SAVE))
        return code
    print(STEPS)
    print("Build it with: python.exe src/RimMandrake/Utils/modcheck/test_site_saves.py build contagion")
    return 0


if __name__ == "__main__":
    sys.exit(main())
