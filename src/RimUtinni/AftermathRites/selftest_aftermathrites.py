#!/usr/bin/env python3
"""selftest_aftermathrites.py -- offline proof for AftermathRites' cross_refs_resolve_by_name chain.

Run bare: python3 src/RimUtinni/AftermathRites/selftest_aftermathrites.py   (exit 0 = clean)

The shipped defs must resolve clean; a synthetic defs folder with one bad godTie, one bad payload incident and one
bad faction must report exactly those three; with no game Data a vanilla-only name is UNMEASURED, never bad and
never silently fine. Then the chain runs through a mock session and must PASS on the real tree.
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
from modcheck import Suite                                     # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
BAD = """<Defs>
  <RimMandrake.Aftermath.RM_AftermathRuleDef><defName>R_Good</defName><payloadIncidentDefName>RaidEnemy</payloadIncidentDefName><godTie>Shkaar</godTie></RimMandrake.Aftermath.RM_AftermathRuleDef>
  <RimMandrake.Aftermath.RM_AftermathRuleDef><defName>R_BadGod</defName><payloadIncidentDefName>RaidEnemy</payloadIncidentDefName><godTie>Shkar</godTie></RimMandrake.Aftermath.RM_AftermathRuleDef>
  <RimMandrake.Aftermath.RM_AftermathRuleDef><defName>R_BadInc</defName><payloadIncidentDefName>RaidEnemyy</payloadIncidentDefName></RimMandrake.Aftermath.RM_AftermathRuleDef>
  <RimMandrake.Aftermath.RM_AlliancePairDef><defName>P_Bad</defName><a>Pirate</a><b>RUT_NoSuchFaction</b></RimMandrake.Aftermath.RM_AlliancePairDef>
</Defs>"""
INDEX = {"IncidentDef": {"RaidEnemy"}, "FactionDef": {"Pirate", "Empire"}}


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def main():
    gods = V.god_names()
    check("God.cs parses to the nine Ninefold gods", len(gods) == 9 and "MobUnloo" in gods, sorted(gods))

    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "a.xml"), "w") as fh:
            fh.write(BAD)
        bad, unm, nr, np_ = V.cross_ref_problems(defs_dir=tmp, gods=gods, index=INDEX, game_ok=True)
        check("synthetic: 3 rules and 1 pair parsed", (nr, np_) == (3, 1), (nr, np_))
        check("synthetic: exactly the bad god, incident and faction are reported",
              len(bad) == 3 and any("Shkar'" in b for b in bad) and any("RaidEnemyy" in b for b in bad)
              and any("RUT_NoSuchFaction" in b for b in bad) and not unm, bad)
        bad2, unm2, _r, _p = V.cross_ref_problems(defs_dir=tmp, gods=gods, index={}, game_ok=False)
        check("no game Data: vanilla names are UNMEASURED; the bad god and our own missing faction stay bad",
              len(bad2) == 2 and any("Shkar'" in b for b in bad2) and any("RUT_NoSuchFaction" in b for b in bad2)
              and len(unm2) == 4, (bad2, unm2))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    game_ok = os.path.isdir(V._GAME_DATA)
    index = V.def_index([V._SRC] + ([V._GAME_DATA] if game_ok else []))
    bad, unm, nr, np_ = V.cross_ref_problems(gods=gods, index=index, game_ok=game_ok)
    check("shipped defs: 8 rules, 6 pairs, nothing unresolvable", (nr, np_, bad) == (8, 6, []), (nr, np_, bad))
    if not game_ok:
        print("note  game Data unreachable: vanilla names UNMEASURED here: %s" % unm)

    suite = Suite("AftermathRitesCrossRefs")
    suite.chain("cross_refs_resolve_by_name")(V.cross_refs_resolve_by_name)
    s = FastSession(transport=MockTransport(MockGame()), strict=False)
    with s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    comps = [(c["name"], c["verdict"]) for ch in res["chains"] for c in ch["components"]]
    want = "PASS" if game_ok else "UNMEASURED"
    check("the chain records %s on the real tree through a session" % want,
          comps == [("gods_incidents_and_factions_resolve", want)], comps)

    if FAILS:
        print("\n%d AftermathRites selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall AftermathRites cross-ref selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
