"""STATION REACH live check (STATION_REACH_CENTRE_RETHINK_FOOTPRINT A2: "a live pumping station draws from water 4 cells off
its long side and not 5"; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/station_reach_live.py [out.json] [--origin X,Z] [--fresh-map]

Two identical scenes 20 squares apart: an RM_PumpingStation_Repaired (3x2, rot North, placed at (4, 4): it covers x 3..5,
z 4..5; reach 4 from the footprint, P11) in DRAW mode (RM_NorthstarProofs.ProofPump ";draw"), an empty RM_LiquidTank touching its east end (6, 4),
a charged Battery wired by PowerConduit; a 3-square dug channel (2 notches, filled) parallel to the long north side at
z = 9 (4 off: scene A) or z = 10 (5 off: scene B). 1000 ticks.
Rows:
  STATION_DRAWS_AT_4    EXPECT scene A's tank gained units / the channel's water fell (ProofPump moved > 0).
  STATION_SKIPS_AT_5    EXPECT scene B moved nothing (tank 0, channel unchanged) while powered. LIES: an unpowered station
                        also moves nothing -> UNMEASURED unless ProofPump read running=True.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
ITEM = "STATION_REACH_CENTRE_RETHINK_FOOTPRINT"


def kv(txt):
    out = {}
    for tok in (txt or "").replace("|", " ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out



def _tank_units(s):
    tank = s["kv"].get("tank") or ""
    tail = tank.split(":")[-1]
    return int(tail) if ":" in tank and tail.isdigit() else None


def moved(s):
    """-> (moved, tank units): water moved into the station's tank, or the channel it draws from fell. A fall is only
    read when every channel fill answered both times: an unread cell after the wait (None) is no drop."""
    units = _tank_units(s) or 0
    w0, w1 = list(s.get("water0") or []), list(s.get("water1") or [])
    read = bool(w0) and len(w0) == len(w1) and all(x is not None for x in w0 + w1)
    return units > 0 or (read and sum(w1) < sum(w0)), units


def rig_readable(s):
    """True when the scene can show a draw: ProofPump named a tank (not tank=none) and every channel fill read answered."""
    w = list(s.get("water0") or []) + list(s.get("water1") or [])
    return _tank_units(s) is not None and bool(s.get("water0")) and bool(s.get("water1")) and all(x is not None for x in w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="60,30")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "station_reach_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "station_reach_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-22s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:500]), flush=True)
        save()

    ox, oz = (int(v) for v in a.origin.split(","))
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("STATION_DRAWS_AT_4", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    rect = (ox, oz, 34, 14)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "station_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        for rid in ("STATION_DRAWS_AT_4", "STATION_SKIPS_AT_5"):
            row(rid, "UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    scenes = {}
    for name, dx, off in (("A", 0, 4), ("B", 20, 5)):
        P = lambda x, z, dx=dx: (ox + dx + x, oz + z)  # noqa: E731
        st, tank, bat = P(4, 4), P(6, 4), P(0, 4)      # a 3x2 at Position (4,4) covers x 3..5, z 4..5
        chan = [P(4 + i, 5 + off) for i in range(3)]
        for c in chan:
            B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=2, setFill=2)
        ops = ["RM_PumpingStation_Repaired:%d,%d" % st, "RM_LiquidTank:%d,%d" % tank, "Battery:%d,%d" % bat,
               "PowerConduit:%d,%d" % P(1, 4), "PowerConduit:%d,%d" % P(2, 4)]
        bb = B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False) or {}
        scenes[name] = dict(st=st, tank=tank, bat=bat, chan=chan, off=off, build=str(bb)[:300])
    B.ticks(2)
    for name, s in scenes.items():
        lt = (B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % s["bat"], limit=2) or {}).get("things") or [{}]
        if lt[0].get("id") is not None:
            B.call("jawa/battery_set", thing=lt[0]["id"], mode="setPct", value=1.0)
        s["draw"] = str((B.call("jawa/static_call", type=NSP, method="ProofPump", args="%d,%d;draw" % s["st"], _answer=True) or {}).get("result"))
        s["water0"] = [(B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=-1) or {}).get("fill") for c in s["chan"]]
    B.ticks(1000)
    for name, s in scenes.items():
        r = B.call("jawa/static_call", type=NSP, method="ProofPump", args="%d,%d" % s["st"], _answer=True) or {}
        t = str(r.get("result") or r.get("message"))
        s["after"] = t
        s["water1"] = [(B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=-1) or {}).get("fill") for c in s["chan"]]
        s["kv"] = kv(t)
    res["scenes"] = scenes
    a_, b_ = scenes["A"], scenes["B"]

    ma, ua = moved(a_)
    mb, ub = moved(b_)
    run_a, run_b = a_["kv"].get("running") == "True", b_["kv"].get("running") == "True"
    rig_b = rig_readable(b_)
    row("STATION_DRAWS_AT_4", "UNMEASURED" if not run_a else ("PASS" if ma else "FAIL"), "SITE" if not run_a else "MOD",
        {"after": a_["after"], "water": [a_["water0"], a_["water1"]], "tankUnits": ua, "off": 4})
    # GPT review 5.4: "did not move" is only evidence when the station had a receiving tank and every water read answered
    row("STATION_SKIPS_AT_5", "UNMEASURED" if not (run_b and rig_b) else ("PASS" if not mb else "FAIL"),
        "SITE" if not (run_b and rig_b) else "MOD",
        {"after": b_["after"], "water": [b_["water0"], b_["water1"]], "tankUnits": ub, "off": 5, "tank": b_["kv"].get("tank"),
         "rigReadable": rig_b})
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return V.rows_exit(rows)     # review 2026-10-26: FAIL -> 1, UNMEASURED -> 2 (was 1)


if __name__ == "__main__":
    sys.exit(main())
