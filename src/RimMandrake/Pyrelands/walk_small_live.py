"""The two small live scenes that replaced the two-week sc_walk (RIMMANDRAKE_SPLIT_PYRELANDS_SEASON_WALK_TO_MINIMUM_TESTS; owner,
2026-11-24: "WHAT is being actually tested here? Should it even be tested? And if so, what's the MINIMUM test necessary to
show it?"). Chains of the Pyrelands suite (validation.py registers them through register()). Kind A, one claim each:

  reload_keeps_the_burn   sc_reload_keeps_the_burn (the tier list). Claim: a player who saves while a front burns and reloads
                          finds the front, the scar's age and bonus, and the scorch-fruit exactly as they were. One pad holds a
                          scar with fruit on it and a lit front; the state is read at the save and after the reload. Control: a
                          save made before any fire must read differently. Entry point: the fire and the fruit are placed; what
                          the save keeps is left to the mod. Forbidden: none. End: the reload's read (about 5,500 ticks played).
                          Planted: PYRE_PLANT_RELOAD=front_lost|old_save, each must FAIL.
  full_list_smoke         sc_full_list_smoke (his full list, run last, in one load). Claim: on his full list one lit fire still
                          walks as a front and Pyrelands writes no error. Opportunity: the running load is his full list and
                          grass burns. Success: fire at three hourly reads, its centre moved. Forbidden: a log error that names
                          Pyrelands. End: three game hours (7,500 ticks), too short for thirst, hunger or an arrival to matter.
                          Planted: PYRE_PLANT_SMOKE=no_front|log_error, each must FAIL.

Live halves UNRUN on 2026-11-24 (no game in that run). Run, on a Pyrelands site of northstar_site.py:
    modcheck run Pyrelands --chains reload_keeps_the_burn        (the pyrelands tier, any free game)
    modcheck run Pyrelands --chains full_list_smoke              (his full list, ArchBig)
Offline: python3 src/RimMandrake/Pyrelands/selftest_pyrelands_walk_small.py (the verdicts against planted faults).
"""
import os
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FULL_LIST = os.path.join(HERE, "..", "..", "..", "infrastructure", "state", "modlists", "ModsConfig.FULL.LATEST.xml")
FULL_SHARE = 0.95          # a running load with fewer of the full list's mods than this is not his full list (UNMEASURED)
RELOAD_SAVE = "pyre_reload"
RELOAD_BURN_TICKS = 5000   # the scar's burn, as fresh_burn_bonus: the grass is gone and the cells carry a burn stamp
RELOAD_FRONT_TICKS = 250   # the front is alight at the save
SMOKE_HOURS = 3
DEEP_ASH = "RM_FE_Ash_Deep"   # the biome's ordinary ground: a fire there ends with its grass
HOUR = 2500
OURS = ("Pyrelands", "RM_FE_", "RM_Pyre", "FireEcologyHook")   # what a log error of ours names
PLANT_RELOAD_ENV, PLANT_SMOKE_ENV = "PYRE_PLANT_RELOAD", "PYRE_PLANT_SMOKE"
RELOAD_FIRE_SLACK = 2      # a load may play one tick (measured 2026-11-15: now=1101501 read 1101502), and a fire may start or end in it
SCAR_SLACK = 0.02          # the same tick on the bonus's clock; the burn stamp itself must be equal
SCAR_FIELDS = ("fertility", "bonus", "burnTick", "base", "wateredFertility", "bonusAgeDays", "bonusDaysLeft")


def scar_part(kv):
    """Pure. The parts of one ProbeCell read that a reload keeps (at the same tick, the bonus's age too)."""
    return dict((k, kv.get(k)) for k in SCAR_FIELDS)


def scar_same(a, b):
    """Pure. Two scar_part dicts equal: the burn stamp exactly, every number within SCAR_SLACK."""
    if not a or not b or set(a) != set(b) or str(a.get("burnTick")) != str(b.get("burnTick")):
        return False
    try:
        return all(abs(float(a[k]) - float(b[k])) <= SCAR_SLACK for k in a)
    except (TypeError, ValueError):
        return False


