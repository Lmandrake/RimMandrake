"""FlowWorks thirst LIVE rows (validation.py THIRST_LIVE): the first live driver for them, written on the 2026-10-17 review
walk. Every row is {id, status PASS|FAIL|UNMEASURED, class MOD|SITE|HARNESS, detail}; "could not ask" is UNMEASURED.

  python.exe src/RimMandrake/FlowWorks/northstar/thirst_live.py [out.json] [--only T2,T4,...] [--site X,Z]

Run from the repo root with python.exe, the bridge held, a Playing map with free ground (the calm test site:
Utils/modcheck/test_site_saves.py load calm). The map is DISPOSABLE: the script paints every potable water cell on the
map to Soil so "no other water" holds (a river 60 cells off is still a drink), spawns its own test colonists and drafts
the map's own colonists out of the way. Never save the map afterwards. Settings it flips are restored in a finally.

HOW EACH ROW READS (PROVE / EXPECT / LIES), in the order run:
  T7   Player.log copy given by --log (the load's own): no exception line naming DubsBadHygiene / RM_Thirst / RM_Bottle_.
       LIES: a log that stopped logging (10,000-message cap) reads clean -> the row needs the 'thirst provider:' line present.
  T1   the same log's '[FlowWorks] thirst provider: Own' on a list without Dubs. Only ONE of the bar's three lists is a
       walk list, so the row is UNMEASURED with the measured arm in detail (never PASS from one arm of three).
  T2   jawa/pawn_need list on every free colonist: exactly one RM_Thirst, no DBHThirst.
  T3   a drafted fresh colonist, thirstHeatScaling OFF (so the site temperature cannot move it), need 0.9, 15,000 ticks:
       drop 0.2 +/- 0.03 x thirstRateMultiplier. LIES: a drink in the window -> drafted, and no water on the map.
  T6   a second drafted colonist held at need 0 for 60,000 ticks: RM_Dehydration 0.30 +/- 0.03.
  T4   need 0.2, a RM_Bottle_FreshWater beside the pawn, ordered Ingest (jawa/ordered_job count 1): level rises >= 0.45
       and a RM_BottleDirty exists afterwards (map rect). LIES: an unreadable level -> UNMEASURED.
  T5   the same order with RM_Bottle_SaltWater on a second pawn: gain = 0.7 x the fresh gain (+/- 0.1), RM_SaltPoisoning
       0.25 +/- 0.03, memory RM_Thought_SaltRelief, no FoodPoisoning hediff.
  T10  a 4x4 WaterShallow pond; a fresh colonist 10 cells off at need 0.2, no bottles anywhere: within 900 ticks its job
       is RM_DrinkFromTerrain and the need rises >= 0.4; drinkFromTerrain OFF on a second colonist: no such job in 900.
  T9   a tame and a wild Muffalo beside that pond at RM_Thirst 0.25: each need rises within 2,500 ticks (no bottle on the
       map, so a rise is a terrain drink: INFERRED, the animal job is not on the bridge).
  T11  three RM_BottleEmpty beside a WaterOceanShallow strip, the fresh pond 20 cells off, hauling allowed: within 6,000
       ticks no RM_Bottle_SaltWater exists and >= 1 RM_Bottle_FreshWater does (UNMEASURED when nothing filled at all).
  T12  fresh pond and fresh bottles removed; a colonist at 0.2 standing on the salt strip: no drink job and no salt bottle
       for 2,000 ticks; then a fresh bottle 30 cells off: within 1,500 ticks the bottle is gone or the job is Ingest.
  T13  a toxic strip (RM_WaterPoisonedShallow) only: at 0.05 no drink job in 1,000 ticks; at 0.0 RM_DrinkFromTerrain on it
       and ToxicBuildup appears.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(os.path.dirname(os.path.dirname(HERE)), "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

S_TH = "RimMandrake.FlowWorks.Thirst.RM_ThirstSettings"
NEED = "RM_Thirst"
POTABLE_TERRAIN = ("WaterShallow", "WaterDeep", "WaterMovingShallow", "WaterMovingChestDeep", "RM_WaterFrigidShallow",
                   "RM_WaterFrigidDeep", "RM_Water_Rust", "RM_Water_Verdigris", "RM_Water_Amber", "RM_Water_Violet",
                   "RM_Water_Chalk", "Marsh")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--only", default="")
    ap.add_argument("--site", default="150,130", help="south-west corner of a 40x40 site")
    ap.add_argument("--log", default="", help="this load's Player.log copy (T1, T7)")
    a = ap.parse_args(argv)
    only = [x.strip().upper() for x in a.only.split(",") if x.strip()]
    import validation_core as V
    B = V.Bridge()
    X0, Z0 = map(int, a.site.split(","))
    out = a.out or os.path.join(HERE, "thirst_live_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "thirst_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        try:
            os.replace(out + ".tmp", out)
        except OSError:          # Windows python over \\wsl.localhost: a replace can be refused while a reader holds the file
            with open(out, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "detail": det})
        print("%-34s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:400]), flush=True)
        save()

    def want(rid):
        return not only or rid.split("_")[0].upper() in only

    # ------------------------------------------------------------------ helpers
    def tg():
        g = B.call("rimworld/get_game_info")
        return g.get("ticksGame") or (g.get("state") or {}).get("tick")

    UNDER_TEST = set()

    def feed_all():
        """Long advances: the clock governor stops on any starving colonist (the drafted bystanders never eat)."""
        for c in colonists():
            pid = re.sub(r"^Thing_", "", c["pawnId"])
            B.call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
            if pid in UNDER_TEST:
                continue
            # bystanders (earlier rows' test pawns, the drafted locals): no sad wander stopping the clock
            for nd, lv in (("Mood", 1.0), ("Rest", 1.0), (NEED, 1.0)):
                B.call("jawa/pawn_need", pawn=pid, action="need", need=nd, level=lv)
            B.call("jawa/pawn_mental", pawn=pid, action="end")

    def ticks(n):
        t0 = tg()
        left = n
        while left > 0:
            k = min(1500, left)
            try:
                B.ticks(k)
            except Exception as ex:  # noqa: BLE001 - clockgate.GovernorStop: a bystander starving / breaking stops the clock
                if "GovernorStop" not in type(ex).__name__:
                    raise
                res.setdefault("governorStops", []).append(str(ex)[:160])
                if len(res["governorStops"]) > 12:
                    raise
                feed_all()
                continue        # the stop's partial advance is re-measured by the t1-t0 top-up below
            left -= k
        t1 = tg()
        if t0 is not None and t1 is not None and t1 - t0 < n:
            B.ticks(n - (t1 - t0))

    def sget(field):
        return B.call("jawa/mod_settings_field", typeName=S_TH, action="get", field=field).get("value")

    def sset(field, value):
        r = B.call("jawa/mod_settings_field", typeName=S_TH, action="set", field=field, value=str(value))
        back = sget(field)
        if str(back).lower() != str(value).lower():
            raise RuntimeError("setting %s did not read back %s (got %s): %s" % (field, value, back, str(r)[:160]))

    def need(pid, level=None):
        if level is not None:
            B.call("jawa/pawn_need", pawn=pid, action="need", need=NEED, level=float(level))
        r = B.call("jawa/pawn_need", pawn=pid, action="list") or {}
        for n in r.get("needs") or []:
            if n.get("need") == NEED:
                return float(n.get("level"))
        return None

    def needs_of(pid):
        r = B.call("jawa/pawn_need", pawn=pid, action="list") or {}
        return [n.get("need") for n in r.get("needs") or []], [m.get("def") for m in r.get("memories") or []]

    def hediffs(pid):
        r = B.call("jawa/pawn_get", pawn=pid) or {}
        ps = r.get("pawns") or []
        out_h = {}
        for h in (ps[0].get("hediffs") if ps else None) or []:
            d = h.get("def") or h.get("defName") or h.get("hediff")
            out_h[d] = max(out_h.get(d, 0.0), float(h.get("severity") or 0.0))
        return out_h

    def colonists():
        r = B.call("rimworld/list_colonists", currentMapOnly=True) or {}
        return [c for c in r.get("colonists") or [] if not c.get("dead")]

    def job(pid):
        for c in colonists():
            if c.get("pawnId") in (pid, "Thing_" + pid) or str(c.get("thingIdNumber")) == re.sub(r"\D", "", pid):
                return c.get("job")
        return None

    def spawn_colonist(x, z):
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, count=1, faction="PlayerColony") or {}
        ids = [p.get("id") or p.get("thingId") for p in (r.get("pawns") or r.get("spawned") or [])]
        if not ids:
            raise RuntimeError("spawn_pawn gave no id: %s" % str(r)[:200])
        pid = ids[0]
        for hd in hediffs(pid):   # a generated colonist can arrive hurt; drop its fresh injuries (chronic ones stay)
            if hd in ("Gunshot", "Cut", "Scratch", "Bite", "Crush", "Crack", "Burn", "Stab", "Bruise", "Shredded"):
                for _ in range(6):
                    B.call("jawa/pawn_health", pawn=pid, action="remove", hediff=hd)
        for nd in ("Food", "Rest", "Joy", "Mood"):
            B.call("jawa/pawn_need", pawn=pid, action="need", need=nd, level=1.0)
        return pid

    def spawn(defn, x, z, n=1):
        r = B.call("rimworld/spawn_thing", defName=defn, x=x, z=z, stackCount=n) or {}
        return re.sub(r"^Thing_", "", str(r.get("thingId") or "")) or None   # jawa/ tools want the bare ThingID

    def count(defn, rect=None):
        kw = {"defName": defn, "limit": 500}
        if rect:
            kw["rect"] = rect
        r = B.call("jawa/list_things", **kw) or {}
        return sum(int(t.get("stackCount") or 1) for t in r.get("things") or [] if (t.get("def") or t.get("defName")) == defn)

    def paint(defn, x, z, w, h):
        B.call("jawa/set_terrain_batch", ops="%s:%d,%d,%d,%d" % (defn, x, z, w, h))

    def draft(pid, on=True):
        B.call("jawa/set_draft", pawnId=pid, drafted=on)

    def poll_job(pid, jobs, budget, step=60):
        # HARNESS (walk 2026-10-17, T13): a job giver is consulted only when the current job ENDS; a colonist mid-way
        # through a long GotoWander (the home area is far from the site) re-thought nothing for 1,200 ticks. End the
        # current job first, as the end of an ordinary short job would.
        B.call("jawa/stop_job", pawnId=pid)
        seen = []
        t = 0
        while t < budget:
            ticks(step)
            t += step
            j = job(pid)
            if j and (not seen or seen[-1] != j):
                seen.append(j)
            if j in jobs:
                return t, seen
        return None, seen

    DRINKS = ("RM_Bottle_FreshWater", "RM_Bottle_IcyWater", "RM_BottleEmpty", "RM_BottleDirty", "RM_Bottle_SaltWater",
              "RM_Bucket_FreshWater", "RM_BlueIceMeltwaterCan")

    def purge_drinks():
        """Every bottle / bucket on the map's ground goes (an empty bottle is refilled by a hauler, which is a source)."""
        left = {}
        for d in DRINKS:
            lt = B.call("jawa/list_things", defName=d, limit=500) or {}
            for t in lt.get("things") or []:
                B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t.get("x"), t.get("z")), categories="Item")
            n = count(d)
            if n:
                left[d] = n
        if left:
            raise RuntimeError("drinks still on the map after the purge: %s" % left)

    SITE = "%d,%d,40,40" % (X0, Z0)
    saved = {}
    keys = ("thirstEnabled", "thirstRateMultiplier", "thirstHeatScaling", "animalsGetThirst", "drinkFromTerrain",
            "waterQualityEffects", "lastResortDrinking", "saltBreakEnabled", "roughDrinkPenalty")
    try:
        for k in keys:
            saved[k] = sget(k)
        res["settings_before"] = saved
        res["running"] = len((B.call("jawa/mod_inventory") or {}).get("mods") or [])

        # ---------------------------------------------------------------- log rows (no map needed)
        if want("T7") or want("T1"):
            txt = ""
            try:
                with open(a.log, "r", encoding="utf-8", errors="replace") as f:
                    txt = f.read()
            except OSError as ex:
                txt = None
                why = str(ex)
            prov = re.findall(r"\[FlowWorks\] thirst provider: (\w+) \(([^)]*)\)", txt or "")
            if want("T7"):
                if txt is None:
                    row("T7_no_dbh_clean_log", "UNMEASURED", "HARNESS", {"why": "no --log: " + why})
                elif not prov:
                    row("T7_no_dbh_clean_log", "UNMEASURED", "HARNESS", {"why": "no 'thirst provider:' line: the log may have stopped"})
                else:
                    exc = [l for l in txt.splitlines() if re.search(r"Exception", l)]
                    bad = [l for l in exc if re.search(r"DubsBadHygiene|RM_Thirst|RM_Bottle_", l)]
                    row("T7_no_dbh_clean_log", "FAIL" if bad else "PASS", "MOD",
                        {"exceptionLines": len(exc), "naming": bad[:3], "firstException": exc[0][:200] if exc else None})
            if want("T1"):
                if not prov:
                    row("T1_provider_line", "UNMEASURED", "HARNESS", {"why": "no provider line in the given log"})
                else:
                    row("T1_provider_line", "UNMEASURED", "HARNESS",
                        {"measuredArm": "no Dubs on the list -> %s (%s)" % prov[-1], "armOk": prov[-1][0] == "Own",
                         "why": "the bar needs three mod lists (no DBH / Lite+Thirst / Lite alone); this run had one"})

        # ---------------------------------------------------------------- the site
        cols0 = colonists()
        for c in cols0:
            draft(re.sub(r"^Thing_", "", c["pawnId"]))
        # every potable cell on the map -> Soil, so the only water is what a row paints
        tb = B.call("jawa/get_terrain_batch", rects="0,0,%d,%d" % (250, 250)) or {}
        wet = [op for op in (tb.get("ops") or "").split(";") if op and op.split(":")[0] in POTABLE_TERRAIN]
        if wet:
            B.call("jawa/set_terrain_batch", ops=";".join("Soil:" + op.split(":")[1] for op in wet))
        bottles = [d for d in ("RM_Bottle_FreshWater", "RM_Bottle_SaltWater", "RM_Bottle_IcyWater") if count(d)]
        res["site"] = {"rect": SITE, "paintedWaterRuns": len(wet), "bottlesOnMap": bottles, "draftedOwn": len(cols0)}
        ok = V.prepare_site(B, (X0, Z0, 40, 40), rows, "site_ready")
        if not ok:
            return 2

        # ---------------------------------------------------------------- T2
        if want("T2"):
            per = {}
            for c in colonists():
                pid = re.sub(r"^Thing_", "", c["pawnId"])
                ns, _ = needs_of(pid)
                per[pid] = [ns.count(NEED), ns.count("DBHThirst")]
            bad = {k: v for k, v in per.items() if v != [1, 0]}
            row("T2_one_thirst_need", "FAIL" if bad or not per else "PASS", "MOD", {"perColonist": per, "bad": bad})

        # ---------------------------------------------------------------- T3 + T6 (one long advance)
        if want("T3") or want("T6"):
            sset("thirstHeatScaling", False)
            pa = spawn_colonist(X0 + 2, Z0 + 2)
            pc = spawn_colonist(X0 + 4, Z0 + 2)
            UNDER_TEST.update((pa, pc))
            draft(pa)
            draft(pc)
            mult = float(sget("thirstRateMultiplier") or 1)
            a0 = need(pa, 0.9)
            need(pc, 0.0)
            ticks(15000)
            a1 = need(pa)
            if want("T3"):
                if a0 is None or a1 is None:
                    row("T3_need_falls", "UNMEASURED", "HARNESS", {"levels": [a0, a1]})
                else:
                    drop = a0 - a1
                    exp = 0.2 * mult
                    row("T3_need_falls", "PASS" if abs(drop - exp) <= 0.03 * mult else "FAIL", "MOD",
                        {"before": a0, "after": a1, "drop": round(drop, 4), "expect": exp, "heatScaling": False,
                         "ticks": 15000})
            if want("T6"):
                for _ in range(3):
                    need(pc, 0.0)
                    ticks(15000)
                need(pc, 0.0)
                h = hediffs(pc)
                sev = h.get("RM_Dehydration")
                st = "UNMEASURED" if not h and sev is None else ("PASS" if sev is not None and abs(sev - 0.30) <= 0.03 else "FAIL")
                row("T6_dehydration_readable", st, "MOD" if st != "UNMEASURED" else "HARNESS",
                    {"RM_Dehydration": sev, "hediffs": h, "heldAtZeroTicks": 60000})
            sset("thirstHeatScaling", saved["thirstHeatScaling"])

        # ---------------------------------------------------------------- T4 / T5 ordered bottles
        fresh_gain = None
        if want("T4") or want("T5"):
            pb = spawn_colonist(X0 + 10, Z0 + 2)
            l0 = need(pb, 0.2)
            bid = spawn("RM_Bottle_FreshWater", X0 + 11, Z0 + 2)
            dirty0 = count("RM_BottleDirty")
            r = B.call("jawa/ordered_job", pawnId=pb, jobDef="Ingest", targetAId=bid, count=1, waitTicks=30) or {}
            ticks(600)
            l1 = need(pb)
            dirty1 = count("RM_BottleDirty")
            fresh_gain = (l1 - l0) if None not in (l0, l1) else None
            if want("T4"):
                if fresh_gain is None or not r.get("accepted"):
                    row("T4_bottle_satisfies", "UNMEASURED", "HARNESS", {"order": {k: r.get(k) for k in ("accepted", "afterJobDef", "message")}, "levels": [l0, l1]})
                else:
                    ok4 = fresh_gain >= 0.45 and dirty1 > dirty0
                    row("T4_bottle_satisfies", "PASS" if ok4 else "FAIL", "MOD",
                        {"levels": [l0, l1], "gain": round(fresh_gain, 4), "dirtyBottles": [dirty0, dirty1]})
            if want("T5"):
                pd = spawn_colonist(X0 + 14, Z0 + 2)
                s0 = need(pd, 0.2)
                sid = spawn("RM_Bottle_SaltWater", X0 + 15, Z0 + 2)
                r = B.call("jawa/ordered_job", pawnId=pd, jobDef="Ingest", targetAId=sid, count=1, waitTicks=30) or {}
                ticks(600)
                s1 = need(pd)
                h = hediffs(pd)
                _, mem = needs_of(pd)
                if None in (s0, s1) or fresh_gain is None or not r.get("accepted"):
                    row("T5_salt_water_quality", "UNMEASURED", "HARNESS", {"levels": [s0, s1], "freshGain": fresh_gain,
                                                                             "order": {k: r.get(k) for k in ("accepted", "afterJobDef", "message")}})
                else:
                    ratio = (s1 - s0) / fresh_gain if fresh_gain else 0
                    sp = h.get("RM_SaltPoisoning")
                    bad = []
                    if abs(ratio - 0.7) > 0.1:
                        bad.append("hydrate x%.2f, want x0.7" % ratio)
                    if sp is None or abs(sp - 0.25) > 0.03:
                        bad.append("RM_SaltPoisoning %s, want 0.25" % sp)
                    if "RM_Thought_SaltRelief" not in mem:
                        bad.append("no RM_Thought_SaltRelief memory")
                    if "FoodPoisoning" in h:
                        bad.append("FoodPoisoning present")
                    row("T5_salt_water_quality", "FAIL" if bad else "PASS", "MOD",
                        {"order": {k: r.get(k) for k in ("accepted", "beforeJobDef", "afterJobDef", "message", "note")},
                         "saltBottleLeft": count("RM_Bottle_SaltWater", "%d,%d,1,1" % (X0 + 15, Z0 + 2)),
                         "levels": [s0, s1], "ratioToFresh": round(ratio, 3), "hediffs": h, "memories": mem, "bad": bad,
                         "note": "one pawn, one bottle (the bar says x4 on test pawns; the per-drink numbers are what it scores)"})

        # ---------------------------------------------------------------- T10 / T9: a pond
        PX, PZ = X0 + 20, Z0 + 20
        if want("T10") or want("T9"):
            paint("WaterShallow", PX, PZ, 4, 4)
        if want("T10"):
            pe = spawn_colonist(PX + 12, PZ + 1)
            l0 = need(pe, 0.2)
            t_hit, seen = poll_job(pe, ("RM_DrinkFromTerrain",), 900)
            trace = []
            l1 = None
            for _ in range(15):          # up to 1,500 ticks after the job starts, one read every 100
                ticks(100)
                l1 = need(pe)
                trace.append([job(pe), l1])
                if l1 is not None and l1 - l0 >= 0.4:
                    break
            pf = spawn_colonist(PX + 12, PZ + 3)
            sset("drinkFromTerrain", False)
            try:
                need(pf, 0.2)
                t_off, seen_off = poll_job(pf, ("RM_DrinkFromTerrain",), 900)
            finally:
                sset("drinkFromTerrain", saved["drinkFromTerrain"])
            bad = []
            if t_hit is None:
                bad.append("no RM_DrinkFromTerrain within 900 ticks (jobs seen %s)" % seen)
            elif l1 is None or l1 - l0 < 0.4:
                bad.append("need rose only %s -> %s" % (l0, l1))
            if t_off is not None:
                bad.append("drinkFromTerrain OFF but the job ran")
            row("T10_terrain_drink", "FAIL" if bad else "PASS", "MOD",
                {"jobAtTick": t_hit, "jobsSeen": seen, "levels": [l0, l1], "trace": trace, "offJobsSeen": seen_off, "bad": bad})
            draft(pe)
            draft(pf)
        if want("T9"):
            got = []
            for fac in ("PlayerColony", "none"):
                r = B.call("jawa/spawn_pawn", kindDef="Muffalo", x=PX - 2, z=PZ + 1, count=1, faction=fac) or {}
                ids = [p.get("id") or p.get("thingId") for p in (r.get("pawns") or r.get("spawned") or [])]
                if ids:
                    got.append((fac, ids[0]))
            lv = {}
            for fac, pid in got:
                lv[pid] = [need(pid, 0.25)]
            ticks(2500)
            for fac, pid in got:
                lv[pid].append(need(pid))
            if len(got) < 2 or any(v[0] is None for v in lv.values()):
                row("T9_animals_drink", "UNMEASURED", "HARNESS", {"spawned": got, "levels": lv,
                                                                  "why": "animal not spawned or carries no RM_Thirst"})
            else:
                rose = {pid: v[1] is not None and v[1] > v[0] + 0.2 for pid, v in lv.items()}
                row("T9_animals_drink", "PASS" if all(rose.values()) else "FAIL", "MOD",
                    {"animals": got, "levels": lv, "rose": rose, "bottlesOnMap": count("RM_Bottle_FreshWater"),
                     "inferred": "no bottle on the map: a rise beside the pond is a terrain drink (the job is not on the bridge)"})

        # ---------------------------------------------------------------- T11 / T12 salt
        SX, SZ = X0 + 2, Z0 + 30
        if want("T11") or want("T12"):
            paint("WaterOceanShallow", SX, SZ, 6, 2)
        if want("T11"):
            if not (want("T10") or want("T9")):
                paint("WaterShallow", PX, PZ, 4, 4)
            for i in range(3):
                spawn("RM_BottleEmpty", SX + i, SZ + 2)
            pg = spawn_colonist(SX + 3, SZ + 3)
            fresh0, salt0 = count("RM_Bottle_FreshWater"), count("RM_Bottle_SaltWater")
            seen = []
            for _ in range(20):
                ticks(300)
                j = job(pg)
                if j and (not seen or seen[-1] != j):
                    seen.append(j)
                if count("RM_Bottle_SaltWater") > salt0:
                    break
            fresh1, salt1 = count("RM_Bottle_FreshWater"), count("RM_Bottle_SaltWater")
            det = {"fresh": [fresh0, fresh1], "salt": [salt0, salt1], "jobsSeen": seen}
            if salt1 > salt0:
                row("T11_autofill_skips_salt", "FAIL", "MOD", det)
            elif fresh1 <= fresh0:
                row("T11_autofill_skips_salt", "UNMEASURED", "SITE", dict(det, why="nothing was filled in 6,000 ticks: the fill giver never ran here"))
            else:
                row("T11_autofill_skips_salt", "PASS", "MOD", det)
            draft(pg)
        if want("T12"):
            paint("Soil", PX, PZ, 4, 4)
            purge_drinks()
            ph = spawn_colonist(SX + 2, SZ)
            l0 = need(ph, 0.2)
            t_any, seen = poll_job(ph, ("RM_DrinkFromTerrain", "Ingest", "RM_DrinkFromContainer"), 2000, step=100)
            salt_b = count("RM_Bottle_SaltWater")
            bid = spawn("RM_Bottle_FreshWater", SX + 32, SZ)
            t_fetch, seen2 = poll_job(ph, ("Ingest",), 1500, step=60)
            ticks(400)
            gone = count("RM_Bottle_FreshWater", "%d,%d,1,1" % (SX + 32, SZ)) == 0
            bad = []
            if t_any is not None:
                bad.append("a drink job ran with only salt in reach: %s" % seen)
            if t_fetch is None and not gone:
                bad.append("the fresh bottle 30 cells off was not fetched")
            row("T12_no_routine_salt", "FAIL" if bad else "PASS", "MOD",
                {"jobsSalt": seen, "jobsAfterBottle": seen2, "bottleGone": gone, "saltBottles": salt_b, "level0": l0, "bad": bad})
            draft(ph)

        # ---------------------------------------------------------------- T13 toxic last resort
        if want("T13"):
            TX, TZ = X0 + 30, Z0 + 30
            paint("Soil", SX, SZ, 6, 2)
            paint("RM_WaterPoisonedShallow", TX, TZ, 4, 2)
            purge_drinks()
            pt = spawn_colonist(TX + 1, TZ + 3)
            need(pt, 0.05)
            t1, seen1 = poll_job(pt, ("RM_DrinkFromTerrain",), 1000, step=100)
            need(pt, 0.0)
            t2, seen2 = poll_job(pt, ("RM_DrinkFromTerrain",), 1200, step=60)
            for _ in range(15):          # let the drink finish (walk + drink ~ 400 ticks in T10)
                ticks(100)
                if job(pt) != "RM_DrinkFromTerrain":
                    break
            lvl = need(pt)
            h = hediffs(pt)
            # the third arm: a fresh bottle on the map beats the toxic strip at need 0
            spawn("RM_Bottle_FreshWater", TX + 1, TZ + 10)
            need(pt, 0.0)
            t3, seen3 = poll_job(pt, ("Ingest", "RM_DrinkFromTerrain"), 900, step=30)
            bad = []
            if not seen3 or seen3[-1] != "Ingest":
                bad.append("with a fresh bottle on the map the desperate pawn chose %s, not the bottle" % seen3)
            if t1 is not None:
                bad.append("drank toxic water at 0.05 (LastResort is need 0 only)")
            if t2 is None:
                bad.append("at need 0 no RM_DrinkFromTerrain on the toxic strip (jobs %s)" % seen2)
            elif "ToxicBuildup" not in h:
                bad.append("drank toxic water but no ToxicBuildup")
            row("T13_desperate_toxic_last", "FAIL" if bad else "PASS", "MOD",
                {"jobsAt005": seen1, "jobsAt0": seen2, "levelAfter": lvl, "hediffs": h, "jobsWithBottle": seen3, "bad": bad})
            draft(pt)
        # ================================================================ batch 2 (written later the same walk)
        def mems(pid):
            return needs_of(pid)[1]

        def wait_job_end(pid, jobname, budget=1500):
            for _ in range(budget // 100):
                ticks(100)
                if job(pid) != jobname:
                    return True
            return False

        # ---------------------------------------------------------------- T27 water item
        if want("T27"):
            purge_drinks()
            pw = spawn_colonist(X0 + 2, Z0 + 12)
            l0 = need(pw, 0.2)
            spawn("RM_BlueIceMeltwaterCan", X0 + 8, Z0 + 12)
            t_hit, seen = poll_job(pw, ("RM_DrinkWaterItem",), 900)
            if t_hit is not None:
                wait_job_end(pw, "RM_DrinkWaterItem")
            l1 = need(pw)
            m = mems(pw)
            bad = []
            if t_hit is None:
                bad.append("no RM_DrinkWaterItem (jobs %s)" % seen)
            elif l1 is None or abs((l1 - l0) - 0.67) > 0.06:
                bad.append("gain %s, want +0.67" % (None if l1 is None else round(l1 - l0, 3)))
            if t_hit is not None and "RM_Thought_DrankDistilled" not in m:
                bad.append("no RM_Thought_DrankDistilled")
            row("T27_water_items", "FAIL" if bad else "PASS", "MOD", {"jobs": seen, "levels": [l0, l1], "memories": m, "bad": bad})
            draft(pw)

        # ---------------------------------------------------------------- T28 sanguophage
        if want("T28"):
            purge_drinks()
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=X0 + 2, z=Z0 + 16, count=1, faction="PlayerColony",
                       xenotype="Sanguophage") or {}
            ps = r.get("pawns") or [{}]
            sg = ps[0].get("id")
            bl = spawn_colonist(X0 + 6, Z0 + 16)
            out28 = {"xenotype": ps[0].get("xenotype"), "applied": ps[0].get("xenotypeApplied")}
            for pid, tag in ((sg, "sang"), (bl, "base")):
                if not pid:
                    continue
                draft(pid)
                l0 = need(pid, 0.2)
                hid = spawn("HemogenPack", *(X0 + 3, Z0 + 16) if tag == "sang" else (X0 + 7, Z0 + 16))
                r2 = B.call("jawa/ordered_job", pawnId=pid, jobDef="Ingest", targetAId=hid, count=1, waitTicks=30) or {}
                wait_job_end(pid, "Ingest", 1500)   # HARNESS: a hemogen pack takes ~480 ticks to ingest (500 read it mid-job)
                ticks(60)
                out28[tag] = {"levels": [l0, need(pid)], "accepted": r2.get("accepted"), "after": r2.get("afterJobDef"),
                              "msg": r2.get("message"), "packLeft": count("HemogenPack")}
            bad = []
            sgl = out28.get("sang", {}).get("levels") or [None, None]
            bsl = out28.get("base", {}).get("levels") or [None, None]
            if out28.get("xenotype") != "Sanguophage" or None in sgl:
                row("T28_sanguophage_blood", "UNMEASURED", "HARNESS", out28)
            else:
                if abs((sgl[1] - sgl[0]) - 0.5) > 0.06:
                    bad.append("sanguophage thirst gain %s, want +0.5" % round(sgl[1] - sgl[0], 3))
                if None not in bsl and (bsl[1] - bsl[0]) > 0.02:
                    bad.append("a baseliner's thirst rose %s on a hemogen pack" % round(bsl[1] - bsl[0], 3))
                row("T28_sanguophage_blood", "FAIL" if bad else "PASS", "MOD", dict(out28, bad=bad,
                    notRead="hemogen up (the gene resource is not on jawa/pawn_need)"))

        # ---------------------------------------------------------------- T19 awkward access (bucket arm + bottle arm)
        if want("T19"):
            purge_drinks()
            pk = spawn_colonist(X0 + 2, Z0 + 20)
            m0 = mems(pk)
            need(pk, 0.2)
            spawn("RM_Bucket_FreshWater", X0 + 8, Z0 + 20)
            t_hit, seen = poll_job(pk, ("RM_DrinkFromContainer", "Ingest"), 900)
            if t_hit is not None:
                wait_job_end(pk, seen[-1])
            m1 = mems(pk)
            bk = (B.call("jawa/list_things", defName="RM_Bucket_FreshWater", limit=5) or {}).get("things") or []
            insp = None
            if bk:
                for t in (B.call("jawa/inspect_string", thingIds=bk[0]["id"]) or {}).get("things") or []:
                    insp = " | ".join(t.get("inspect") or [])
            pb2 = spawn_colonist(X0 + 12, Z0 + 20)
            draft(pb2)
            need(pb2, 0.2)
            bid = spawn("RM_Bottle_FreshWater", X0 + 13, Z0 + 20)
            B.call("jawa/ordered_job", pawnId=pb2, jobDef="Ingest", targetAId=bid, count=1, waitTicks=30)
            ticks(500)
            mb = mems(pb2)
            bad = []
            if "RM_DrinkFromContainer" not in seen:
                bad.append("no RM_DrinkFromContainer from the only bucket (jobs %s)" % seen)
            elif "RM_Thought_DrankRough" not in m1 or "RM_Thought_DrankRough" in m0:
                bad.append("bucket drink left no RM_Thought_DrankRough")
            if bk and "Partly drunk" not in (insp or ""):
                bad.append("bucket inspect %r has no 'Partly drunk'" % insp)
            if "RM_Thought_DrankRough" in mb:
                bad.append("a bottle drink at home gave RM_Thought_DrankRough")
            row("T19_awkward_access", "FAIL" if bad else "PASS", "MOD",
                {"jobs": seen, "memAfterBucket": m1, "bucketInspect": insp, "memAfterBottle": mb, "bad": bad,
                 "notRun": "tank arm, Ascetic/tribal arms, pond arm"})
            draft(pk)

        # ---------------------------------------------------------------- T24 bucket douses fire
        if want("T24"):
            purge_drinks()
            FX, FZ = X0 + 25, Z0 + 5
            B.call("jawa/destroy_batch", rects="%d,%d,14,10" % (FX - 6, FZ - 3), categories="Plant,Item,Filth")
            B.call("jawa/map_zones", action="paintArea", area="Home", rect="%d,%d,14,10" % (FX - 6, FZ - 3), value=True)
            pf = spawn_colonist(FX - 5, FZ + 1)
            spawn("RM_Bucket_FreshWater", FX - 3, FZ + 1)
            empty0 = count("RM_BucketEmpty") + count("RM_BucketDirty")
            # fuel: ChanceToStartFireIn refuses bare soil (live: 9 of 9 cells refused), so the 3x3 gets grown grass first
            B.call("jawa/set_plants", ops="Plant_Grass:%d,%d,3,3" % (FX, FZ), growth=1.0)
            B.call("jawa/map_fire", action="start", rect="%d,%d,3,3" % (FX, FZ), fireSize=0.8)
            fires0 = count("Fire", "%d,%d,3,3" % (FX, FZ))
            B.call("jawa/stop_job", pawnId=pf)
            seen = []
            for _ in range(20):
                ticks(30)
                j = job(pf)
                if j and (not seen or seen[-1] != j):
                    seen.append(j)
                if j == "RM_DouseFireWithBucket":
                    break
            if "RM_DouseFireWithBucket" in seen:
                wait_job_end(pf, "RM_DouseFireWithBucket", 900)
            fires1 = count("Fire", "%d,%d,5,5" % (FX - 1, FZ - 1))
            empty1 = count("RM_BucketEmpty") + count("RM_BucketDirty")
            B.call("jawa/map_fire", action="extinguish", rect="%d,%d,14,10" % (FX - 6, FZ - 3))
            bad = []
            if fires0 < 1:
                row("T24_bucket_douses_fire", "UNMEASURED", "SITE", {"why": "no fire took on the plot", "fires": fires0})
            else:
                if "RM_DouseFireWithBucket" not in seen:
                    bad.append("no RM_DouseFireWithBucket (jobs %s)" % seen)
                # the douse puts out the fires within 1.5 cells of the cell it targets (not read on the bridge): from a 3x3
                # that is 4 (corner target) to 9 (centre), so one job taking out >= 4 is the area douse; fires left over
                # from an edge/corner target are not a fault (first live run: 9 -> 3)
                if fires0 - fires1 < 4 and "RM_DouseFireWithBucket" in seen:
                    bad.append("one douse put out only %d fires (an area douse takes >= 4 of a 3x3)" % (fires0 - fires1))
                if empty1 <= empty0 and "RM_DouseFireWithBucket" in seen:
                    bad.append("no empty bucket left")
                row("T24_bucket_douses_fire", "FAIL" if bad else "PASS", "MOD",
                    {"jobs": seen, "fires": [fires0, fires1], "emptyBuckets": [empty0, empty1], "bad": bad,
                     "notRun": "the no-bucket BeatFire arm"})
            draft(pf)
    finally:
        for k, v in saved.items():
            try:
                B.call("jawa/mod_settings_field", typeName=S_TH, action="set", field=k, value=str(v))
            except Exception:  # noqa: BLE001 - restore every one we can
                pass
        res["settings_after"] = {k: sget(k) for k in saved}
        res["ended"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
