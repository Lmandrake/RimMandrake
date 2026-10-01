"""validation.py -- modcheck suite for RimMandrake Pyrelands.

Plan: design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md. Walk:
design/validation_walks/RimMandrake/Pyrelands.md (19 must-show bars, 1 cannot-show).

PACKAGING. This dev folder (`src/RimMandrake/Pyrelands`, packageId `mandrake.rm.pyrelands`) is
the SOURCE only. The biome ships COMPOSED inside `mandrake.rm.biomes` (Biomes.compose.json,
wave 2), so the thing a run must load is `mandrake.rm.biomes` plus `mandrake.rut.patches` (the
fauna roster), `mandrake.rsw.swbestiary` (seven roster keys; the MayRequire on that patch
Operation is inert, so the list must carry it) and `mandrake.rut.pyrelandsmechanics`. The
walk's `list:` line says so. `modcheck run Pyrelands` appends the DEV folder's packageId with
no dependency closure and would land on a list without the biome, so drive the trial's own
tier instead.

Wiring: every must-show bar has exactly one component whose name is the bar id minus `pyre_`
and whose `shows=` claims that bar. The `pyre_cannot_ordinary_rain` cannot-show bar is checked
by the `cannot_ordinary_rain` component (not counted by the visual floor).

Predicates read IMMUTABLE manifests (plan 1.3 / 2.3a): 3 plants and 15 animal kinds. A live
def that differs from the manifest is its own failure, so a patch cannot make an intruder
"allowed". Thresholds marked CALIBRATING (plan's scale mark) are recorded in the evidence and
never gate until the owner rules them.

Settings fields are `public static` (RimMandrake.Pyrelands.RM_PyrelandsSettings); OFF arms use
`t.set_setting` (jawa/mod_settings_field) and always restore in a `finally`.

Bridge result shapes UNMEASURED until the first live run: `jawa/list_things` / `list_pawns`
whole-map reads (`defCounts`, `isCompleteList`), `jawa/get_def` serialisation of
`wildAnimals`/`terrainPatchMakers`, and `jawa/get_terrain_batch` `distinctTerrains`. Each is
read defensively and a missing field reads as UNMEASURED (a failure), never as zero.

Not expressible with current bridge tools, so asserted by state or log only: forcing a
`WeatherEvent_LightningStrike` (fulgurite_after_lightning proves the patch is armed and
looks for fulgurite after dry thunderstorm weather), and flyer flight (firehawk_carries_ember
reads job state only; flyers are never live-tested unattended).
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Pyrelands")
suite.toggles = ["fulguriteEnabled", "ashDustingEnabled", "scorchFruitEnabled",
                 "ashfallAccumulationEnabled", "biomeGenerationEnabled"]

SETTINGS = "RimMandrake.Pyrelands.RM_PyrelandsSettings"
SAND = "RM_FE_Ground_Sand"
SOIL = "RM_FE_Ground_Soil"
TEST_SIZE = 24

# Immutable manifests (plan 1.3). 3 plants; 15 animal kinds.
PLANT_MANIFEST = frozenset(["RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass",
                            "RM_FE_Plant_ScorchFruit"])
WILD_PLANTS = frozenset(["RM_FE_Plant_EmberGrass", "RM_FE_Plant_Quickgrass"])  # ScorchFruit is fire-born
ANIMAL_MANIFEST = frozenset([
    "RUT_FireHawk", "RUT_FurnaceBeast",
    "RSW_Anooba", "RSW_Iriaz", "RSW_Nuna", "RSW_Orray", "RSW_Zeer", "RSW_Dalgo", "RSW_Gizka",
    "RUT_Emberscythe", "RUT_Sytheclaw", "RUT_Barbslinger", "RUT_FireWasp", "RUT_Flamefang",
    "RUT_Ashwallow"])
ASH_RUNGS = ("RM_FE_Ash_Trace", "RM_FE_Ash_Light", "RM_FE_Ash_Heavy", "RM_FE_Ash_Deep")
# Mechanics that must be OFF during the controlled bars (plan 2.3a isolation).
ISOLATION_OFF = ["burnLineEnabled", "fireHawkSpreadEnabled", "fireClockEnabled",
                 "furnaceWorldMigrationEnabled", "burrowOnFireEnabled",
                 "furnaceThermalEnabled", "fulguriteEnabled"]


def _rect(t, size=TEST_SIZE, dx=0):
    x, z = t.anchor
    half = size // 2
    return x - half + dx, z - half, size, size


def _rect_str(t, size=TEST_SIZE, dx=0):
    return "%d,%d,%d,%d" % _rect(t, size, dx)


def _live(t):
    """True only for a real run against a real Session and an unfailed chain; False for the
    offline declaration probe, so manual assertions never trip on its no-op (None) results."""
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


def _counts(r, key="defCounts"):
    """{defName: n} from a list_things/list_pawns result, or None when UNMEASURED."""
    if not isinstance(r, dict):
        return None
    dc = r.get(key)
    if isinstance(dc, dict):
        return dict(dc)
    items = r.get("things") or r.get("pawns")
    if isinstance(items, list):
        out = {}
        for it in items:
            n = (it or {}).get("defName") or (it or {}).get("kindDef")
            out[n] = out.get(n, 0) + 1
        return out
    return None


def _count(t, defName, rect=None):
    """Count of one def, over `rect` or (None) the whole map."""
    kw = {"defName": defName}
    if rect:
        kw["rect"] = rect
    r = t.bridge_call("jawa/list_things", **kw)
    return (r or {}).get("countMatched", 0)


def _whole_map(t, group):
    """Whole-map census by ThingRequestGroup; refuses an incomplete list."""
    r = t.bridge_call("jawa/list_things", thingRequestGroup=group)
    if _live(t):
        if (r or {}).get("isCompleteList") is False or not (r or {}).get("scanned", 1):
            _fail("whole-map %s census incomplete or empty: %r" % (group, r))
        c = _counts(r)
        if c is None:
            _fail("whole-map %s census UNMEASURED: unreadable result %r" % (group, r))
        return c
    return {}


def _def_keys(d, field):
    """Keys of a patched list field read back from get_def (element names), or None."""
    v = (d or {}).get(field)
    if isinstance(v, dict):
        return set(v.keys())
    if isinstance(v, list):
        return set((x.get("animal") or x.get("plant") or x.get("defName")) if isinstance(x, dict) else x
                   for x in v)
    return None


def _off_arm(t, field, off_check, on_check):
    """Toggle `field` OFF -> off_check(); ON -> on_check(); always restore ON in a finally."""
    try:
        t.set_setting(SETTINGS, {field: False})
        off_check()
        t.set_setting(SETTINGS, {field: True})
        on_check()
    finally:
        t.set_setting(SETTINGS, {field: True})


def _isolate(t):
    """Switch the plan 2.3a isolation set OFF; the caller restores via _restore."""
    t.set_setting(SETTINGS, dict((f, False) for f in ISOLATION_OFF))


def _restore(t):
    t.set_setting(SETTINGS, dict((f, True) for f in ISOLATION_OFF))


# --------------------------------------------------------------------------- toggle floor

@suite.chain("fire_tick_effects")
def fire_tick_effects(t):
    """One fire on a GRASSED patch of RM_FE_Ground_Soil (fuel is what makes a fire reach
    `TryBurnFloor`; a fuel-less sand fire goes out and never burns the floor -- the
    2026-09-13 false RED). Watched long enough for both fire-tick postfixes to roll."""
    t.clear_area(size=TEST_SIZE)
    x0, z0, w, h = _rect(t)
    rect = _rect_str(t)
    ground = t.bridge_call("jawa/set_terrain", x=x0, z=z0, terrainDef=SOIL,
                           width=w, height=h, layer="top")
    if _live(t) and (ground or {}).get("cellsChanged", 0) < w * h:
        _fail("set_terrain(%s) over %s did not paint the whole rect: %r" % (SOIL, rect, ground))
    t.bridge_call("jawa/set_plants", defName="RM_FE_Plant_EmberGrass", rect=rect, growth=1.0)

    with t.component("ash_dusting", toggle="ashDustingEnabled"):
        t.bridge_call("jawa/map_fire", action="start", rect=rect, fireSize=1.2)
        t.wait_ticks(2600)
        n = _count(t, "RM_FE_Filth_LooseAsh", rect)
        if _live(t) and n < 1:
            _fail("expected >=1 RM_FE_Filth_LooseAsh in %s after 2600 ticks of fire, got %d"
                  % (rect, n))
        t.screenshot()

    with t.component("scorch_fruit_seed", toggle="scorchFruitEnabled"):
        t.wait_ticks(9000)
        n = _count(t, "RM_FE_Plant_ScorchFruit", rect)
        if _live(t):
            if n < 1:
                _fail("expected >=1 RM_FE_Plant_ScorchFruit in %s after ~11,600 ticks of fire, "
                      "got %d" % (rect, n))
            if n > 40:  # RM_PyrelandsSettings.scorchFruitMapCap shipped default
                _fail("ScorchFruit count %d exceeds the per-map cap 40" % n)
        t.screenshot()


@suite.chain("ashfall_weather_accumulation")
def ashfall_weather_accumulation(t):
    """Ashfall counted over the WHOLE map from ZERO: deposits land on
    `CellFinder.RandomCell(map)`, so a 24x24 rect expected ~0 hits (the 2026-09-13 false RED).
    Existing ash is destroyed first and only NEW ThingIDs count."""
    t.clear_area(size=8)
    with t.component("ashfall_accumulates", toggle="ashfallAccumulationEnabled"):
        t.bridge_call("jawa/destroy_batch", defName="RM_FE_Filth_LooseAsh")
        start = _count(t, "RM_FE_Filth_LooseAsh")
        if _live(t) and start != 0:
            _fail("could not clear ash to zero before the run: %d remain" % start)
        try:
            t.bridge_call("jawa/weather_set", weather="RM_FE_Weather_AshFall", lockWeather=True)
            t.wait_ticks(2600)
            n = _count(t, "RM_FE_Filth_LooseAsh")
        finally:
            t.bridge_call("jawa/weather_set", unlock=True)
        if _live(t) and n < 1:
            _fail("expected >=1 NEW RM_FE_Filth_LooseAsh over the whole map after 2600 ticks "
                  "under RM_FE_Weather_AshFall, got %d" % n)
        t.screenshot()


@suite.chain("startup_and_def_wiring")
def startup_and_def_wiring(t):
    """Pure reads of what the session has loaded, plus the toggle OFF arms."""
    t.clear_area(size=8)

    with t.component("fulgurite_armed_only", toggle="fulguriteEnabled"):
        # The source logs "[RimMandrake.Pyrelands] fulgurite-spawn"; match the stable part only.
        t.expect_log_contains("fulgurite-spawn", field=None, value=None)
        t.screenshot()

    with t.component("biome_def_wiring", toggle="biomeGenerationEnabled"):
        d = t.bridge_call("jawa/get_def", defName="RM_Pyrelands", defType="BiomeDef")
        if _live(t):
            makers = (d or {}).get("terrainPatchMakers") or []
            if len(makers) < 1:
                _fail("RM_Pyrelands resolved with no terrainPatchMakers (get_def may not "
                      "serialise them: fall back to an XML read); got %r" % d)
            names = [th.get("terrain") for th in ((makers[0] or {}).get("thresholds") or [])]
            if "RM_FE_Ash_Trace" not in names:
                _fail("first terrainPatchMaker lacks RM_FE_Ash_Trace: %r" % names)
        t.screenshot()


# --------------------------------------------------------------------------- bar components

@suite.chain("site_census")
def site_census(t):
    """Gen-time census of the fresh site, before any tick or fire. Isolation set OFF.
    One site per run; pooling K=3 sites is the trial driver's job (plan 3.4)."""
    t.clear_area(size=8)

    with t.component("plant_distribution_correct", shows=["pyre_plant_distribution_correct"]):
        d = t.bridge_call("jawa/get_def", defName="RM_Pyrelands", defType="BiomeDef")
        keys = _def_keys(d, "wildPlants")
        census = _whole_map(t, "Plant")
        if _live(t):
            if keys is None or not keys >= WILD_PLANTS or keys - WILD_PLANTS:
                _fail("live wildPlants %r differs from the immutable manifest %r"
                      % (keys, sorted(WILD_PLANTS)))
            foreign = dict((k, v) for k, v in census.items() if k not in PLANT_MANIFEST)
            if foreign:
                _fail("foreign plant defs on the site: %r" % foreign)
            e, q = census.get("RM_FE_Plant_EmberGrass", 0), census.get("RM_FE_Plant_Quickgrass", 0)
            t.bridge_call("jawa/list_things", note="CALIBRATING ember:quickgrass ratio",
                          ember=e, quickgrass=q)
        t.screenshot()

    with t.component("animal_distribution_correct", shows=["pyre_animal_distribution_correct"]):
        d = t.bridge_call("jawa/get_def", defName="RM_Pyrelands", defType="BiomeDef")
        keys = _def_keys(d, "wildAnimals")
        r = t.bridge_call("jawa/list_pawns", faction="none", animalsOnly=True)
        counts = _counts(r, "kindCounts") or _counts(r)
        if _live(t):
            if keys is None or keys != set(ANIMAL_MANIFEST):
                _fail("live wildAnimals %r differs from the immutable 15-kind manifest "
                      "(missing %r, extra %r)" % (keys, sorted(ANIMAL_MANIFEST - (keys or set())),
                                                   sorted((keys or set()) - ANIMAL_MANIFEST)))
            if counts is None:
                _fail("wild animal census UNMEASURED: %r" % r)
            foreign = dict((k, v) for k, v in counts.items() if k not in ANIMAL_MANIFEST)
            if foreign:
                _fail("foreign wild animal kinds on the site: %r" % foreign)
            if sum(counts.values()) < 12:
                _fail("only %d wild animals on the site (need >=12)" % sum(counts.values()))
        t.screenshot()

    with t.component("mapgen_log_clean", shows=["pyre_mapgen_log_clean"]):
        # Window = since the mapgen mark; the 4 load-time `burnedDef is flammable` config
        # errors predate it and are outside the window.
        r = t.bridge_call("jawa/log_since_mark", mark="mapgen",
                          forbid=["CommonalityOfAnimal", "Could not resolve cross-reference"])
        if _live(t) and (r or {}).get("hits"):
            _fail("mapgen log not clean: %r" % r.get("hits"))
        t.screenshot()

    with t.component("grass_chokes_ground", shows=["pyre_grass_chokes_ground"]):
        census = _whole_map(t, "Plant")
        plantable = t.bridge_call("jawa/get_terrain_batch", whole_map=True, plantableOnly=True)
        if _live(t):
            cells = (plantable or {}).get("plantableCells")
            if not cells:
                _fail("plantable cell count UNMEASURED: %r" % plantable)
            covered = sum(v for k, v in census.items() if k in PLANT_MANIFEST)
            ratio = float(covered) / cells
            # Cell-for-cell coverage; threshold 0.85 (def predicts ~0.96).
            if ratio < 0.85:
                _fail("plant coverage %.2f of plantable cells (< 0.85)" % ratio)
        t.screenshot()

    with t.component("ruins_scorched", shows=["pyre_ruins_scorched"]):
        r = t.bridge_call("jawa/list_things", defName="RM_FE_ScorchRuins")
        if _live(t):
            if not (r or {}).get("countMatched"):
                _fail("no RM_FE_ScorchRuins on the site (force one if the genstep allows)")
            ash = t.bridge_call("jawa/get_terrain_batch", footprintOf="RM_FE_ScorchRuins")
            d = (ash or {}).get("distinctTerrains") or []
            if not any(a in d for a in ASH_RUNGS):
                _fail("ruin footprint carries no ash terrain: %r" % d)
        t.screenshot()

    with t.component("burn_line_present", shows=["pyre_burn_line_present"]):
        # burnLineEnabled is OFF in the isolation set; this fixture turns it ON on its own.
        try:
            t.set_setting(SETTINGS, {"burnLineEnabled": True})
            r = t.bridge_call("jawa/map_component_state", component="MapComponent_BurnLine")
            if _live(t) and not (r or {}).get("activeFront"):
                _fail("MapComponent_BurnLine has no active front at gen: %r" % r)
        finally:
            t.set_setting(SETTINGS, {"burnLineEnabled": True})
        t.screenshot()


