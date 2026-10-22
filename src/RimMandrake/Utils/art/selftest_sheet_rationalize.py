#!/usr/bin/env python3
"""selftest_sheet_rationalize.py — picture sets are tidied before he sees them (owner, 2026-10-21: "ensure that the art is
'rationalized' … not a tangle of random E, W, S, N facings missing gaps … Same with random pool").

  rationalize_row  `set_merges` builds ONE full set from two half-sets (and IN GAME), never deleting a picture; with
                   `rationalize: true` a set whose every picture is already in another set of its lane is left off (never
                   the in-game set); `drop_sets` leaves off named sets after merging, each with its reason
  poolable         SLX.poolToggle accepts a creature's adult body (g.poolable) and records pool.add; a plain slot refuses
  enact            a lane the snapshot lists in `pools` is a random pool to enact.is_pool, so his '+ random pool' ships

    python3 src/RimMandrake/Utils/art/selftest_sheet_rationalize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def lane():
    return {"res": "X/Beast", "role": "body", "cols": [
        {"letter": "A", "kind": "live", "winner": True, "label": "IN GAME — Mod", "faces": {"south": "as", "east": "ae", "north": "an"}},
        {"kind": "artpipe", "label": "render beast_v1", "faces": {"south": "crate", "east": "ae", "north": "v1n"}},
        {"kind": "artpipe", "label": "render beast_v2", "faces": {"south": "v2s"}},
        {"kind": "artpipe", "label": "render beast_v3", "faces": {"north": "an"}},
        {"kind": "artpipe", "label": "render beast_meat", "faces": {"single": "meat"}}]}


def rationalize_tests():
    import art_sheet as A
    g = lane()
    row = {"key": "RSW_Beast", "set_merges": [{"label": "v2 south + v1 north", "from": {"south": "beast_v2", "east": "IN GAME", "north": "beast_v1"}}],
           "drop_sets": ["beast_v1", "beast_meat"], "drop_why": {"beast_v1": "its south is a crate"}}
    notes = A.rationalize_row(row, [g], rationalize=True)
    labs = [c["label"] for c in g["cols"]]
    m = next((c for c in g["cols"] if c.get("merged")), None)
    check(m is not None and m["faces"] == {"south": "v2s", "east": "ae", "north": "v1n"} and not m["winner"],
          "set_merges: one full set from v2 south + in-game east + v1 north")
    check("render beast_v2" not in labs, "rationalize: the south-only half is left off (the merged set holds it)")
    check("render beast_v3" not in labs, "rationalize: a set that is a copy of in-game pictures is left off")
    check("render beast_v1" not in labs and "render beast_meat" not in labs and any("crate" in n for n in notes),
          "drop_sets: the crate set and the misjoined meat are left off after merging, with the reason")
    check(labs[0].startswith("IN GAME"), "the in-game set is never left off")
    g2 = lane()
    A.rationalize_row({"key": "RSW_Beast"}, [g2], rationalize=False)
    check(len(g2["cols"]) == 5, "nothing is tidied without the census asking for it")
    g3 = lane()
    n3 = A.rationalize_row({"key": "RSW_Beast", "set_merges": [{"label": "bad", "from": {"south": "nope_v9"}}]}, [g3])
    check(len(g3["cols"]) == 5 and any("not built" in n for n in n3), "a merge naming a missing set is reported, not built")


def js_tests():
    import sheet_js_harness as H
    if not H.node():
        print("SKIP js: node not found (UNMEASURED)")
        return
    it = {"id": "RM_Beast", "graphics": [
        {"key": "B/Beast", "lane": "slot", "primary": True, "pool": False, "poolable": True, "slot": {"label": "ADULT"},
         "cols": [{"letter": "A", "winner": True, "faces": {"south": "a"}, "setId": "sa"},
                  {"letter": "B", "kind": "artpipe", "faces": {"south": "b"}, "setId": "sb"}]},
        {"key": "B/Young", "lane": "slot", "primary": False, "pool": False, "slot": {"label": "YOUNG"},
         "cols": [{"letter": "C", "kind": "artpipe", "faces": {"south": "c"}, "setId": "sc"}]}]}
    o = H.run_js("const S = window.SLX; const it = " + json.dumps(it) + "; const q = {};"
                 "const r1 = S.poolToggle(it, q, 'B/Beast', 'B'); const r2 = S.poolToggle(it, q, 'B/Young', 'C');"
                 "console.log(JSON.stringify({r1, r2, pool: q.pool}));")
    check(o["r1"]["ok"] and o["pool"]["B/Beast"]["add"] == ["B"] and o["pool"]["B/Beast"]["baseline"] == ["sa"],
          "poolToggle on a creature's adult body records pool.add [B] with the in-game baseline")
    check(not o["r2"]["ok"] and "B/Young" not in o["pool"], "poolToggle on a plain slot is refused")


def enact_tests():
    import enact as E
    check(E.is_pool(None, None, {"pools": ["B/Beast"]}, "B/Beast", set()),
          "enact.is_pool: a lane the snapshot lists in pools (poolable adult body) takes his pool add")


if __name__ == "__main__":
    rationalize_tests()
    js_tests()
    enact_tests()
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL")
    sys.exit(1 if FAILS else 0)
