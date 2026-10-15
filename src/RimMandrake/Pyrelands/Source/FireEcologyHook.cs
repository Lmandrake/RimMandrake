using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.Pyrelands
{
    // 🔴 THE ONE LIGHT C# HOOK budgeted by FIRE_ECOLOGY_LOOP_1's item spec —
    // "the one light C# hook: strike-spawns-prop." Two postfixes sharing one
    // small spawn helper, not two hooks: the item's own text says "the
    // weather doc's v2 reuses this same hook," so both trigger points
    // (a lightning strike; a fire actively burning) drive the SAME narrow
    // "roll a chance, spawn a prop nearby" shape rather than inventing a
    // second mechanism for scorch-fruit.
    //
    // Everything else in FIRE_ECOLOGY_LOOP_1 (the weather-table strip, Black
    // Rain's trigger, burnedDef to deep ash, the firebreak) is pure XML riding
    // vanilla mechanisms that already exist — see the .xml files' own
    // comments for the RimSage citations. Only "a specific prop appears at a
    // specific cell because a specific event just happened here" has no
    // XML-only route, because neither WeatherEvent_LightningStrike nor
    // Fire.TickInterval exposes an event, signal or XML hook a def can bind.
    [StaticConstructorOnStartup]
    public static class FireEcologyHookMod
    {
        // Both terrain families the doc names as fulgurite-eligible ground:
        // this engine's own scorchable-sand clone, and plain vanilla Sand —
        // a strike on sand off the Pyrelands qualifies too (see IsPyrelandsGround).
        // STILLSAND_GLASS_LENS_CHAIN_1 §10(a): vanilla SoftSand and FlowWorks'
        // RM_DeepSand (the Stillsand's dune ground) join the family.
        private static readonly string[] SandTerrainDefNames =
        {
            "RM_FE_Ground_Sand", "Sand", "SoftSand", "RM_DeepSand",
        };

        // The Pyrelands' own fire-ecology ground. Only strikes here are governed by
        // the Pyrelands master switch; a strike on any other sand needs only the
        // fulgurite toggle (STILLSAND_GLASS_LENS_CHAIN_1 §10(b)).
        internal static bool IsPyrelandsGround(TerrainDef terrain)
        {
            return terrain != null && RM_FireEcoKernel.IsPyrelandsGround(terrain.defName);
        }

        // Shipped defaults for the numbers below now live as tunable fields on
        // RM_PyrelandsSettings (MOD_OPTIONS_RETROFIT_1) — read those at the
        // call sites, not these. Kept only as the historical/default record.
        internal const float FulguriteChancePerStrike = 0.35f;
        internal const float AshDustingChancePerFireTick = 0.02f;
        internal const float ScorchFruitChancePerFireTick = 0.0025f;
        internal const int MinFireSizeForAshDusting = 1; // any live Fire counts — not yet gated on; reserved for a future fire-size check

        static FireEcologyHookMod()
        {
            var h = new Harmony("mandrake.rm.pyrelands");

            Apply(h, AccessTools.Method(typeof(WeatherEvent_LightningStrike), "DoStrike"),
                  typeof(Patch_LightningStrike_Fulgurite), "fulgurite-spawn",
                  "armed; strikes on sand-family ground may leave a fulgurite");

            Apply(h, AccessTools.Method(typeof(Fire), "TickInterval"),
                  typeof(Patch_FireTick_AshAndScorchFruit), "fire-tick-ash-scorchfruit",
                  "armed; burning cells on scorchable ground may dust loose ash "
                  + "and rarely seed a scorch-fruit pod");
        }

        private static void Apply(Harmony h, MethodBase target, Type patchClass,
                                  string rule, string detail)
        {
            if (target == null)
            {
                Log.Error("[RimMandrake.Pyrelands] " + rule + ": TARGET METHOD NOT FOUND — "
                          + "this rule is NOT in effect. A game update renamed it. The other "
                          + "rule in this assembly is unaffected.");
                return;
            }
            try
            {
                h.Patch(target, postfix: new HarmonyMethod(patchClass, "Postfix"));
                Log.Message("[RimMandrake.Pyrelands] " + rule + ": " + detail);
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] " + rule + ": patch FAILED, rule NOT "
                          + "in effect — " + e.Message);
            }
        }

        internal static bool IsSandFamily(TerrainDef terrain)
        {
            return terrain != null && RM_FireEcoKernel.IsSandFamily(terrain.defName, SandTerrainDefNames);
        }

        // Scorchable ground: ANY Pyrelands ground (RM_FE_*, deep ash included,
        // not the firebreak) OR vanilla Soil/Sand/Gravel/SoilRich, so this stays
        // reusable off any biome that opts in via XML wiring.
        internal static bool IsScorchableGround(TerrainDef terrain)
        {
            return terrain != null && RM_FireEcoKernel.IsScorchableGround(terrain.defName);
        }
    }

    // Postfix on the STATIC WeatherEvent_LightningStrike.DoStrike(IntVec3
    // strikeLoc, Map map, ref Mesh boltMesh). `strikeLoc` is reassigned
    // inside the original method (Invalid -> a real cell) before the strike
    // resolves; Harmony's postfix parameter of the same name reads that
    // resolved value, not the caller's original argument — verified against
    // the method body (RimSage) before writing this.
    public static class Patch_LightningStrike_Fulgurite
    {
        public static void Postfix(IntVec3 strikeLoc, Map map)
        {
            try
            {
                if (!RM_PyrelandsSettings.fulguriteEnabled) return;
                if (map == null || !strikeLoc.IsValid || !strikeLoc.InBounds(map)) return;
                TerrainDef terrain = strikeLoc.GetTerrain(map);
                // The master switch governs the Pyrelands' own ground only, so Stillsand
                // fulgurites do not need the Pyrelands on (STILLSAND_GLASS_LENS_CHAIN_1 §10(b)).
                if (!RM_FireEcoKernel.FulguriteMayRoll(true, true, FireEcologyHookMod.IsSandFamily(terrain),
                        PyrelandsMechanicsGate.On, FireEcologyHookMod.IsPyrelandsGround(terrain))) return;
                if (!Rand.Chance(RM_PyrelandsSettings.fulguriteChance)) return;

                ThingDef fulguriteDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Fulgurite");
                if (fulguriteDef == null) return; // mod not loaded / def missing — no-op, not a crash

                Thing fulgurite = ThingMaker.MakeThing(fulguriteDef);
                GenPlace.TryPlaceThing(fulgurite, strikeLoc, map, ThingPlaceMode.Near);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] fulgurite-spawn: " + e.Message, 0x46E01);
            }
        }
    }

    // Postfix on the PROTECTED instance Fire.TickInterval(int delta). Runs
    // once per live Fire thing per tick-interval batch — cheap, low-chance
    // rolls only, never per-frame. `delta` is the batch's tick-interval size
    // (GenTicks.GetCameraUpdateRate: 15 ticks off-screen, 1-5 up close), and
    // Harmony binds our own `delta` parameter to it by name; both chances
    // below are scaled by it so a watched fire and an unwatched fire roll at
    // the same effective per-tick rate instead of the watched one rolling up
    // to 15x more often.
    public static class Patch_FireTick_AshAndScorchFruit
    {
        // Fire thingIDNumbers that already took their one scorch-fruit roll
        // (taken only once a legal spot exists -- see TakeFruitRoll), one set
        // PER MAP, never static: a reload re-issues the same thingIDNumbers,
        // and a static set then blocked every reloaded fire's roll
        // (PYRE_SCORCHFRUIT_DIAGNOSE_FIRE_BEARS_NOTHING, RM_FireEcoKernel.RollSetFor).
        // Never shrunk per-fire (despawn hooks cost more than they save);
        // cleared wholesale when it grows past a bound no live map reaches.
        private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<object, HashSet<int>> rolledFiresByMap =
            new System.Runtime.CompilerServices.ConditionalWeakTable<object, HashSet<int>>();

        // Bound past which rolledFires is cleared wholesale (RM_FireEcoKernel.MarkOnce).
        private const int RolledBound = 100000;

        public static void Postfix(Fire __instance, int delta)
        {
            try
            {
                if (__instance == null) return;
                // Pawn/animal-attached fires (a burning colonist, a boomrat that
                // caught) are not ground fires - skip them entirely, or a lit
                // pawn dusts ash and seeds scorch-fruit along its whole running
                // path (flavor-wrong, and an ignite-a-boomrat exploit for free
                // fruit). BENCH review finding, 2026-09-01.
                Map map = __instance.Map;
                IntVec3 pos = __instance.Position;
                bool usable = __instance.Spawned && map != null && pos.InBounds(map);
                TerrainDef terrain = usable ? pos.GetTerrain(map) : null;
                bool scorchable = FireEcologyHookMod.IsScorchableGround(terrain);
                // The fresh-burn stamp (PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED §4): this cell burned now. Its own toggle, independent
                // of dusting and fruit. The gate is any Pyrelands ground, deep ash included (RM_FireEcoKernel.IsScorchableGround).
                if (RM_FireEcoKernel.BurnStampMay(PyrelandsMechanicsGate.On, RM_PyrelandsSettings.freshBurnBonusEnabled, usable,
                        __instance.parent != null, scorchable))
                {
                    MapComponent_PyrelandsAshField.For(map)?.StampBurn(pos, Find.TickManager.TicksGame);
                }
                if (!RM_FireEcoKernel.FireTickMayRoll(PyrelandsMechanicsGate.On, RM_PyrelandsSettings.ashDustingEnabled,
                        RM_PyrelandsSettings.scorchFruitEnabled, usable, __instance.parent != null, scorchable)) return;

                // Loose ash dusting — rides alongside vanilla's own
                // unconditional Filth_Ash spawn (DamageWorker_Flame), does
                // not replace it.
                if (RM_PyrelandsSettings.ashDustingEnabled)
                {
                    ThingDef ashFilth = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Filth_LooseAsh");
                    if (ashFilth != null && Rand.Chance(RM_FireEcoKernel.DustChance(RM_PyrelandsSettings.ashDustingChance, delta)))
                    {
                        FilthMaker.TryMakeFilth(pos, map, ashFilth);
                    }
                }

                // Scorch-fruit — rare, and only ever appears this way (never
                // in a biome's ordinary wildPlants list). Plain 3x3 scan
                // instead of a GenAdj/LINQ combinator: fewer ways to get the
                // overload wrong. It runs each interval only until the fire has
                // rolled (a set lookup gates it), i.e. while its grass burns.
                //
                // ONE roll per Fire instance (a Fire thing sits on one cell),
                // not per tick: the old per-tick chance compounded over a
                // fire's lifetime, so every long-burning cell fruited and a
                // map-wide burn seeded an orchard. Owner, 2026-09-16: "the
                // fires generate way too many scorch fruits ... perhaps one
                // in twenty squares" — scorchFruitChance is now that
                // per-burned-cell probability, default 0.05.
                //
                // The roll waits for a legal spot (SCORCH_FRUIT_FIX_ROLLS_BEFORE_
                // THE_ASHES, 2026-10-12): rolled on the fire's first interval, the
                // grass it is about to burn still stood in its cell and all eight
                // neighbours, so the roll was spent with nowhere to land and a fully
                // grassed burn grew 0 fruit. Now the fire takes its roll the first
                // interval its own cell (scanned first) or a neighbour is bare --
                // i.e. once its plant has burned away -- still one roll per fire.
                HashSet<int> rolledFires = RM_PyrelandsSettings.scorchFruitEnabled ? RM_FireEcoKernel.RollSetFor(rolledFiresByMap, map) : null;
                if (rolledFires != null && !rolledFires.Contains(__instance.thingIDNumber))
                {
                    int spotIndex = RM_FireEcoKernel.TakeFruitRoll(rolledFires, __instance.thingIDNumber, RolledBound,
                        (dx, dz) =>
                        {
                            IntVec3 c = pos + new IntVec3(dx, 0, dz);
                            return c.InBounds(map) && c.Standable(map) && c.GetPlant(map) == null;
                        });
                    if (spotIndex >= 0 && Rand.Chance(RM_PyrelandsSettings.scorchFruitChance))
                    {
                        ThingDef fruitDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_ScorchFruit");
                        // A map-wide burn runs hundreds of concurrent Fire things;
                        // uncapped this seeds an orchard, not a harvest. BENCH
                        // review finding, 2026-09-01.
                        if (fruitDef != null && RM_FireEcoKernel.UnderFruitCap(map.listerThings.ThingsOfDef(fruitDef).Count, RM_PyrelandsSettings.scorchFruitMapCap))
                        {
                            IntVec3 spot = pos + new IntVec3(RM_FireEcoKernel.FruitSpotDx[spotIndex], 0, RM_FireEcoKernel.FruitSpotDz[spotIndex]);
                            Thing fruit = ThingMaker.MakeThing(fruitDef);
                            GenSpawn.Spawn(fruit, spot, map);
                        }
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] fire-tick-ash-scorchfruit: "
                                + e.Message, 0x46E02);
            }
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // BIOME PLACEMENT — the second thing in this mod that XML cannot do.
    //
    // BiomeDef has NO temperature, rainfall or elevation field. RimWorld
    // assigns a tile's biome by asking every BiomeDef's `workerClass` for
    // a score and keeping the highest (RimSage,
    // RimWorld/Planet/WorldGenStep_Terrain.cs:288 BiomeFrom), so a biome
    // with no C# worker simply never generates anywhere. This is that
    // worker, and it is the ONLY route.
    //
    // The numbers themselves stay in XML so they can be retuned without a
    // rebuild — see the <modExtensions> block on RM_Pyrelands in
    // Defs/BiomeDefs/Pyrelands.xml.
    // ════════════════════════════════════════════════════════════════════

    // TRIGGERED BY: the <modExtensions><li Class="...PyrelandsBiomeRanges">
    // block on a BiomeDef. Absent, the defaults below apply unchanged.
    public class PyrelandsBiomeRanges : DefModExtension
    {
        public FloatRange temperature = new FloatRange(25f, 60f);
        public FloatRange rainfall = new FloatRange(550f, 1000f);
        public FloatRange elevation = new FloatRange(0f, 2200f);
        public float baseScore = 30f;
        public float degreeWeight = 2.6f;
        public float rainfallDivisor = 120f;
    }

    // TRIGGERED BY: <workerClass> on the RM_Pyrelands BiomeDef.
    //
    // Scored against vanilla's own BiomeWorker_AridShrubland, which owns
    // this rainfall corridor today (22.5 + (T-20)*2.2 + (R-600)/100).
    // ⚠️ CODE REVIEW CORRECTION, 2026-09-09: with the shipped numbers
    // (baseScore=30) the crossover is NOT near 25 degC — it works out to
    // T≈32.5-34.4 degC across this band's 550-1000mm rainfall span (see
    // the worked-through arithmetic in Pyrelands.xml's modExtension
    // comment). Tiles between the 25 degC floor and ~33 degC stay arid
    // shrubland regardless of rainfall; outside 550-1000mm rainfall this
    // worker returns 0 and never competes at all.
    public class BiomeWorker_Pyrelands : BiomeWorker
    {
        private static readonly PyrelandsBiomeRanges FallbackRanges = new PyrelandsBiomeRanges();

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            // WORLDGEN-AFFECTING toggle: off means this biome never wins tile
            // placement on a newly generated world. An already-generated
            // planet is untouched — this only ever runs during generation.
            PyrelandsBiomeRanges r = biome.GetModExtension<PyrelandsBiomeRanges>() ?? FallbackRanges;

            // Rainfall is half-open, matching vanilla's own workers exactly so the band edges butt up against theirs with no
            // overlap; grass savanna, not highland (the exclusion BiomeWorker_Grasslands makes).
            return RM_FireEcoKernel.BiomeScore(RM_PyrelandsSettings.biomeGenerationEnabled, tile != null, tile != null && tile.WaterCovered,
                tile != null ? tile.temperature : 0f, tile != null ? tile.rainfall : 0f, tile != null ? tile.elevation : 0f,
                tile != null && (tile.hilliness == Hilliness.Mountainous || tile.hilliness == Hilliness.Impassable),
                r.temperature.min, r.temperature.max, r.rainfall.min, r.rainfall.max, r.elevation.min, r.elevation.max,
                r.baseScore, r.degreeWeight, r.rainfallDivisor);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // ASH ACCUMULATION DURING ASH FALL — the third thing XML cannot do.
    //
    // TRIGGERED BY: WeatherDef RM_FE_Weather_AshFall (and, at under half
    // the rate, RM_FE_Weather_Cinderfall) being the map's current weather.
    //
    // WHY NOT `snowRate`. That is the vanilla field for "falling weather
    // that piles up", and it piles into map.snowGrid: white, drawn white,
    // and melted the instant outdoor temperature is above freezing
    // (RimSage, SteadyEnvironmentEffects.cs:96 AddFallenSnowAt). This
    // biome's placement band starts at 25 degC, so snowRate would deposit
    // nothing at all, and would look like snow if it did. `sandRate` is
    // Odyssey-gated (SteadyEnvironmentEffects.cs:101 checks
    // ModsConfig.OdysseyActive) and deposits sand, not ash.
    //
    // So the drifts are laid as RM_FE_Filth_LooseAsh — the SAME filth the
    // fire-tick hook above already drops, deliberately: a bank left by
    // weather and a bank left by a fire are one thing, they thicken into
    // each other, and both are washed off by RM_FE_BlackRain through
    // vanilla's own rainWashes handling. No new grid, no new save data.
    // ════════════════════════════════════════════════════════════════════
    public class MapComponent_PyrelandsAshfall : MapComponent
    {
        // A batch every 250 ticks (~4 per in-game hour) rather than a
        // per-tick roll: this component exists on EVERY map in every save,
        // including ones with no Pyrelands anywhere, so the not-my-weather
        // path has to be nearly free.
        private const int CheckIntervalTicks = 250;

        // One deposit attempt per this many map cells per batch. A 250x250
        // map (62,500 cells) gets ~15 per batch, ~60 per in-game hour —
        // visible drifts over an afternoon, not a filth explosion.
        private const float CellsPerDepositAttempt = 4000f;

        private const float CinderfallRateFactor = 0.45f;

        private static ThingDef ashFilthDef;
        private static WeatherDef ashFallWeather;
        private static WeatherDef cinderfallWeather;
        private static bool defsResolved;

        public MapComponent_PyrelandsAshfall(Map map)
            : base(map)
        {
        }

        private static void ResolveDefs()
        {
            defsResolved = true;
            ashFilthDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Filth_LooseAsh");
            ashFallWeather = DefDatabase<WeatherDef>.GetNamedSilentFail("RM_FE_Weather_AshFall");
            cinderfallWeather = DefDatabase<WeatherDef>.GetNamedSilentFail("RM_FE_Weather_Cinderfall");
        }

        public override void MapComponentTick()
        {
            if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.ashfallAccumulationEnabled)
            {
                return;
            }
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }
            if (!defsResolved)
            {
                ResolveDefs();
            }
            if (ashFilthDef == null)
            {
                return;
            }

            WeatherManager wm = map.weatherManager;
            WeatherDef current = (wm != null) ? wm.curWeather : null;

            bool isNativeBiome = map.Biome != null && map.Biome.defName == "RM_Pyrelands";

            // Cross-biome opt-in (MOD_OPTIONS_RETROFIT_1 §6a): an opted-in non-Pyrelands biome gets ambient ash drift regardless
            // of its own current weather, scaled by crossBiomeCoverage. Off by default; never fires unless the owner names this
            // biome or ticks "every biome". A rate of zero (coverage slider at 0) deposits nothing.
            float rate = RM_FireEcoKernel.AshRate(current != null && current == ashFallWeather, current != null && current == cinderfallWeather,
                CinderfallRateFactor, isNativeBiome, !isNativeBiome && RM_PyrelandsSettings.AppliesToBiome(map.Biome),
                RM_PyrelandsSettings.crossBiomeCoverage, RM_PyrelandsSettings.ashfallRateMultiplier);
            if (rate < 0f)
            {
                return;
            }

            int attempts = RM_FireEcoKernel.AshAttempts(map.Area, CellsPerDepositAttempt, rate);

            try
            {
                for (int i = 0; i < attempts; i++)
                {
                    IntVec3 c = CellFinder.RandomCell(map);
                    // Under a roof the ash never lands; on water it sinks.
                    // FilthMaker itself rejects unwalkable cells, and
                    // shouldPropagate:false stops it hunting an 8-way
                    // neighbour every time it hits a wall.
                    if (map.roofGrid.Roofed(c) || c.GetTerrain(map).IsWater)
                    {
                        continue;
                    }
                    FilthMaker.TryMakeFilth(c, map, ashFilthDef, 1, FilthSourceFlags.None, false);
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] ashfall-accumulation: "
                                + e.Message, 0x46E03);
            }
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // SCORCHED RUINS (PYRELANDS_SCORCHED_RUINS_1) — the fourth thing XML
    // cannot do: react to WHERE another genstep just built something.
    //
    // TRIGGERED BY: <extraGenSteps><li>RM_FE_ScorchRuins</li></extraGenSteps>
    // on RM_Pyrelands (Defs/BiomeDefs/Pyrelands.xml). BiomeDef.extraGenSteps
    // is concatenated into a map's genstep list ONLY when that map's biome IS
    // RM_Pyrelands (RimSage, Verse/MapGenerator.cs:163 —
    // `map.Biome.extraGenSteps.Where(IsValidBiome)`), so this genstep never
    // runs, and needs no internal biome check, on any other biome's map.
    //
    // The paired GenStepDef (Defs/GenStepDefs/PyrelandsGenSteps.xml) sets
    // order=760 — right after ScatterRuinsSimple's order=750 (RimSage) and
    // well before Plants' order=900 — so the scorched ground is already in
    // place before wild plants roll what grows on it.
    //
    // GenStep_ScatterRuinsSimple.ScatterAt records every ruin's footprint into
    // MapGenerator.UsedRects (RimSage, Verse/MapGenerator.cs:58/GenStep_
    // ScatterRuinsSimple.cs ScatterAt) before this step runs. Mutator-placed
    // ancient structures (MutatorCriticalStructures, order=500) land in the
    // same UsedRects list, so those get scorched too — consistent with the
    // owner's brief ("ruins should be scorched and burned to warn the player
    // of what happens here"), not scoped narrowly to GenStep_ScatterRuinsSimple
    // alone.
    //
    // No new art: the burn reads through terrain and filth defs this mod
    // already ships (AshField.xml's RM_FE_Ash_Deep, Filth_LooseAsh.xml) —
    // deep ash on the footprint and its rim (PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED
    // retired the light/heavy rungs; most cells are deep ash already, so the
    // loose-ash filth, denser on the footprint, is the visible scorch).
    // ════════════════════════════════════════════════════════════════════
    //
    // LATE SWEEP (PYRE_RUINS_DIAGNOSE_JUNKYARD_STAYS_PRISTINE, 2026-10-12). The
    // UsedRects pass above misses most of what a player reads as ruins (RimSage,
    // Defs/Core/MapGeneration/CommonMapGenerator.xml + Defs/Ideology/MapGeneration/
    // CommonMapGenerator.xml): AncientJunkClusters, ScatterRoadDebris,
    // ScatterCaveDebris, MechanoidRemains, AncientFences and the other Ideology
    // scatters run at order 960, AFTER 760, and GenStep_ScatterGroup never adds a
    // used rect; GenStep_ScatterAncientUtilityBuilding (750) checks UsedRects but
    // never adds its own. So a second GenStepDef (RM_FE_ScorchRuinsLate, order
    // 965, after every 960 scatter) runs this class with sweepUnownedBuildings
    // set: every unowned artificial building's footprint and a one-cell rim go to
    // deep ash with loose-ash filth, whichever genstep placed it.
    public class GenStep_ScorchPyrelandsRuins : GenStep
    {
        // XML-set: false = the UsedRects pass (order 760), true = the late sweep.
        public bool sweepUnownedBuildings;

        // Rim width around a swept building's occupied rect (the bar samples a 3x3 at its root cell).
        private const int SweepRim = 1;

        public override int SeedPart => sweepUnownedBuildings ? 1993482202 : 1993482201;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.scorchedRuinsEnabled) return;
            if (sweepUnownedBuildings)
            {
                SweepUnownedBuildings(map);
                return;
            }
            if (!MapGenerator.TryGetVar<List<CellRect>>("UsedRects", out var usedRects)
                || usedRects.NullOrEmpty())
            {
                return; // no ruin (or other used-rect structure) placed on this map — nothing to scorch
            }

            ThingDef ashFilth = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Filth_LooseAsh");
            TerrainDef ashDeep = DefDatabase<TerrainDef>.GetNamedSilentFail(RM_FireEcoKernel.DeepAshDefName);
            if (ashDeep == null && ashFilth == null)
            {
                return; // defs not loaded — no-op, not a crash
            }

            try
            {
                foreach (CellRect rect in usedRects)
                {
                    CellRect clipped = rect.ClipInsideMap(map);
                    foreach (IntVec3 c in clipped.Cells)
                    {
                        if (!c.InBounds(map)) continue;

                        bool atRim = c.x == clipped.minX || c.x == clipped.maxX
                                  || c.z == clipped.minZ || c.z == clipped.maxZ;
                        TerrainDef cur = map.terrainGrid.TerrainAt(c);
                        if (ashDeep != null && RM_FireEcoKernel.RuinScorchLays(cur != null && cur.IsWater, cur?.defName))
                        {
                            map.terrainGrid.SetTerrain(c, ashDeep);
                        }
                        if (ashFilth != null && Rand.Chance(atRim ? 0.35f : 0.7f))
                        {
                            // shouldPropagate:false — a wall cell (unwalkable)
                            // simply gets no filth rather than pushing it onto
                            // a neighbour outside the ruin's own footprint.
                            FilthMaker.TryMakeFilth(c, map, ashFilth, 1, FilthSourceFlags.None, false);
                        }
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] scorch-ruins: " + e.Message, 0x46E04);
            }
        }

        private static void SweepUnownedBuildings(Map map)
        {
            ThingDef ashFilth = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Filth_LooseAsh");
            TerrainDef ashDeep = DefDatabase<TerrainDef>.GetNamedSilentFail(RM_FireEcoKernel.DeepAshDefName);
            if (ashDeep == null)
            {
                return; // defs not loaded - no-op, not a crash
            }

            try
            {
                // Collect first: setting terrain can destroy plants/filth, never buildings, but the lister is not walked while we write.
                var rects = new List<CellRect>();
                // The same group the walk bar's census reads (jawa/list_things group=BuildingArtificial).
                foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial))
                {
                    if (!(t is Building b)) continue;
                    if (!RM_FireEcoKernel.IsScorchableRuin(b.def.IsBuildingArtificial, b.Faction != null, b.def.destroyable,
                            b.def.building != null && b.def.building.isNaturalRock))
                    {
                        continue;
                    }
                    rects.Add(b.OccupiedRect());
                }

                foreach (CellRect occupied in rects)
                {
                    CellRect swept = occupied.ExpandedBy(SweepRim).ClipInsideMap(map);
                    foreach (IntVec3 c in swept.Cells)
                    {
                        Building edifice = c.GetEdifice(map);
                        if (edifice != null && edifice.def.building != null && edifice.def.building.isNaturalRock)
                        {
                            continue; // mountain face beside the ruin: leave the rock's floor alone
                        }
                        TerrainDef cur = map.terrainGrid.TerrainAt(c);
                        bool atRim = !occupied.Contains(c);
                        if (cur != null && cur.IsWater) continue;
                        if (RM_FireEcoKernel.RuinScorchLays(false, cur?.defName)) map.terrainGrid.SetTerrain(c, ashDeep);
                        if (ashFilth != null && Rand.Chance(atRim ? 0.35f : 0.7f))
                        {
                            FilthMaker.TryMakeFilth(c, map, ashFilth, 1, FilthSourceFlags.None, false);
                        }
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] scorch-ruins-sweep: " + e.Message, 0x46E05);
            }
        }
    }
}
