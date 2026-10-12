"""FlowWorks liquid live checks L2 (Dump drains: slow without a pump, fast with a pump on Pour) and L6 (liquid theft: a witness
catches our Fill tank drawing a neutral faction's tank; the free end names the faction; --theft-day: goodwill falls).

  python.exe src/RimMandrake/FlowWorks/northstar/liquid_checks.py [out.json] [--only L2,L6] [--fresh-map] [--theft-day]

Promoted out of Transient/bench_live_20261011/fw_live_checks.py (debug_process.md: the checks that found real bugs persist).
Run from the repo root with python.exe, bridge held; map = a 250x250 FlowWorks-tier quicktest. Exit 0 = every row PASS.
Rows {id, status PASS|FAIL|UNMEASURED, class MOD|SITE|HARNESS, detail}; "could not ask" is UNMEASURED, never PASS.

WHY L6 IS TIMED (THEFT_ROW_REPAIR_WITNESS_WALKS_OFF, 2026-10-12): RM_LiquidTheft.TheftTick runs at TicksGame % 250 == 7. A lordless
neutral villager spawned at the start of a 1,000-tick watch WALKS OFF long before the first check, so the old row read
caught 0 -> 0 whatever the mod did (a probe that spawned the witness 3 ticks before the check read 0 -> 1 and the letter). So
here the witness is spawned at TicksGame % 250 == WITNESS_PHASE (3 ticks before the check), its position is read AT the check, and
a witness that is dead, downed or absent at the check makes the row UNMEASURED (HARNESS) -- a FAIL needs a live witness present.
The old --theft-day loop also let colonists idle (a Tantrum smashed our Fill tank before a day of touched ticks accrued): every
colonist is drafted before the day loop, and both tanks are refilled/emptied every REFILL_EVERY (2,000) ticks, so every
cycle is touched.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

CYCLE = 250                 # RM_LiquidTheft.TheftTick cadence
CHECK_PHASE = 7             # TicksGame % 250 == 7
WITNESS_PHASE = 4           # spawn here: 3 ticks before the check
REFILL_EVERY = 2000
DAY_TICKS = 60000
MAX_WITNESS_CYCLES = 4      # theft attempts (one fresh witness pair per cycle) before the row calls it a FAIL
THEFT = "RimMandrake.FlowWorks.Machinery.RM_LiquidTheft"
S_HOSE = "RimMandrake.FlowWorks.Hose.RM_HoseSettings"
S_MACH = "RimMandrake.FlowWorks.Machinery.RM_MachinerySettings"
FW_PKG = "mandrake.rm.flowworks"


# ============================================================================ pure logic (selftest_liquid_checks.py)
def ticks_until(tick, phase, cycle=CYCLE):
    """Ticks to step so that tick % cycle == phase (0 if already there)."""
    return (phase - tick) % cycle


def witness_alive(w):
    """A witness counts only if it is present and neither dead nor downed at the check."""
    return bool(w) and not w.get("dead") and not w.get("downed")


def theft_verdict(drawn, caught0, caught1, letters0, letters1, witness_at_check, precondition=None):
    """(status, class, detail) for L6_theft_spotted_letter.

    UNMEASURED: a precondition failed; nothing was drawn (no theft to spot); or the witness was not alive and present at
    the check (we cannot tell 'LOS blocked' from 'walked off'). FAIL: a live witness was present at the check and the mod caught
    nothing / sent no letter. PASS: caught rose AND a letter arrived."""
    det = {"caught": [caught0, caught1], "letters": [letters0, letters1], "witnessAtCheck": witness_at_check, "drawn": drawn}
    if precondition:
        return "UNMEASURED", "SITE", dict(det, why=precondition)
    if caught0 is None or caught1 is None:
        return "UNMEASURED", "HARNESS", dict(det, why="RM_LiquidTheft.caught not readable")
    if not drawn or drawn <= 0:
        return "UNMEASURED", "SITE", dict(det, why="nothing was taken from their tank, so there was no theft to spot")
    if (caught1 or 0) > (caught0 or 0) and letters1 > letters0:
        return "PASS", "MOD", det
    if not any(witness_alive(w) for w in (witness_at_check or [])):
        return "UNMEASURED", "HARNESS", dict(det, why="no live witness present at the theft check: the harness lost him, not the mod")
    return "FAIL", "MOD", det


def goodwill_verdict(gw0, gw1, gc0, gc1, per, caught):
    if not caught:
        return "UNMEASURED", "HARNESS", {"why": "the theft was never caught"}
    if None in (gw0, gw1):
        return "UNMEASURED", "HARNESS", {"why": "goodwill not readable", "goodwill": [gw0, gw1]}
    det = {"goodwill": [gw0, gw1], "goodwillCharged": [gc0, gc1], "perDay": per}
    ok = int(gc1 or 0) - int(gc0 or 0) <= -int(per or 2) and gw1 < gw0
    return ("PASS" if ok else "FAIL"), "MOD", det


def dump_no_pump_verdict(tank_trace, canal0, canal1, precondition=None):
    """L2a: the Dump tank loses units through an Outflow end with no pump AND the dry canal gained fill."""
    drained = (tank_trace[0] or 0) - (tank_trace[-1] or 0) if tank_trace else None
    det = {"tankUnits": tank_trace, "drainedPer1000": drained, "canalFillSum": [canal0, canal1]}
    if precondition or not tank_trace or not tank_trace[0]:
        return "UNMEASURED", "SITE", dict(det, why=precondition or "tank never held liquid")
    return ("PASS" if drained > 0 and canal1 > canal0 else "FAIL"), "MOD", det


def dump_pump_verdict(tank_trace, reach0, reach1, no_pump_rate, precondition=None):
    """L2b: the pump on Pour drains the Dump tank strictly faster than the no-pump rate and wets the reach."""
    drained = (tank_trace[0] or 0) - (tank_trace[-1] or 0) if tank_trace else None
    det = {"tankUnits": tank_trace, "drainedPer1000": drained, "vsNoPump": no_pump_rate, "reachFillSum": [reach0, reach1]}
    if precondition or not tank_trace or not tank_trace[0]:
        return "UNMEASURED", "SITE", dict(det, why=precondition or "tank never held liquid")
    if no_pump_rate is None:
        return "UNMEASURED", "HARNESS", dict(det, why="the no-pump scene did not run: no slow rate to compare")
    return ("PASS" if drained > no_pump_rate and drained > 0 and reach1 > reach0 else "FAIL"), "MOD", det


# ============================================================================ live driver
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--only", default="", help="comma list: L2,L6")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--theft-day", action="store_true", help="L6: also run one in-game day for the goodwill charge")
    ap.add_argument("--origin-l2", default="60,150")
    ap.add_argument("--origin-l2b", default="100,150")
    ap.add_argument("--origin-l6", default="60,172")
    a = ap.parse_args(argv)
    only = [b.strip().upper() for b in a.only.split(",") if b.strip()]
    import proof_hose as PH           # bridge-side imports only on a live run
    V = PH.V
    B = PH.PB()
    WATER = PH.LIQUID_WATER
    out = a.out or os.path.join(HERE, "liquid_checks_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "liquid_checks.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-40s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def tg():
        g = B.call("rimworld/get_game_info")
        return g.get("ticksGame") or (g.get("state") or {}).get("tick")

    raw_ticks = B.ticks

    def ticks(n):
        t0 = tg()
        left = n
        while left > 0:
            k = min(1500, left)
            raw_ticks(k)
            left -= k
        t1 = tg()
        if t0 is not None and t1 is not None and t1 - t0 < n:
            raw_ticks(n - (t1 - t0))
    B.ticks = ticks

    def step_to(phase):
        t = tg()
        n = ticks_until(t, phase)
        if n:
            B.ticks(n)
        return tg()

    def sget(typ, field):
        return B.call("jawa/mod_settings_field", typeName=typ, action="get", field=field).get("value")

    def build(*ops, faction="player"):
        return B.call("jawa/build_batch", ops=";".join(o for o in ops if o), faction=faction, wipeExisting=False)

    def dig(c, depth):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=depth, setFill=-1)

    def proof(typ, method, arg):
        r = B.call("jawa/static_call", type=typ, method=method, args=arg)
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return r.get("success") is True and not txt.startswith("REFUSED"), txt

    def fills(cells):
        xs, zs = [c[0] for c in cells], [c[1] for c in cells]
        ok, txt = proof("RimMandrake.FlowWorks.RM_PromotionProofs", "ProofFluidRow",
                        "%d,%d,%d,%d" % (min(xs), min(zs), max(xs) - min(xs) + 1, max(zs) - min(zs) + 1))
        got = {}
        for tok in (txt.split(" ", 3)[3] if ok and txt.count(" ") >= 3 else "").split(";"):
            if ":" in tok:
                xz, rest = tok.split(":", 1)
                x, z = map(int, xz.split(","))
                got[(x, z)] = int(rest.split("/", 3)[1])
        return sum(got.get(tuple(c), 0) for c in cells)

    def units(cell):
        return PH._tank(B, cell).get("units")

    def inspect(thing_id):
        r = B.call("jawa/inspect_string", thingIds=thing_id) or {}
        for t in r.get("things") or r.get("results") or []:
            return t.get("inspect") or []
        return []

    def tank_job(cell):
        tid = PH._tank(B, cell).get("id")
        if tid is None:
            return None
        for line in inspect("RM_LiquidTank%d" % tid) + inspect("RM_UniversalCargoTank%d" % tid):
            m = re.search(r"Job: (\w+)", str(line))
            if m:
                return m.group(1)
        return None

    def gizmo_cycle(cell, prefix, want, max_clicks=4):
        out_g = {"clicks": 0, "ok": False}
        B.call("rimworld/set_god_mode", enabled=True)
        try:
            B.call("rimworld/clear_selection")
            B.call("rimworld/click_cell", x=cell[0], z=cell[1])
            for _ in range(max_clicks + 1):
                gz = (B.call("rimworld/list_selected_gizmos") or {}).get("gizmos") or []
                g = next((q for q in gz if str(q.get("label") or "").startswith(prefix)), None)
                if g is None:
                    out_g["labels"] = [q.get("label") for q in gz][:20]
                    return out_g
                out_g["label"] = g.get("label")
                if g.get("label") == want:
                    out_g["ok"] = True
                    return out_g
                r = B.call("rimworld/execute_gizmo", gizmoId=g.get("gizmoId") or g.get("id"))
                out_g["clicks"] += 1
                if r.get("success") is False:
                    out_g["error"] = r
                    return out_g
            return out_g
        finally:
            B.call("rimworld/set_god_mode", enabled=False)
            B.call("rimworld/clear_selection")

    def set_job(tank, job):
        g = gizmo_cycle(tank, "Job:", "Job: " + job)
        g["readBack"] = tank_job(tank)
        g["ok"] = bool(g.get("ok")) and g["readBack"] == job
        return g

    def set_role(reel, role):
        g = gizmo_cycle(reel, "Free end:", "Free end: " + role)
        hid = PH._hose(B, reel).get("id")
        vals = ((B.call("jawa/comp_read", thing="RM_HoseReel%d" % hid, comp="CompHoseReel", members="freeEndRole") or {})
                .get("values") or {}) if hid is not None else {}
        g["readBack"] = vals.get("freeEndRole")
        g["ok"] = bool(g.get("ok")) and str(g["readBack"]) == role
        return g

    def letters(text):
        return [l for l in (B.call("jawa/letter_list").get("letters") or []) if text in json.dumps(l, default=str)]

    def goodwill(defname):
        return next((f.get("goodwill") for f in B.call("jawa/list_factions").get("factions") or []
                     if f.get("defName") == defname), None)

    def draft_all():
        got = []
        for p in (B.hp("colonists").get("pawns") or []):
            if B.hp("pawn:%d=draft" % p["id"]).get("success"):
                got.append(p["id"])
        return got

    class Plot(PH.Scene):
        def __init__(self, o):
            self.B = B
            self.o = o
            ox, oz = o
            self.channel = [(ox + 2 + k, oz + 6) for k in range(3)]
            self.pump = (ox + 3, oz + 7)
            self.battery = (ox + 6, oz + 6)
            self.reel = (ox + 3, oz + 8)
            self.end = (ox + 16, oz + 9)
            self.tank = (ox + 17, oz + 9)
            self.north_tank = (ox + 3, oz + 10)

        def rect(self, extra_h=0):
            return (self.o[0] - PH.RF_WEST, self.o[1], PH.RF_PW + PH.RF_WEST, PH.RF_PH + extra_h)

        def ready(self, rid, extra_h=0):
            return V.prepare_site(B, self.rect(extra_h), rows, rid)

    def xz(s):
        return tuple(int(v) for v in s.split(","))

    # ---------------------------------------------------------------- preflight
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, waited = V._wait_playing(B, leave_s=0)
    rm = B.call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False) or {}
    running = [p.lower() for p in rm.get("packageIds") or []]
    B.hp("defaults")
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    B.call("jawa/incident_queue_clear")
    B.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
    drafted = draft_all()                   # nobody idles into a Tantrum next to our tanks
    res["settings_before"] = {f: sget(t, f) for t, f in (
        (S_HOSE, "tankModesEnabled"), (S_HOSE, "freeEndRolesEnabled"), (S_HOSE, "hoseHoldsLiquid"),
        (S_HOSE, "tankUnitsPerCycle"), (S_HOSE, "dumpUnitsPerCycle"), (S_MACH, "liquidTheftEnabled"),
        (S_MACH, "liquidTheftSightRange"), (S_MACH, "liquidTheftGoodwillPerDay"))}
    facs = B.call("jawa/list_factions").get("factions") or []
    nonhostile = [f for f in facs if not f.get("isPlayer") and not f.get("hostile") and not f.get("permanentEnemy")
                  and not f.get("hidden")]
    neutral = next((f for f in nonhostile if str(f.get("defName", "")).startswith("Outlander")), None) or \
        (nonhostile[0] if nonhostile else None)
    res["preflight"] = {"playing": ok, "flowworks": FW_PKG in running, "drafted": drafted, "neutral": neutral}
    good = ok and FW_PKG in running
    row("LC_preflight", "PASS" if good else "UNMEASURED", "HARNESS", res["preflight"])
    if not good:
        return 2

    # ---------------------------------------------------------------- L2
    def blk_L2():
        pa = Plot(xz(a.origin_l2))
        rate = None
        if pa.ready("L2a_site_ready"):
            canal = [pa.P(16 + k, 9) for k in range(3)]
            for c in canal:
                dig(c, 2)
            pa.build("RM_LiquidTank:%d,%d" % pa.north_tank, "RM_HoseReel:%d,%d" % pa.reel)
            B.ticks(2)
            ft = B.hp("filltank:%d,%d=%s,100" % (pa.north_tank + (WATER,)))
            lay = pa.lay(pa.P(15, 9))
            role = set_role(pa.reel, "Outflow")
            job = set_job(pa.north_tank, "Dump")
            f0 = fills(canal)
            tr = [units(pa.north_tank)]
            for _ in range(4):
                B.ticks(250)
                tr.append(units(pa.north_tank))
            f1 = fills(canal)
            pre = None if (ft.get("success") and lay.get("success") and role["ok"] and job["ok"]) else \
                "precondition: filltank %s, lay %s, role %s, job %s" % (ft.get("units"), lay.get("success"), role, job)
            st, cls, det = dump_no_pump_verdict(tr, f0, f1, pre)
            rate = det.get("drainedPer1000")
            row("L2_dump_tank_drains_without_pump", st, cls, dict(det, lay=lay, role=role, job=job))
        pb = Plot(xz(a.origin_l2b))
        if pb.ready("L2b_site_ready"):
            for c in pb.channel:
                dig(c, 2)
            pb.build("RM_LiquidPump:%d,%d" % pb.pump, "Battery:%d,%d" % pb.battery, "RM_UniversalPipe:%d,%d" % pb.P(3, 8),
                     "RM_UniversalPipe:%d,%d" % pb.P(3, 9), "RM_LiquidTank:%d,%d" % pb.north_tank)
            B.ticks(2)
            pb.charge()
            pw = PH._powered(B, pb.pump)
            ft = B.hp("filltank:%d,%d=%s,100" % (pb.north_tank + (WATER,)))
            job = set_job(pb.north_tank, "Dump")
            ok_p, pour = proof("RimMandrake.FlowWorks.RM_NorthstarProofs", "ProofPump", "%d,%d;pour" % pb.pump)
            f0 = fills(pb.channel)
            tr = [units(pb.north_tank)]
            for _ in range(4):
                B.ticks(250)
                tr.append(units(pb.north_tank))
            f1 = fills(pb.channel)
            pre = None if (ft.get("success") and job["ok"] and ok_p and "pour=True" in pour and pw is not None) else \
                "precondition: filltank %s, job %s, pour %s, pump powered after %s" % (ft.get("units"), job, pour, pw)
            st, cls, det = dump_pump_verdict(tr, f0, f1, rate, pre)
            row("L2_pump_pour_drains_dump_fast", st, cls, dict(det, pumpProof=pour, job=job, pumpPoweredAfterTicks=pw))

    # ---------------------------------------------------------------- L6
    def blk_L6():
        if not neutral:
            row("L6_theft_spotted_letter", "UNMEASURED", "SITE", "no non-hostile, non-hidden faction in this world")
            return
        nf = neutral["defName"]
        s = Plot(xz(a.origin_l6))
        if not s.ready("L6_site_ready", extra_h=6):
            return
        s.build("RM_LiquidTank:%d,%d" % s.north_tank, "RM_HoseReel:%d,%d" % s.reel)
        build("RM_LiquidTank:%d,%d" % s.tank, faction=nf)
        B.ticks(2)
        ft = B.hp("filltank:%d,%d=%s,100" % (s.tank + (WATER,)))
        lay = s.lay(s.P(16, 9))
        B.ticks(70)
        fe = PH._hose(B, s.reel).get("freeEnd") or {}
        job = set_job(s.north_tank, "Fill")
        draft_all()
        cc0, l0 = sget(THEFT, "caught"), len(letters("Liquid theft"))
        u_start = units(s.tank)
        wx, wz = s.P(20, 13)                     # 5 cells NE of the foreign tank
        att, cc1, l1, at_check = [], cc0, l0, []
        for i in range(MAX_WITNESS_CYCLES):
            t_sp = step_to(WITNESS_PHASE)
            w = B.call("jawa/spawn_pawn", kindDef="Villager", x=wx, z=wz, faction=nf, count=2)
            ids = [p.get("id") for p in (w.get("pawns") or [])]
            t_chk = step_to(CHECK_PHASE + 2)     # passes the check at % 250 == 7
            plist = B.call("jawa/list_pawns", faction=nf, limit=40).get("pawns") or []
            at_check = [{k: q.get(k) for k in ("id", "x", "z", "downed", "dead")} for q in plist if q.get("id") in ids]
            cc1, l1 = sget(THEFT, "caught"), len(letters("Liquid theft"))
            att.append({"cycle": i, "spawnTick": t_sp, "checkTick": t_chk, "spawned": w.get("success"), "witnesses": at_check,
                        "caught": cc1})
            if (cc1 or 0) > (cc0 or 0):
                break
        drawn = (u_start or 0) - (units(s.tank) or 0)
        pre = None if (ft.get("success") and lay.get("success") and job["ok"]) else \
            "precondition: foreign filltank %s, lay %s, our job %s" % (ft.get("units"), lay.get("success"), job)
        st, cls, det = theft_verdict(drawn, cc0, cc1, l0, l1, at_check, pre)
        row("L6_foreign_tank_drawn", ("UNMEASURED" if pre else "PASS" if drawn > 0 else "FAIL"), "MOD" if not pre else "SITE",
            {"foreignUnits": [u_start, units(s.tank)], "ours": units(s.north_tank)})
        row("L6_theft_spotted_letter", st, cls, dict(det, attempts=att, faction=nf,
                                                     sightRange=res["settings_before"].get("liquidTheftSightRange")))
        fname = str(neutral.get("name") or "")
        row("L6_free_end_names_their_faction",
            "PASS" if (fname and fname in str(fe.get("describe")) and fe.get("portFaction") == fname) else
            ("FAIL" if lay.get("success") else "UNMEASURED"), "MOD", {"freeEnd": fe, "factionName": fname})
        if not a.theft_day:
            row("L6_goodwill_after_a_day", "UNMEASURED", "HARNESS", "not run: pass --theft-day (ticks ~60,000)")
            return
        gw0, gc0 = goodwill(nf), sget(THEFT, "goodwillCharged")
        draft_all()
        for _ in range(DAY_TICKS // REFILL_EVERY + 1):       # every cycle touched
            B.hp("filltank:%d,%d=%s,100" % (s.tank + (WATER,)))
            B.hp("filltank:%d,%d=%s,0" % (s.north_tank + (WATER,)))
            B.ticks(REFILL_EVERY)
        gw1, gc1 = goodwill(nf), sget(THEFT, "goodwillCharged")
        per = res["settings_before"].get("liquidTheftGoodwillPerDay")
        st, cls, det = goodwill_verdict(gw0, gw1, gc0, gc1, per, (cc1 or 0) > (cc0 or 0))
        row("L6_goodwill_after_a_day", st, cls, det)

    try:
        for nm, fn in (("L2", blk_L2), ("L6", blk_L6)):
            if only and nm not in only:
                continue
            print("== %s" % nm, flush=True)
            try:
                B.call("jawa/incident_queue_clear")
                fn()
            except Exception as ex:  # noqa: BLE001
                row("%s_block" % nm, "UNMEASURED", "HARNESS", {"raised": repr(ex)})
    finally:
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        res["counts"] = {s_: sum(1 for r in rows if r["status"] == s_) for s_ in ("PASS", "FAIL", "UNMEASURED")}
        save()
        print("result:", out, json.dumps(res["counts"]))
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