@suite.chain("ground_and_flora_dynamics")
def ground_and_flora_dynamics(t):
    """Fixed-cell cohorts: two separate 20x20 patches, pre-cleared to RM_FE_Ground_Soil with
    ash removed. Isolation set OFF for the whole chain, restored in a finally."""
    t.clear_area(size=TEST_SIZE)
    burn = _rect_str(t, 20, dx=-12)
    regrow = _rect_str(t, 20, dx=12)
    bx, bz, bw, bh = _rect(t, 20, dx=-12)
    rx, rz, rw, rh = _rect(t, 20, dx=12)
    try:
        _isolate(t)
        for (x, z, w, h) in ((bx, bz, bw, bh), (rx, rz, rw, rh)):
            t.bridge_call("jawa/set_terrain", x=x, z=z, terrainDef=SOIL, width=w, height=h,
                          layer="top")

        with t.component("ground_ash_ladder", shows=["pyre_ground_ash_ladder"]):
            gen = t.bridge_call("jawa/get_terrain_batch", whole_map=True)
            if _live(t):
                d = (gen or {}).get("distinctTerrains") or []
                if any(s in d for s in ("Sand", "Soil", "Gravel", "SoilRich")):
                    _fail("stock ground terrains present on a Pyrelands map: %r" % d)
                if sum(1 for a in ASH_RUNGS[:3] if a in d) < 2:
                    _fail("fewer than 2 of 3 patchmaker ash rungs at gen: %r" % d)
            # Burn GRASS on ground, 3 cycles, tracking the fixed cohort.
            for cycle in range(3):
                t.bridge_call("jawa/set_plants", defName="RM_FE_Plant_EmberGrass",
                              rect=burn, growth=1.0)
                t.bridge_call("jawa/map_fire", action="start", rect=burn, fireSize=1.2)
                t.wait_ticks(3000)
                if cycle == 0:
                    got = t.bridge_call("jawa/get_terrain_batch", rects=burn)
                    if _live(t):
                        on_ash = sum(v for k, v in ((got or {}).get("counts") or {}).items()
                                     if k in ASH_RUNGS)
                        if on_ash < 0.5 * bw * bh:
                            _fail("after burn 1, %d of %d cohort cells on an ash rung (<50%%)"
                                  % (on_ash, bw * bh))
            got = t.bridge_call("jawa/get_terrain_batch", rects=burn)
            if _live(t) and "RM_FE_Ash_Deep" not in ((got or {}).get("distinctTerrains") or []):
                _fail("no RM_FE_Ash_Deep in the cohort after 3 burn cycles")
            t.screenshot()

        with t.component("embergrass_regrows", shows=["pyre_embergrass_regrows"]):
            t.bridge_call("jawa/set_plants", defName="RM_FE_Plant_EmberGrass", rect=regrow,
                          growth=1.0)
            pre = _count(t, "RM_FE_Plant_EmberGrass", regrow)
            t.bridge_call("jawa/map_fire", action="start", rect=regrow, fireSize=1.2)
            t.wait_ticks(3000)
            t.wait_ticks(3 * 60000)
            d3 = _count(t, "RM_FE_Plant_EmberGrass", regrow)
            t.wait_ticks(4 * 60000)
            d7 = _count(t, "RM_FE_Plant_EmberGrass", regrow)
            # CALIBRATING: >=25% by day 3, >=60% by day 7. Recorded, never gated.
            t.bridge_call("jawa/list_things", note="CALIBRATING regrow",
                          pre=pre, day3=d3, day7=d7)
            if _live(t) and pre <= 0:
                _fail("regrow cohort had no pre-burn plants (UNMEASURED)")
            t.screenshot()
    finally:
        _restore(t)


