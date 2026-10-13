"""BENCH live checks round 1 (2026-10-13): POND_RETURN_LEG_BUILD_WATER_GOES_HOME.

A1 channel route (short form, 6-cell limited pond): pond -> pump1 draw -> tank -> pump2 Pour -> dug channel B ->
   pump2 draw -> tank -> pump1 Pour -> pond. L0 ledger (FlowWorksDebugActions.ReportLedger) read at every phase,
   equal within 1e-3; the pond's wet set at the end equals the fresh snapshot. Two pumps on one pipe net; only one is
   switched on at a time (flick). pump1 touches only the pond, pump2 touches only B.
A2 occupied-bed refill delay: draw the pond down again; a drafted colonist on dry bed square s1, a PowerConduit on s2,
   a Steel stack on s3; refill on (rate COMPRESSED, restored after). Expect: s1, s2 stay dry while the rest re-wets;
   s3 re-wets and the Steel ends on dry shore (not a pond square). Then remove pawn + conduit: s1, s2 re-wet.

Governed time only (B.ticks -> jawa/safe_advance in 250-tick steps). Run from a git-archive root under python.exe:
  python.exe pond_channel_probe.py <out.json> [--origin X,Z] [--fresh-map] [--refill-rate R]
"""
import argparse
import json
import os
import re
import sys
import time

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar"))
import proof_hose as PH  # noqa: E402

