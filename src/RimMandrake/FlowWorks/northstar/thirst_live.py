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
  T15  four 2x2 slime pools (red/green/white/yellow), a colonist at 0.0 beside each, one at 0.05: each drinks ITS pool
       (RM_Thought_DrankSlime, RM_SlimePurge, its colour's hediff and NO other colour's), the 0.05 pawn drinks nothing.
       LIES: the 60-tick job sample can miss a short drink, so a missed RM_DrinkFromTerrain is not a failure by itself;
       the hediffs are the drink. A pawn carrying ANOTHER pool's hediff walked to that pool: see T15R.
  T15R (opt-in: --only T15R; it RELOADS the --reload-site save twice, so it runs last and alone) the stale terrain mark.
       Load, spawn A first, need 0.2 with no water (its search fails: marked for 600 ticks); reload, spawn B first (same
       thingIDNumber, ticks restarted), a red pool beside it, need 0: B drinks within 300 ticks. LIES: B not holding A's
       ID, or B's search tick outside [A's mark tick, +600) -> the collision was not reproduced -> UNMEASURED, never PASS.
       Live 2026-10-17 round 2 on the fixed DLL: PASS (B = A's Human36705, B's search at tick 92 in [2, 602), drank in 30).
       Its red against the pre-fix DLL (6f092b3ce8^) is inferred from the mechanism, not observed.