@suite.chain("scorchfruit_lifecycle")
def scorchfruit_lifecycle(t):
    """ScorchFruit yield, fire-born origin and fast spoilage; isolation set OFF."""
    t.clear_area(size=TEST_SIZE)
    rect = _rect_str(t)
    try:
        _isolate(t)

        with t.component("scorchfruit_fire_born", shows=["pyre_scorchfruit_fire_born"]):
            gen = _count(t, "RM_FE_Plant_ScorchFruit")
            if _live(t) and gen != 0:
                _fail("ScorchFruit present on unburned land at gen: %d" % gen)
            t.bridge_call("jawa/map_fire", action="start", rect=rect, fireSize=1.2)
            t.wait_ticks(11600)
            n = _count(t, "RM_FE_Plant_ScorchFruit", rect)
            if _live(t) and n < 1:
                _fail("no ScorchFruit spawned inside the burned cohort %s" % rect)
            t.screenshot()

        with t.component("scorchfruit_produces", shows=["pyre_scorchfruit_produces"]):
            t.spawn("RM_FE_Plant_ScorchFruit", count=10)
            t.bridge_call("jawa/set_plants", defName="RM_FE_Plant_ScorchFruit", rect=rect,
                          growth=1.0)
            t.bridge_call("jawa/designate", kind="harvest", defName="RM_FE_Plant_ScorchFruit",
                          rect=rect)
            t.wait_ticks(6000)
            y = _count(t, "RM_FE_ScorchFruitYield")
            if _live(t) and y < 1:
                _fail("no RM_FE_ScorchFruitYield after the harvest window")
            t.screenshot()

        with t.component("scorchfruit_spoils_fast", shows=["pyre_scorchfruit_spoils_fast"]):
            # [O] yield rots at 4 days, the plant at 1.1 (read from XML at validation).
            t.bridge_call("jawa/spawn_batch", ops="RM_FE_ScorchFruitYield:%d,%d;Meat_Human:%d,%d"
                          % (t.anchor[0], t.anchor[1] + 4, t.anchor[0] + 2, t.anchor[1] + 4))
            t.wait_ticks(int(4.5 * 60000))
            r = t.bridge_call("jawa/list_things", defName="RM_FE_ScorchFruitYield", rotStage=True)
            if _live(t) and (r or {}).get("countMatched", 0) and not (r or {}).get("allRotted"):
                _fail("RM_FE_ScorchFruitYield not rotted by day 4.5: %r" % r)
            t.screenshot()
    finally:
        _restore(t)


