using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.StarWars.FireEcology
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
    // Rain's trigger, the ash ladder, the firebreak) is pure XML riding
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
        // kept generic (no "Pyrelands"/"Ash'karr" reference) because this
        // assembly ships in the RimStarWars-tier mod.
        private static readonly string[] SandTerrainDefNames =
        {
            "RM_FE_Ground_Sand", "Sand",
        };

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
                Log.Error("[RimMandrake.StarWars.FireEcology] " + rule + ": TARGET METHOD NOT FOUND — "
                          + "this rule is NOT in effect. A game update renamed it. The other "
                          + "rule in this assembly is unaffected.");
                return;
            }
            try
            {
                h.Patch(target, postfix: new HarmonyMethod(patchClass, "Postfix"));
                Log.Message("[RimMandrake.StarWars.FireEcology] " + rule + ": " + detail);
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.StarWars.FireEcology] " + rule + ": patch FAILED, rule NOT "
                          + "in effect — " + e.Message);
            }
        }

        internal static bool IsSandFamily(TerrainDef terrain)
        {
            if (terrain == null) return false;
            for (int i = 0; i < SandTerrainDefNames.Length; i++)
                if (terrain.defName == SandTerrainDefNames[i])
                    return true;
            return false;
        }

        // Scorchable ground (our own clones OR vanilla Soil/Sand/Gravel/
        // SoilRich, so this stays reusable off any biome that opts in via
        // XML wiring, not hardcoded to the Pyrelands' terrain choices).
        internal static bool IsScorchableGround(TerrainDef terrain)
        {
            if (terrain == null) return false;
            string n = terrain.defName;
            return n.StartsWith("RM_FE_Ground_")
                || n == "Sand" || n == "Gravel" || n == "Soil" || n == "SoilRich";
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
                if (map == null || !strikeLoc.IsValid || !strikeLoc.InBounds(map)) return;
                TerrainDef terrain = strikeLoc.GetTerrain(map);
                if (!FireEcologyHookMod.IsSandFamily(terrain)) return;
                if (!Rand.Chance(FireEcologyHookMod.FulguriteChancePerStrike)) return;

                ThingDef fulguriteDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Fulgurite");
                if (fulguriteDef == null) return; // mod not loaded / def missing — no-op, not a crash

                Thing fulgurite = ThingMaker.MakeThing(fulguriteDef);
                GenPlace.TryPlaceThing(fulgurite, strikeLoc, map, ThingPlaceMode.Near);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.StarWars.FireEcology] fulgurite-spawn: " + e.Message, 0x46E01);
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
        private const int ScorchFruitMapCap = 40;

        public static void Postfix(Fire __instance, int delta)
        {
            try
            {
                if (__instance == null || !__instance.Spawned) return;
                // Pawn/animal-attached fires (a burning colonist, a boomrat that
                // caught) are not ground fires - skip them entirely, or a lit
                // pawn dusts ash and seeds scorch-fruit along its whole running
                // path (flavor-wrong, and an ignite-a-boomrat exploit for free
                // fruit). BENCH review finding, 2026-09-01.
                if (__instance.parent != null) return;
                Map map = __instance.Map;
                IntVec3 pos = __instance.Position;
                if (map == null || !pos.InBounds(map)) return;

                TerrainDef terrain = pos.GetTerrain(map);
                if (!FireEcologyHookMod.IsScorchableGround(terrain)) return;

                // Loose ash dusting — rides alongside vanilla's own
                // unconditional Filth_Ash spawn (DamageWorker_Flame), does
                // not replace it.
                ThingDef ashFilth = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Filth_LooseAsh");
                if (ashFilth != null && Rand.Chance(FireEcologyHookMod.AshDustingChancePerFireTick * delta))
                {
                    FilthMaker.TryMakeFilth(pos, map, ashFilth);
                }

                // Scorch-fruit — rare, and only ever appears this way (never
                // in a biome's ordinary wildPlants list). Plain 3x3 scan
                // instead of a GenAdj/LINQ combinator: fewer ways to get the
                // overload wrong, and this runs at most a few times a fire.
                if (Rand.Chance(FireEcologyHookMod.ScorchFruitChancePerFireTick * delta))
                {
                    ThingDef fruitDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_ScorchFruit");
                    // A map-wide burn runs hundreds of concurrent Fire things;
                    // uncapped this seeds an orchard, not a harvest. BENCH
                    // review finding, 2026-09-01.
                    if (fruitDef != null && map.listerThings.ThingsOfDef(fruitDef).Count >= ScorchFruitMapCap)
                    {
                        fruitDef = null;
                    }
                    if (fruitDef != null)
                    {
                        IntVec3 spot = IntVec3.Invalid;
                        for (int dx = -1; dx <= 1 && !spot.IsValid; dx++)
                        {
                            for (int dz = -1; dz <= 1; dz++)
                            {
                                IntVec3 c = pos + new IntVec3(dx, 0, dz);
                                if (!c.InBounds(map) || !c.Standable(map) || c.GetPlant(map) != null)
                                    continue;
                                spot = c;
                                break;
                            }
                        }
                        if (spot.IsValid)
                        {
                            Thing fruit = ThingMaker.MakeThing(fruitDef);
                            GenSpawn.Spawn(fruit, spot, map);
                        }
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.StarWars.FireEcology] fire-tick-ash-scorchfruit: "
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
    // rebuild — see the <modExtensions> block on RM_FE_Pyrelands in
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

    // TRIGGERED BY: <workerClass> on the RM_FE_Pyrelands BiomeDef.
    //
    // Scored against vanilla's own BiomeWorker_AridShrubland, which owns
    // this rainfall corridor today (22.5 + (T-20)*2.2 + (R-600)/100). With
    // the shipped numbers the crossover sits near 25 degC: cooler tiles
    // stay arid shrubland, hotter ones become pyrelands, and outside
    // 550-1000mm rainfall this worker returns 0 and never competes at all.
    public class BiomeWorker_Pyrelands : BiomeWorker
    {
        private static readonly PyrelandsBiomeRanges FallbackRanges = new PyrelandsBiomeRanges();

        public override float GetScore(BiomeDef biome, Tile tile, PlanetTile planetTile)
        {
            if (tile == null || tile.WaterCovered)
            {
                return -100f;
            }

            PyrelandsBiomeRanges r = biome.GetModExtension<PyrelandsBiomeRanges>() ?? FallbackRanges;

            if (tile.temperature < r.temperature.min || tile.temperature > r.temperature.max)
            {
                return 0f;
            }
            // Half-open on rainfall, matching vanilla's own workers exactly
            // so the band edges butt up against theirs with no overlap.
            if (tile.rainfall < r.rainfall.min || tile.rainfall >= r.rainfall.max)
            {
                return 0f;
            }
            if (tile.elevation < r.elevation.min || tile.elevation > r.elevation.max)
            {
                return 0f;
            }
            // Grass savanna, not highland: same exclusion BiomeWorker_Grasslands makes.
            if (tile.hilliness == Hilliness.Mountainous || tile.hilliness == Hilliness.Impassable)
            {
                return 0f;
            }

            float divisor = (r.rainfallDivisor > 0.0001f) ? r.rainfallDivisor : 1f;
            return r.baseScore
                 + (tile.temperature - r.temperature.min) * r.degreeWeight
                 + (tile.rainfall - r.rainfall.min) / divisor;
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
            if (current == null)
            {
                return;
            }

            float rate;
            if (current == ashFallWeather)
            {
                rate = 1f;
            }
            else if (current == cinderfallWeather)
            {
                rate = CinderfallRateFactor;
            }
            else
            {
                return;
            }

            int attempts = (int)((float)map.Area / CellsPerDepositAttempt * rate);
            if (attempts < 1)
            {
                attempts = 1;
            }

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
                Log.WarningOnce("[RimMandrake.StarWars.FireEcology] ashfall-accumulation: "
                                + e.Message, 0x46E03);
            }
        }
    }
}