BATCH 3 (thirst live round 2, 2026-10-17), on a second cleared site east of the first (X0+45..+95); every row dries the
whole map of liquid first and quenches every bystander (a thirsty earlier-row pawn otherwise drinks the test's water):
  T18  UNMEASURED SITE unless Dubs Bad Hygiene Lite + Thirst is loaded (provider Dbh); the walk list has no Dubs.
  T14  native = RM_ThirstUtility.NativeHere (the MAP biome's roster, read live by static_call over candidate kinds), not a
       salt-biome map: a native and a non-native wild animal at 0.2 beside salt water only, 2,500 ticks: the native rises
       > 0.2 with no FoodPoisoning, the non-native does not rise. First run: Dromedary native, Muffalo not, on AridShrubland.
  T16  RM_Slime_Liquid painted 2x2 (the drink rule is the terrain's extension, not the biome): at 0 -> RM_DrinkFromTerrain,
       RM_Slimification, the slime thought; lastResortDrinking OFF -> no drink in 900 ticks.
  T20  ordered RM_DrinkFromContainer on one bucket until it is gone: exactly 10 drinks (15 L / 1.5 L), then a dirty bucket;
       a bucket with 3 drinks taken, poured by order (RM_EmptyIntoTankJob) into a Store tank: +105 units (10.5 L).
  T23  a Fill tank (ProofTank) holding brine 100, a brine strip, 3 empty buckets, one undrafted hauler: brine gathered and
       poured unasked (units rise); Store: no new brine bucket. LIES: a bucket CARRIED mid-pour when the others are
       destroyed drops at stop_job and reads as a new fill (first run: FAIL 1 bucket, no fill job) -> judged from the drop.
  T25  snow depth 1 on 8x8 (jawa/set_weather_buildup), an empty bucket, no liquid water: RM_GatherSnow -> RM_BucketSnow,
       melts to RM_Bucket_FreshWater within 7,000 ticks above 0 C (first run: 5,000 at 31 C); with a pond near: no snow job.
  T26  a refuelled Campfire, bill RM_MeltBlueIceIntoBucket (repeatMode 'repeatcount'; 'count' is refused), 5 RM_BlueIce + a
       WoodLog RM_BucketEmpty, a Cooking worker: a WoodLog RM_Bucket_FreshWater, no Player.log error line meanwhile.
  T29  target = filledBottlesPerColonist x FreeColonistsSpawned (all test colonists count), picked so the deficit is > 10;
       the stock is RM_BottleStock.Have (ground + PACKED). LIES: the ground count falls as colonists pack bottles (first
       run read 10, 18, 16, 14 ...), and bottles packed in an earlier run survive purge_drinks (second run: one step of
       14) -> steps are measured from Have before the empties drop. PASS: Have ends exactly at target, every step <= 10,
       and a deficit over 10 takes more than one step.

DEBUG RECORD, T15 run 1 (live walk 2026-10-17, b5.json): the red pawn carried the WHITE slime's RM_SporeFlesh and no
RM_ContagionTouched; a rerun from the same save (b6.json) was exact. Theories, in the order weighed:
  - FALSE: a wrong or cached terrain -> liquid lookup (LiquidAt / RM_DrinkableTerrainExtension). b5 and b6 ran on the same
    load, and green/white/yellow mapped right in b5; a lookup is the same answer for the whole load.
  - FALSE: a shared static in RowEffects, or a stale hediff from an earlier row. RowEffects reads only the liquid it is
    handed, and the red pawn was freshly spawned (its SporeFlesh 0.0022 < white's 0.0096 says it drank LATER, not earlier).
  - FALSE: pawn reuse between rows in this driver. Every row spawns its own colonists.
  - TRUE (mechanism, inferred from the numbers, not replayed): RM_ThirstUtility.noTerrainUntil, a STATIC dictionary keyed by
    thingIDNumber, survived the 'load calm' between the session before and b5. Both restart the ID counter and the tick, so
    the first pawn spawned (red) inherited a fresh-looking "no water here" mark from the previous session's first-spawned
    pawn; the 2026-10-17 B2 guard only dropped marks MORE than 600 ticks ahead. Red refused every terrain drink, took a long
    GotoWander (only job ever sampled; RM_Dehydration 0.00825 = ~1,650 ticks at zero vs 0.0015 for the others) and drank
    the nearest pool when it finally re-thought: white's. b6's red was clean because b5 had expired and dropped that entry.
    Fix: the marks are cleared when Current.Game changes (selftest Thirst_review_fixes_B2_B3_in_source). T15R is the
    red-before-the-fix check.
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
    ap.add_argument("--reload-site", default="calm", help="test_site_saves site T15R reloads (twice)")
    a = ap.parse_args(argv)
    only = [x.strip().upper() for x in a.only.split(",") if x.strip()]
    import validation_core as V
    B = V.Bridge()
    X0, Z0 = map(int, a.site.split(","))
    out = a.out or os.path.join(HERE, "thirst_live_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "thirst_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    import driver_stamp
    driver_stamp.stamp(res, B.call)      # validation.py reads a result only at the current mod hash AND deployed DLL

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
                # review 2026-10-17: retrying the whole chunk overshot n by the stop's partial advance (T3 reads a rate
                # over exactly n ticks); what is left is measured off the clock instead
                now = tg()
                if t0 is not None and now is not None:
                    left = n - (now - t0)
                continue
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
    WETS = POTABLE_TERRAIN + ("WaterOceanShallow", "WaterOceanDeep", "RM_WaterBrineShallow", "RM_WaterBrineDeep",
                              "RM_WaterPoisonedShallow", "RM_Slime_Liquid", "RM_SlimeRedShallow", "RM_SlimeGreenShallow",
                              "RM_SlimeWhiteShallow", "RM_SlimeYellowShallow")

    def dry_all():
        """Every liquid cell on the map -> Soil (potable, salt, brine, toxic, slime): the row paints its own."""
        tb3 = B.call("jawa/get_terrain_batch", rects="0,0,250,250") or {}
        wet3 = [op for op in (tb3.get("ops") or "").split(";") if op and op.split(":")[0] in WETS]
        if wet3:
            B.call("jawa/set_terrain_batch", ops=";".join("Soil:" + op.split(":")[1] for op in wet3))
        # a player tank is a drink source too (round 2: T15's desperate pawns drank T20's leftover fresh tank): empty them
        for t in (B.call("jawa/list_things", defName="RM_LiquidTank", limit=50) or {}).get("things") or []:
            B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
                   args="%s,%s;Store;RM_Liquid_FreshWater;0" % (t.get("x"), t.get("z")))
        return len(wet3)

    saved = {}
    keys = ("thirstEnabled", "thirstRateMultiplier", "thirstHeatScaling", "animalsGetThirst", "drinkFromTerrain",
            "waterQualityEffects", "lastResortDrinking", "saltBreakEnabled", "roughDrinkPenalty", "snowGathering",
            "filledBottlesPerColonist")
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
        # ---------------------------------------------------------------- T15 slime last resort, four colours
        if want("T15"):
            # HARNESS (full run, round 2, 2026-10-17): T13's toxic strip was still on the map, and toxic (quality 3) outranks
            # slime (4) in JobGiver_RM_Drink's BetterPick, so all four desperate pawns walked to the toxic water (ToxicBuildup
            # 0.118 each, no slime hediff): a correct pick by the ruled ranking. The row dries every liquid first.
            dry_all()
            purge_drinks()
            cols = (("RM_SlimeRedShallow", "RM_ContagionTouched"), ("RM_SlimeGreenShallow", "RM_Slimification"),
                    ("RM_SlimeWhiteShallow", "RM_SporeFlesh"), ("RM_SlimeYellowShallow", "RM_SlimeNausea"))
            subj = []
            for i, (terr, hd) in enumerate(cols):
                bx, bz = X0 + 2 + 10 * i, Z0 + 34
                paint(terr, bx, bz, 2, 2)
                pid = spawn_colonist(bx, bz + 3)
                UNDER_TEST.add(pid)
                subj.append((terr, hd, pid))
            p5 = spawn_colonist(X0 + 36, Z0 + 37)
            UNDER_TEST.add(p5)
            need(p5, 0.05)
            for _, _, pid in subj:
                need(pid, 0.0)
                B.call("jawa/stop_job", pawnId=pid)
            B.call("jawa/stop_job", pawnId=p5)
            jobs = {pid: [] for _, _, pid in subj + [(0, 0, p5)]}
            for _ in range(20):
                ticks(60)
                for pid in jobs:
                    j = job(pid)
                    if j and (not jobs[pid] or jobs[pid][-1] != j):
                        jobs[pid].append(j)
            ticks(600)
            out15, bad = {}, []
            colour_hd = set(c[1] for c in cols)
            for terr, hd, pid in subj:
                h, m = hediffs(pid), mems(pid)
                out15[terr] = {"pawn": pid, "jobs": jobs[pid], "hediffs": h, "memories": m}
                if "RM_DrinkFromTerrain" not in jobs[pid] and "RM_Thought_DrankSlime" not in m:
                    bad.append("%s: no terrain drink" % terr)
                    continue
                other = sorted(x for x in colour_hd - {hd} if x in h)
                if other:
                    # run 1 (2026-10-17): the pawn walked to ANOTHER pool after a long wander; a stale noTerrainUntil mark
                    # (see DEBUG RECORD above, and T15R) is the known way to get here
                    bad.append("%s: carries another pool's %s (drank elsewhere; jobs %s)" % (terr, other, jobs[pid]))
                if "RM_Thought_DrankSlime" not in m:
                    bad.append("%s: no RM_Thought_DrankSlime" % terr)
                if "RM_SlimePurge" not in h:
                    bad.append("%s: no RM_SlimePurge" % terr)
                want_sev = {"RM_ContagionTouched": 1.0, "RM_Slimification": 0.3}.get(hd)
                if hd not in h or (want_sev is not None and h[hd] < want_sev - 0.01):
                    bad.append("%s: %s %s" % (terr, hd, h.get(hd)))
            if "RM_DrinkFromTerrain" in jobs[p5]:
                bad.append("a pawn at 0.05 drank slime")
            out15["at0.05"] = jobs[p5]
            row("T15_slime_effects", "FAIL" if bad else "PASS", "MOD", dict(out15, bad=bad))
            for _, _, pid in subj + [(0, 0, p5)]:
                draft(pid)

        # ---------------------------------------------------------------- T17 salt break (forced start)
        if want("T17"):
            purge_drinks()
            SX2, SZ2 = X0 + 2, Z0 + 2
            paint("WaterOceanShallow", SX2, SZ2, 6, 2)
            ps = spawn_colonist(SX2 + 2, SZ2 + 4)
            UNDER_TEST.add(ps)
            need(ps, 0.05)
            B.call("jawa/pawn_need", pawn=ps, action="need", need="Mood", level=0.05)
            r = B.call("jawa/pawn_force_mental_break", pawn=ps, breakDef="RM_Break_DrinkBrine") or {}
            trace = []
            for _ in range(30):
                ticks(100)
                ms = B.call("jawa/pawn_mental", pawn=ps, action="list") or {}
                st = json.dumps(ms.get("pawns") or ms.get("state") or ms)[:120]
                trace.append([job(ps), need(ps), st])
                if need(ps) is not None and need(ps) >= 0.9 and "DrinkBrine" not in st:
                    break
            h, m = hediffs(ps), mems(ps)
            lvl = need(ps)
            bad = []
            if not r.get("started"):
                row("T17_salt_break", "UNMEASURED", "HARNESS", {"force": {k: r.get(k) for k in ("started", "message", "breakDef")}})
            else:
                if lvl is None or lvl < 0.9:
                    bad.append("the break ended with thirst %s (want >= 0.9)" % lvl)
                if "RM_Thought_SaltRelief" not in m:
                    bad.append("no RM_Thought_SaltRelief")
                sp = h.get("RM_SaltPoisoning")
                if sp is None or abs(sp / 0.25 - round(sp / 0.25)) > 0.05:
                    bad.append("RM_SaltPoisoning %s is not 0.25 a drink" % sp)
                row("T17_salt_break", "FAIL" if bad else "PASS", "MOD",
                    {"force": {k: r.get(k) for k in ("started", "breakDef")}, "trace": trace[-4:], "hediffs": h, "memories": m,
                     "bad": bad, "notRun": "the break being OFFERED (mood gate, dev list) and not offered with a fresh bottle: the start is forced"})
            draft(ps)
        # ================================================================ batch 3 (thirst live round 2, 2026-10-17)
        # A second, freshly cleared site east of the first (X3..X3+50 x Z0..Z0+40), so these rows never meet the first
        # batch's ponds, salt strips and slime pools. Every row starts by drying it and quenching every bystander, so a
        # thirsty pawn from an earlier row never drinks the test's water or bottles.
        X3 = X0 + 45
        batch3 = [r_ for r_ in ("T14", "T16", "T18", "T20", "T23", "T25", "T26", "T29") if want(r_) and (only or True)]
        site3_ok = False
        if batch3:
            site3_ok = V.prepare_site(B, (X3, Z0, 50, 40), rows, "site3_ready")

        def quench_all(keep=()):
            for c in colonists():
                pid = re.sub(r"^Thing_", "", c["pawnId"])
                if pid not in keep:
                    need(pid, 1.0)

        _hp = []

        def tank_units(x, z):
            """The hose probe's tank read (decilitres), as sprinkler_live reads it: validation_hose.H().hp."""
            if not _hp:
                _fw = os.path.dirname(HERE)
                if _fw not in sys.path:
                    sys.path.insert(0, _fw)
                import validation_hose as VH
                _hp.append(VH.H())
            r = _hp[0].hp("tank:%d,%d" % (x, z)) or {}
            return r.get("units") if r.get("success") else None

        def things(defn, rect=None):
            kw = {"defName": defn, "limit": 200}
            if rect:
                kw["rect"] = rect
            return [t for t in (B.call("jawa/list_things", **kw) or {}).get("things") or [] if (t.get("def") or t.get("defName")) == defn]

        def worker(x, z, work=("Hauling",)):
            """An undrafted fresh colonist with the given work types at priority 1 (every other bystander drafted).
            HARNESS (full run, round 2, 2026-10-17): T25 sat idle for 3,000 ticks with snow and an empty bucket beside it,
            and its pond arm filled nothing either: a generated colonist can be incapable of the work (set_work_priority
            refuses a disabled type with success=false, which was not read). A refused pawn is drafted and replaced."""
            for _ in range(6):
                pid = spawn_colonist(x, z)
                UNDER_TEST.add(pid)
                ok = all((B.call("jawa/set_work_priority", pawnId=pid, workType=w, priority=1) or {}).get("success") is not False
                         for w in work)
                if ok:
                    need(pid, 1.0)
                    return pid
                draft(pid)
            raise RuntimeError("six colonists in a row were incapable of %s" % (work,))

        def draft_bystanders(keep):
            for c in colonists():
                pid = re.sub(r"^Thing_", "", c["pawnId"])
                if pid not in keep:
                    draft(pid)

        # ---------------------------------------------------------------- T18 Dubs mode (needs a list with Dubs)
        if want("T18"):
            row("T18_dubs_last_resort", "UNMEASURED", "SITE",
                {"why": "needs Dubs Bad Hygiene Lite + its Thirst add-on loaded; this list runs provider Own (T1's arm)"})

        if batch3 and not site3_ok:
            for r_ in batch3:
                if r_ != "T18":
                    row(r_ + "_site3", "UNMEASURED", "SITE", {"why": "site3 did not clear (see site3_ready)"})
            batch3 = []

        # ---------------------------------------------------------------- T14 native animal, terrible water
        # Mechanism (RM_ThirstUtility.NativeHere): native = on the MAP's biome wild-animal roster (CommonalityOfAnimal > 0),
        # so the bar's "salt/brine biome map" reduces to "an animal on this map's roster" beside salt water; the row reads
        # NativeHere for each candidate rather than guessing the roster.
        if "T14" in batch3:
            dry_all()
            quench_all()
            AX, AZ = X3 + 2, Z0 + 2
            paint("WaterOceanShallow", AX, AZ, 8, 3)
            cands = ("Dromedary", "Gazelle", "Iguana", "Hare", "Rat", "Elephant", "Rhinoceros", "Ostrich", "Emu",
                     "Muffalo", "Squirrel", "Deer", "Boar", "Alpaca", "Megasloth", "Tortoise", "Cobra", "Raccoon", "Fox_Fennec")
            nat = non = None
            tried = {}
            for k in cands:
                if nat and non:
                    break
                r = B.call("jawa/spawn_pawn", kindDef=k, x=AX + 3, z=AZ + 4, count=1, faction="none") or {}
                ids = [p.get("id") or p.get("thingId") for p in (r.get("pawns") or r.get("spawned") or [])]
                if not ids:
                    tried[k] = "no spawn"
                    continue
                v = str((B.call("jawa/static_call", type="RimMandrake.FlowWorks.Thirst.RM_ThirstUtility", method="NativeHere",
                                args=ids[0]) or {}).get("result"))
                tried[k] = v
                if v == "True" and not nat:
                    nat = ids[0]
                elif v == "False" and not non:
                    non = ids[0]
            if not (nat and non):
                row("T14_native_animal_terrible_water", "UNMEASURED", "HARNESS", {"tried": tried, "why": "no native/non-native pair"})
            else:
                lv = {nat: [need(nat, 0.2)], non: [need(non, 0.2)]}
                ticks(2500)
                lv[nat].append(need(nat))
                lv[non].append(need(non))
                hn = hediffs(nat)
                bad = []
                if None in lv[nat] or None in lv[non]:
                    row("T14_native_animal_terrible_water", "UNMEASURED", "HARNESS", {"levels": lv, "why": "no RM_Thirst read"})
                else:
                    if not lv[nat][1] > lv[nat][0] + 0.2:
                        bad.append("the native animal did not drink the salt water (%s)" % lv[nat])
                    if lv[non][1] > lv[non][0] + 0.05:
                        bad.append("the non-native animal's thirst rose with only salt water on the map (%s)" % lv[non])
                    if "FoodPoisoning" in hn:
                        bad.append("native drinker got FoodPoisoning")
                    row("T14_native_animal_terrible_water", "FAIL" if bad else "PASS", "MOD",
                        {"native": nat, "nonNative": non, "tried": tried, "levels": lv, "nativeHediffs": hn, "bad": bad,
                         "inferred": "the map holds no other liquid, so a rise is a salt drink (the animal job is not on the bridge)",
                         "notRun": "a real salt/brine biome map (native read off the live roster instead)"})
            dry_all()

        # ---------------------------------------------------------------- T16 living slime (RM_Slime_Liquid)
        if "T16" in batch3:
            dry_all()
            quench_all()
            LX, LZ = X3 + 14, Z0 + 2
            paint("RM_Slime_Liquid", LX, LZ, 2, 2)
            p16 = spawn_colonist(LX, LZ + 3)
            UNDER_TEST.add(p16)
            need(p16, 0.0)
            t_on, seen_on = poll_job(p16, ("RM_DrinkFromTerrain",), 900, step=30)
            if t_on is not None:
                wait_job_end(p16, "RM_DrinkFromTerrain", 900)
            ticks(120)
            h16, m16 = hediffs(p16), mems(p16)
            draft(p16)
            sset("lastResortDrinking", False)
            p16b = spawn_colonist(LX + 3, LZ + 3)
            UNDER_TEST.add(p16b)
            need(p16b, 0.0)
            t_off, seen_off = poll_job(p16b, ("RM_DrinkFromTerrain",), 900, step=60)
            sset("lastResortDrinking", True)
            draft(p16b)
            bad = []
            if t_on is None:
                bad.append("at need 0 beside living slime only: no RM_DrinkFromTerrain (jobs %s)" % seen_on)
            elif "RM_Slimification" not in h16:
                bad.append("drank living slime but no RM_Slimification")
            if t_on is not None and "RM_Thought_DrankSlime" not in m16:
                bad.append("no RM_Thought_DrankSlime")
            if t_off is not None:
                bad.append("lastResortDrinking OFF and the pawn still drank slime")
            row("T16_living_slime", "FAIL" if bad else "PASS", "MOD",
                {"jobsOn": seen_on, "hediffs": h16, "memories": m16, "jobsOff": seen_off, "bad": bad,
                 "notRun": "a Gelatinous Slime biome map: RM_Slime_Liquid painted on the calm site (the drink rule is the terrain's)"})
            paint("Soil", LX, LZ, 2, 2)

        # ---------------------------------------------------------------- T20 bucket drunk dry; part-drunk pour
        if "T20" in batch3:
            dry_all()
            purge_drinks()
            quench_all()
            BX, BZ = X3 + 22, Z0 + 2
            p20 = spawn_colonist(BX, BZ + 2)
            UNDER_TEST.add(p20)
            draft(p20)
            bid = spawn("RM_Bucket_FreshWater", BX + 1, BZ)
            drinks, trace = 0, []
            for i in range(14):
                cur = things("RM_Bucket_FreshWater")
                if not cur:
                    break
                need(p20, 0.1)
                r = B.call("jawa/ordered_job", pawnId=p20, jobDef="RM_DrinkFromContainer", targetAId=cur[0]["id"], waitTicks=30) or {}
                wait_job_end(p20, "RM_DrinkFromContainer", 900)
                ticks(30)
                drinks += 1
                trace.append([r.get("accepted"), r.get("afterJobDef"), round(need(p20) or 0, 3)])
            dirty = count("RM_BucketDirty") + count("RM_BucketEmpty")
            left = count("RM_Bucket_FreshWater")
            # arm 2: drink 3 (4.5 L of 15), then a player's order pours what is left into a Store tank
            TX, TZ = BX + 6, BZ + 4
            B.call("jawa/destroy_batch", rects="%d,%d,4,4" % (TX - 1, TZ - 1), categories="Building,Item,Plant")
            B.call("jawa/build_batch", ops="RM_LiquidTank:%d,%d" % (TX, TZ), faction="player", wipeExisting=False)
            fill_r = str(B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
                                args="%d,%d;Store;RM_Liquid_FreshWater;100" % (TX, TZ)).get("result"))
            b2 = spawn("RM_Bucket_FreshWater", BX + 1, BZ)
            for i in range(3):
                need(p20, 0.1)
                cur = things("RM_Bucket_FreshWater")
                B.call("jawa/ordered_job", pawnId=p20, jobDef="RM_DrinkFromContainer", targetAId=cur[0]["id"], waitTicks=30)
                wait_job_end(p20, "RM_DrinkFromContainer", 900)
                ticks(30)
            cur = things("RM_Bucket_FreshWater")
            insp = None
            if cur:
                for t in (B.call("jawa/inspect_string", thingIds=cur[0]["id"]) or {}).get("things") or []:
                    insp = " | ".join(t.get("inspect") or [])
            u0 = tank_units(TX, TZ)
            pr = {}
            if cur:
                pr = B.call("jawa/ordered_job", pawnId=p20, jobDef="RM_EmptyIntoTankJob", targetAId=cur[0]["id"],
                            targetBId=(things("RM_LiquidTank", "%d,%d,2,2" % (TX, TZ)) or [{}])[0].get("id"), waitTicks=30) or {}
                wait_job_end(p20, "RM_EmptyIntoTankJob", 1200)
                ticks(60)
            u1 = tank_units(TX, TZ)
            bad = []
            if drinks == 0 or not trace or not trace[0][0]:
                row("T20_bucket_drunk_dry", "UNMEASURED", "HARNESS", {"trace": trace, "why": "the ordered bucket drink was refused"})
            else:
                if left != 0 or drinks != 10:
                    bad.append("the 15 L bucket took %d drinks (want 10), %d still filled" % (drinks, left))
                if dirty < 1:
                    bad.append("no dirty/empty bucket after the last drink")
                if None in (u0, u1):
                    bad.append("tank units unreadable (%s -> %s); pour arm not judged" % (u0, u1))
                elif u1 - u0 != 105:
                    bad.append("pouring a bucket with 4.5 L drunk added %s units (want 105 = 10.5 L)" % (u1 - u0))
                if insp is not None and "Partly drunk" not in insp:
                    bad.append("part-drunk bucket inspect %r has no 'Partly drunk'" % insp)
                row("T20_bucket_drunk_dry", "FAIL" if bad else "PASS", "MOD",
                    {"drinks": drinks, "trace": trace[-3:], "dirtyOrEmpty": dirty, "tank": fill_r, "units": [u0, u1],
                     "pour": {k: pr.get(k) for k in ("accepted", "afterJobDef", "message")}, "inspect": insp, "bad": bad})

        # ---------------------------------------------------------------- T23 a Fill tank of brine is the order
        if "T23" in batch3:
            dry_all()
            purge_drinks()
            quench_all()
            FX3, FZ3 = X3 + 34, Z0 + 2
            B.call("jawa/destroy_batch", rects="%d,%d,14,14" % (FX3 - 1, FZ3 - 1), categories="Building,Item,Plant")
            paint("RM_WaterBrineShallow", FX3, FZ3, 8, 2)
            TX, TZ = FX3 + 2, FZ3 + 8
            B.call("jawa/build_batch", ops="RM_LiquidTank:%d,%d" % (TX, TZ), faction="player", wipeExisting=False)
            tank_r = str(B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
                                args="%d,%d;Fill;RM_Liquid_Brine;100" % (TX, TZ)).get("result"))
            for i in range(3):
                spawn("RM_BucketEmpty", FX3 + 5 + i, FZ3 + 5)
            p23 = worker(FX3 + 4, FZ3 + 4)
            draft_bystanders({p23})
            u0 = tank_units(TX, TZ)
            seen, made = [], 0
            for _ in range(40):
                ticks(150)
                quench_all()
                j = job(p23)
                if j and (not seen or seen[-1] != j):
                    seen.append(j)
                u = tank_units(TX, TZ)
                if u is not None and u0 is not None and u > u0:
                    break
            made = count("RM_Bucket_Brine")
            u1 = tank_units(TX, TZ)
            # arm 2: Store mode -> the standing order is gone; no new brine fills
            for t in things("RM_Bucket_Brine"):
                B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t.get("x"), t.get("z")), categories="Item")
            B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
                   args="%d,%d;Store;RM_Liquid_Brine;100" % (TX, TZ))
            for _ in range(3 - count("RM_BucketEmpty")):
                spawn("RM_BucketEmpty", FX3 + 5, FZ3 + 6)
            B.call("jawa/stop_job", pawnId=p23)
            # HARNESS (first live run, 2026-10-17): a brine bucket CARRIED mid-pour is not on the ground when the others are
            # destroyed; stop_job drops it, and the Store arm then counted it as a new fill (1 bucket, no fill job seen).
            # The Store arm is judged against what is on the ground after the drop.
            # Full run, round 2: base2 read 0 after 30 ticks, yet one brine bucket lay beside the shore by the end with no
            # fill job sampled (150-tick samples; brine tank unchanged; the only tank fill seen was from T20's FRESH tank).
            # A mid-fill job stopped by stop_job can still finish its carry later, so the arm now settles 300 ticks,
            # clears the ground again, then samples every 30 ticks and names where each new brine bucket lies.
            ticks(300)
            for t in things("RM_Bucket_Brine"):
                B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t.get("x"), t.get("z")), categories="Item")
            base2 = count("RM_Bucket_Brine")
            seen2 = []
            for _ in range(100):
                ticks(30)
                j = job(p23)
                if j and (not seen2 or seen2[-1] != j):
                    seen2.append(j)
            made2 = count("RM_Bucket_Brine") - base2
            where2 = [(t.get("x"), t.get("z")) for t in things("RM_Bucket_Brine")]
            u2 = tank_units(TX, TZ)
            bad = []
            if u0 is None or u1 is None:
                row("T23_fill_tank_is_the_order", "UNMEASURED", "HARNESS", {"tank": tank_r, "units": [u0, u1]})
            else:
                if not (u1 > u0 or made > 0 or "RM_FillBottleJob" in seen):
                    bad.append("Fill tank holding brine: no brine gathered unforced in 6,000 ticks (jobs %s)" % seen)
                if made2 > 0 or "RM_FillBottleJob" in seen2:
                    bad.append("Store tank: brine still gathered (%d buckets, jobs %s)" % (made2, seen2))
                row("T23_fill_tank_is_the_order", "FAIL" if bad else "PASS", "MOD",
                    {"tank": tank_r, "units": [u0, u1], "brineBuckets": made, "jobsFill": seen, "jobsStore": seen2,
                     "brineBucketsAfterStore": made2, "droppedAtSwitch": base2, "brineAt": where2,
                     "storeTankUnits": u2, "bad": bad})
            draft(p23)

        # ---------------------------------------------------------------- T25 snow into water
        if "T25" in batch3:
            dry_all()
            purge_drinks()
            quench_all()
            SX3, SZ3 = X3 + 2, Z0 + 14
            B.call("jawa/destroy_batch", rects="%d,%d,14,10" % (SX3, SZ3), categories="Building,Item,Plant")
            sb = B.call("jawa/set_weather_buildup", kind="snow", mode="set", rect="%d,%d,8,8" % (SX3, SZ3), depth=1.0) or {}
            spawn("RM_BucketEmpty", SX3 + 10, SZ3 + 2)
            p25 = worker(SX3 + 10, SZ3 + 4)
            draft_bystanders({p25})
            temp = (B.call("jawa/cell_temperature", cell="%d,%d" % (SX3, SZ3)) or {})
            seen = []
            for _ in range(30):
                ticks(100)
                quench_all()
                j = job(p25)
                if j and (not seen or seen[-1] != j):
                    seen.append(j)
                if count("RM_BucketSnow"):
                    break
            snowb = count("RM_BucketSnow")
            sd = B.call("jawa/set_weather_buildup", kind="snow", mode="add", rect="%d,%d,8,8" % (SX3, SZ3), depth=0.0) or {}
            fresh0 = count("RM_Bucket_FreshWater")
            melted = None
            melt_trace = []
            # Full run, round 2: the snow bucket was made but no melt was seen in 7,000 ticks (the isolated run melted at
            # 5,000 at 31 C). The arm now traces the snow bucket itself every 500 ticks: where it lies, that cell's
            # temperature and CompRM_Melt's own fields, so a haul into a cold room or a carry is visible.
            if snowb:
                for k in range(14):
                    ticks(500)
                    quench_all()
                    sb_ = things("RM_BucketSnow")
                    smp = {"t": (k + 1) * 500, "snow": [(t.get("x"), t.get("z")) for t in sb_], "fresh": count("RM_Bucket_FreshWater")}
                    if sb_:
                        smp["cellC"] = (B.call("jawa/cell_temperature", cell="%s,%s" % (sb_[0].get("x"), sb_[0].get("z"))) or {}).get("temperature")
                        cr = B.call("jawa/comp_read", thing=sb_[0].get("id"), comp="RM_Melt") or {}
                        smp["comp"] = str(cr.get("fields") or cr.get("members") or cr.get("message"))[:160]
                    melt_trace.append(smp)
                    if smp["fresh"] > fresh0 and not sb_:
                        melted = (k + 1) * 500
                        break
            # arm 2: a pond near -> the bucket fills from it, no snow job
            draft(p25)
            purge_drinks()
            B.call("jawa/set_weather_buildup", kind="snow", mode="set", rect="%d,%d,8,8" % (SX3, SZ3), depth=1.0)
            paint("WaterShallow", SX3 + 10, SZ3 + 8, 3, 2)
            spawn("RM_BucketEmpty", SX3 + 10, SZ3 + 2)
            draft(p25, False)
            B.call("jawa/stop_job", pawnId=p25)
            seen2 = []
            for _ in range(20):
                ticks(100)
                quench_all()
                j = job(p25)
                if j and (not seen2 or seen2[-1] != j):
                    seen2.append(j)
                if count("RM_Bucket_FreshWater"):
                    break
            bad = []
            if "RM_GatherSnow" not in seen and not snowb:
                bad.append("no RM_GatherSnow and no RM_BucketSnow with snow beside the bucket (jobs %s)" % seen)
            if snowb and melted is None:
                bad.append("the bucket of snow did not melt into water within 7,000 ticks at %s C" % temp.get("temperature"))
            if "RM_GatherSnow" in seen2:
                bad.append("gathered snow with a pond near")
            row("T25_snow_to_water", "FAIL" if bad else "PASS", "MOD",
                {"snowSet": {k: sb.get(k) for k in ("success", "cellsChanged")}, "jobs": seen, "bucketsSnow": snowb,
                 "snowAfter": sd.get("sample") or sd.get("depths"), "meltTicks": melted, "meltTrace": melt_trace[-5:], "temp": temp.get("temperature"),
                 "jobsPond": seen2, "bad": bad, "notRun": "snow depth drop 0.4 (read back is a sample only)"})
            draft(p25)
            paint("Soil", SX3 + 10, SZ3 + 8, 3, 2)
            B.call("jawa/set_weather_buildup", kind="snow", mode="set", rect="%d,%d,8,8" % (SX3, SZ3), depth=0.0)

        # ---------------------------------------------------------------- T26 blue ice -> bucket at a campfire
        if "T26" in batch3:
            dry_all()
            purge_drinks()
            quench_all()
            CX, CZ = X3 + 18, Z0 + 16
            B.call("jawa/destroy_batch", rects="%d,%d,8,8" % (CX - 2, CZ - 2), categories="Building,Item,Plant")
            B.call("jawa/build_batch", ops="Campfire:%d,%d" % (CX, CZ), faction="player", wipeExisting=False)
            fire = (things("Campfire", "%d,%d,1,1" % (CX, CZ)) or [{}])[0].get("id")
            B.call("jawa/thing_refuel", thingId=fire)
            ba = B.call("jawa/bill_add", giverId=fire, recipe="RM_MeltBlueIceIntoBucket", repeatMode="repeatcount", repeatCount=1) or {}
            B.call("jawa/spawn_batch", ops="RM_BlueIce:%d,%d,5" % (CX + 2, CZ))
            B.call("jawa/spawn_batch", ops="RM_BucketEmpty:%d,%d,1" % (CX + 2, CZ + 1), stuff="WoodLog")
            logp = os.path.join(os.environ.get("USERPROFILE", r"C:\Users\Mandrake"), "AppData", "LocalLow", "Ludeon Studios",
                                "RimWorld by Ludeon Studios", "Player.log")
            try:
                log0 = os.path.getsize(logp)
            except OSError:
                log0 = None
            p26 = worker(CX + 1, CZ + 3, work=("Cooking",))
            draft_bystanders({p26})
            seen = []
            for _ in range(30):
                ticks(200)
                quench_all()
                j = job(p26)
                if j and (not seen or seen[-1] != j):
                    seen.append(j)
                if count("RM_Bucket_FreshWater"):
                    break
            made = things("RM_Bucket_FreshWater")
            errs = []
            if log0 is not None:
                with open(logp, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(log0)
                    errs = [l for l in f.read().splitlines() if re.search(r"Exception|\bError\b", l)]
            bad = []
            if not ba.get("success", True) or fire is None:
                row("T26_ice_block_bill", "UNMEASURED", "HARNESS", {"bill": str(ba)[:200], "fire": fire})
            else:
                if not made:
                    bad.append("no RM_Bucket_FreshWater after the bill (jobs %s)" % seen)
                elif "Wood" not in str(made[0].get("stuff") or made[0].get("label") or ""):
                    bad.append("the bucket is not wooden: %s" % {k: made[0].get(k) for k in ("stuff", "label")})
                if errs:
                    bad.append("Player.log errors during the bill: %s" % errs[:2])
                row("T26_ice_block_bill", "FAIL" if bad else "PASS", "MOD",
                    {"jobs": seen, "made": [{k: t.get(k) for k in ("id", "stuff", "label")} for t in made[:2]],
                     "blueIceLeft": count("RM_BlueIce"), "logErrors": errs[:3], "bad": bad})
            draft(p26)

        # ---------------------------------------------------------------- T29 bottle stock and batches
        # Deficit = filledBottlesPerColonist x FreeColonistsSpawned - filled potable bottles held (RM_BottleStock); the
        # bar's "2 colonists, target 3 -> 6" is one instance, so the row reads the live colonist count and spawns
        # deficit + 10 empties, so the stop is visible.
        if "T29" in batch3:
            dry_all()
            purge_drinks()
            quench_all()
            WX, WZ = X3 + 30, Z0 + 20
            B.call("jawa/destroy_batch", rects="%d,%d,14,12" % (WX - 2, WZ - 2), categories="Building,Item,Plant")
            paint("WaterShallow", WX, WZ, 4, 3)
            p29 = worker(WX + 6, WZ + 5)
            draft_bystanders({p29})
            # HARNESS (first live run, 2026-10-17): counting bottles on the GROUND read 10, 18, then -2 every 150 ticks: the
            # colonists pack filled bottles into their inventories (packed ones count toward the target, by ruling), so the
            # ground count is not the stock. The row reads the mod's own stock, RM_BottleStock.Have (ground + packed).
            def have():
                v = (B.call("jawa/static_call", type="RimMandrake.FlowWorks.Thirst.RM_BottleStock", method="Have",
                            args="current") or {}).get("result")
                try:
                    return int(v)
                except (TypeError, ValueError):
                    return None

            ncol = len(colonists())
            h_ = have() or 0
            # the smallest target that leaves a deficit over one trip (10), so the batch split is visible
            per = next((p_ for p_ in (1, 2, 3, 4, 5) if p_ * ncol - h_ > 10), 5)
            sset("filledBottlesPerColonist", per)
            target = per * ncol
            empties = max(0, target - (have() or 0)) + 10
            B.call("jawa/spawn_batch", ops="RM_BottleEmpty:%d,%d,%d" % (WX + 6, WZ + 1, empties))
            # HARNESS (second live run): bottles packed in an EARLIER run stay in inventories after purge_drinks (ground
            # only), so the first read jumped 14; the steps are measured from the stock before the empties are dropped.
            have0 = have()
            series, seen = [have0], []
            last_change = 0
            for k in range(60):
                ticks(150)
                quench_all()
                j = job(p29)
                if j and (not seen or seen[-1] != j):
                    seen.append(j)
                f = have()
                if not series or f != series[-1]:
                    series.append(f)
                    last_change = k
                if f >= target and k - last_change >= 10:
                    break
            ticks(1500)
            final = have()
            ground = count("RM_Bottle_FreshWater")
            jumps = [b - a for a, b in zip(series, series[1:]) if None not in (a, b)]
            deficit = target - (have0 or 0)
            sset("filledBottlesPerColonist", 3)
            bad = []
            if final is None:
                bad.append("RM_BottleStock.Have unreadable")
            elif final != target:
                bad.append("filled %d bottles, want exactly the target %d (%d x %d colonists)" % (final, target, per, ncol))
            if jumps and max(jumps) > 10:
                bad.append("one step filled %d bottles (a trip is at most 10)" % max(jumps))
            if deficit > 10 and len([x for x in jumps if x > 0]) < 2:
                bad.append("a deficit of %d (over 10) should take more than one fill trip (steps %s)" % (deficit, jumps))
            row("T29_bottle_stock_and_batches", "FAIL" if bad else "PASS", "MOD",
                {"colonists": ncol, "perColonist": per, "target": target, "stockBefore": have0, "empties": empties, "series": series,
                 "final": final, "onGround": ground, "jobs": seen, "bad": bad,
                 "notRun": "15 dirty bottles washed in two trips"})
            draft(p29)

        # ---------------------------------------------------------------- T15R stale terrain mark across a reload
        if "T15R" in only:
            _mc = os.path.join(os.path.dirname(os.path.dirname(HERE)), "Utils", "modcheck")
            if _mc not in sys.path:
                sys.path.insert(0, _mc)
            import test_site_saves as TSS

            def reload_site():
                rec = TSS.load_site(B.call, a.reload_site)
                tb2 = B.call("jawa/get_terrain_batch", rects="0,0,%d,%d" % (250, 250)) or {}
                wet2 = [op for op in (tb2.get("ops") or "").split(";") if op and op.split(":")[0] in POTABLE_TERRAIN]
                if wet2:
                    B.call("jawa/set_terrain_batch", ops=";".join("Soil:" + op.split(":")[1] for op in wet2))
                for c in colonists():
                    draft(re.sub(r"^Thing_", "", c["pawnId"]))
                return rec

            RX, RZ = X0 + 20, Z0 + 20
            r1 = reload_site()
            pa_ = spawn_colonist(RX, RZ)
            UNDER_TEST.add(pa_)
            need(pa_, 0.2)                       # thirsty, not desperate, no water on the map: the search fails -> marked
            ta = tg()                            # the stop_job think runs at this tick: the mark is ta + 600
            B.call("jawa/stop_job", pawnId=pa_)
            ticks(60)
            r2 = reload_site()
            pb_ = spawn_colonist(RX, RZ)
            UNDER_TEST.add(pb_)
            ticks(90)                            # past A's mark tick, so 'until - now' is inside the 600-tick window
            paint("RM_SlimeRedShallow", RX - 1, RZ + 2, 2, 2)
            need(pb_, 0.0)
            tb = tg()                            # B's first search (poll_job's stop_job) runs at this tick
            t_drink, seen_r = poll_job(pb_, ("RM_DrinkFromTerrain",), 300, step=30)
            det = {"pawnA": pa_, "pawnB": pb_, "tickA": ta, "tickB": tb, "jobsB": seen_r, "drinkAfter": t_drink,
                   "loads": [r1.get("verified"), r2.get("verified")], "hediffsB": hediffs(pb_)}
            if not (r1.get("verified") and r2.get("verified")):
                row("T15R_reload_mark", "UNMEASURED", "HARNESS", dict(det, why="a site load did not verify"))
            elif pa_ != pb_:
                row("T15R_reload_mark", "UNMEASURED", "HARNESS", dict(det, why="B did not get A's thing ID: collision not reproduced"))
            elif None in (ta, tb) or not ta <= tb < ta + 600:
                # the pre-fix guard honoured a mark only while now < until <= now + 600: outside that window the old DLL
                # passes too, so a PASS here would prove nothing
                row("T15R_reload_mark", "UNMEASURED", "HARNESS", dict(det, why="B's search is outside A's mark window"))
            else:
                row("T15R_reload_mark", "PASS" if t_drink is not None else "FAIL", "MOD", det)
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