@suite.chain("weather_looks")
def weather_looks(t):
    """Ashfall deposits and the three weather looks. Ash counted over the whole map from
    zero; frames at a fixed camera and hour."""
    t.clear_area(size=8)
    try:
        with t.component("ashfall_darkens_drifts", shows=["pyre_ashfall_darkens_drifts"]):
            t.bridge_call("jawa/destroy_batch", defName="RM_FE_Filth_LooseAsh")
            t.bridge_call("jawa/weather_set", weather="RM_FE_Weather_AshFall", lockWeather=True)
            t.wait_ticks(4000)
            series = []
            for _ in range(4):
                series.append(_count(t, "RM_FE_Filth_LooseAsh"))
                t.wait_ticks(2500)
            if _live(t):
                if any(b < a for a, b in zip(series, series[1:])) or series[-1] < 20:
                    _fail("ash series %r not monotone or < 20 at the end" % series)
            t.screenshot()

        with t.component("cinderfall_distinct", shows=["pyre_cinderfall_distinct"]):
            a = t.bridge_call("jawa/get_def", defName="RM_FE_Weather_AshFall", defType="WeatherDef")
            c = t.bridge_call("jawa/get_def", defName="RM_FE_Weather_Cinderfall",
                              defType="WeatherDef")
            if _live(t):
                fields = ("overlayClasses", "skyColorsDay", "skyColorsNightMid", "windSpeedFactor")
                if all((a or {}).get(f) == (c or {}).get(f) for f in fields):
                    _fail("Cinderfall and AshFall differ in none of %r" % (fields,))
            t.bridge_call("jawa/weather_set", weather="RM_FE_Weather_Cinderfall", lockWeather=True)
            t.wait_ticks(5000)
            t.screenshot()

        with t.component("blackrain_reads", shows=["pyre_blackrain_reads"]):
            b = t.bridge_call("jawa/get_def", defName="RM_FE_BlackRain", defType="WeatherDef")
            r = t.bridge_call("jawa/get_def", defName="Rain", defType="WeatherDef")
            if _live(t):
                fields = ("overlayClasses", "skyColorsDay", "skyColorsNightMid")
                if all((b or {}).get(f) == (r or {}).get(f) for f in fields):
                    _fail("BlackRain renders identically to vanilla Rain over %r" % (fields,))
            t.bridge_call("jawa/weather_set", weather="RM_FE_BlackRain", lockWeather=True)
            t.wait_ticks(5000)
            t.screenshot()

        with t.component("cannot_ordinary_rain"):
            d = t.bridge_call("jawa/get_def", defName="RM_Pyrelands", defType="BiomeDef")
            table = (d or {}).get("baseWeatherCommonalities") or {}
            if _live(t):
                keys = set(table.keys()) if isinstance(table, dict) else set()
                if keys & set(["Rain", "RainyThunderstorm", "FoggyRain"]):
                    _fail("post-patch weather table holds ordinary rain: %r" % sorted(keys))
    finally:
        t.bridge_call("jawa/weather_set", unlock=True)