def reload_verdict(pre, mid, again):
    """Pure. Three reads of the pad {"fires": [cells], "fruit": [cells], "scar": {cell: parts}}: before any fire, at the save,
    after the reload of that save -> (ok, why); ok None is no valid opportunity, never a verdict."""
    for name, d in (("before", pre), ("at the save", mid), ("after the reload", again)):
        if not isinstance(d, dict) or any(d.get(k) is None for k in ("fires", "fruit", "scar")):
            return None, "the read %s is missing" % name
    if not mid["fires"]:
        return None, "no front burned at the save"
    if not mid["fruit"]:
        return None, "no scorch-fruit stood at the save"
    if not mid["scar"] or not all(float(p.get("bonus") or 0) > 0 for p in mid["scar"].values()):
        return None, "the scar carried no fresh-burn bonus at the save: %r" % mid["scar"]
    if pre["fires"] or pre["fruit"] or pre["scar"] == mid["scar"]:
        return None, "the control save, made before any fire, reads like the save made during it"
    if len(set(again["fires"]) ^ set(mid["fires"])) > RELOAD_FIRE_SLACK:
        return False, "after the reload the front is not where it was: %d fire cells, %d at the save (lost %r, new %r)" % (
            len(again["fires"]), len(mid["fires"]), sorted(set(mid["fires"]) - set(again["fires"]))[:5],
            sorted(set(again["fires"]) - set(mid["fires"]))[:5])
    if sorted(again["fruit"]) != sorted(mid["fruit"]):
        return False, "after the reload the fruit is not what it was: %r, %r at the save" % (again["fruit"], mid["fruit"])
    bad = dict((c, {"saved": p, "reloaded": again["scar"].get(c)}) for c, p in mid["scar"].items()
               if not scar_same(again["scar"].get(c), p))
    if bad:
        return False, "after the reload the scar is not what it was: %r" % bad
    return True, "%d fire cells, %d fruit and %d scar cells read the same after the reload" % (
        len(mid["fires"]), len(mid["fruit"]), len(mid["scar"]))


def our_errors(lines):
    """Pure. drain_log lines -> the error and exception lines that name Pyrelands; other mods' errors are theirs."""
    out = []
    for m in lines or []:
        if str(m.get("type") or m.get("level") or "").lower() in ("error", "exception") \
                and any(w in str(m.get("text", "")) + str(m.get("stackTrace") or "") for w in OURS):
            out.append(str(m.get("text", ""))[:200])
    return out


def full_list_missing(running, want):
    """Pure. (running ids, the full list's ids) -> (share present, missing ids); (None, []) when a list was not read."""
    if not running or not want:
        return None, []
    have = set(str(x).lower() for x in running)
    missing = [x for x in want if x.lower() not in have]
    return 1.0 - float(len(missing)) / len(want), missing


def full_list_ids(path=FULL_LIST):
    return [li.text.strip().lower() for li in ET.parse(path).getroot().find("activeMods") if li.text]


def smoke_verdict(rows, errors, front_walks, share):
    """Pure. Hourly {hour, fires, cx, cz} rows, our error lines, validation.front_walks, and the share of his full list that
    runs -> (ok, why). An error of ours FAILS whatever the rest reads (a forbidden effect)."""
    if errors:
        return False, "the log holds %d error line(s) that name Pyrelands: %r" % (len(errors), errors[:2])
    if share is None:
        return None, "the running mod list was not read"
    if share < FULL_SHARE:
        return None, "the running load holds %.0f%% of his full list" % (100 * share)
    if len(rows) < SMOKE_HOURS:
        return None, "%d of %d hourly reads" % (len(rows), SMOKE_HOURS)
    return front_walks(rows)


