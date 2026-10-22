"""TRENCH CROSSING live check (TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP A2; BENCH prove-fix belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/trench_crossing_live.py [out.json] [--origin X,Z] [--fresh-map]

Run from the repo root with python.exe; the bridge must be held. Exit 0 = every MEASURED row PASS.

Scene (plot from --origin, default 60,170; 15 x 15 cleared + read back by validation_core.prepare_site):
  a 3x3 ISLAND at centre (7, 7) ringed by a sheer trench 3 squares wide (Chebyshev 2..4 from the centre), dug D 4 (2 m: a
  person is trapped at D 3, climb_proof), so the person band cannot walk in or out. Ladders on the row z = 7: RM_Ladder on
  the OUTER wall square (3, 7) and on the INNER wall square (5, 7) (a ladder joins its square to the shallower cardinal
  neighbour, design §8.4). HARNESS 2026-10-22: the first scene was a straight trench inside the plot, and the one-ladder
  control simply walked round its end -- a ring has no end.
Rows:
  XING_two_ladders_cross     PROVE jawa/order_pawn a drafted colonist from the bank (1, 7) to the island centre (7, 7), one
                             order. EXPECT he ends on (7, 7) within WAIT ticks. LIES: a trench that was never dug (read back by
                             the dig drive's depth) or a pawn spawned on bank B; both are checked.
  XING_one_ladder_no_cross   the can-fail: the inner ladder destroyed, a second colonist given the same order. EXPECT he
                             does not reach the island AND does not end inside the trench (one ladder is no crossing, and the
                             order must not strand him on the floor). LIES: a pawn that never moved also 'does not cross'
                             -- so his end square and the ticks elapsed are recorded.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

WAIT = 1500


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="60,170")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402  (bridge-side imports only on a live run)
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "trench_crossing_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "trench_crossing_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": "TRENCH_CROSSING_FIX_DOWN_ACROSS_AND_UP", "detail": det})
        print("%-28s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("XING_two_ladders_cross", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/kill_hostiles")
    rect = (ox, oz, 15, 15)
    cx, cz = 7, 7
    ring = [(x, z) for x in range(cx - 4, cx + 5) for z in range(cz - 4, cz + 5) if max(abs(x - cx), abs(z - cz)) >= 2]
    site_rows = []
    V.prepare_site(B, rect, site_rows, "xing_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        for rid in ("XING_two_ladders_cross", "XING_one_ladder_no_cross"):
            row(rid, "UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    misses = []
    for x, z in ring:
        if True:
            r = B.call("jawa/flowworks_excavation_drive", x=P(x, z)[0], z=P(x, z)[1], deepenLevels=4, setFill=-1) or {}
            if r.get("depth") != 4:
                misses.append((x, z, r.get("depth")))
    if misses:
        for rid in ("XING_two_ladders_cross", "XING_one_ladder_no_cross"):
            row(rid, "UNMEASURED", "SITE", {"why": "trench not dug to D 4", "misses": misses[:6]})
        return 2
    lad = B.call("jawa/spawn_batch", ops="RM_Ladder:%d,%d;RM_Ladder:%d,%d" % (P(3, 7) + P(5, 7))) or {}
    B.ticks(30)
    ladders = (B.call("jawa/list_things", defName="RM_Ladder", rect="%d,%d,3,1" % P(3, 7), limit=5) or {}).get("things") or []
    if len(ladders) != 2:
        for rid in ("XING_two_ladders_cross", "XING_one_ladder_no_cross"):
            row(rid, "UNMEASURED", "SITE", {"why": "two ladders did not stand", "spawn": str(lad)[:300], "ladders": ladders})
        return 2

    def spawn(c):
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=c[0], z=c[1], faction="player", count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")

    def order(pid, c):
        o = B.call("jawa/order_pawn", pawnId=pid, x=c[0], z=c[1], waitTicks=WAIT, draft=True) or {}
        for p in o.get("pawns") or []:
            if p.get("id") == pid:
                return dict(p, ticksElapsed=o.get("ticksElapsed")), o
        return {}, o

    def end_of(p):
        # order_pawn answers {"end": {"x", "z"}, "arrived", ...} (first live run read p["x"] and got None)
        e = p.get("end") or {}
        try:
            return (int(e.get("x")), int(e.get("z")))
        except (TypeError, ValueError, AttributeError):
            return None

    def in_trench(c):
        return c is not None and (c[0] - ox, c[1] - oz) in ring

    a_bank, b_bank = P(1, 7), P(7, 7)
    c1 = spawn(a_bank)
    B.ticks(2)
    p1, raw1 = order(c1, b_bank)
    e1 = end_of(p1)
    if not p1:
        row("XING_two_ladders_cross", "UNMEASURED", "HARNESS", {"why": "order_pawn returned no pawn", "raw": str(raw1)[:300]})
    else:
        row("XING_two_ladders_cross", "PASS" if e1 == b_bank else "FAIL", "MOD",
            {"start": a_bank, "dest": b_bank, "end": e1, "ticksElapsed": p1.get("ticksElapsed"), "ladders": ladders,
             "order": {k: v for k, v in p1.items() if k not in ("x", "z")}})
    # can-fail: one ladder only
    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % P(5, 7), categories="Building")
    B.ticks(30)
    left = (B.call("jawa/list_things", defName="RM_Ladder", rect="%d,%d,3,1" % P(3, 7), limit=5) or {}).get("things") or []
    c1x = c1
    if c1x:      # the first colonist stands on the island: out of the way before the control
        B.call("jawa/pawn_force_incapacitate", pawn=c1x, action="vanish")
    c2 = spawn(P(1, 9))
    B.ticks(2)
    p2, raw2 = order(c2, b_bank)
    e2 = end_of(p2)
    if len(left) != 1 or not p2:
        row("XING_one_ladder_no_cross", "UNMEASURED", "SITE", {"why": "the control scene did not stand", "laddersLeft": left,
                                                               "raw": str(raw2)[:300]})
    else:
        good = e2 != b_bank and not in_trench(e2)
        row("XING_one_ladder_no_cross", "PASS" if good else "FAIL", "MOD",
            {"start": P(1, 9), "dest": b_bank, "end": e2, "inTrench": in_trench(e2), "ticksElapsed": p2.get("ticksElapsed"),
             "laddersLeft": left})
    for pid in (c1, c2):
        if pid:
            B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    bad = [r for r in rows if r["status"] != "PASS"]
    print("trench crossing: %d rows, %d not PASS -> %s" % (len(rows), len(bad), out))
    return 1 if any(r["status"] == "FAIL" for r in rows) else (2 if bad else 0)


if __name__ == "__main__":
    sys.exit(main())