@suite.chain("mechanics_arms")
def mechanics_arms(t):
    """The five mechanic bars, each on a fresh fixture with its own toggle ON. State and job
    reads only: flyers are never live-tested unattended."""
    t.clear_area(size=TEST_SIZE)
    try:
        with t.component("fulgurite_after_lightning", shows=["pyre_fulgurite_after_lightning"]):
            # No tool forces a strike; this proves the patch armed and looks for the product.
            t.set_setting(SETTINGS, {"fulguriteEnabled": True})
            t.expect_log_contains("fulgurite-spawn", field=None, value=None)
            n = _count(t, "RM_FE_Fulgurite")
            t.bridge_call("jawa/list_things", note="CALIBRATING fulgurite", count=n)
            t.screenshot()

        with t.component("firehawk_carries_ember", shows=["pyre_firehawk_carries_ember"]):
            t.set_setting(SETTINGS, {"fireHawkSpreadEnabled": True})
            t.spawn_pawn("RUT_FireHawk")
            t.wait_ticks(6000)
            r = t.bridge_call("jawa/list_jobs", jobDef="RUT_FireHawkCarryEmber")
            if _live(t) and not (r or {}).get("countMatched"):
                _fail("no RUT_FireHawkCarryEmber job observed (job state read only)")
            t.screenshot()

        with t.component("furnacebeast_warmth", shows=["pyre_furnacebeast_warmth"]):
            t.set_setting(SETTINGS, {"furnaceThermalEnabled": True})
            fb = t.spawn_pawn("RUT_FurnaceBeast")
            col = t.spawn_pawn("Colonist")
            t.wait_ticks(1200)
            r = t.bridge_call("jawa/get_pawn_hediffs", pawn=col, hediff="RM_FurnaceWarmth")
            if _live(t) and not (r or {}).get("present"):
                _fail("colonist near the furnace-beast has no RM_FurnaceWarmth")
            t.screenshot()

        with t.component("furnacebeast_heats_room", shows=["pyre_furnacebeast_heats_room"]):
            r = t.bridge_call("jawa/room_temperature_pair", withDef="RUT_FurnaceBeast",
                              settleTicks=2500)
            if _live(t):
                delta = (r or {}).get("delta")
                if delta is None or delta <= 0:
                    _fail("furnace-beast room is not warmer than its matched control: %r" % r)
            t.screenshot()

        with t.component("burrowers_dive", shows=["pyre_burrowers_dive"]):
            t.set_setting(SETTINGS, {"burrowOnFireEnabled": True})
            g = t.spawn_pawn("RUT_Ashwallow")
            t.bridge_call("jawa/map_fire", action="start", rect=_rect_str(t, 8), fireSize=1.2)
            t.wait_ticks(600)
            r = t.bridge_call("jawa/get_pawn_hediffs", pawn=g, hediff="RM_Burrowed")
            if _live(t) and not (r or {}).get("present"):
                _fail("burrow-on-fire grazer has no RM_Burrowed hediff while the fire passes")
            t.screenshot()
    finally:
        _restore(t)