LOG = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
EPS = 1e-3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--origin", default="150,40")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--refill-rate", type=float, default=300.0)
    ap.add_argument("--max-cycles", type=int, default=14)
    a = ap.parse_args()
    V = PH.V
    B = PH.PB()
    res = {"script": "pond_channel_probe.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": [], "phases": []}

    def save():
        with open(a.out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(a.out + ".tmp", a.out)

    def row(rid, st, det):
        res["rows"].append({"id": rid, "status": st, "detail": det})
        print("%-44s %-10s %s" % (rid, st, json.dumps(det, default=str)[:700]), flush=True)
        save()

    def tg():
        g = B.call("rimworld/get_game_info")
        return g.get("ticksGame") or (g.get("state") or {}).get("tick")

    def sget(f):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    def ledger():
        r = B.call("jawa/static_call", type="RimMandrake.FlowWorks.FlowWorksDebugActions", method="ReportLedger", args="")
        time.sleep(1.0)
        with open(LOG, "r", encoding="utf-8", errors="replace") as f:
            lines = [l for l in f.read().splitlines() if "L0 ledger (tank units)" in l]
        line = lines[-1] if lines else ""
        m = re.search(r"total=([0-9.\-]+)", line)
        return {"call": r.get("success"), "line": line, "total": float(m.group(1)) if m else None, "n": len(lines)}

    def terr(c):
        return ((B.call("rimworld/get_cell_info", x=c[0], z=c[1]) or {}).get("cell") or {}).get("terrainDefName")

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)                        # noqa: E731
    pond = [P(x, z) for z in (5, 6) for x in (2, 3, 4)]
    pump1, tank, pump2 = P(3, 7), P(3, 10), P(7, 8)
    battery = P(6, 5)
    chanB = [P(8, 7), P(8, 8), P(8, 9)]

    def wet():
        return {"%d,%d" % c: terr(c) for c in pond}

    def body():
        r = B.call("jawa/flowworks_body_report", x=P(3, 6)[0], z=P(3, 6)[1], classify=False) or {}
        return r.get("body") or {}

    def units():
        r = B.hp("tank:%d,%d" % tank)
        return r.get("units") if r.get("success") else None

    def bfill():
        return [(B.call("jawa/flowworks_excavation_report", x=c[0], z=c[1]) or {}).get("fill") for c in chanB]

    def only(on):
        """Switch exactly one pump on (flick), the other off; read back both."""
        off = pump2 if on == pump1 else pump1
        return {"on": B.hp("flick:%d,%d=on" % on), "off": B.hp("flick:%d,%d=off" % off)}

    def run_phase(name, stop):
        tr = []
        for _ in range(a.max_cycles):
            B.ticks(250)
            bd = body()
            tr.append({"tick": tg(), "units": units(), "stock": bd.get("stock"), "receded": bd.get("recededCount"),
                       "B": bfill()})
            if stop(tr):
                break
        L = ledger()
        ph = {"phase": name, "trace": tr, "ledger": L.get("total"), "ledgerLine": L.get("line")}
        res["phases"].append(ph)
        save()
        print("phase %-10s ledger %s  end %s" % (name, L.get("total"), json.dumps(tr[-1] if tr else None)), flush=True)
        return ph

    def stalled(tr, k="units"):
        return len(tr) > 2 and tr[-1].get(k) == tr[-2].get(k) == tr[-3].get(k)

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, waited = V._wait_playing(B, leave_s=0)
    B.hp("defaults")
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    FIELDS = ("refillEnabled", "refillRateMultiplier", "refillWaitsForOccupants", "recessionEnabled", "liquidPumpEnabled",
              "tankCapacityMultiplier")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before
    spawned_pawn = None
    try:
        if not ok or not V.prepare_site(B, (ox, oz, 24, 24), res["rows"], "SITE_ready"):
            row("SITE", "UNMEASURED", {"why": "site not ready / not playing"})
            return 2
        # draft every colonist so none wanders onto the bed (the A2 occupants are placed by hand)
        cols = B.call("rimworld/list_colonists", currentMapOnly=True).get("colonists") or []
        res["drafted"] = [B.call("jawa/set_draft", pawnId=str(c.get("pawnId") or c.get("id")), drafted=True).get("success")
                          for c in cols]
        sset("refillEnabled", False)
        sset("liquidPumpEnabled", True)
        B.call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,3,2" % P(2, 5))
        cls = (B.call("jawa/flowworks_body_report", x=P(3, 6)[0], z=P(3, 6)[1], classify=True) or {}).get("body") or {}
        res["pond"] = {k: cls.get(k) for k in ("cellCount", "capacity", "stock", "limitless")}
        ops = ["RM_LiquidPump:%d,%d" % pump1, "RM_UniversalPipe:%d,%d" % P(3, 8), "RM_UniversalPipe:%d,%d" % P(3, 9),
               "RM_LiquidTank:%d,%d" % tank, "RM_UniversalPipe:%d,%d" % P(4, 8), "RM_UniversalPipe:%d,%d" % P(5, 8),
               "RM_UniversalPipe:%d,%d" % P(6, 8), "RM_LiquidPump:%d,%d" % pump2, "Battery:%d,%d" % battery]
        bb = B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False)
        res["build"] = {k: bb.get(k) for k in ("success", "built", "failed")}
        B.ticks(2)
        lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,1,2" % battery, limit=2) or {}
        bid = ((lt.get("things") or [{}])[0]).get("id")
        if bid is not None:
            B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
        res["digB"] = [B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=2, setFill=0).get("success")
                       for c in chanB]
        B.ticks(2)
        res["B0"] = [B.call("jawa/flowworks_excavation_report", x=c[0], z=c[1]) for c in chanB]
        snap = wet()
        res["wet_snapshot"] = snap
        L0 = ledger()
        res["phases"].append({"phase": "start", "ledger": L0["total"], "ledgerLine": L0["line"], "units": units(),
                              "B": bfill(), "pumps": [B.hp("pump:%d,%d" % pump1), B.hp("pump:%d,%d" % pump2)]})
        print("L0 start:", L0["line"], flush=True)
        # 1 pond -> tank (pump1 draw)
        res["sw1"] = only(pump1)
        B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofPump", args="%d,%d;draw" % pump1)
        B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofPump", args="%d,%d;draw" % pump2)
        p1 = run_phase("pond_draw", lambda tr: stalled(tr))
        drew = (p1["trace"][-1].get("units") or 0) if p1["trace"] else 0
        # 2 tank -> B (pump2 pour); tank jobs off so Pour drains any tank (Building_LiquidPump.TryPour)
        res["tankModesOff"] = B.hp("set:tankModesEnabled=False")
        res["sw2"] = only(pump2)
        B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofPump", args="%d,%d;pour" % pump2)
        p2 = run_phase("B_pour", lambda tr: stalled(tr))
        inB = sum(x or 0 for x in (p2["trace"][-1]["B"] if p2["trace"] else []))
        # 3 B -> tank (pump2 draw)
        B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofPump", args="%d,%d;draw" % pump2)
        p3 = run_phase("B_draw", lambda tr: sum(x or 0 for x in tr[-1]["B"]) == 0 or stalled(tr))
        outB = sum(x or 0 for x in (p3["trace"][-1]["B"] if p3["trace"] else [1]))
        # 4 tank -> pond (pump1 pour)
        res["sw4"] = only(pump1)
        B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofPump", args="%d,%d;pour" % pump1)
        p4 = run_phase("pond_pour", lambda tr: tr[-1].get("units") == 0 or stalled(tr))
        B.ticks(260)
        Lend = ledger()
        after = wet()
        bend = body()
        totals = [L0["total"], p1["ledger"], p2["ledger"], p3["ledger"], p4["ledger"], Lend["total"]]
        cons = all(t is not None for t in totals) and max(totals) - min(totals) <= EPS
        same = after == snap
        moved = drew > 0 and inB > 0 and outB == 0
        det = {"tankAfterDraw": drew, "levelsIntoB": inB, "BafterDraw": outB, "ledger": totals, "wetSetEqualsSnapshot": same,
               "after": after, "snapshot": snap, "bodyEnd": {k: bend.get(k) for k in ("stock", "capacity", "recededCount")},
               "tankEnd": units()}
        if not moved:
            row("A1_channel_route_round_trip", "UNMEASURED", dict(det, why="a leg moved nothing (see phases)"))
        else:
            row("A1_channel_route_round_trip", "PASS" if cons and same else "FAIL", det)
        # ---------------- A2: occupied bed squares delay refill
        res["sw5"] = only(pump1)
        B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofPump", args="%d,%d;draw" % pump1)
        res["tankModesOn"] = B.hp("set:tankModesEnabled=True")
        run_phase("A2_draw", lambda tr: stalled(tr))
        res["sw6"] = {"off1": B.hp("flick:%d,%d=off" % pump1), "off2": B.hp("flick:%d,%d=off" % pump2)}
        B.ticks(260)
        w = wet()
        dry = [c for c in pond if w["%d,%d" % c] != "WaterShallow"]
        res["A2_dry"] = dry
        if len(dry) < 3:
            row("A2_occupied_bed_waits", "UNMEASURED", {"why": "fewer than 3 dry bed squares after the draw", "wet": w})
            return 2
        s1, s2, s3 = dry[0], dry[1], dry[2]
        sp = B.call("jawa/spawn_pawn", kindDef="Colonist", x=s1[0], z=s1[1], faction="player")
        pid = None
        for p in sp.get("pawns") or sp.get("spawned") or []:
            pid = p.get("id") or p.get("pawnId") or p.get("thingId")
        spawned_pawn = pid
        res["A2_pawn"] = {"spawn": {k: sp.get(k) for k in ("success", "pawns", "spawned", "error")}, "id": pid,
                          "draft": B.call("jawa/set_draft", pawnId=str(pid), drafted=True) if pid else None}
        res["A2_conduit"] = {k: v for k, v in (B.call("jawa/build_batch", ops="PowerConduit:%d,%d" % s2, faction="player",
                                                      wipeExisting=False) or {}).items() if k in ("success", "built", "failed")}
        res["A2_steel"] = B.call("rimworld/spawn_thing", defName="Steel", x=s3[0], z=s3[1])
        B.ticks(2)

        def where_pawn():
            if not pid:
                return None
            for p in B.call("jawa/list_pawns", faction="player", limit=100).get("pawns") or []:
                if str(p.get("id")) == str(pid) or str(p.get("pawnId")) == str(pid):
                    return p.get("position") or p.get("pos") or [p.get("x"), p.get("z")]
            return None

        def steel_at():
            lt = B.call("jawa/list_things", defName="Steel", rect="%d,%d,24,24" % (ox, oz), limit=20) or {}
            return [(t.get("position") or t.get("pos") or [t.get("x"), t.get("z")]) for t in lt.get("things") or []]

        res["A2_placed"] = {"pawnAt": where_pawn(), "steelAt": steel_at(), "s1": s1, "s2": s2, "s3": s3}
        sset("refillRateMultiplier", a.refill_rate)
        sset("refillEnabled", True)
        tr = []
        for _ in range(12):
            B.ticks(250)
            w = wet()
            bd = body()
            tr.append({"tick": tg(), "stock": bd.get("stock"), "cap": bd.get("capacity"), "receded": bd.get("recededCount"),
                       "wet": w, "pawnAt": where_pawn()})
            others = [c for c in pond if c not in (s1, s2)]
            if all(w["%d,%d" % c] == "WaterShallow" for c in others) and (bd.get("stock") or 0) >= (bd.get("capacity") or 1e9) - EPS:
                break
        res["A2_trace"] = tr
        last = tr[-1]["wet"]
        steel = steel_at()
        pondset = {tuple(c) for c in pond}
        steel_ashore = bool(steel) and all(tuple(s[:2]) not in pondset for s in steel if s and s[0] is not None)
        others_wet = all(last["%d,%d" % c] == "WaterShallow" for c in pond if c not in (s1, s2))
        held = last["%d,%d" % s1] != "WaterShallow" and last["%d,%d" % s2] != "WaterShallow"
        pawn_stayed = (tr[-1].get("pawnAt") or [None])[:2] == list(s1)
        det = {"s1_pawn": s1, "s2_conduit": s2, "s3_steel": s3, "endWet": last, "steelNow": steel, "steelAshore": steel_ashore,
               "pawnStayed": pawn_stayed, "stockEnd": tr[-1]["stock"], "cap": tr[-1]["cap"], "ticks": len(tr) * 250,
               "refillRateMultiplier": a.refill_rate}
        if not others_wet:
            row("A2_occupied_bed_waits", "UNMEASURED", dict(det, why="refill did not reach the free squares in the bounded wait"))
        elif not pawn_stayed:
            row("A2_occupied_bed_waits", "UNMEASURED", dict(det, why="the colonist left s1; the pawn half is not measured"))
        else:
            row("A2_occupied_bed_waits", "PASS" if held and steel_ashore and last["%d,%d" % s3] == "WaterShallow" else "FAIL", det)
        # release: remove the pawn and the conduit -> s1, s2 re-wet
        rel = {}
        if pid:
            rel["pawnWalk"] = {k: v for k, v in (B.call("jawa/order_pawn", pawnId=str(pid), x=P(12, 2)[0], z=P(12, 2)[1],
                                                         draft=True, waitTicks=400) or {}).items() if k in ("success", "ticksElapsed")}
        rel["conduit"] = {k: v for k, v in (B.call("jawa/destroy_batch", rects="%d,%d,1,1" % s2, categories="Building") or {}).items()
                          if k != "sample"}
        B.ticks(2)
        pa = where_pawn()
        rel["pawnNow"] = pa
        rel["pawnGone"] = not pa or list(pa[:2]) != list(s1)
        rel["conduitGone"] = not ((B.call("jawa/list_things", defName="PowerConduit", rect="%d,%d,1,1" % s2, limit=2) or {}).get("things"))
        res["A2_release"] = rel
        tr2 = []
        for _ in range(8):
            B.ticks(250)
            w = wet()
            tr2.append({"tick": tg(), "s1": w["%d,%d" % s1], "s2": w["%d,%d" % s2], "stock": body().get("stock")})
            if tr2[-1]["s1"] == "WaterShallow" and tr2[-1]["s2"] == "WaterShallow":
                break
        res["A2_release_trace"] = tr2
        ok2 = bool(tr2) and tr2[-1]["s1"] == "WaterShallow" and tr2[-1]["s2"] == "WaterShallow"
        row("A2_freed_squares_rewet", "PASS" if ok2 else ("UNMEASURED" if not (rel["pawnGone"] and rel["conduitGone"]) else "FAIL"),
            {"release": rel, "trace": tr2})
        return 0
    finally:
        res["hose_defaults_restored"] = B.hp("defaults")
        res["settings_restored"] = {f: sset(f, before[f]).get("success") for f in FIELDS if before.get(f) is not None}
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("result:", a.out)


if __name__ == "__main__":
    sys.exit(main())
