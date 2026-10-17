#!/usr/bin/env python3
"""selftest_flowworks_driver_rows.py -- validation.py's THIRST_LIVE / SPRINKLER_LIVE rows read the walk drivers' results.

northstar/thirst_live.py and northstar/sprinkler_live.py (2026-10-17 review walk) each run a subset of rows and write a
result JSON into northstar/. validation.py (driver_rows_at, _driver_live_report) turns them into components. This reds on:
a result at another mod hash, not live, or from a game running another DLL being read; an older row beating a newer one for the same id; T21/T22 (thirst rows
the sprinkler driver measures) not reaching the thirst chain; a missing row reading anything but UNMEASURED; a driver FAIL
not failing its component; one FAIL/UNMEASURED row blanking the rows after it; a live row losing its toggle declaration.
No game, no bridge, no files outside a temp dir.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(os.path.dirname(HERE), "Utils"), os.path.join(HERE, "northstar"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import validation as V  # noqa: E402
from modcheck import status as ST  # noqa: E402
from modcheck import TestContext  # noqa: E402 - modcheck re-exports the top-level `suite` module's classes (identity matters)

FAILS = []


def check(what, ok):
    print("%s  %s" % ("ok  " if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def write(d, name, started, h, rows, mode="live", dll="DLL"):
    with open(os.path.join(d, name), "w", encoding="utf-8") as f:
        json.dump({"mode": mode, "mod_hash": h, "started": started, "rows": rows, "env": {"assembly_sha256": dll}}, f)


class _T(TestContext):
    def __init__(self):
        super(_T, self).__init__(session=None)


def main():
    d = tempfile.mkdtemp(prefix="fw_driver_rows_")
    write(d, "thirst_live_result_a.json", "2026-10-17T10:00:00", "H",
          [{"id": "T15_slime_effects", "status": "PASS"}, {"id": "T2_one_thirst_need", "status": "PASS", "detail": {"x": 1}}])
    write(d, "thirst_live_result_b.json", "2026-10-17T11:00:00", "H", [{"id": "T15_slime_effects", "status": "FAIL",
                                                                         "class": "MOD", "detail": {"bad": ["red drank white"]}}])
    write(d, "sprinkler_live_result_c.json", "2026-10-17T09:00:00", "H", [{"id": "T21_drinking_reserve", "status": "PASS"}])
    write(d, "thirst_live_result_d.json", "2026-10-17T12:00:00", "OLD", [{"id": "T2_one_thirst_need", "status": "FAIL"}])
    write(d, "thirst_live_result_e.json", "2026-10-17T12:00:00", "H", [{"id": "T3_need_falls", "status": "PASS"}], mode="partial")
    write(d, "thirst_live_result_f.json", "2026-10-17T12:30:00", "H", [{"id": "T4_bottle_satisfies", "status": "UNMEASURED",
                                                                         "class": "SITE"}])
    write(d, "thirst_live_result_g.json", "2026-10-17T13:00:00", "H", [{"id": "T5_salt_water_quality", "status": "PASS"}],
          dll="OLDDLL")
    write(d, "thirst_live_result_h.json", "2026-10-17T13:00:00", "H", [{"id": "T6_dehydration_readable", "status": "PASS"}],
          dll=None)
    g = V.driver_rows_at("H", ns=d, dll_sha="dll")
    check("newest row per id wins (later FAIL over earlier PASS)", g.get("T15_slime_effects", ({},))[0].get("status") == "FAIL")
    check("a result at another mod hash is not read", g.get("T2_one_thirst_need", ({},))[0].get("status") == "PASS")
    check("a non-live result is not read", "T3_need_falls" not in g)
    check("the sprinkler driver's T21 is in the pool", "T21_drinking_reserve" in g)
    check("no mod hash -> nothing read", V.driver_rows_at(None, ns=d, dll_sha="DLL") == {})
    check("a game running another DLL is not read (an undeployed fix certifies nothing)", "T5_salt_water_quality" not in g)
    check("a result without the assembly sha is not read", "T6_dehydration_readable" not in g)
    check("no repo DLL sha -> nothing read", V.driver_rows_at("H", ns=d) == {})

    # the chain half, on a real TestContext with the pool and the hash pinned
    real_at, real_hash = V.driver_rows_at, ST.mod_hash
    V.driver_rows_at = lambda h, ns=None, dll_sha=None: real_at("H", ns=d, dll_sha="DLL")
    ST.mod_hash = lambda _dir: "H"
    try:
        t = _T()
        V._driver_live_report(t, V.THIRST_LIVE, "thirst_live.py", "ITEM")
    finally:
        V.driver_rows_at, ST.mod_hash = real_at, real_hash
    by = {c.name: c for c in t.components}
    check("one component per THIRST_LIVE row", [c.name for c in t.components] == [r[0] for r in V.THIRST_LIVE])
    check("driver FAIL -> FAIL", by["T15_slime_effects"].verdict == "FAIL")
    check("driver PASS -> PASS (after a FAIL row: not blanked)", by["T2_one_thirst_need"].verdict == "PASS")
    check("T21 read from the sprinkler driver -> PASS", by["T21_drinking_reserve"].verdict == "PASS")
    check("driver UNMEASURED -> UNMEASURED", by["T4_bottle_satisfies"].verdict == "UNMEASURED")
    check("absent row -> UNMEASURED naming the driver",
          by["T16_living_slime"].verdict == "UNMEASURED" and "thirst_live.py" in (by["T16_living_slime"].detail or ""))
    check("absent T22 names the sprinkler driver", "sprinkler_live.py" in (by["T22_no_brine_spray"].detail or ""))
    check("PASS carries its evidence", any("T2_one_thirst_need" in e.get("call", "") for e in by["T2_one_thirst_need"].evidence))

    decl = {}
    probe_t = V.suite.components_declared()
    check("the declaration probe still runs", len(probe_t) > 0)
    for rid, toggle, _ in V.THIRST_LIVE + V.SPRINKLER_LIVE:
        decl[rid] = toggle
    toggles = {x["toggle"] for x in probe_t if x["toggle"]}
    check("every live row's toggle is declared", all(tg in toggles for tg in decl.values() if tg))
    print("%s: %d failing" % (os.path.basename(__file__), len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