def register(suite, V):
    """Adds the two chains to the Pyrelands suite. V is validation.py's namespace (its helpers and constants)."""

    def cells_of(t, defName, rect):
        cells, unplaced = V.fire_cells(V._things(t, defName, V._rs(rect), limit=2000))
        if unplaced:
            V._unmeasured(t, "list_things gave %d %s row(s) with no cell" % (len(unplaced), defName))
        return [tuple(c) for c in cells]

    def burn_state(t, rect, scar_cells):
        if not V._live(t):
            return {}
        return {"fires": cells_of(t, "Fire", rect), "fruit": cells_of(t, V.FRUIT_PLANT, rect),
                "scar": dict((c, scar_part(V._probe(t, *c))) for c in scar_cells)}

    @suite.chain("reload_keeps_the_burn")
    @V._teardown(fire=True, weather=True)
    def reload_keeps_the_burn(t):
        V._pad(t, V.PAD_FIRE_BORN)
        t.clear_area(size=V.TEST_SIZE)
        x, z, w, h = V._rect(t)
        half = (w - 4) // 2
        scar, gap, front = (x, z, half, h), (x + half, z, 4, h), (x + half + 4, z, half, h)
        scar_cells = [(x + 2 + 2 * i, z + h // 2) for i in range(3)]
        with V._wildlife_shield(t), V._comp(t, "reload_keeps_the_burn"):
            plant = os.environ.get(PLANT_RELOAD_ENV) or ""
            if plant:
                V._note(t, "PLANTED FAULT", "%s=%s" % (PLANT_RELOAD_ENV, plant))
            t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
            V._extinguish(t)
            V._clear_scorchfruit(t)
            V._firebreak(t, (x, z, w, h))
            V._soil(t, (x, z, w, h))
            t.bridge_call("jawa/set_terrain", x=gap[0], z=gap[1], terrainDef=V.FIREBREAK, width=gap[2], height=gap[3], layer="top")
            t.bridge_call("jawa/set_plants", ops="CLEAR:%s" % V._rs(gap))
            V._plants(t, "RM_FE_Plant_EmberGrass", front)
            V._plants(t, "RM_FE_Plant_EmberGrass", scar)
            t.bridge_call("rimworld/save_game", saveName=RELOAD_SAVE + "_pre")
            V._fire(t, scar)
            V._wait(t, RELOAD_BURN_TICKS)
            V._extinguish(t)
            V._plants(t, V.FRUIT_PLANT, (x + 2, z + 2, 3, 1))
            V._plants(t, "RM_FE_Plant_EmberGrass", front)
            V._fire(t, (front[0], front[1] + h // 2 - 2, 2, 4))
            V._wait(t, RELOAD_FRONT_TICKS)
            t.bridge_call("rimworld/save_game", saveName=RELOAD_SAVE + "_mid")
            mid = burn_state(t, (x, z, w, h), scar_cells)
            t.screenshot(rect=(x, z, w, h))
            V._load_site_save(t, RELOAD_SAVE + ("_pre" if plant == "old_save" else "_mid"))
            if plant == "front_lost":
                V._extinguish(t)
            again = burn_state(t, (x, z, w, h), scar_cells)
            V._load_site_save(t, RELOAD_SAVE + "_pre")
            pre = burn_state(t, (x, z, w, h), scar_cells)
            if V._live(t):
                ok, why = reload_verdict(pre, mid, again)
                V._note(t, "the pad before any fire, at the save and after its reload",
                        {"pre": repr(pre), "mid": repr(mid), "again": repr(again), "why": why})
                if ok is None:
                    V._unmeasured(t, why)
                if not ok:
                    V._fail(why)

    @suite.chain("full_list_smoke")
    @V._teardown(fire=True, weather=True)
    def full_list_smoke(t):
        V._pad(t, V.PAD_FIRE_BORN)
        t.clear_area(size=V.TEST_SIZE)
        x, z, w, h = V._rect(t)
        V._walk_steady_colonists(t)   # SITE (visit 8): a colonist's generated ailment from another mod downed him in the walk
        with V._walk_shield(t), V._comp(t, "full_list_one_front_walks_clean_log"):
            plant = os.environ.get(PLANT_SMOKE_ENV) or ""
            if plant:
                V._note(t, "PLANTED FAULT", "%s=%s" % (PLANT_SMOKE_ENV, plant))
            r = t.bridge_call("jawa/running_mods", details=False, assembly="")
            share, missing = None, []
            if V._live(t):
                import live_def_check  # noqa: E402 - on sys.path via the modcheck package
                share, missing = full_list_missing(live_def_check.running_ids(r), full_list_ids())
            info = t.bridge_call("jawa/map_info") or {}
            if V._live(t) and info.get("mapBiome") != "RM_Pyrelands":
                V._unmeasured(t, "the current map is %r, not RM_Pyrelands" % info.get("mapBiome"))
            if V._live(t) and (share is None or share < FULL_SHARE):
                V._unmeasured(t, "not his full list: %r of it runs, missing %r" % (share, missing[:5]))
            mark = V._log_mark(t)
            t.bridge_call("jawa/weather_set", weather="Clear", lockWeather=True)
            V._extinguish(t)
            # SITE (visit 8, 2026-11-24): the pad was never-burned soil, where vanilla keeps a fire 7,500 ticks after its grass is
            # gone (Fire.TryBurnFloor); every fire of the 3 hours still burned, so the centre moved half the front's way
            t.bridge_call("jawa/set_terrain", x=x, z=z, terrainDef=DEEP_ASH, width=w, height=h, layer="top")
            V._plants(t, "RM_FE_Plant_EmberGrass", (x, z, w, h))
            V._fire(t, (x, z + h // 2 - 3, 2, 6))
            rows = []
            if plant == "log_error" and V._live(t):
                t.bridge_call("jawa/static_call", type="Verse.Log", method="Error", args="[RimMandrake.Pyrelands] planted fault")
            for hour in range(1, SMOKE_HOURS + 1):
                V._wait(t, HOUR)
                if plant == "no_front":
                    V._extinguish(t)
                cells = V._r6_fires(t)
                n = len(cells) or 1
                rows.append({"hour": hour, "fires": len(cells), "cx": sum(c[0] for c in cells) / float(n),
                             "cz": sum(c[1] for c in cells) / float(n)})
            t.screenshot(rect=(x, z, w, h))
            lines = V._log_since(t, mark)
            if V._live(t):
                errs = our_errors(lines)
                ok, why = smoke_verdict(rows, errs, V.front_walks, share)
                V._note(t, "one front over %d h on his full list" % SMOKE_HOURS,
                        {"rows": rows, "ourErrors": errs, "logLines": len(lines), "fullListShare": share, "why": why})
                if ok is None:
                    V._unmeasured(t, why)
                if not ok:
                    V._fail(why)
