"""r5 live probe for POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE A1 (deep middle + walk-out).

Scene (plot from --origin): a 4x3 natural pond, WaterShallow rim with a 2-cell WaterDeep middle at (3,5),(4,5);
a basic RM_LiquidPump on the north bank at (3,7) draws it into two RM_LiquidTanks until the body has receded as far
as recession goes (keep-last-cell leaves one cell wet). Rows:
  PB_pond_limited     the classified body is limited, 12 cells
  PB_bed_shape        every receded cell reads a hollow of the water it held: shallow -> depth 2 + RM_Lakebed_Shallow,
                      deep -> depth 4 + RM_Lakebed_Deep (jawa/flowworks_excavation_report DepthAt reads the dry bed)
  PB_walk_out_deep    a drafted colonist teleported onto a DRY deep (D4) bed square, ordered to a cell outside the pond,
                      arrives (relative climb D4 -> D2 rim -> D0)
PROVE/EXPECT/LIES: a cell that never receded reads its water terrain and depth 0 -> row UNMEASURED (not drained), never
PASS; the walk-out row is UNMEASURED unless the order was taken and ticks elapsed.
"""
import argparse, json, os, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
NS = os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar")
sys.path.insert(0, NS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--origin", default="180,40")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--max-cycles", type=int, default=48)
    a = ap.parse_args()
    import proof_hose as PH
    V = PH.V
    S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
    B = PH.PB()
    rows = []
    res = {"script": "pond_bed_deep.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-22s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:600]), flush=True)
        save()

    def sget(f):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field=f).get("value")

    def sset(f, v):
        return B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field=f, value=str(v))

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    pond = [P(x, z) for z in (4, 5, 6) for x in (2, 3, 4, 5)]
    deep = [P(3, 5), P(4, 5)]
    shallow = [c for c in pond if c not in deep]
    pump, battery = P(3, 7), P(8, 6)
    rect = (ox, oz, 16, 16)

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, waited = V._wait_playing(B, leave_s=0)
    B.hp("defaults")
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    res["destroy"] = {k: v for k, v in (B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False) or {}).items()
                      if k in ("success", "destroyed", "count")}
    hostile = [t for t in (B.call("jawa/list_things", group="BuildingArtificial", limit=5000).get("things") or [])
               if t.get("faction") and not str(t.get("faction")).startswith("Player") and t.get("x") is not None]
    for t in hostile:
        B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t["x"], t["z"]), categories="Building")
    res["hostile_structures_destroyed"] = len(hostile)
    FIELDS = ("refillEnabled", "liquidPumpEnabled", "recessionEnabled", "pondBedHollowEnabled", "depthEngineEnabled")
    before = {f: sget(f) for f in FIELDS}
    res["settings_before"] = before

    def body():
        r = B.call("jawa/flowworks_body_report", x=deep[0][0], z=deep[0][1], classify=False) or {}
        return r.get("body") or {}

    def cells():
        out = {}
        for c in pond:
            ci = (B.call("rimworld/get_cell_info", x=c[0], z=c[1]) or {}).get("cell") or {}
            ex = B.call("jawa/flowworks_excavation_report", x=c[0], z=c[1]) or {}
            out["%d,%d" % c] = {"terrain": ci.get("terrainDefName"), "depth": ex.get("depth"), "fill": ex.get("fill"),
                                "dug": ex.get("isExcavated")}
        return out

    try:
        if not ok or not V.prepare_site(B, rect, rows, "PB_site_ready"):
            row("PB_bed_shape", "UNMEASURED", "SITE", {"why": "site not ready / not playing"})
            return 2
        B.call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,4,3;WaterDeep:%d,%d,2,1" % (P(2, 4) + P(3, 5)))
        cls = B.call("jawa/flowworks_body_report", x=deep[0][0], z=deep[0][1], classify=True) or {}
        b0 = cls.get("body") or {}
        res["classify"] = cls
        res["cells_fresh"] = cells()
        if not b0 or b0.get("limitless") or b0.get("cellCount") != 12:
            row("PB_pond_limited", "UNMEASURED", "SITE", {"body": b0, "cells": res["cells_fresh"]})
            return 2
        row("PB_pond_limited", "PASS", "SITE", {"body": b0})
        sset("refillEnabled", False)
        sset("liquidPumpEnabled", True)
        sset("pondBedHollowEnabled", True)
        ops = ["RM_LiquidPump:%d,%d" % pump, "Battery:%d,%d" % battery]
        ops += ["RM_UniversalPipe:%d,%d" % P(x, 8) for x in range(3, 10)] + ["RM_UniversalPipe:%d,%d" % P(3, 9),
                                                                              "RM_UniversalPipe:%d,%d" % P(9, 9)]
        ops += ["RM_LiquidTank:%d,%d" % P(3, 10), "RM_LiquidTank:%d,%d" % P(9, 10)]
        bb = B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False)
        res["build"] = {k: bb.get(k) for k in ("success", "built", "failed")}
        B.ticks(2)
        lt = B.call("jawa/list_things", defName="Battery", rect="%d,%d,2,2" % battery, limit=2) or {}
        bid = ((lt.get("things") or [{}])[0]).get("id")
        if bid is not None:
            B.call("jawa/battery_set", thing=bid, mode="setPct", value=1.0)
        res["pumpPoweredAfterTicks"] = PH._powered(B, pump)
        trace = []
        last_rc, flat = -1, 0
        for i in range(a.max_cycles):
            B.ticks(250)
            bd = body()
            rc = bd.get("recededCount")
            trace.append({"i": i, "stock": bd.get("stock"), "receded": rc, "pump": B.hp("pump:%d,%d" % pump).get("status")})
            if rc is not None and rc >= 11:
                break
            flat = flat + 1 if rc == last_rc else 0
            last_rc = rc
            if flat >= 8:
                break
        res["draw_trace"] = trace
        cs = cells()
        res["cells_drained"] = cs
        wet = [k for k, v in cs.items() if v["terrain"] in ("WaterShallow", "WaterDeep")]
        bad = []
        for c in pond:
            k = "%d,%d" % c
            v = cs[k]
            if k in wet:
                continue
            want = (4, "RM_Lakebed_Deep") if c in deep else (2, "RM_Lakebed_Shallow")
            if (v["depth"], v["terrain"]) != want:
                bad.append({k: v, "want": want})
        dry_deep = [c for c in deep if "%d,%d" % c not in wet]
        det = {"wet": wet, "dryDeep": dry_deep, "mismatch": bad, "lastTrace": trace[-1:] if trace else None}
        if not dry_deep or len(wet) > 1:
            row("PB_bed_shape", "UNMEASURED", "SITE", dict(det, why="pond did not drain to its last cell"))
        else:
            row("PB_bed_shape", "PASS" if not bad else "FAIL", "MOD", det)
        # walk out of the dry deep middle
        if dry_deep:
            cols = [p for p in (B.hp("colonists").get("pawns") or []) if not p.get("downed")]
            if not cols:
                row("PB_walk_out_deep", "UNMEASURED", "SITE", {"why": "no free colonist"})
            else:
                pid = cols[0]["id"]
                tp = B.hp("pawn:%d=tp:%d,%d" % ((pid,) + dry_deep[0]))
                B.hp("pawn:%d=draft" % pid)
                B.ticks(2)
                pos0 = next((p.get("pos") for p in B.hp("colonists").get("pawns") or [] if p["id"] == pid), None)
                dest = P(3, 1)
                o = B.call("jawa/order_pawn", pawnId=str(pid), x=dest[0], z=dest[1], waitTicks=1500, draft=True) or {}
                pos1 = next((p.get("pos") for p in B.hp("colonists").get("pawns") or [] if p["id"] == pid), None)
                row_o = next((r for r in (o.get("pawns") or o.get("results") or []) if str(r.get("pawnId")) in (str(pid), "Human%d" % pid)), o)
                arrived = row_o.get("arrived") if isinstance(row_o, dict) else None
                if arrived is None and o.get("pawnCount") == 1 and isinstance(o.get("arrivedCount"), int) \
                        and (o.get("ticksElapsed") or 0) > 0:
                    arrived = o["arrivedCount"] == 1 and bool(pos1) and tuple(pos1) == tuple(dest)
                d = {"pawn": pid, "tp": tp.get("success"), "start": pos0, "dest": dest, "end": pos1, "arrived": arrived,
                     "order": json.dumps(o, default=str)[:900]}
                if not tp.get("success") or (pos0 and tuple(pos0) != tuple(dry_deep[0])):
                    row("PB_walk_out_deep", "UNMEASURED", "SITE", dict(d, why="colonist not placed on the dry deep square"))
                elif arrived is None:
                    row("PB_walk_out_deep", "UNMEASURED", "HARNESS", dict(d, why="order result unreadable"))
                else:
                    row("PB_walk_out_deep", "PASS" if arrived else "FAIL", "MOD", d)
        return 0
    finally:
        res["settings_restored"] = {f: sset(f, before[f]).get("success") for f in FIELDS if before.get(f) is not None}
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        print("result:", a.out)


if __name__ == "__main__":
    sys.exit(main())
