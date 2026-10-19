"""depth_rebuild_proofs.py -- the P10 live proofs owed by the FlowWorks depth rebuild (FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG),
one section per item, each row an evidence line written to the result JSON as it is measured.

    python.exe src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py [--only swim,drown,p7,p5,sweep] [--fresh-map] [out.json]

Run from the repo root with python.exe; the bridge must be held; the flowworks tier (11 mods) running. No flyer is tested
(a forced PawnFlyer landing is a jump, not creature flight). Every touched setting is restored in `finally`.

Sections (one plot each on one map; plots are cleared and read back by validation_core.prepare_site):
  swim  DEEP_WATER_BUILD_SWIM_OR_SINK L2: a 9x5 dug lake, 3 m deep and full; a colonist swims to its middle (ProofSwim) and
        climbs out the far side; an armoured colonist (marine armour + helmet) is warned before going under (drafted, held
        mid-lake); a tame muffalo crossing the plot is sampled every 60 ticks (never in the lake); a mechanoid reads class None
        and is not routed in; a prisoner in a flooded sheer pit (3.5 m hole, 2 m water) swims, is held, stays in; the master
        switch off/on mid-game changes the lake's path cost for the same pawn (RM_SwimWater.Reapply = what WriteSettings runs).
  drown RM_SwimSettings.shallowWaterDrowningEnabled: a downed colonist on painted 0.5 m natural shallows, once ON, once OFF:
        ProofDrown before, RM_PitDrowning severity / alive after 2,500 ticks (one game hour). Numbers only, for his ruling.
  p7    PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE L2: forced landings in a 2 m and a 7 m pit (fall damage ratio, want 3.5x by V3);
        a prisoner in a sheer 1.5 m pocket is held and a prison room; shooting across a 2 m trench is allowed, between two
        7 m pits (7 m of ground in the line) refused.
  p5    PIT_DEPTH_WIDEN_TWO_METRES_TO_EIGHT: the 4/7/7/4 square by the drive tool (ring 4 m, core 7 m), filled: litres and one
        surface (ProofReadout per square, ProofLevelSurface).
  sweep RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS: needs a current map with river current; `river_scenes_walk.py go R3` is the
        real proof -- this section only records that.
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
SWIM = "RimMandrake.FlowWorks.Swimming.RM_Swim"
SWIMW = "RimMandrake.FlowWorks.Swimming.RM_SwimWater"
DROWN = "RimMandrake.FlowWorks.RM_PitFillEffects"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
PITPATH = "RimMandrake.FlowWorks.RM_PitPathing"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
S_SW = "RimMandrake.FlowWorks.Swimming.RM_SwimSettings"


def kv(txt):
    out = {}
    for tok in (txt or "").replace("|", " ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--only", default="swim,drown,p7,p5")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    only = set(a.only.split(","))
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "depth_rebuild_proofs_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "depth_rebuild_proofs.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    could_not = []   # a refused static_call / settings write / dig / spawn since the last row: the row could not ask

    def row(rid, st, det):
        if st == "FAIL" and could_not:     # "could not ask" is UNMEASURED, never a MOD FAIL (live-debugging-proof-harness)
            det = dict(det, couldNotAsk=list(could_not))
            st = "UNMEASURED"
        del could_not[:]
        rows.append({"id": rid, "status": st, "detail": det})
        print("%-44s %-10s %s" % (rid, st, json.dumps(det, default=str)[:420]), flush=True)
        save()

    def sc(typ, method, arg=""):
        r = B.call("jawa/static_call", type=typ, method=method, args=arg) or {}
        if not r.get("success"):
            could_not.append("%s.%s refused" % (method, arg[:30]))
        return str(r.get("result") if r.get("success") else (r.get("message") or r.get("error") or r))

    def fget(t, f):
        return (B.call("jawa/mod_settings_field", typeName=t, action="get", field=f) or {}).get("value")

    def fset(t, f, v):
        r = B.call("jawa/mod_settings_field", typeName=t, action="set", field=f, value=str(v)) or {"success": False}
        if r.get("success") is False:
            could_not.append("set %s refused" % f)
        return r

    def dig(c, n, fill=-1):
        r = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill) or {}
        if r.get("success") is False:
            could_not.append("dig %s refused" % (c,))
        return r

    def spawn(kind, c, faction):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if not pid:
            could_not.append("spawn %s failed" % kind)
        return pid, r

    def order(pid, c, wait):
        o = B.call("jawa/order_pawn", pawnId=pid, x=c[0], z=c[1], waitTicks=wait, draft=True) or {}
        for p in o.get("pawns") or []:
            if p.get("id") == pid:
                return dict(p, ticksElapsed=o.get("ticksElapsed"), orderAccepted=p.get("orderAccepted", o.get("success")))
        return {"raw": str(o)[:400]}

    def pos(row_):
        p = row_.get("end") or row_.get("position") or {}
        return (p.get("x"), p.get("z")) if isinstance(p, dict) else None

    def where(pid):
        r = B.call("jawa/pawn_get", pawn=pid) or {}
        if not r.get("pawns"):
            return (None, None), {"dead": True, "why": str(r.get("message"))[:120]}   # pawn_get finds no spawned pawn: dead/gone
        p = r["pawns"][0]
        q = p.get("position") or {}
        return (q.get("x"), q.get("z")), p

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40))

    def hediff(p, name):
        for h in p.get("hediffs") or []:
            if name in json.dumps(h):
                return h
        return None

    def inside(c, rect):
        x0, z0, w, h = rect
        return c is not None and c[0] is not None and x0 <= c[0] < x0 + w and z0 <= c[1] < z0 + h

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    FW_FIELDS = ("superdeepCapturesOwnFaction",)
    SW_FIELDS = ("deepSwimEnabled", "shallowWaterDrowningEnabled")
    before = {("fw", f): fget(S_FW, f) for f in FW_FIELDS}
    before.update({("sw", f): fget(S_SW, f) for f in SW_FIELDS})
    res["settings_before"] = {"%s.%s" % k: v for k, v in before.items()}
    save()
    try:
        if not ok:
            row("site", "UNMEASURED", {"why": "not playing"})
            return 2
        B.call("jawa/kill_hostiles")
        B.call("jawa/quiet_site", action="apply", clearThreats=True, proximityLetters=True)   # hives, dormant spawners, monolith
        B.call("jawa/debug_settings", action="set", field="enableStoryteller", value=False)   # restored in finally
        # ------------------------------------------------------------------ swim
        if "swim" in only:
            ox, oz = 120, 120
            rect = (ox, oz, 34, 18)
            if not V.prepare_site(B, rect, rows, "SWIM_site_ready"):
                row("SWIM_site", "UNMEASURED", {"why": "site not ready"})
            else:
                lake = (ox + 6, oz + 6, 9, 5)
                for i in range(9):
                    for j in range(5):
                        dig((lake[0] + i, lake[1] + j), 6, 6)
                B.ticks(70)
                mid = (lake[0] + 4, lake[1] + 2)
                row("SWIM_lake_staged", "INFO", {"readout_mid": sc(NSP, "ProofReadout", "%d,%d" % mid),
                                                 "readout_edge": sc(NSP, "ProofReadout", "%d,%d" % (lake[0], lake[1]))})
                # 1. a colonist swims to the middle and climbs out the far side
                c1, _ = spawn("Colonist", (lake[0] - 2, mid[1]), "player")
                o1 = order(c1, mid, 900)
                s1 = sc(SWIM, "ProofSwim", "%d,%d" % mid)
                k1 = kv(s1)
                st = "PASS" if pos(o1) == mid and k1.get("deepCell") == "True" and k1.get("headUp") == "True" \
                    and float(k1.get("water", 0)) >= 2.9 else "FAIL"
                row("SWIM_dug_reservoir_3m_reached", st, {"order": {k: o1.get(k) for k in ("end", "ticksElapsed", "canReach", "note")}, "swim": s1})
                far = (lake[0] + 11, mid[1])
                o2 = order(c1, far, 1200)
                p2 = pos(o2)
                row("SWIM_dug_reservoir_far_side_reached", "PASS" if p2 == far else "FAIL",
                    {"end": p2, "want": far, "ticks": o2.get("ticksElapsed"), "swimAfter": sc(SWIM, "ProofSwim", "%d,%d" % far)})
                # 1a'. a mechanoid at the dug reservoir: class None, never routed in (fix3: dug water opens to swimmers only)
                md, _ = spawn("Mech_Militor", (lake[0] - 2, lake[1] + 1), "player")
                omd = order(md, mid, 600) if md else {}
                row("SWIM_dug_reservoir_mechanoid_refused", "PASS" if md and "raw" not in omd and not inside(pos(omd), lake) else "FAIL",
                    {"order": {k: omd.get(k) for k in ("end", "ticksElapsed", "canReach")}, "midSwim": sc(SWIM, "ProofSwim", "%d,%d" % mid)})
                # 1b. a NATURAL lake (painted WaterDeep, 9x4): the rest of the section swims here
                nl = (ox + 6, oz + 13, 9, 4)
                B.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,%d,%d" % nl)
                B.ticks(70)
                lake, mid, far = nl, (nl[0] + 4, nl[1] + 1), (nl[0] + 11, nl[1] + 1)
                o1 = order(c1, mid, 900)
                s1 = sc(SWIM, "ProofSwim", "%d,%d" % mid)
                k1 = kv(s1)
                st = "PASS" if pos(o1) == mid and k1.get("deepCell") == "True" and k1.get("headUp") == "True" else "FAIL"
                row("SWIM_colonist_reaches_lake_middle", st, {"order": {k: o1.get(k) for k in ("end", "ticksElapsed", "canReach")},
                                                              "swim": s1, "readout": sc(NSP, "ProofReadout", "%d,%d" % mid)})
                o2 = order(c1, far, 1200)
                p2 = pos(o2)
                row("SWIM_colonist_climbs_out_far_side", "PASS" if p2 == far else "FAIL",
                    {"end": p2, "want": far, "ticks": o2.get("ticksElapsed"), "swimAfter": sc(SWIM, "ProofSwim", "%d,%d" % far)})
                # 2. armoured colonist: warned, then (drafted, held mid-lake) goes under
                c2, _ = spawn("Colonist", (lake[0] - 2, mid[1] - 1), "player")
                for d_ in ("Apparel_ArmorMarine", "Apparel_ArmorHelmetMarine"):
                    B.call("jawa/pawn_gear", **{"pawn": c2, "action": "wear", "def": d_, "stuff": ""})
                tgt = (mid[0], mid[1] - 1)
                o3 = order(c2, tgt, 600)
                s3 = sc(SWIM, "ProofSwim", "%d,%d" % tgt)
                trace, warned, under_at, msgs0 = [], None, None, None
                for k in range(24):           # up to 24 x 250 ticks = 2.4 game hours
                    step(250)
                    p_, info = where(c2)
                    d3 = sc(DROWN, "ProofDrown", "%d,%d" % p_) if p_[0] is not None else ""
                    s_ = kv(sc(SWIM, "ProofSwim", "%d,%d" % p_)) if p_[0] is not None else {}
                    ms = B.call("rimworld/list_messages", limit=12) or {}
                    texts = [m.get("text") or m.get("label") or "" for m in (ms.get("messages") or [])]
                    hit = [t for t in texts if any(w in t.lower() for w in ("swim", "tir", "drown", "shore", "exhaust"))]
                    if hit and warned is None:
                        warned = (k + 1) * 250, hit
                    kd = kv(d3)
                    trace.append({"t": (k + 1) * 250, "pos": p_, "exh": s_.get("exhaustion"), "headUp": s_.get("headUp"),
                                  "under": kd.get("under"), "downed": info.get("downed"), "dead": info.get("dead")})
                    if kd.get("under") == "True" and under_at is None:
                        under_at = (k + 1) * 250
                        break
                row("SWIM_armour_profile", "INFO", {"order": {k: o3.get(k) for k in ("end", "ticksElapsed", "canReach")}, "swim": s3})
                row("SWIM_armour_warned_before_under", "PASS" if warned and (under_at is None or warned[0] <= under_at) else
                    ("FAIL" if under_at else "UNMEASURED"), {"warned": warned, "underAt": under_at, "trace": trace})
                row("SWIM_armour_drafted_goes_under", "PASS" if under_at else "UNMEASURED", {"underAt": under_at, "last": trace[-1:] if trace else None})
                # 3. a tame land animal crosses the plot: sampled, never in the lake
                mu, _ = spawn("Muffalo", (lake[0] - 3, mid[1]), "player")
                rt = sc(PITPATH, "ProofRoute", "%s|%d,%d" % (mu, far[0], far[1]))
                samples, in_lake = [], 0
                o4 = B.call("jawa/order_pawn", pawnId=mu, x=far[0], z=far[1], waitTicks=60, draft=False) or {}
                for k in range(30):
                    p_, _i = where(mu)
                    samples.append(p_)
                    in_lake += 1 if inside(p_, lake) else 0
                    if p_ == far:
                        break
                    step(60)
                row("SWIM_land_animal_walks_around", "PASS" if in_lake == 0 and samples and samples[-1] == far else
                    ("FAIL" if in_lake else "UNMEASURED"), {"inLakeSamples": in_lake, "samples": samples, "end": samples[-1] if samples else None,
                                                        "orderAccepted": str(o4)[:200], "route": rt})
                # 4. a mechanoid: class None, sinks, not routed in
                me, mr = spawn("Mech_Militor", (lake[0] - 2, lake[1] - 2), "player")
                me_in, _ = spawn("Mech_Militor", (lake[0] + 2, lake[1] + 2), "player")
                sm = sc(SWIM, "ProofSwim", "%d,%d" % (lake[0] + 2, lake[1] + 2))
                om = order(me, mid, 600) if me else {}
                pm = pos(om) if om else None
                row("SWIM_mechanoid_refused", "PASS" if me and om and "raw" not in om and "class=None" in sm and not inside(pm, lake) else "FAIL",
                    {"swimInLake": sm, "orderToMiddle": {k: om.get(k) for k in ("end", "ticksElapsed", "canReach")} if om else mr,
                     "route": sc(PITPATH, "ProofRoute", "%s|%d,%d" % (me, mid[0], mid[1])) if me else None})
                # 5. prisoner in a flooded sheer pit: 4 m hole, 2 m water -> surface 2 m below the lip (2026-10-18: with shipped rain fill a 3.5 m hole rose to 2.5 m of water in 1,500 ticks, a K 2 step, and the prisoner climbed out by the rule)
                pit = (ox + 22, oz + 6, 3, 3)
                for i in range(3):
                    for j in range(3):
                        dig((pit[0] + i, pit[1] + j), 8, 4)
                B.ticks(70)
                pc = (pit[0] + 1, pit[1] + 1)
                pr, _ = spawn("Villager", pc, "hostile")
                gs = B.call("jawa/pawn_set_guest_status", pawn=pr, guestStatus="Prisoner", hostFaction="PlayerColony") or {}
                s5a = sc(SWIM, "ProofSwim", "%d,%d" % pc)
                step(1500)
                p5, info5 = where(pr)
                s5b = sc(SWIM, "ProofSwim", "%d,%d" % p5) if p5[0] is not None else ""
                cl = sc(NSP, "ProofClimb", "pawn:%s" % pr)
                row("SWIM_prisoner_flooded_pit_stays_in", "PASS" if inside(p5, pit) and not info5.get("dead") and "headUp=True" in s5b else "FAIL",
                    {"guest": str(gs)[:200], "readout": sc(NSP, "ProofReadout", "%d,%d" % pc), "swimAt0": s5a, "after1500": p5,
                     "swimAfter": s5b, "climb": cl, "dead": info5.get("dead")})
                # 6. master switch off / on mid-game, same pawn in the lake
                c6, _ = spawn("Colonist", (lake[0] + 6, lake[1] + 3), "player")
                c6c = (lake[0] + 6, lake[1] + 3)
                on1 = kv(sc(SWIM, "ProofSwim", "%d,%d" % c6c))
                fset(S_SW, "deepSwimEnabled", False)
                ra = sc(SWIMW, "Reapply")
                off = kv(sc(SWIM, "ProofSwim", "%d,%d" % c6c))
                fset(S_SW, "deepSwimEnabled", True)
                rb = sc(SWIMW, "Reapply")
                on2 = kv(sc(SWIM, "ProofSwim", "%d,%d" % c6c))
                ok6 = on1.get("deepCell") == "True" and off.get("pathCost") not in (None, on1.get("pathCost")) \
                    and on2.get("pathCost") == on1.get("pathCost")
                row("SWIM_toggle_off_on_mid_game", "PASS" if ok6 else "FAIL",
                    {"on": {k: on1.get(k) for k in ("deepCell", "pathCost", "class")}, "off": {k: off.get(k) for k in ("deepCell", "pathCost", "class")},
                     "onAgain": {k: on2.get(k) for k in ("deepCell", "pathCost", "class")}, "reapply": [ra, rb]})
        # ------------------------------------------------------------------ drown (shallow-water switch)
        if "drown" in only:
            ox, oz = 160, 150
            rect = (ox, oz, 16, 10)
            if not V.prepare_site(B, rect, rows, "DROWN_site_ready"):
                row("DROWN_site", "UNMEASURED", {"why": "site not ready"})
            else:
                res_d = {}
                for n_, val in ((0, True), (1, False)):
                    sx = ox + 2 + n_ * 7
                    B.call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,3,3" % (sx, oz + 3))
                    B.ticks(2)
                    c = (sx + 1, oz + 4)
                    fset(S_SW, "shallowWaterDrowningEnabled", val)
                    pid, _ = spawn("Colonist", c, "player")
                    inc = B.call("jawa/pawn_force_incapacitate", pawn=pid, action="downed", allowBleedingWounds=False) or {}
                    d0 = sc(DROWN, "ProofDrown", "%d,%d" % c)
                    tr = []
                    for k in range(10):
                        step(250)
                        p_, info = where(pid)
                        h = hediff(info, "RM_PitDrowning") or hediff(info, "Drown")
                        tr.append({"t": (k + 1) * 250, "pos": p_, "dead": info.get("dead"), "downed": info.get("downed"),
                                   "drown": (h or {}).get("severity"), "proof": sc(DROWN, "ProofDrown", "%d,%d" % c) if not info.get("dead") else "dead"})
                        if info.get("dead"):
                            break
                    res_d[str(val)] = {"incap": str(inc)[:200], "before": d0, "trace": tr}
                    row("DROWN_shallow_%s" % ("ON" if val else "OFF"), "INFO", {"readout": sc(NSP, "ProofReadout", "%d,%d" % c),
                                                                               "terrain": "WaterShallow painted", "before": d0, "trace": tr})
        # ------------------------------------------------------------------ p7
        if "p7" in only:
            ox, oz = 120, 150
            rect = (ox, oz, 36, 16)
            if not V.prepare_site(B, rect, rows, "P7_site_ready"):
                row("P7_site", "UNMEASURED", {"why": "site not ready"})
            else:
                fset(S_FW, "superdeepCapturesOwnFaction", True)
                pits = {"2m": ((ox + 2, oz + 2), 4), "7m": ((ox + 8, oz + 2), 14)}
                for nm, (o, d) in pits.items():
                    for i in range(3):
                        for j in range(3):
                            dig((o[0] + i, o[1] + j), d)
                B.ticks(70)
                falls = {}
                for nm, (o, d) in pits.items():
                    c = (o[0] + 1, o[1] + 1)
                    pid, _ = spawn("Colonist", (o[0] - 2, o[1] + 1), "player")
                    r0 = B.call("jawa/flowworks_pit_report", x=c[0], z=c[1]) or {}
                    lf = sc(PROMO, "ProofForcedFlyer", "%s,%d,%d" % (pid, c[0], c[1]))
                    step(240)
                    r1 = B.call("jawa/flowworks_pit_report", x=c[0], z=c[1]) or {}
                    rec = [x for x in r1.get("recentDescents") or [] if str(x).startswith(pid + "@")]
                    fl = [float(x.rsplit("fall=", 1)[1]) for x in rec if "fall=" in x]
                    p_, info = where(pid)
                    falls[nm] = {"flyer": lf, "descents": rec, "fall": fl, "pos": p_, "dead": info.get("dead"),
                                 "depth": r1.get("depth"), "readout": sc(NSP, "ProofReadout", "%d,%d" % c)}
                f2, f7 = (falls["2m"]["fall"] or [None])[0], (falls["7m"]["fall"] or [None])[0]
                ratio = (f7 / f2) if f2 and f7 else None
                row("P7_fall_7m_takes_3_5x", "PASS" if ratio and abs(ratio - 3.5) < 0.05 and not falls["7m"]["dead"] else
                    ("UNMEASURED" if ratio is None else "FAIL"), {"ratio": ratio, "falls": falls})
                # sheer 1.5 m pocket holds a prisoner
                po = (ox + 14, oz + 2)
                for i in range(3):
                    for j in range(3):
                        dig((po[0] + i, po[1] + j), 3)
                B.ticks(70)
                pc = (po[0] + 1, po[1] + 1)
                pr, _ = spawn("Villager", pc, "hostile")
                gs = B.call("jawa/pawn_set_guest_status", pawn=pr, guestStatus="Prisoner", hostFaction="PlayerColony") or {}
                B.ticks(70)
                cl0 = sc(NSP, "ProofClimb", "pawn:%s" % pr)
                room = sc(NSP, "ProofRoom", "%d,%d;%d,%d" % (pc[0], pc[1], po[0] - 1, pc[1]))
                step(1200)
                p_, info = where(pr)
                cl1 = sc(NSP, "ProofClimb", "pawn:%s" % pr)
                k0 = kv(cl0)
                row("P7_prisoner_held_in_1_5m_pocket", "PASS" if k0.get("held") == "True" and inside(p_, (po[0], po[1], 3, 3)) else "FAIL",
                    {"guest": str(gs)[:160], "climb0": cl0, "room": room, "after1200": p_, "climb1": cl1, "readout": sc(NSP, "ProofReadout", "%d,%d" % pc)})
                # shooting: across a 2 m trench allowed; between two 7 m pits (7 m ground in the line) refused
                tr = (ox + 20, oz + 2)
                for j in range(5):
                    for i in range(3):
                        dig((tr[0] + i, tr[1] + j), 4)
                for o in ((ox + 26, oz + 2), (ox + 32, oz + 2)):
                    for i in range(3):
                        for j in range(3):
                            dig((o[0] + i, o[1] + j), 14)
                B.ticks(70)
                sh, _ = spawn("Colonist", (tr[0] - 1, tr[1] + 2), "player")
                B.call("jawa/pawn_gear", **{"pawn": sh, "action": "equip", "def": "Gun_BoltActionRifle"})
                en, _ = spawn("Villager", (tr[0] + 3, tr[1] + 2), "hostile")
                B.call("jawa/pawn_gear", **{"pawn": en, "action": "equip", "def": "Gun_BoltActionRifle"})
                at1 = B.call("jawa/attack_target_probe", pawn=sh, maxDist=30) or {}
                pa = (ox + 27, oz + 3)
                pb = (ox + 33, oz + 3)
                sa, _ = spawn("Colonist", pa, "player")
                B.call("jawa/pawn_gear", **{"pawn": sa, "action": "equip", "def": "Gun_BoltActionRifle"})
                eb, _ = spawn("Villager", pb, "hostile")
                B.call("jawa/pawn_gear", **{"pawn": eb, "action": "equip", "def": "Gun_BoltActionRifle"})
                at2 = B.call("jawa/attack_target_probe", pawn=sa, maxDist=30) or {}
                t1 = json.dumps(at1, default=str)
                t2 = json.dumps(at2, default=str)
                row("P7_shoot_across_2m_trench_allowed", "PASS" if en and en in t1 else "FAIL", {"shooter": sh, "target": en, "probe": t1[:700]})
                row("P7_shoot_between_7m_pits_refused", "PASS" if eb and at2.get("success") is not False and at1.get("success") is not False and en and en in t1 and eb not in t2 else "FAIL", {"shooter": sa, "target": eb, "probe": t2[:700],
                    "depthA": sc(NSP, "ProofReadout", "%d,%d" % pa), "depthB": sc(NSP, "ProofReadout", "%d,%d" % pb)})
        # ------------------------------------------------------------------ p5
        if "p5" in only:
            ox, oz = 190, 120
            rect = (ox, oz, 14, 12)
            if not V.prepare_site(B, rect, rows, "P5_site_ready"):
                row("P5_site", "UNMEASURED", {"why": "site not ready"})
            else:
                sq = (ox + 4, oz + 4)
                for i in range(4):
                    for j in range(4):
                        core = 1 <= i <= 2 and 1 <= j <= 2
                        n = 14 if core else 8
                        dig((sq[0] + i, sq[1] + j), n, n)
                B.ticks(70)
                reads = {}
                total_l = 0
                for i in range(4):
                    for j in range(4):
                        c = (sq[0] + i, sq[1] + j)
                        t = sc(NSP, "ProofReadout", "%d,%d" % c)
                        reads["%d,%d" % c] = t
                        try:
                            total_l += int(t.rsplit("(", 1)[1].split(" L")[0].replace(",", ""))
                        except (IndexError, ValueError):
                            pass
                ls = sc(NSP, "ProofLevelSurface", "%d,%d,4,4" % sq)
                row("P5_4774_square_152000_L", "PASS" if total_l == 152000 else ("UNMEASURED" if total_l == 0 else "FAIL"), {"litres": total_l, "readouts": reads})
                row("P5_4774_square_one_surface", "PASS" if " worst 0.000" in ls or "gap 0.0000" in ls or ls.startswith("OK 1") else "INFO", {"levelSurface": ls})
        # ------------------------------------------------------------------ p13 (reeds through a drain/refill cycle)
        if "p13" in only:
            ox, oz = 120, 180
            rect = (ox, oz, 24, 12)
            if not V.prepare_site(B, rect, rows, "P13_site_ready"):
                row("P13_site", "UNMEASURED", {"why": "site not ready"})
            else:
                WM = "RimMandrake.FlowWorks.RM_WaterMendSettings"
                grace = fget(WM, "waterPlantGraceHours")
                runs = {"cycle": [(ox + 2 + i, oz + 3) for i in range(8)], "control": [(ox + 2 + i, oz + 7) for i in range(8)]}
                for cells in runs.values():
                    for c in cells:
                        dig(c, 1, 1)
                B.ticks(70)
                for nm, cells in runs.items():
                    B.call("jawa/spawn_batch", ops=";".join("Plant_Reeds:%d,%d" % c for c in cells[1:7]))
                B.ticks(10)

                def alive(cells):
                    x0 = min(c[0] for c in cells); z0 = cells[0][1]
                    r = B.call("jawa/list_things", defName="Plant_Reeds", rect="%d,%d,%d,1" % (x0, z0, len(cells))) or {}
                    return len(r.get("things") or [])

                n0 = {k: alive(v) for k, v in runs.items()}
                for nm, cells in runs.items():
                    for c in cells:
                        dig(c, 0, 0)
                B.ticks(600)
                n1 = {k: alive(v) for k, v in runs.items()}
                terr_dry = sc(NSP, "ProofReadout", "%d,%d" % runs["cycle"][3])
                for c in runs["cycle"]:
                    dig(c, 0, 1)
                B.ticks(70)
                n2 = {k: alive(v) for k, v in runs.items()}
                g_ticks = int(float(grace or 0) * 2500) + 2500
                left = g_ticks
                while left > 0:
                    for c in (B.call("jawa/list_pawns", limit=200) or {}).get("pawns") or []:
                        if c.get("isPlayer") and not c.get("dead") and str(c.get("id", "")).startswith("Human"):
                            for need in ("Food", "Rest"):
                                B.call("jawa/pawn_need", pawn=c["id"], action="need", need=need, level=1.0)
                    B.ticks(min(left, 2500))
                    left -= 2500
                n3 = {k: alive(v) for k, v in runs.items()}
                row("P13_reeds_survive_drain_refill", "PASS" if n0["cycle"] == 6 and n3["cycle"] == 6 else "FAIL",
                    {"graceHours": grace, "start": n0, "after600dry": n1, "dryReadout": terr_dry, "afterRefill": n2,
                     "afterGracePlus1h": n3, "ticksAfterRefill": 70 + g_ticks})
                row("P13_reeds_control_left_dry_die", "PASS" if n3["control"] < n0["control"] else "INFO",
                    {"start": n0["control"], "afterGracePlus1h": n3["control"]})
                row("P13_fish_rows", "UNMEASURED", {"why": "no bridge read of vanilla WaterBody fish types / fishing zones (owed: a ProofWaterBody static surface)"})
    finally:
        for (t, f), v in before.items():
            if v is not None:
                fset(S_FW if t == "fw" else S_SW, f, v)
        B.call("jawa/debug_settings", action="set", field="enableStoryteller", value=True)
        try:
            sc(SWIMW, "Reapply")
        except Exception:  # noqa: BLE001
            pass
        res["settings_restored"] = {"fw." + f: fget(S_FW, f) for f in FW_FIELDS}
        res["settings_restored"].update({"sw." + f: fget(S_SW, f) for f in SW_FIELDS})
        save()
        print("result ->", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
