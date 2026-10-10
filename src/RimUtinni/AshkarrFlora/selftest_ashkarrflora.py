#!/usr/bin/env python3
"""selftest_ashkarrflora.py -- offline proof for src/RimUtinni/AshkarrFlora/validation.py.

Run bare: python3 src/RimUtinni/AshkarrFlora/selftest_ashkarrflora.py   (exit 0 = clean)

A mock game serves every def this mod ships exactly as its own XML says (statBases via jawa/get_def, the plant
block via jawa/get_defs). The clean run must be all-green; each injected break must redden exactly the component
that owns it -- so the every-shipped-def readback can go red, and goes red for the right reason.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)

import runner                                                  # noqa: E402
import validation as V                                         # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
CHAIN = "every_shipped_def_reads_back"


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def make_ext(brk):
    defs = dict((n, (ty, stats, plant)) for ty, n, stats, plant in V.shipped_defs())

    def ext(game, tool, p):
        if tool == "jawa/get_def":
            _ty, stats, plant = defs.get(p.get("defName"), (None, {}, {}))
            stats = dict(stats)
            if "stat_drift" in brk and p.get("defName") == "RUT_Grellbush":
                stats["MaxHitPoints"] = "999"
            # a live readback carries the sweetline's expected stats as the original chain asserts them
            if p.get("defName") == V.DEF_NAME:
                stats.update(V.EXPECT_STATBASES)
            return {"success": True, "statBases": stats}
        if tool == "jawa/get_defs":
            want = [s.split("/", 1)[1] for s in str(p.get("defs") or "").split(";") if "/" in s]
            rows, missing = [], []
            for n in want:
                if n not in defs or ("not_loaded" in brk and n == "RUT_Fuzz"):
                    missing.append(n)
                    continue
                plant = dict(defs[n][2])
                if n == V.DEF_NAME:
                    plant.update(V.EXPECT_PLANT)
                    plant["visualSizeRange"] = {"min": 7.7, "max": 10.0}
                if "plant_drift" in brk and n == "RUT_WildHealroot":
                    plant["growDays"] = "1"
                if "bool_case" in brk and n == "RUT_Grellbush":
                    plant["allowAutoCut"] = "True"          # live bools print capitalised: must still match
                rows.append({"defName": n, "fields": {"plant": plant}})
            return {"success": True, "foundCount": len(rows), "notFound": missing, "requested": len(want),
                    "defs": rows}
        if tool == "rimworld/take_screenshot":
            return {"success": True, "path": "/nonexistent/mock.png"}   # else suite.py falls back to a REAL desktop capture
        if tool == "jawa/drain_log":
            return {"success": True, "messages": []}
        return None
    return ext


def run(brk=()):
    game = MockGame()
    game.ext = make_ext(set(brk))
    saved = V.shipped_defs
    if "blind_parse" in brk:
        V.shipped_defs = lambda defs_dir=None: []
    try:
        s = FastSession(transport=MockTransport(game), strict=False)
        with s:
            res = runner.run_suite(V.suite, s, anchor=None, mod=None)
    finally:
        V.shipped_defs = saved
    out = {}
    for ch in res["chains"]:
        for c in ch["components"]:
            out["%s.%s" % (ch["name"], c["name"])] = (c["verdict"], c.get("detail") or "")
    return out


def reds(result):
    return sorted(k for k, (v, _) in result.items() if v == "FAIL")


def main():
    parsed = V.shipped_defs()
    names = [n for _t, n, _s, _p in parsed]
    check("sanity: the Defs/ parse sees all five shipped defs (six until MATERIAL_MERGES_CLEANUP_1 dropped RUT_SweetlineWool)", len(names) == 5 and "RUT_Grellspine" in names, names)
    check("sanity: plant fields are parsed (RUT_Grellbush growDays 3)",
          dict((n, p) for _t, n, _s, p in parsed).get("RUT_Grellbush", {}).get("growDays") == "3")
    check("ranges are skipped, not compared", all("~" not in v for _t, _n, _s, p in parsed for v in p.values()))

    clean = run()
    check("clean run is all green", not reds(clean), reds(clean))
    ours = [k for k in clean if k.startswith(CHAIN + ".")]
    check("the new chain ran its three components", len(ours) == 3, ours)
    check("its components PASS (not UNMEASURED)", all(clean[k][0] == "PASS" for k in ours),
          dict((k, clean[k]) for k in ours))

    cases = [
        ("stat_drift", {CHAIN + ".every_shipped_def_statbases_match_xml"}),
        ("plant_drift", {CHAIN + ".every_shipped_plant_block_matches_xml"}),
        ("not_loaded", {CHAIN + ".every_shipped_def_is_found_and_the_list_is_sane"}),
        ("blind_parse", {CHAIN + ".every_shipped_def_is_found_and_the_list_is_sane"}),
        ("bool_case", set()),
    ]
    for brk, want in cases:
        got = set(reds(run((brk,))))
        check("break %-12s reddens exactly %s" % (brk, sorted(want)), got == want, "got %s" % sorted(got))

    if FAILS:
        print("\n%d AshkarrFlora selftest(s) FAILED" % len(FAILS))
        return 1
    print("\nall AshkarrFlora suite selftests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
