"""FlowWorks thirst LIVE rows (validation.py THIRST_LIVE): the first live driver for them, written on the 2026-10-17 review
walk. Every row is {id, status PASS|FAIL|UNMEASURED, class MOD|SITE|HARNESS, detail}; "could not ask" is UNMEASURED.

  python.exe src/RimMandrake/FlowWorks/northstar/thirst_live.py [out.json] [--only T2,T4,...] [--site X,Z]
  python3    src/RimMandrake/FlowWorks/northstar/thirst_live.py --dry-run [--only ...]   print the plan, touch no bridge
  python3    src/RimMandrake/FlowWorks/northstar/thirst_live.py --mock [--mock-faults a,b] [--only ...]
             every row's control flow against thirst_fake.ThirstFakeBridge (a world model, NOT the mod): proves the driver's
             wait/timeout/replacement branches run, never the mod. The result says mode "mock" and is written to the temp dir.
             Faults and their effect: thirst_fake.py docstring; selftest: selftest_thirst_live.py.

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
       LIES: several snow buckets gather at staggered times; waiting for ALL of them to go read a FAIL on a mod that
       melted on time (full run 2) -> the bucket(s) seen at the gather are followed by ID (see the row's comment).
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

DEBUG RECORD, 2026-10-18 BENCH reruns (Transient/bench_live_20261018{,b}/, offline diagnosis):
  - FALSE: "26a47408f7 / ea44bf7957 broke the salt bottle". Their FlowWorks diff touches no thirst, ingest or liquid-quality
    code, and T5 already FAILED once at edb4b72b49 (thirst_run1) while T4 itself failed twice at ea44bf7957 and PASSED in
    the same load's T4,T5 rerun (thirst_t45). Flaky, not a regression.
  - TRUE (T4/T5, HARNESS): every failing arm reads the bottle gone from its cell, no dirty bottle, no hydration, no
    poisoning: the Ingest job was still running. Vanilla carries the drink to a chew spot (a chair at a table within
    chairSearchRadius 32) and chews 500 / EatingSpeed ticks; the outcome doers run only at the end, and the row waited a
    fixed 600 ticks. Fix: ingest_done() waits for the job to end (budget 3,000), UNMEASURED if it never does.
  - TRUE (T16/T27, SITE): the 10-17 PASS runs loaded 20 mods incl. mandrake.rm.biomes; the 10-18 runs loaded the
    11-mod flowworks tier. T27's meltwater can and T16's living-slime terrain are biomes content. Rows now read
    UNMEASURED SITE without it.
  - FALSE for T15 (2026-10-26, THIRST_FIX_SLIME_ROWS_NEED_BIOMES_TIER): the purge and the thought are FlowWorks rows,
    applied for every colour. Red/green/white ended with dehydration HEALED, and a slime drink (0.3) cannot heal, so
    they drank Potable water instead. RM_Fill_Slime*/Tar/BoilingWater/IcyWater are Water-tagged with no liquid, which
    DrinkLiquidAt (RM_ThirstUtility.cs:141-144) maps to FreshWater, and WETS did not dry them. Fixed both ways: the
    slime fills name their liquid (FlowWorks_SlimeTerrain.xml) and WETS now dries every canal fill.
"""
import argparse
import json
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# The plan --dry-run prints: (--only key, row ids it emits, what it proves). selftest_thirst_live.py checks every emitted id is declared.
PLAN = (
    ("T7", ("T7_no_dbh_clean_log",), "no thirst/Dubs exception in --log"),
    ("T1", ("T1_provider_line",), "provider line (one arm of three: always UNMEASURED)"),
    ("T2", ("T2_one_thirst_need",), "exactly one RM_Thirst, no DBHThirst"),
    ("T3", ("T3_need_falls",), "15,000 ticks drop 0.2 x rate"),
    ("T6", ("T6_dehydration_readable",), "60,000 ticks at 0 -> RM_Dehydration 0.30"),
    ("T4", ("T4_bottle_satisfies",), "ordered fresh bottle: ingest_done waits the job out; gain and dirty bottle"),
    ("T5", ("T5_salt_water_quality",), "salt bottle x0.7, poisoning 0.25, relief thought"),
    ("T10", ("T10_terrain_drink",), "pond drink; OFF setting -> no job"),
    ("T9", ("T9_animals_drink",), "tame and wild Muffalo drink the pond"),
    ("T11", ("T11_autofill_skips_salt",), "autofill never fills from salt"),
    ("T12", ("T12_no_routine_salt",), "no routine salt drink; fresh bottle 30 cells off is fetched"),
    ("T13", ("T13_desperate_toxic_last",), "toxic only at need 0, bottle beats toxic"),
    ("T27", ("T27_water_items",), "meltwater can (UNMEASURED SITE without biomes)"),
    ("T28", ("T28_sanguophage_blood",), "hemogen pack hydrates a Sanguophage only"),
    ("T19", ("T19_awkward_access",), "bucket drink: rough thought, Partly drunk"),
    ("T24", ("T24_bucket_douses_fire",), "Firefighter priority, refused pawn replaced, area douse"),
    ("T15", ("T15_slime_effects",), "four slime colours, each pawn its own pool"),
    ("T17", ("T17_salt_break",), "forced brine break ends quenched, poisoning in 0.25 steps"),
    ("T18", ("T18_dubs_last_resort",), "needs Dubs: UNMEASURED SITE"),
    ("T14", ("T14_native_animal_terrible_water",), "native animal drinks salt, non-native does not"),
    ("T16", ("T16_living_slime",), "RM_Slime_Liquid last resort; setting OFF -> none"),
    ("T20", ("T20_bucket_drunk_dry",), "10 drinks per bucket; part-drunk pour +105"),
    ("T23", ("T23_fill_tank_is_the_order",), "Fill tank gathers brine; Store tank does not (baseline drains in-flight fill)"),
    ("T25", ("T25_snow_to_water",), "snow bucket melts within 7,000 ticks; pond -> no snow job"),
    ("T26", ("T26_ice_block_bill",), "blue-ice bill makes a wooden fresh bucket"),
    ("T29", ("T29_bottle_stock_and_batches",), "stock reaches the target exactly, steps <= 10"),
    ("T15R", ("T15R_reload_mark",), "opt-in: stale terrain mark across a reload"),
)
SITE_ROWS = ("site_ready", "site3_ready", "settings_restored")
for _p in (HERE, os.path.join(os.path.dirname(os.path.dirname(HERE)), "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

S_TH = "RimMandrake.FlowWorks.Thirst.RM_ThirstSettings"
NEED = "RM_Thirst"
THIRST_KEYS = ("thirstEnabled", "thirstRateMultiplier", "thirstHeatScaling", "animalsGetThirst", "drinkFromTerrain",
               "waterQualityEffects", "lastResortDrinking", "saltBreakEnabled", "roughDrinkPenalty", "snowGathering",
               "filledBottlesPerColonist")
POTABLE_TERRAIN = ("WaterShallow", "WaterDeep", "WaterMovingShallow", "WaterMovingChestDeep", "RM_WaterFrigidShallow",
                   "RM_WaterFrigidDeep", "RM_Water_Rust", "RM_Water_Verdigris", "RM_Water_Amber", "RM_Water_Violet",
                   "RM_Water_Chalk", "Marsh",
                   # the P14 freshwater depth ladder (RM_WaterLadder): a drawn-down pond is restaged onto these, and thirst
                   # reads them as fresh water by fallback. Missing here, dry_all left them wet and a "dried" map still
                   # offered fresh water (THIRST_FIX_SALT_DRUNK_ROUTINELY / THIRST_FIX_DESPERATE_SKIPS_BOTTLE).
                   "RM_WaterVeryShallow", "RM_WaterThin", "RM_WaterChestDeepStill")


def main(argv=None, bridge=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--only", default="")
    ap.add_argument("--site", default="150,130", help="south-west corner of a 40x40 site")
    ap.add_argument("--log", default="", help="this load's Player.log copy (T1, T7)")
    ap.add_argument("--reload-site", default="calm", help="test_site_saves site T15R reloads (twice)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan (rows, settings, site) and exit; no bridge")
    ap.add_argument("--mock", action="store_true", help="run against thirst_fake.ThirstFakeBridge (offline; mode 'mock')")
    ap.add_argument("--mock-faults", default="", help="comma list of thirst_fake faults to inject (see thirst_fake.py)")
    ap.add_argument("--t25-empties", type=int, default=1, help="empty buckets T25 lays (the full run once met 3 leftovers)")
    a = ap.parse_args(argv)
    only = [x.strip().upper() for x in a.only.split(",") if x.strip()]
    X0, Z0 = map(int, a.site.split(","))
    if a.dry_run:
        known = set(k for k, _, _ in PLAN)
        unknown = [o for o in only if o not in known]
        print("thirst_live plan (dry run, no bridge): site %s (40x40 at %d,%d, second site %d east), reload-site %s" % (a.site, X0, Z0, 45, a.reload_site))
        for k, ids, what in PLAN:
            on = (k in only) if k == "T15R" else (not only or k in only)
            print("  %-5s %-4s %-36s %s" % (k, "RUN" if on else "skip", ",".join(ids), what))
        print("  settings flipped (restored in a finally): %s" % ", ".join(sorted(THIRST_KEYS)))
        if unknown:
            print("  UNKNOWN --only keys: %s" % unknown)
            return 2
        return 0
    import validation_core as V
    if bridge is not None:
        B = bridge
    elif a.mock:
        import thirst_fake
        B = thirst_fake.ThirstFakeBridge(faults=[f for f in a.mock_faults.split(",") if f])
    else:
        B = V.Bridge()
    mock = bridge is not None or a.mock
    out = a.out or os.path.join(tempfile.gettempdir() if mock else HERE, "thirst_live_%sresult_%s.json" % ("mock_" if mock else "", time.strftime("%Y%m%dT%H%M%S")))
    rows = []
    res = {"script": "thirst_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    import driver_stamp
    driver_stamp.stamp(res, B.call)      # validation.py reads a result only at the current mod hash AND deployed DLL
    if mock:
        res["mode"] = "mock"             # never 'live': validation.py must refuse a result no game produced
    # THIRST_ROWS_DIAGNOSE_SLIME_SITS_STILL (2026-10-18): T27's RM_BlueIceMeltwaterCan (BlueDesert), T16's RM_Slime_Liquid
    # (GelatinousSlime) and T15's red/green/white hediffs (Contagion, GelatinousSlime, TheRot) all live in the composed
    # mandrake.rm.biomes mod. The flowworks tier (11 mods) does not load it, so those rows read SITE there, never MOD.
    RUNNING = (res.get("env") or {}).get("running")
    BIOMES = "mandrake.rm.biomes"
    biomes_absent = RUNNING is not None and BIOMES not in RUNNING

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        try:
            os.replace(out + ".tmp", out)
        except OSError:          # Windows python over \\wsl.localhost: a replace can be refused while a reader holds the file
            with open(out, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)

    def row(rid, st, cls, det):
        # review 2026-10-27 F16: a row's test pawns stop being "under test" when the row is written -- left in the set, a
        # later row's feed_all would skip refilling them, and their thirst would drive them to drink that row's source
        UNDER_TEST.clear()
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
    # THIRST_STORE_TANK_DIAGNOSE_LATE_BRINE (live J20261028T014816Z-d2e098): vanilla AutoUndrafter undrafts a pawn that
    # has stood drafted and idle (Wait_Combat) for 10,000 ticks, and Pawn_DraftController.Drafted returns early when the
    # value is unchanged -- so drafting an already-drafted bystander re-arms NOTHING. A bystander drafted ~10,000 ticks
    # earlier came free mid-T23, filled brine for the Fill tank and landed a bucket in the settle. The driver now owns
    # the timer: DRAFT_AT is the tick each pawn's undraft clock was last armed by us; ticks() re-arms an idle drafted
    # pawn (undraft + draft, no tick between) before a chunk would carry it past AUTO_UNDRAFT - REARM_MARGIN.
    AUTO_UNDRAFT, REARM_MARGIN = 10000, 1000
    DRAFT_AT = {}
    CLOCK = [0]

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
        if t0 is not None:
            CLOCK[0] = t0
        left = n
        while left > 0:
            k = min(1500, left)
            rearm_due(k)
            try:
                B.ticks(k)
                CLOCK[0] += k
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
                if now is not None:
                    CLOCK[0] = now
                if t0 is not None and now is not None:
                    left = n - (now - t0)
                continue
            left -= k
        t1 = tg()
        if t1 is not None:
            CLOCK[0] = t1
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

    # a hediff that appears while a pawn is NOT drinking: dehydration is the expected cost of a refused drink, not a drink
    NOT_A_DRINK = frozenset(("RM_Dehydration",))

    def ids_of(defn, rect=None):
        """The ids of every spawned `defn` (review 2026-10-27: rows follow THEIR thing by id, not a cell or a global
        count). None when the read was refused (an unread map is not an empty one)."""
        kw = {"defName": defn, "limit": 500}
        if rect:
            kw["rect"] = rect
        r = B.call("jawa/list_things", **kw) or {}
        if r.get("success") is False:
            return None
        return {re.sub(r"^Thing_", "", str(t.get("id") or t.get("thingId"))): t for t in r.get("things") or []
                if (t.get("def") or t.get("defName")) == defn}

    def draft_others(keep):
        """Every colonist but `keep` drafted: an undrafted bystander is a hauler / packer / drinker no row staged."""
        for c in colonists():
            pid = re.sub(r"^Thing_", "", c["pawnId"])
            if pid not in keep:
                draft(pid)

    def paint(defn, x, z, w, h):
        B.call("jawa/set_terrain_batch", ops="%s:%d,%d,%d,%d" % (defn, x, z, w, h))

    def draft(pid, on=True):
        """set_draft, read back: a refused draft (a Lord forbids it) leaves a pawn free to wander off and drink, so the
        refusal is recorded in res['draftRefused'] and returned; rows that REQUIRE the draft read it (T3, T6)."""
        r = B.call("jawa/set_draft", pawnId=pid, drafted=on) or {}
        ok_ = r.get("success") is True and r.get("drafted") in (None, on)
        if ok_ and on and r.get("wasDrafted") is not False:
            # already drafted (or the bridge did not say): its undraft clock is unknown -- re-arm it (see DRAFT_AT)
            ok_ = rearm(pid)
        if not ok_:
            res.setdefault("draftRefused", []).append({"pawn": pid, "wanted": on, "reply": str(r)[:160]})
        elif on:
            DRAFT_AT[pid] = CLOCK[0]
        else:
            DRAFT_AT.pop(pid, None)
        return ok_

    def rearm(pid):
        """Undraft then draft, no tick between: Notify_Drafted restarts the AutoUndrafter clock."""
        r0 = B.call("jawa/set_draft", pawnId=pid, drafted=False) or {}
        r1 = B.call("jawa/set_draft", pawnId=pid, drafted=True) or {}
        ok_ = r0.get("success") is True and r1.get("success") is True and r1.get("drafted") in (None, True)
        if ok_:
            res["draftRearms"] = res.get("draftRearms", 0) + 1
            DRAFT_AT[pid] = CLOCK[0]
        else:
            # GPT review 2026-10-28: a half-done rearm leaves the pawn UNDRAFTED; say so (rows that need the draft read it)
            res.setdefault("draftRefused", []).append({"pawn": pid, "wanted": "rearm", "reply": (str(r0) + str(r1))[:160]})
            DRAFT_AT.pop(pid, None)
        return ok_

    def rearm_due(k):
        """Before a k-tick chunk: every pawn we drafted whose clock would pass AUTO_UNDRAFT - REARM_MARGIN in it. A pawn
        on a real job (an ordered drink, a carry) is re-armed by the game itself; only an idle one is re-armed here."""
        due = [pid for pid, t in DRAFT_AT.items() if CLOCK[0] + k - t >= AUTO_UNDRAFT - REARM_MARGIN]
        if not due:
            return
        jobs = {}
        for c in colonists():
            jobs[re.sub(r"^Thing_", "", str(c.get("pawnId")))] = c.get("job")
        for pid in due:
            if pid not in jobs:
                DRAFT_AT.pop(pid, None)          # gone from the map (dead, despawned): nothing to keep drafted
            elif jobs[pid] in (None, "Wait_Combat"):
                rearm(pid)
            else:
                DRAFT_AT[pid] = CLOCK[0]

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

    def ingest_done(pid, budget=3000, step=100):
        """HARNESS (SALT_BOTTLE_DIAGNOSE_DRUNK_FOR_NOTHING, 2026-10-18): an ordered Ingest is walk to the bottle, carry it to
        a chew spot (vanilla Toils_Ingest.TryFindChairOrSpot: a chair at a table within chairSearchRadius 32, else a spot
        near), then chew baseIngestTicks 500 / EatingSpeed; the outcome doers (hydrate, residue) run only at the END. The
        old fixed 600-tick wait read a pawn still carrying or chewing as "drank for nothing". Wait for the job to end."""
        t, seen = 0, []
        while t < budget:
            j = job(pid)
            if j and (not seen or seen[-1] != j):
                seen.append(j)
            if t >= 60 and j != "Ingest":
                return {"ended": True, "ticks": t, "jobs": seen}
            ticks(step if t else 60)
            t += step if t else 60
        return {"ended": job(pid) != "Ingest", "ticks": t, "jobs": seen}

    DRINKS = ("RM_Bottle_FreshWater", "RM_Bottle_IcyWater", "RM_BottleEmpty", "RM_BottleDirty", "RM_Bottle_SaltWater",
              "RM_Bucket_FreshWater", "RM_BlueIceMeltwaterCan",
              # review 2026-10-27 F11: a snow bucket melts into a fresh one on its own -- a source no row staged
              "RM_BucketSnow")

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
                              "RM_SlimeWhiteShallow", "RM_SlimeYellowShallow",
                              # review 2026-10-17: canal fill water is fresh water too (round 2's T25 replay ran
                              # RM_FillBottleJob on the 'dried' map, so the 'no liquid water' arm was not). LIES: the canal
                              # sim may repaint a cell it still holds depth for; a fill job in T25's jobs list says so.
                              "RM_Fill_Water_Trace", "RM_Fill_Water_Half", "RM_Fill_Water_Brim", "RM_Fill_Water_Superdeep") + tuple(
        # THIRST_FIX_SLIME_ROWS_NEED_BIOMES_TIER: every other canal fill is Water-tagged too, and until its def
        # names a liquid DrinkLiquidAt reads it as FreshWater (Potable, outranks any test pool within 60 cells).
        # A fill this tuple misses is a drink source the row did not stage.
        "RM_Fill_%s_%s" % (f, t) for f in ("SlimeRed", "SlimeGreen", "SlimeWhite", "SlimeYellow", "Tar",
                                           "BoilingWater", "IcyWater")
        for t in ("Trace", "Half", "Brim", "Superdeep"))

    msize = []

    def wet_cells(kinds):
        """Ops of every cell on the map whose terrain is in `kinds`; None when the terrain read was refused.
        GPT review 5.2: the whole map as jawa/map_info sizes it (a fixed 250x250 left water on a 325 map); no size -> None."""
        if not msize:
            mi = B.call("jawa/map_info") or {}
            sx, sz = mi.get("sizeX"), mi.get("sizeZ") or mi.get("sizeY")
            if not sx or not sz:
                return None
            msize.extend((int(sx), int(sz)))
        tb_ = B.call("jawa/get_terrain_batch", rects="0,0,%d,%d" % tuple(msize)) or {}
        if tb_.get("success") is False:
            return None
        return [op for op in (tb_.get("ops") or "").split(";") if op and op.split(":")[0] in kinds]

    def dry_cells(kinds):
        """Paint every `kinds` cell to Soil and READ BACK: 'no other water on the map' is a claim the rows rest on, so a
        refused read or paint (or water the canal sim repainted) stops the run instead of passing on a wet map."""
        wet_ = wet_cells(kinds)
        if wet_ is None:
            raise RuntimeError("terrain read refused: cannot dry the map")
        if wet_:
            B.call("jawa/set_terrain_batch", ops=";".join("Soil:" + op.split(":")[1] for op in wet_))
            left_ = wet_cells(kinds)
            if left_ is None:      # GPT review 5.3: a refused read-back is not a dry map
                raise RuntimeError("terrain read-back refused after painting Soil: cannot confirm the map is dry")
            if left_:
                raise RuntimeError("%d liquid cells still on the map after painting Soil (first %s)" % (len(left_), left_[:2]))
        return wet_

    def dry_all():
        """Every liquid cell on the map -> Soil (potable, salt, brine, toxic, slime): the row paints its own."""
        wet3 = dry_cells(WETS)
        # a player tank is a drink source too (round 2: T15's desperate pawns drank T20's leftover fresh tank): empty them
        for t in (B.call("jawa/list_things", defName="RM_LiquidTank", limit=50) or {}).get("things") or []:
            B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
                   args="%s,%s;Store;RM_Liquid_FreshWater;0" % (t.get("x"), t.get("z")))
        return len(wet3)

    saved = {}
    keys = THIRST_KEYS
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
                    # review 2026-10-27 F15: an exception names the faulting type in its STACK, not on its headline
                    # ("NullReferenceException: Object reference ..." then "  at RimMandrake.RM_Thirst..."): judge the
                    # whole block -- the headline plus the indented / "at " frame lines that follow it
                    lines_ = txt.splitlines()
                    exc, bad = [], []
                    for i_, l in enumerate(lines_):
                        if not re.search(r"Exception", l):
                            continue
                        exc.append(l)
                        blk = [l]
                        for f_ in lines_[i_ + 1:i_ + 40]:
                            if re.match(r"\s+(at |\[|--- )|\s*at |\(wrapper |\s*Rethrow as ", f_):
                                blk.append(f_)
                            else:
                                break
                        if re.search(r"DubsBadHygiene|RM_Thirst|RM_Bottle_", "\n".join(blk)):
                            bad.append(" | ".join(x.strip() for x in blk[:3]))
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
        wet = dry_cells(POTABLE_TERRAIN)
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
            drafted_ok = draft(pa) and draft(pc)
            mult = float(sget("thirstRateMultiplier") or 1)
            a0 = need(pa, 0.9)
            need(pc, 0.0)
            ticks(15000)
            a1 = need(pa)
            if want("T3"):
                if a0 is None or a1 is None or not drafted_ok:
                    row("T3_need_falls", "UNMEASURED", "HARNESS", {"levels": [a0, a1], "drafted": drafted_ok,
                                                                   "draftRefused": res.get("draftRefused")})
                else:
                    drop = a0 - a1
                    exp = 0.2 * mult
                    row("T3_need_falls", "PASS" if abs(drop - exp) <= 0.03 * mult else "FAIL", "MOD",
                        {"before": a0, "after": a1, "drop": round(drop, 4), "expect": exp, "heatScaling": False,
                         "ticks": 15000})
            if want("T6"):
                # live J20261028T005149Z-1f7ee6: T3's row() cleared UNDER_TEST (F16), so a governor stop mid-T6 ran
                # feed_all over pc and refilled its thirst -> RM_Dehydration 0.12, a harness false FAIL. pc is under test again.
                UNDER_TEST.add(pc)
                for _ in range(3):
                    need(pc, 0.0)
                    ticks(15000)
                need(pc, 0.0)
                h = hediffs(pc)
                sev = h.get("RM_Dehydration")
                st = "UNMEASURED" if (not h and sev is None) or not drafted_ok else ("PASS" if sev is not None and abs(sev - 0.30) <= 0.03 else "FAIL")
                row("T6_dehydration_readable", st, "MOD" if st != "UNMEASURED" else "HARNESS",
                    {"RM_Dehydration": sev, "hediffs": h, "heldAtZeroTicks": 60000, "drafted": drafted_ok})
            sset("thirstHeatScaling", saved["thirstHeatScaling"])

        # ---------------------------------------------------------------- T4 / T5 ordered bottles
        fresh_gain = None
        if want("T4") or want("T5"):
            pb = spawn_colonist(X0 + 10, Z0 + 2)
            l0 = need(pb, 0.2)
            bid = spawn("RM_Bottle_FreshWater", X0 + 11, Z0 + 2)
            dirty0 = count("RM_BottleDirty")
            r = B.call("jawa/ordered_job", pawnId=pb, jobDef="Ingest", targetAId=bid, count=1, waitTicks=30) or {}
            ing4 = ingest_done(pb)
            l1 = need(pb)
            dirty1 = count("RM_BottleDirty")
            fresh_gain = (l1 - l0) if None not in (l0, l1) else None
            if want("T4"):
                if fresh_gain is None or not r.get("accepted") or not ing4["ended"]:
                    row("T4_bottle_satisfies", "UNMEASURED", "HARNESS", {"order": {k: r.get(k) for k in ("accepted", "afterJobDef", "message")}, "levels": [l0, l1], "ingest": ing4})
                else:
                    ok4 = fresh_gain >= 0.45 and dirty1 > dirty0
                    row("T4_bottle_satisfies", "PASS" if ok4 else "FAIL", "MOD",
                        {"levels": [l0, l1], "gain": round(fresh_gain, 4), "dirtyBottles": [dirty0, dirty1], "ingest": ing4})
            if want("T5"):
                pd = spawn_colonist(X0 + 14, Z0 + 2)
                s0 = need(pd, 0.2)
                sid = spawn("RM_Bottle_SaltWater", X0 + 15, Z0 + 2)
                r = B.call("jawa/ordered_job", pawnId=pd, jobDef="Ingest", targetAId=sid, count=1, waitTicks=30) or {}
                ing5 = ingest_done(pd)
                s1 = need(pd)
                h = hediffs(pd)
                _, mem = needs_of(pd)
                if None in (s0, s1) or fresh_gain is None or not r.get("accepted") or not ing5["ended"] or not ing4["ended"]:
                    row("T5_salt_water_quality", "UNMEASURED", "HARNESS", {"levels": [s0, s1], "freshGain": fresh_gain,
                                                                             "ingest": ing5, "freshIngest": ing4,
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
                         "levels": [s0, s1], "ratioToFresh": round(ratio, 3), "hediffs": h, "memories": mem, "bad": bad, "ingest": ing5,
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
                if l0 is not None and l1 is not None and l1 - l0 >= 0.4:
                    break
            pf = spawn_colonist(PX + 12, PZ + 3)
            sset("drinkFromTerrain", False)
            try:
                o0 = need(pf, 0.2)
                oh0 = hediffs(pf)
                t_off, seen_off = poll_job(pf, ("RM_DrinkFromTerrain",), 900)
                # review 2026-10-27 F13: a drink that starts and ends between two 60-tick samples is invisible to the job
                # poll; the NEED over the whole window is not (900 ticks of decay is -0.012; a drink is +0.4 or more)
                o1 = need(pf)
                oh1 = hediffs(pf)
            finally:
                sset("drinkFromTerrain", saved["drinkFromTerrain"])
            bad = []
            if t_hit is None:
                bad.append("no RM_DrinkFromTerrain within 900 ticks (jobs seen %s)" % seen)
            elif l0 is None or l1 is None or l1 - l0 < 0.4:
                bad.append("need rose only %s -> %s" % (l0, l1))
            if t_off is not None:
                bad.append("drinkFromTerrain OFF but the job ran")
            if o0 is not None and o1 is not None and o1 > o0 + 0.02:
                bad.append("drinkFromTerrain OFF but the need rose %s -> %s over the window (a drink between samples)" % (o0, o1))
            new_oh = sorted(set(oh1) - set(oh0) - NOT_A_DRINK)
            if new_oh:
                bad.append("drinkFromTerrain OFF but new hediffs %s" % new_oh)
            unm = l0 is None or o0 is None or o1 is None
            row("T10_terrain_drink", "UNMEASURED" if unm else ("FAIL" if bad else "PASS"),
                "HARNESS" if unm else "MOD",
                {"jobAtTick": t_hit, "jobsSeen": seen, "levels": [l0, l1], "trace": trace, "offJobsSeen": seen_off,
                 "offLevels": [o0, o1], "offNewHediffs": new_oh, "bad": bad})
            draft(pe)
            draft(pf)
        if want("T9"):
            # review 2026-10-27 F3: "no bottle on the map" was inferred, never made -- a leftover bottle (or a tank, or
            # another water body) is a source an animal could have used. Make it true, then repaint the row's pond.
            dry_all()
            purge_drinks()
            paint("WaterShallow", PX, PZ, 4, 4)
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
                     "inferred": "map dried and every bottle/bucket purged before the pond was repainted: a rise is a pond drink (the job is not on the bridge)"})

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
            if bid is None or not count("RM_Bottle_FreshWater", "%d,%d,1,1" % (SX + 32, SZ)):
                # no bottle laid: "not fetched" would pass vacuously below (gone == True because it never existed)
                row("T12_no_routine_salt", "UNMEASURED", "HARNESS", {"why": "the fresh bottle 30 cells off was not laid",
                                                                    "jobsSalt": seen})
                draft(ph)
                bid = False
            # review 2026-10-27 F4: "the cell is empty" is not "ph fetched and drank it" -- an undrafted bystander could
            # pack or drink the bottle. Every other colonist is drafted, the bottle is followed by id, and the fetch is
            # read as ph's own need rising with that id gone.
            if bid is not False:
                draft_others((ph,))
            nb = need(ph) if bid is not False else None
            t_fetch, seen2 = poll_job(ph, ("Ingest",), 1500, step=60) if bid is not False else (None, [])
            if bid is not False and t_fetch is not None:
                ingest_done(ph)
            else:
                ticks(400) if bid is not False else None
            na = need(ph) if bid is not False else None
            live = ids_of("RM_Bottle_FreshWater") if bid is not False else None
            gone = None if live is None else bid not in live
            rose = None if None in (nb, na) else na > nb + 0.3
            bad = []
            if t_any is not None:
                bad.append("a drink job ran with only salt in reach: %s" % seen)
            if salt_b:
                bad.append("%d salt bottles appeared while only salt water was in reach" % salt_b)
            if gone is not None and rose is not None and not (gone and rose):
                bad.append("the fresh bottle 30 cells off was not fetched and drunk by the pawn (bottle gone %s, need %s -> %s)" % (gone, nb, na))
            if bid is not False:
                unm = gone is None or rose is None or l0 is None
                row("T12_no_routine_salt", "UNMEASURED" if unm and not bad else ("FAIL" if bad else "PASS"),
                    "HARNESS" if unm and not bad else "MOD",
                    {"jobsSalt": seen, "jobsAfterBottle": seen2, "bottleId": bid, "bottleGone": gone,
                     "needAroundFetch": [nb, na], "saltBottles": salt_b, "level0": l0, "bad": bad})
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
        if want("T27") and biomes_absent:
            row("T27_water_items", "UNMEASURED", "SITE", {"why": "RM_BlueIceMeltwaterCan is BlueDesert's (%s not loaded)" % BIOMES})
        elif want("T27"):
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
            elif l0 is None or l1 is None or abs((l1 - l0) - 0.67) > 0.06:
                bad.append("gain %s, want +0.67" % (None if None in (l0, l1) else round(l1 - l0, 3)))
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
                # HARNESS: a hemogen pack takes ~480 ticks to ingest (500 read it mid-job). Review 2026-10-27 F5: the
                # result is READ -- a baseliner still chewing at the end of the budget has not been measured at all
                ended = wait_job_end(pid, "Ingest", 1500)
                ticks(60)
                live = ids_of("HemogenPack")
                out28[tag] = {"levels": [l0, need(pid)], "accepted": r2.get("accepted"), "after": r2.get("afterJobDef"),
                              "msg": r2.get("message"), "packLeft": count("HemogenPack"), "jobEnded": ended,
                              "packId": hid, "packGone": None if live is None or not hid else hid not in live}
            bad = []
            sgl = out28.get("sang", {}).get("levels") or [None, None]
            bsl = out28.get("base", {}).get("levels") or [None, None]
            # "a baseliner's thirst did not rise" is vacuous unless the baseliner's Ingest order was accepted
            base_ordered = bool(out28.get("base", {}).get("accepted"))
            ended_all = all(out28.get(t_, {}).get("jobEnded") for t_ in ("sang", "base"))
            if out28.get("xenotype") != "Sanguophage" or None in sgl or None in bsl or not base_ordered or not ended_all:
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
            # HARNESS (job J20261026T060806Z-09152f): T13's toxic strip and T10/T11's water were still on the map, so the pawn
            # at 0.2 walked to RM_DrinkFromTerrain instead of the only bucket; dry the liquids first, like T15 does
            dry_all()
            purge_drinks()
            pk = spawn_colonist(X0 + 2, Z0 + 20)
            m0 = mems(pk)
            k0 = need(pk, 0.2)
            draft_others((pk,))
            # review 2026-10-27 F6: the row's OWN bucket is followed by id -- "the first fresh bucket on the map" may be
            # another one, and "no bucket left" skipped the Partly-drunk check outright
            bkid = spawn("RM_Bucket_FreshWater", X0 + 8, Z0 + 20)
            t_hit, seen = poll_job(pk, ("RM_DrinkFromContainer", "Ingest"), 900)
            if t_hit is not None:
                wait_job_end(pk, seen[-1])
            k1 = need(pk)
            m1 = mems(pk)
            live_bk = ids_of("RM_Bucket_FreshWater")
            insp = None
            if live_bk and bkid in live_bk:
                for t in (B.call("jawa/inspect_string", thingIds=bkid) or {}).get("things") or []:
                    insp = " | ".join(t.get("inspect") or [])
            pb2 = spawn_colonist(X0 + 12, Z0 + 20)
            draft(pb2)
            b0 = need(pb2, 0.2)
            bid = spawn("RM_Bottle_FreshWater", X0 + 13, Z0 + 20)
            ob = B.call("jawa/ordered_job", pawnId=pb2, jobDef="Ingest", targetAId=bid, count=1, waitTicks=30) or {}
            ing19 = ingest_done(pb2)         # not a fixed 500 ticks: the outcome doers run only when the Ingest job ENDS
            b1 = need(pb2)
            mb = mems(pb2)
            live_bt = ids_of("RM_Bottle_FreshWater")
            # the bottle arm measured a drink only when THIS bottle is gone and THIS pawn's need rose (an Ingest that
            # ended early, cancelled, consumed nothing: the 'no rough thought' it leaves is vacuous)
            bottle_drunk = (live_bt is not None and bid is not None and bid not in live_bt and None not in (b0, b1)
                            and b1 > b0 + 0.3)
            bad = []
            bottle_arm_ok = bool(ob.get("accepted")) and ing19["ended"] and bid is not None and bottle_drunk
            if "RM_DrinkFromContainer" not in seen:
                bad.append("no RM_DrinkFromContainer from the only bucket (jobs %s)" % seen)
            elif "RM_Thought_DrankRough" not in m1 or "RM_Thought_DrankRough" in m0:
                bad.append("bucket drink left no RM_Thought_DrankRough")
            if "RM_DrinkFromContainer" in seen and None not in (k0, k1) and k1 <= k0 + 0.05:
                bad.append("the bucket drink hydrated nothing (%s -> %s)" % (k0, k1))
            if live_bk is not None and "RM_DrinkFromContainer" in seen:
                if bkid not in live_bk:
                    bad.append("one drink used up the 15 L bucket %s (it is gone, not partly drunk)" % bkid)
                elif "Partly drunk" not in (insp or ""):
                    bad.append("bucket inspect %r has no 'Partly drunk'" % insp)
            if "RM_Thought_DrankRough" in mb:
                bad.append("a bottle drink at home gave RM_Thought_DrankRough")
            # "no rough thought after a bottle drink" is vacuous when no bottle drink happened
            row("T19_awkward_access", "FAIL" if bad else ("PASS" if bottle_arm_ok else "UNMEASURED"),
                "MOD" if bad or bottle_arm_ok else "HARNESS",
                {"bottleOrder": {k: ob.get(k) for k in ("accepted", "afterJobDef", "message")}, "bottleIngest": ing19,
                 "bottleId": bid, "bottleDrunk": bottle_drunk, "bottleLevels": [b0, b1], "bucketId": bkid,
                 "bucketLevels": [k0, k1], "bucketLeft": None if live_bk is None else bkid in live_bk,
                 "jobs": seen, "memAfterBucket": m1, "bucketInspect": insp, "memAfterBottle": mb, "bad": bad,
                 "notRun": "tank arm, Ascetic/tribal arms, pond arm"})
            draft(pk)

        # ---------------------------------------------------------------- T24 bucket douses fire
        if want("T24"):
            purge_drinks()
            FX, FZ = X0 + 25, Z0 + 5
            B.call("jawa/destroy_batch", rects="%d,%d,14,10" % (FX - 6, FZ - 3), categories="Plant,Item,Filth")
            mz = B.call("jawa/map_zones", action="paintArea", area="Home", rect="%d,%d,14,10" % (FX - 6, FZ - 3), value=True) or {}
            home_painted = mz.get("success") is True
            # HARNESS (T24 failed once in the full run at ea44bf7957, passed in the isolated run with the same DLL): the douse
            # giver is skipped for a pawn whose Firefighting is disabled (WorkGiver_RM_DouseFireWithBucket.ShouldSkip,
            # RM_BucketFirefighting.cs:120), and a generated colonist can be incapable of it (T25 hit the same with Hauling);
            # fires 9 -> 9 with only wander jobs is that signature. Replace refused pawns, as worker() does, and set priority 1.
            for _ in range(6):
                pf = spawn_colonist(FX - 5, FZ + 1)
                UNDER_TEST.add(pf)
                if (B.call("jawa/set_work_priority", pawnId=pf, workType="Firefighter", priority=1) or {}).get("success") is True:
                    break
                draft(pf)
            else:
                raise RuntimeError("six colonists in a row were incapable of Firefighting")
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
            if not home_painted:
                row("T24_bucket_douses_fire", "UNMEASURED", "HARNESS", {"why": "the Home area was not painted over the plot (map_zones refused): "
                                                                       "the douse giver works only inside it", "reply": str(mz)[:160]})
            elif fires0 < 1:
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
            q0 = need(p5, 0.05)
            qh0 = hediffs(p5)
            for _, _, pid in subj:
                need(pid, 0.0)
                B.call("jawa/stop_job", pawnId=pid)
            B.call("jawa/stop_job", pawnId=p5)
            jobs = {pid: [] for _, _, pid in subj + [(0, 0, p5)]}
            # review 2026-10-27 F13: the last 600 ticks were advanced blind, so the 0.05 arm's "no drink" covered only the
            # first 1,200 -- every tick of the window is sampled now, and the need/hediffs say what the job samples miss
            for _ in range(30):
                ticks(60)
                for pid in jobs:
                    j = job(pid)
                    if j and (not jobs[pid] or jobs[pid][-1] != j):
                        jobs[pid].append(j)
            q1 = need(p5)
            qh1 = hediffs(p5)
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
            if None not in (q0, q1) and q1 > q0 + 0.02:
                bad.append("the pawn at 0.05 drank: need %s -> %s over the window" % (q0, q1))
            new_q = sorted(set(qh1) - set(qh0) - NOT_A_DRINK)
            if new_q:
                bad.append("the pawn at 0.05 gained %s" % new_q)
            out15["at0.05"] = jobs[p5]
            out15["at0.05levels"] = [q0, q1]
            # red/green/white's colour hediffs come from Contagion / GelatinousSlime / TheRot (all in mandrake.rm.biomes);
            # without it only yellow's RM_SlimeNausea and the shared purge/thought can be scored
            foreign = ("RM_ContagionTouched", "RM_Slimification", "RM_SporeFlesh")
            unscorable = [b_ for b_ in bad if biomes_absent and any(b_.endswith(": %s None" % f_) for f_ in foreign)]
            rest = [b_ for b_ in bad if b_ not in unscorable]
            if rest:
                row("T15_slime_effects", "FAIL", "MOD", dict(out15, bad=rest, unscorable=unscorable))
            elif None in (q0, q1):
                row("T15_slime_effects", "UNMEASURED", "HARNESS", dict(out15, bad=[], why="the 0.05 arm's need was unreadable"))
            elif unscorable:
                row("T15_slime_effects", "UNMEASURED", "SITE", dict(out15, bad=[], unscorable=unscorable,
                                                                    why="%s not loaded: three colour hediffs absent" % BIOMES))
            else:
                row("T15_slime_effects", "PASS", "MOD", dict(out15, bad=bad))
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
            # review 2026-10-27 F14: the loop could run out with the pawn still in the break (its effects applied) and pass
            msf = B.call("jawa/pawn_mental", pawn=ps, action="list") or {}
            st_final = None if msf.get("success") is False else json.dumps(msf.get("pawns") or msf.get("state") or msf)[:160]
            bad = []
            if not r.get("started"):
                row("T17_salt_break", "UNMEASURED", "HARNESS", {"force": {k: r.get(k) for k in ("started", "message", "breakDef")}})
            else:
                if lvl is None or lvl < 0.9:
                    bad.append("the break ended with thirst %s (want >= 0.9)" % lvl)
                if "RM_Thought_SaltRelief" not in m:
                    bad.append("no RM_Thought_SaltRelief")
                sp = h.get("RM_SaltPoisoning")
                if sp is None or sp <= 0.01 or abs(sp / 0.25 - round(sp / 0.25)) > 0.05:
                    bad.append("RM_SaltPoisoning %s is not 0.25 a drink (and at least one drink)" % sp)
                if st_final is not None and "DrinkBrine" in st_final:
                    bad.append("the break never ended in 3,000 ticks (state %s)" % st_final)
                unm17 = st_final is None and not bad
                row("T17_salt_break", "UNMEASURED" if unm17 else ("FAIL" if bad else "PASS"), "HARNESS" if unm17 else "MOD",
                    {"force": {k: r.get(k) for k in ("started", "breakDef")}, "trace": trace[-4:], "hediffs": h, "memories": m,
                     "finalMental": st_final,
                     "bad": bad, "notRun": "the break being OFFERED (mood gate, dev list) and not offered with a fresh bottle: the start is forced"})
            draft(ps)
        # ================================================================ batch 3 (thirst live round 2, 2026-10-17)
        # A second, freshly cleared site east of the first (X3..X3+50 x Z0..Z0+40), so these rows never meet the first
        # batch's ponds, salt strips and slime pools. Every row starts by drying it and quenching every bystander, so a
        # thirsty pawn from an earlier row never drinks the test's water or bottles.
        X3 = X0 + 45
        batch3 = [r_ for r_ in ("T14", "T16", "T18", "T20", "T23", "T25", "T26", "T29") if want(r_)]
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
            if hasattr(B, "tank_units"):      # the offline fake answers directly (no hose probe on a mock)
                return B.tank_units(x, z)
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
                ok = all((B.call("jawa/set_work_priority", pawnId=pid, workType=w, priority=1) or {}).get("success") is True
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
            purge_drinks()       # review 2026-10-27 F3: "no other liquid" also means no bottle / bucket an animal can drink
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
                         "inferred": "the map was dried and every bottle/bucket purged, so a rise is a salt drink (the animal job is not on the bridge)",
                         "notRun": "a real salt/brine biome map (native read off the live roster instead)"})
            dry_all()

        # ---------------------------------------------------------------- T16 living slime (RM_Slime_Liquid)
        if "T16" in batch3 and biomes_absent:
            row("T16_living_slime", "UNMEASURED", "SITE", {"why": "RM_Slime_Liquid is GelatinousSlime's (%s not loaded)" % BIOMES})
        elif "T16" in batch3:
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
            o0 = need(p16b, 0.0)
            oh0 = hediffs(p16b)
            try:
                t_off, seen_off = poll_job(p16b, ("RM_DrinkFromTerrain",), 900, step=60)
                # review 2026-10-27 F13: a drink between two samples shows in the need / hediffs, not in the job poll
                o1 = need(p16b)
                oh1 = hediffs(p16b)
            finally:
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
            if None not in (o0, o1) and o1 > o0 + 0.02:
                bad.append("lastResortDrinking OFF and the need rose %s -> %s (a drink between samples)" % (o0, o1))
            new_oh = sorted(set(oh1) - set(oh0) - NOT_A_DRINK)
            if new_oh:
                bad.append("lastResortDrinking OFF and new hediffs %s" % new_oh)
            unm16 = None in (o0, o1) and not bad
            row("T16_living_slime", "UNMEASURED" if unm16 else ("FAIL" if bad else "PASS"), "HARNESS" if unm16 else "MOD",
                {"jobsOn": seen_on, "hediffs": h16, "memories": m16, "jobsOff": seen_off, "offLevels": [o0, o1],
                 "offNewHediffs": new_oh, "bad": bad,
                 "notRun": "a Gelatinous Slime biome map: RM_Slime_Liquid painted on the calm site (the drink rule is the terrain's)"})
            paint("Soil", LX, LZ, 2, 2)

        # ---------------------------------------------------------------- T20 bucket drunk dry; part-drunk pour
        if "T20" in batch3:
            dry_all()
            purge_drinks()
            quench_all()
            BX, BZ = X3 + 22, Z0 + 2
            # HARNESS (job 832567, 2026-10-27): purge_drinks leaves empty/dirty buckets (T24's douse bucket), and an
            # undrafted colonist refilled it (WorkGiver_FillBottle) mid-loop: a second fresh bucket took drinks 11-14 and
            # was the 'part-drunk' bucket the pour arm read. Every leftover bucket goes, bystanders are drafted, and both
            # arms follow the bucket they spawned by id.
            for d_ in ("RM_BucketEmpty", "RM_BucketDirty", "RM_Bucket_FreshWater"):
                for t_ in things(d_):
                    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t_.get("x"), t_.get("z")), categories="Item")
            p20 = spawn_colonist(BX, BZ + 2)
            UNDER_TEST.add(p20)
            drafted20 = draft(p20)
            draft_bystanders({p20})

            def bare(tid):
                return re.sub(r"^Thing_", "", str(tid or ""))

            def the_bucket(tid):
                """[the spawned fresh bucket] while it is still a fresh bucket; [] once drunk dry (or never spawned)."""
                return [t for t in things("RM_Bucket_FreshWater") if tid and bare(t.get("id")) == bare(tid)]

            bid = spawn("RM_Bucket_FreshWater", BX + 1, BZ)
            drinks, trace = 0, []
            for i in range(14):
                cur = the_bucket(bid)
                if not cur:
                    break
                n_a = need(p20, 0.1)
                r = B.call("jawa/ordered_job", pawnId=p20, jobDef="RM_DrinkFromContainer", targetAId=cur[0]["id"], waitTicks=30) or {}
                ended20 = wait_job_end(p20, "RM_DrinkFromContainer", 900)
                ticks(30)
                n_b = need(p20)
                # review 2026-10-27 F7: a drink is counted only when it was accepted, ended and HYDRATED -- an order the
                # pawn never carried out (or a last drink that emptied the bucket for nothing) is not a drink
                took = bool(r.get("accepted")) and ended20 and None not in (n_a, n_b) and n_b > n_a + 0.02
                drinks += 1 if took else 0
                trace.append([r.get("accepted"), r.get("afterJobDef"), round(n_b or 0, 3), ended20, took])
            dirty = count("RM_BucketDirty") + count("RM_BucketEmpty")
            left = len(the_bucket(bid))   # the spawned bucket still fresh (a stray one is purged above)
            # arm 2: drink 3 (4.5 L of 15), then a player's order pours what is left into a Store tank
            TX, TZ = BX + 6, BZ + 4
            B.call("jawa/destroy_batch", rects="%d,%d,4,4" % (TX - 1, TZ - 1), categories="Building,Item,Plant")
            B.call("jawa/build_batch", ops="RM_LiquidTank:%d,%d" % (TX, TZ), faction="player", wipeExisting=False)
            fill_r = str(B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
                                args="%d,%d;Store;RM_Liquid_FreshWater;100" % (TX, TZ)).get("result"))
            b2 = spawn("RM_Bucket_FreshWater", BX + 1, BZ)
            for i in range(3):
                need(p20, 0.1)
                cur = the_bucket(b2)
                if not cur:          # review: an IndexError here lost the whole run; the pour arm then reads the absence
                    break
                B.call("jawa/ordered_job", pawnId=p20, jobDef="RM_DrinkFromContainer", targetAId=cur[0]["id"], waitTicks=30)
                wait_job_end(p20, "RM_DrinkFromContainer", 900)
                ticks(30)
            cur = the_bucket(b2)
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
            pour_unread = False
            if not drafted20 or drinks == 0 or not trace or not trace[0][0]:
                row("T20_bucket_drunk_dry", "UNMEASURED", "HARNESS", {"trace": trace, "drafted": drafted20,
                                                                      "why": "the drinker was not drafted, or the ordered bucket drink was refused / hydrated nothing"})
            else:
                if left != 0 or drinks != 10:
                    bad.append("the 15 L bucket took %d drinks (want 10), %d still filled" % (drinks, left))
                if dirty < 1:
                    bad.append("no dirty/empty bucket after the last drink")
                if None in (u0, u1) or not pr.get("accepted"):
                    pour_unread = True     # GPT review 5.10: a refused pour order is no pour; not a mod defect
                elif u1 - u0 != 105:
                    bad.append("pouring a bucket with 4.5 L drunk added %s units (want 105 = 10.5 L)" % (u1 - u0))
                if insp is not None and "Partly drunk" not in insp:
                    bad.append("part-drunk bucket inspect %r has no 'Partly drunk'" % insp)
                # the pour arm cannot be judged without a tank read: UNMEASURED (HARNESS), never a FAIL of the mod
                row("T20_bucket_drunk_dry", "FAIL" if bad else ("UNMEASURED" if pour_unread else "PASS"),
                    "MOD" if bad or not pour_unread else "HARNESS",
                    {"pourTankUnreadable": pour_unread, "drinks": drinks, "trace": trace[-3:], "dirtyOrEmpty": dirty, "tank": fill_r, "units": [u0, u1],
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
            PLOT23 = "%d,%d,14,14" % (FX3 - 1, FZ3 - 1)
            # review 2026-10-27 F1/F8: brine buckets are followed by id. pre23 = every brine bucket on the map before the
            # order could run (an old one is not a fill), and the positive arm passes only on THIS tank's units rising
            # -- a brine bucket made, or a fill job seen, is not the tank being filled.
            pre23 = ids_of("RM_Bucket_Brine")
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
            now23 = ids_of("RM_Bucket_Brine")
            made = None if now23 is None or pre23 is None else len(set(now23) - set(pre23))
            u1 = tank_units(TX, TZ)
            # arm 2: Store mode -> the standing order is gone; no new brine fills. The worker's job at the switch says
            # what may still land: one fill / pour already in flight may finish (one bucket); anything more is an order.
            j_sw = job(p23)
            allow = 1 if j_sw in ("RM_FillBottleJob", "RM_EmptyIntoTankJob") else 0
            known = set(now23 or ()) | set(pre23 or ())
            B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
                   args="%d,%d;Store;RM_Liquid_Brine;100" % (TX, TZ))
            B.call("jawa/stop_job", pawnId=p23)
            # HARNESS history (first live run 2026-10-17; round 2; ea44bf7957 2 of 3): a fill or pour in flight at the
            # switch can finish its carry well after it (no job sampled, one brine bucket at the shore). The settle waits
            # until the pawn is off every fill/pour job, then 600 more ticks -- and every brine bucket that lands in it
            # is COUNTED against the in-flight allowance instead of being cleared blind.
            # live J20261028T005149Z-1f7ee6: one brine bucket landed here with GotoWander at the switch -- the settle's
            # jobs are now recorded so the finding says whether a fill STARTED after the Store order (diagnostic only)
            # live J20261028T014816Z-d2e098: the settle bucket came from ANOTHER colonist (a bystander the AutoUndrafter
            # freed, see DRAFT_AT) -- every other colonist's non-idle jobs in the settle are recorded too (diagnostic)
            settle_jobs, others_jobs = [], {}

            def settle(n):
                for _ in range(n // 30):
                    ticks(30)
                    for c in colonists():
                        cid, jj = re.sub(r"^Thing_", "", str(c.get("pawnId"))), c.get("job")
                        seq = settle_jobs if cid == p23 else others_jobs.setdefault(cid, [])
                        if jj and jj != "Wait_Combat" and (not seq or seq[-1] != jj):
                            seq.append(jj)
            settle(300)
            for _ in range(20):
                if job(p23) not in ("RM_FillBottleJob", "RM_EmptyIntoTankJob"):
                    break
                settle(60)
            settle(600)
            set23 = ids_of("RM_Bucket_Brine")
            settle_new = None if set23 is None else sorted(set(set23) - known)
            # clear only what is known: the row's brine buckets (by cell, each one read above), never a blind sweep
            for tid in (settle_new or []) + sorted(set(now23 or ()) - set(pre23 or ())):
                t = (set23 or {}).get(tid) or (now23 or {}).get(tid)
                if t:
                    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t.get("x"), t.get("z")), categories="Item")
            known |= set(settle_new or ())
            # the window needs empties to fill: top up to 3 on the plot and READ them back
            for _ in range(3 - count("RM_BucketEmpty", PLOT23)):
                spawn("RM_BucketEmpty", FX3 + 5, FZ3 + 6)
            empties2 = count("RM_BucketEmpty", PLOT23)
            base2 = ids_of("RM_Bucket_Brine")
            seen2 = []
            for _ in range(100):
                ticks(30)
                j = job(p23)
                if j and (not seen2 or seen2[-1] != j):
                    seen2.append(j)
            end2 = ids_of("RM_Bucket_Brine")
            new2 = None if end2 is None or base2 is None else sorted(set(end2) - set(base2))
            made2 = None if new2 is None else len(new2)
            where2 = [(end2[t].get("x"), end2[t].get("z")) for t in new2 or []]
            u2 = tank_units(TX, TZ)
            bad = []
            det23 = {"tank": tank_r, "units": [u0, u1], "brineBucketsMade": made, "jobsFill": seen, "jobAtSwitch": j_sw,
                     "inFlightAllowance": allow, "landedInSettle": settle_new, "settleJobs": settle_jobs,
                     "othersInSettle": {k: v for k, v in others_jobs.items() if v}, "draftRearms": res.get("draftRearms", 0),
                     "emptiesForWindow": empties2,
                     "jobsStore": seen2, "brineBucketsAfterStore": made2, "brineAt": where2, "storeTankUnits": u2}
            if u0 is None or u1 is None or settle_new is None or made2 is None or empties2 < 1:
                row("T23_fill_tank_is_the_order", "UNMEASURED", "HARNESS",
                    dict(det23, why="tank unread, brine buckets unread, or no empty bucket for the Store window"))
            else:
                if not u1 > u0:
                    bad.append("Fill tank holding brine: its units never rose in 6,000 ticks (%s -> %s; %s brine buckets made, jobs %s)"
                               % (u0, u1, made, seen))
                if len(settle_new) > allow:
                    bad.append("Store tank: %d brine buckets landed in the settle after the switch (in flight allowed %d)"
                               % (len(settle_new), allow))
                if made2 > 0 or "RM_FillBottleJob" in seen2:
                    bad.append("Store tank: brine still gathered (%d buckets, jobs %s)" % (made2, seen2))
                row("T23_fill_tank_is_the_order", "FAIL" if bad else "PASS", "MOD", dict(det23, bad=bad))
            draft(p23)

        # ---------------------------------------------------------------- T25 snow into water
        if "T25" in batch3:
            dry_all()
            purge_drinks()
            quench_all()
            SX3, SZ3 = X3 + 2, Z0 + 14
            B.call("jawa/destroy_batch", rects="%d,%d,14,10" % (SX3, SZ3), categories="Building,Item,Plant")
            sb = B.call("jawa/set_weather_buildup", kind="snow", mode="set", rect="%d,%d,8,8" % (SX3, SZ3), depth=1.0) or {}
            # Full run, round 2: three leftover empty buckets (T20/T23) were all gathered, and none of the three snow buckets
            # was seen melting in 7,000 ticks at 26 C, while the one-bucket run melts at 5,000. The row now clears every
            # leftover bucket first and lays --t25-empties of its own (default the bar's one; 3 replays the full run).
            for d_ in ("RM_BucketEmpty", "RM_BucketDirty", "RM_BucketSnow"):
                for t_ in things(d_):
                    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t_.get("x"), t_.get("z")), categories="Item")
            for i_ in range(max(1, a.t25_empties)):
                spawn("RM_BucketEmpty", SX3 + 10 + i_, SZ3 + 2)
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
            # Full run, round 2 (thirst_live_result_20261017T145433.json): FAIL "did not melt within 7,000 ticks". It DID
            # melt: that run laid one empty and met three leftovers, so FOUR snow buckets were gathered at staggered times;
            # at t=5000 three snow buckets lay and fresh read 1 (the first had melted on time; fresh0 was not recorded, but purge_drinks ran just before), at 6500 two lay and fresh 2.
            # The old test 'fresh rose AND no snow bucket left' waited for the LAST-gathered bucket. HARNESS, not MOD. The
            # arm now follows the snow bucket(s) that existed when the gather was seen, by ID: melted = all of those gone
            # AND fresh water up by at least their count (a carry also drops an ID from the ground list, so fresh must rise).
            # Theories weighed, from code + that trace (no replay): FALSE - temperature (the bucket's cell read 24.9-26.3 C,
            # CompRM_Melt counts any rare tick above 0 C); FALSE - an earlier row's stove/bill (the only bill row, T26,
            # runs after T25, and the passive melt needs no bill); FALSE - the worker busy or the bucket forbidden/reserved
            # (all four were gathered; the melt comp reads neither); FALSE - a carried bucket not ticking (all three
            # stayed on their scoop cells (205,145..147) through the trace). The 145433 'comp: None' was the instrument:
            # that driver read comp_read's 'fields'/'members' keys, the tool answers 'values'.
            first = [t_.get("id") for t_ in things("RM_BucketSnow")]
            first_n = snowb
            # review 2026-10-27 F9: "the followed id left the ground list and SOME fresh bucket appeared" also reads a
            # bucket carried off plus an unrelated fresh bucket. CompRM_Melt replaces a spawned snow bucket with water
            # placed at the same PositionHeld (RM_ThirstWaterSources.cs): so each followed bucket must be replaced by a
            # fresh bucket with a NEW id on ITS cell. The worker is drafted now, so nothing carries a snow bucket away.
            snow_at = {str(t_.get("id")): (t_.get("x"), t_.get("z")) for t_ in things("RM_BucketSnow")}
            fresh_ids0 = set(ids_of("RM_Bucket_FreshWater") or ())
            drafted25 = draft(p25)
            replaced = {}
            if snowb:
                for k in range(14):
                    ticks(500)
                    quench_all()
                    sb_ = things("RM_BucketSnow")
                    smp = {"t": (k + 1) * 500, "snow": [(t.get("x"), t.get("z")) for t in sb_], "fresh": count("RM_Bucket_FreshWater")}
                    if sb_:
                        smp["cellC"] = (B.call("jawa/cell_temperature", cell="%s,%s" % (sb_[0].get("x"), sb_[0].get("z"))) or {}).get("temperature")
                        cr = B.call("jawa/comp_read", thing=sb_[0].get("id"), comp="CompRM_Melt", members="warmTicks") or {}
                        smp["warmTicks"] = (cr.get("values") or {}).get("warmTicks")
                        for t_ in (B.call("jawa/inspect_string", thingIds=",".join(x.get("id") for x in sb_)) or {}).get("things") or []:
                            smp.setdefault("inspect", []).append(" | ".join(t_.get("inspect") or [])[:80])
                    melt_trace.append(smp)
                    ids_now = set(str(t.get("id")) for t in sb_)
                    fr_ = ids_of("RM_Bucket_FreshWater") or {}
                    for sid_, cell_ in snow_at.items():
                        if sid_ not in ids_now and sid_ not in replaced:
                            hit_ = [f_ for f_, t_ in fr_.items() if f_ not in fresh_ids0 and (t_.get("x"), t_.get("z")) == cell_]
                            replaced[sid_] = hit_[0] if hit_ else None
                    smp["replaced"] = dict(replaced)
                    if first and all(replaced.get(sid_) for sid_ in snow_at):
                        melted = (k + 1) * 500
                        break
                    if first and len(replaced) == len(snow_at):
                        break         # every followed bucket left the ground; one was not replaced on its cell
            # arm 2: a pond near -> the bucket fills from it, no snow job
            # review 2026-10-27 F10: "no RM_GatherSnow" alone also passes a pawn that did nothing; the arm must see the
            # laid bucket FILLED from the pond (its id gone, a new fresh bucket) and the undraft must have taken
            draft(p25)
            purge_drinks()           # DRINKS holds RM_BucketSnow: the melt arm's snow buckets go too
            for d_ in ("RM_BucketEmpty", "RM_BucketDirty"):
                for t_ in things(d_):
                    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % (t_.get("x"), t_.get("z")), categories="Item")
            B.call("jawa/set_weather_buildup", kind="snow", mode="set", rect="%d,%d,8,8" % (SX3, SZ3), depth=1.0)
            paint("WaterShallow", SX3 + 10, SZ3 + 8, 3, 2)
            eid = spawn("RM_BucketEmpty", SX3 + 10, SZ3 + 2)
            undrafted25 = draft(p25, False)
            B.call("jawa/stop_job", pawnId=p25)
            seen2 = []
            filled = None
            for _ in range(20):
                ticks(100)
                quench_all()
                j = job(p25)
                if j and (not seen2 or seen2[-1] != j):
                    seen2.append(j)
                fr2 = ids_of("RM_Bucket_FreshWater")
                em2 = ids_of("RM_BucketEmpty")
                if fr2 and em2 is not None and eid and eid not in em2:
                    filled = sorted(fr2)
                    break
            bad = []
            if not snowb:     # a gather job SEEN but no snow bucket made in 3,000 ticks leaves the melt arm untested: not a PASS
                bad.append("no RM_BucketSnow with snow beside the bucket in 3,000 ticks (jobs %s)" % seen)
            if snowb and melted is None:
                bad.append("the followed snow bucket(s) %s were not each replaced by water on their cell within 7,000 ticks at %s C (replaced %s)"
                           % (first, temp.get("temperature"), replaced))
            if "RM_GatherSnow" in seen2:
                bad.append("gathered snow with a pond near")
            elif undrafted25 and eid and not filled:
                bad.append("pond arm: the laid empty bucket %s was not filled from the pond in 2,000 ticks (jobs %s)" % (eid, seen2))
            snow_laid = sb.get("success") is True    # a refused snow set must not blame the mod for "no gather"
            unm25 = not snow_laid or not drafted25 or ((not undrafted25 or not eid) and not bad)
            row("T25_snow_to_water", "UNMEASURED" if unm25 else ("FAIL" if bad else "PASS"),
                "HARNESS" if unm25 else "MOD",
                {"snowSet": {k: sb.get(k) for k in ("success", "cellsChanged")}, "jobs": seen, "bucketsSnow": snowb,
                 "snowAfter": sd.get("sample") or sd.get("depths"), "meltTicks": melted, "followed": first, "meltTrace": melt_trace, "temp": temp.get("temperature"),
                 "replacedOnCell": replaced, "draftedForMelt": drafted25, "pondUndrafted": undrafted25, "pondEmpty": eid,
                 "pondFilled": filled, "jobsPond": seen2, "bad": bad, "notRun": "snow depth drop 0.4 (read back is a sample only)"})
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
            laid26 = count("RM_BlueIce") > 0 and count("RM_BucketEmpty") > 0     # read back: a refused spawn is not a mod fault
            # review 2026-10-27 F11: "some wooden fresh bucket exists" also passes a snow bucket left by an earlier row
            # melting, or a hauler's fill: the bill's product is a NEW fresh bucket at the campfire and the ice is used.
            ice0 = count("RM_BlueIce")
            fresh26_0 = ids_of("RM_Bucket_FreshWater")
            SITE26 = "%d,%d,9,9" % (CX - 4, CZ - 4)
            logp = __import__("game_paths").PLAYER_LOG
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
                now26 = ids_of("RM_Bucket_FreshWater", SITE26)
                if now26 and fresh26_0 is not None and set(now26) - set(fresh26_0):
                    break
            now26 = ids_of("RM_Bucket_FreshWater", SITE26)
            made = [t_ for f_, t_ in (now26 or {}).items() if fresh26_0 is not None and f_ not in fresh26_0]
            ice1 = count("RM_BlueIce")
            errs = []
            if log0 is not None:
                with open(logp, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(log0)
                    errs = [l for l in f.read().splitlines() if re.search(r"Exception|\bError\b", l)]
            bad = []
            if ba.get("success") is not True or fire is None or not laid26 or fresh26_0 is None or now26 is None:
                row("T26_ice_block_bill", "UNMEASURED", "HARNESS", {"bill": str(ba)[:200], "fire": fire, "iceAndBucketLaid": laid26,
                                                                    "freshRead": [fresh26_0 is not None, now26 is not None]})
            else:
                if not made:
                    bad.append("no NEW RM_Bucket_FreshWater at the campfire after the bill (jobs %s)" % seen)
                if not ice1 < ice0:
                    bad.append("the bill used no RM_BlueIce (%s before, %s after)" % (ice0, ice1))
                elif "Wood" not in str(made[0].get("stuff") or made[0].get("label") or ""):
                    bad.append("the bucket is not wooden: %s" % {k: made[0].get(k) for k in ("stuff", "label")})
                if errs:
                    bad.append("Player.log errors during the bill: %s" % errs[:2])
                row("T26_ice_block_bill", "FAIL" if bad else "PASS", "MOD",
                    {"jobs": seen, "made": [{k: t.get(k) for k in ("id", "stuff", "label")} for t in made[:2]],
                     "blueIceBefore": ice0, "blueIceLeft": ice1, "logErrors": errs[:3], "bad": bad})
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

            # review 2026-10-27 F12: bottles packed by an earlier row (or the starting kit) count toward the stock, and
            # the old fallback per=5 left a deficit of 10 or less, so "more than one trip" was never asked. Every
            # colonist's inventory is emptied first; a refused clear, or no target with a deficit over 10, is UNMEASURED.
            cleared29 = []
            for c in colonists():
                cr = B.call("jawa/pawn_gear", pawn=re.sub(r"^Thing_", "", c["pawnId"]), action="clear", clearWhat="inventory") or {}
                cleared29.append(cr.get("success") is True)
            ncol = len(colonists())
            h_ = have()
            # the smallest target that leaves a deficit over one trip (10), so the batch split is visible
            per = next((p_ for p_ in (1, 2, 3, 4, 5) if h_ is not None and p_ * ncol - h_ > 10), None)
            setup29 = None
            if not cleared29 or not all(cleared29):
                setup29 = "an inventory clear was refused (%s)" % cleared29
            elif per is None:
                setup29 = "no target up to 5 per colonist leaves a deficit over 10 (stock %s, %d colonists)" % (h_, ncol)
            if setup29:
                row("T29_bottle_stock_and_batches", "UNMEASURED", "HARNESS",
                    {"why": setup29, "colonists": ncol, "stockAfterClear": h_, "cleared": cleared29})
            else:
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
                    if f is not None and f >= target and k - last_change >= 10:   # review: an unreadable Have crashed the row
                        break
                ticks(1500)
                final = have()
                ground = count("RM_Bottle_FreshWater")
                jumps = [b - a for a, b in zip(series, series[1:]) if None not in (a, b)]
                deficit = target - (have0 or 0)
                sset("filledBottlesPerColonist", 3)
                bad = []
                if final is None or have0 is None:
                    bad.append("RM_BottleStock.Have unreadable")      # judged UNMEASURED below, never a FAIL of the mod
                elif final != target:
                    bad.append("filled %d bottles, want exactly the target %d (%d x %d colonists)" % (final, target, per, ncol))
                if jumps and max(jumps) > 10:
                    bad.append("one step filled %d bottles (a trip is at most 10)" % max(jumps))
                if deficit > 10 and len([x for x in jumps if x > 0]) < 2:
                    bad.append("a deficit of %d (over 10) should take more than one fill trip (steps %s)" % (deficit, jumps))
                unread29 = final is None or have0 is None
                row("T29_bottle_stock_and_batches", "UNMEASURED" if unread29 else ("FAIL" if bad else "PASS"),
                    "HARNESS" if unread29 else "MOD",
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
                rec = B.reload() if hasattr(B, "reload") else TSS.load_site(B.call, a.reload_site)
                # review 2026-10-27 F2: a reloaded save brings back its own water (a canal, a tank) and bottles; with a
                # potable cell left, A's "failed search" may never have failed and B's drink may not be the slime
                dry_all()
                purge_drinks()
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
            # A's search must be SEEN to fail (no drink job, need unchanged): only then is there a mark to go stale
            ja_, na_ = job(pa_), need(pa_)
            a_failed = (ja_ is not None and "Drink" not in str(ja_) and "Ingest" not in str(ja_)
                        and na_ is not None and abs(na_ - 0.2) < 0.02)
            r2 = reload_site()
            pb_ = spawn_colonist(RX, RZ)
            UNDER_TEST.add(pb_)
            ticks(90)                            # past A's mark tick, so 'until - now' is inside the 600-tick window
            paint("RM_SlimeRedShallow", RX - 1, RZ + 2, 2, 2)
            need(pb_, 0.0)
            tb = tg()                            # B's first search (poll_job's stop_job) runs at this tick
            hb0 = hediffs(pb_)
            t_drink, seen_r = poll_job(pb_, ("RM_DrinkFromTerrain",), 300, step=30)
            # B's drink must END and leave the slime's mark (RM_ContagionTouched / RM_SlimePurge): a job that started
            # and was cancelled is not a drink
            b_ended = wait_job_end(pb_, "RM_DrinkFromTerrain", 900) if t_drink is not None else False
            hb1 = hediffs(pb_)
            b_marked = any(k_ in hb1 and k_ not in hb0 for k_ in ("RM_ContagionTouched", "RM_SlimePurge"))
            det = {"pawnA": pa_, "pawnB": pb_, "tickA": ta, "tickB": tb, "jobsB": seen_r, "drinkAfter": t_drink,
                   "jobA": ja_, "needA": na_, "aSearchFailed": a_failed, "bDrinkEnded": b_ended, "bSlimeMarked": b_marked,
                   "loads": [r1.get("verified"), r2.get("verified")], "hediffsB": hb1}
            if not (r1.get("verified") and r2.get("verified")):
                row("T15R_reload_mark", "UNMEASURED", "HARNESS", dict(det, why="a site load did not verify"))
            elif pa_ != pb_:
                row("T15R_reload_mark", "UNMEASURED", "HARNESS", dict(det, why="B did not get A's thing ID: collision not reproduced"))
            elif not a_failed:
                row("T15R_reload_mark", "UNMEASURED", "HARNESS", dict(det, why="A's search was not seen to fail: no mark to go stale"))
            elif None in (ta, tb) or not ta <= tb < ta + 600:
                # the pre-fix guard honoured a mark only while now < until <= now + 600: outside that window the old DLL
                # passes too, so a PASS here would prove nothing
                row("T15R_reload_mark", "UNMEASURED", "HARNESS", dict(det, why="B's search is outside A's mark window"))
            else:
                row("T15R_reload_mark", "PASS" if (t_drink is not None and b_ended and b_marked) else "FAIL", "MOD", det)
    finally:
        for k, v in saved.items():
            try:
                B.call("jawa/mod_settings_field", typeName=S_TH, action="set", field=k, value=str(v))
            except Exception:  # noqa: BLE001 - restore every one we can
                pass
        res["settings_after"] = {k: sget(k) for k in saved}
        unrestored = {k: [saved[k], res["settings_after"][k]] for k in saved
                      if str(res["settings_after"][k]).lower() != str(saved[k]).lower()}
        if unrestored:       # the settings are the user's: a restore that did not read back is a finding, not a footnote
            row("settings_restored", "FAIL", "HARNESS", {"notRestored(before,after)": unrestored})
        res["ended"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
    return V.rows_exit(rows)     # review 2026-10-26: UNMEASURED -> 2 (was 1), no rows -> 2 (was 0)


if __name__ == "__main__":
    sys.exit(main())
