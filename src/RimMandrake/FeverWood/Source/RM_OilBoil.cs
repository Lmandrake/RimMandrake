using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_OIL_BOIL_WEATHER_1 (feverwood_bedazzle_review_2026-10-02; filed by FEVERWOOD_SCORING_SITTING_1).
    // On hot still days the seep oil boils: weather RM_FeverWood_OilBoil lays a low iridescent haze, and while it
    // lasts RM_OilBoilCondition (a) doubles the seepril's seep-oil harvest and (b) makes the haze fuel. The haze lies
    // on ground-level cells only (not the boughway, bough-soil, stilt platforms, trunk or water, and not under a
    // roof). A shot fired from or landing in a hazed cell, a fire or a burning pawn standing in one, or a
    // dry-lightning strike into one FLASHES fire along the connected hazed cells within a radius, ends the
    // condition and clears the weather. Melee never ignites. A flash that reaches a cell beside a registered pool
    // wakes the deep: an ordinary emergence there (never the reserved Great Emergence).
    //
    // The heat gate is vanilla's own: WeatherDecider.CurrentWeatherCommonality returns 0 for a weather whose
    // temperatureRange excludes the outdoor temperature, so the setting writes temperatureRange.min. Commonality is
    // the biome's own record, scaled by the setting (0 when off). Both applied at startup and on every settings write.
    public static class RM_OilBoil
    {
        public const string WeatherName = "RM_FeverWood_OilBoil";
        public const string ConditionName = "RM_OilBoilCondition";
        public const string BiomeName = "RM_FeverWood";
        private static float? baseCommonality;

        // FEVERWOOD_OIL_FLASH_BARE_GROUND_1: the haze IS the fuel. Vanilla FireUtility.ChanceToStartFireIn evaluates
        // this curve BEFORE its num > 0 gate, so a hazed cell of bare soil or stone (flammability 0) still catches;
        // a cell already holding a fire, an impassable edifice interior and no-fire filth still refuse.
        public static readonly SimpleCurve HazeFlashChance = new SimpleCurve
        {
            new CurvePoint(0f, 0.5f),
            new CurvePoint(1f, 1f)
        };

        private static readonly HashSet<string> RaisedTerrain = new HashSet<string>
        {
            "RUT_Boughway", "RUT_BoughSoil", "RUT_StiltPlatform", "RM_Boughway", "RM_BoughSoil", "RM_StiltPlatform",
        };

        private static readonly HashSet<string> TrunkDefs = new HashSet<string>
        {
            "RUT_FeverTrunkCore", "RUT_FeverTrunkHeartwood", "RM_FeverTrunkCore", "RM_FeverTrunkHeartwood",
        };

        public static WeatherDef Weather => DefDatabase<WeatherDef>.GetNamedSilentFail(WeatherName);
        public static GameConditionDef Condition => DefDatabase<GameConditionDef>.GetNamedSilentFail(ConditionName);

        public static void ApplySettings()
        {
            WeatherDef w = Weather;
            BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail(BiomeName);
            if (w == null)
            {
                return;
            }
            w.temperatureRange = new FloatRange(RM_FeverWoodSettings.oilBoilMinTempC, 999f);
            WeatherCommonalityRecord rec = biome?.baseWeatherCommonalities?.FirstOrDefault(r => r.weather == w);
            if (rec != null)
            {
                if (baseCommonality == null)
                {
                    baseCommonality = rec.commonality;
                }
                rec.commonality = RM_FeverWoodSettings.oilBoilEnabled
                    ? baseCommonality.Value * Mathf.Max(0f, RM_FeverWoodSettings.oilBoilCommonalityMultiplier)
                    : 0f;
            }
        }

        /// <summary>The gate's answer: could the weather decider pick the oil boil on this map now.</summary>
        public static bool CanOccur(Map map)
        {
            WeatherDef w = Weather;
            if (map == null || w == null || !RM_FeverWoodSettings.oilBoilEnabled)
            {
                return false;
            }
            WeatherCommonalityRecord rec = map.Biome.baseWeatherCommonalities?.FirstOrDefault(r => r.weather == w);
            return rec != null && rec.commonality > 0f && w.temperatureRange.Includes(map.mapTemperature.OutdoorTemp);
        }

        public static RM_GameCondition_OilBoil ActiveOn(Map map)
        {
            GameConditionDef def = Condition;
            return map == null || def == null ? null : map.gameConditionManager.GetActiveCondition(def) as RM_GameCondition_OilBoil;
        }

        public static bool IsHazed(IntVec3 c, Map map)
        {
            if (!c.InBounds(map) || map.roofGrid.Roofed(c))
            {
                return false;
            }
            TerrainDef t = map.terrainGrid.TerrainAt(c);
            TerrainDef f = map.terrainGrid.FoundationAt(c);
            if (t == null || t.IsWater || RaisedTerrain.Contains(t.defName) || (f != null && RaisedTerrain.Contains(f.defName)))
            {
                return false;
            }
            Building b = c.GetEdifice(map);
            return b == null || !TrunkDefs.Contains(b.def.defName);
        }

        /// <summary>Connected hazed cells within radius of the spark, breadth-first.</summary>
        public static List<IntVec3> FlashCells(IntVec3 spark, Map map, float radius)
        {
            var result = new List<IntVec3>();
            if (!IsHazed(spark, map))
            {
                return result;
            }
            var seen = new HashSet<IntVec3> { spark };
            var queue = new Queue<IntVec3>();
            queue.Enqueue(spark);
            float r2 = radius * radius;
            while (queue.Count > 0)
            {
                IntVec3 c = queue.Dequeue();
                result.Add(c);
                foreach (IntVec3 d in GenAdj.CardinalDirections)
                {
                    IntVec3 n = c + d;
                    if (seen.Add(n) && (n - spark).LengthHorizontalSquared <= r2 && IsHazed(n, map))
                    {
                        queue.Enqueue(n);
                    }
                }
            }
            return result;
        }

        /// <summary>Spark at a cell: flashes if the condition is active and the cell is hazed. True if it flashed.</summary>
        public static bool TrySpark(Map map, IntVec3 cell, string cause)
        {
            RM_GameCondition_OilBoil cond = ActiveOn(map);
            return cond != null && IsHazed(cell, map) && cond.Flash(cell, cause);
        }

        [StaticConstructorOnStartup]
        public static class Startup
        {
            static Startup()
            {
                ApplySettings();
            }
        }
    }

    public class RM_GameCondition_OilBoil : GameCondition
    {
        private const int ScanInterval = 60;
        public static int lastLightningTick = -9999;

        public bool Flashed { get; private set; }

        public override void GameConditionTick()
        {
            base.GameConditionTick();
            if (Flashed || Find.TickManager.TicksGame % ScanInterval != 0)
            {
                return;
            }
            foreach (Map map in AffectedMaps)
            {
                bool lightning = Find.TickManager.TicksGame - lastLightningTick < 120;
                foreach (Thing fire in map.listerThings.ThingsOfDef(ThingDefOf.Fire).ToList())
                {
                    if (fire.Spawned && RM_OilBoil.IsHazed(fire.Position, map)
                        && Flash(fire.Position, lightning ? "a dry-lightning strike" : "a fire in the haze"))
                    {
                        return;
                    }
                }
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned.ToList())
                {
                    if (p.IsBurning() && RM_OilBoil.IsHazed(p.Position, map) && Flash(p.Position, "a burning " + p.LabelShort))
                    {
                        return;
                    }
                }
            }
        }

        /// <summary>Fire along the connected haze, the condition ends, the weather clears; wakes the deep if the flash
        /// touches a pool. Returns false if already flashed.</summary>
        public bool Flash(IntVec3 spark, string cause)
        {
            Map map = AffectedMaps.FirstOrDefault();
            if (Flashed || map == null)
            {
                return false;
            }
            Flashed = true;
            List<IntVec3> cells = RM_OilBoil.FlashCells(spark, map, RM_FeverWoodSettings.oilBoilFlashRadius);
            int lit = 0;
            foreach (IntVec3 c in cells)
            {
                if (FireUtility.TryStartFireIn(c, map, Rand.Range(0.25f, 0.6f), null, RM_OilBoil.HazeFlashChance))
                {
                    lit++;
                }
            }
            int woke = 0;
            if (RM_FeverWoodSettings.oilBoilWakesDeep)
            {
                RUT_MapComponent_TheTenant tenant = map.GetComponent<RUT_MapComponent_TheTenant>();
                IntVec3 poolSide = IntVec3.Invalid;
                if (tenant != null)
                {
                    poolSide = cells.FirstOrFallback(c => GenAdj.CardinalDirections.Any(d => (c + d).InBounds(map)
                        && tenant.IsRegisteredWater(c + d)), IntVec3.Invalid);
                }
                if (poolSide.IsValid)
                {
                    woke = map.GetComponent<RM_MapComponent_TentacleWatch>()?.ForceEmergenceNear(poolSide) ?? 0;
                }
            }
            Find.LetterStack.ReceiveLetter("The oil haze flashed",
                "The boiled oil hanging over the ground caught: " + cause + " set it off, and "
                + (lit > 0 ? "fire ran along the haze (" + lit + " cells)." : "it burned off without catching anything.")
                + " The haze has burned off." + (woke > 0 ? "\n\nThe fire reached a pool's edge, and something below has woken." : ""),
                LetterDefOf.ThreatSmall, new TargetInfo(spark, map));
            map.weatherManager.TransitionTo(WeatherDefOf.Clear);
            End();
            return true;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            bool f = Flashed;
            Scribe_Values.Look(ref f, "flashed", false);
            Flashed = f;
        }
    }

    /// <summary>Starts the condition when the oil boil weather arrives (letter), ends it when the weather leaves.</summary>
    public class RM_MapComponent_OilBoil : MapComponent
    {
        public RM_MapComponent_OilBoil(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % 250 != 0)
            {
                return;
            }
            WeatherDef w = RM_OilBoil.Weather;
            GameConditionDef cd = RM_OilBoil.Condition;
            if (w == null || cd == null)
            {
                return;
            }
            bool boiling = map.weatherManager.curWeather == w && RM_FeverWoodSettings.oilBoilEnabled;
            GameCondition active = map.gameConditionManager.GetActiveCondition(cd);
            if (boiling && active == null)
            {
                Start(map);
            }
            else if (!boiling && active != null)
            {
                active.End();
            }
        }

        public static GameCondition Start(Map map)
        {
            GameCondition c = GameConditionMaker.MakeConditionPermanent(RM_OilBoil.Condition);
            map.gameConditionManager.RegisterCondition(c);
            Find.LetterStack.ReceiveLetter("The oil is boiling",
                "The day is hot and still enough that the seep oil is boiling off the ground: a low, rainbow-sheened haze "
                + "lies over every open cell below the crown. Seepril yield double while it lasts.\n\nThe haze is fuel. A shot, "
                + "a flame or a lightning strike in it will flash fire along it. Keep sparks out of it.",
                LetterDefOf.NeutralEvent, new TargetInfo(map.Center, map));
            return c;
        }
    }

    [StaticConstructorOnStartup]
    public class RM_WeatherOverlay_OilBoilHaze : WeatherOverlayDualPanner
    {
        // Vanilla's fog material copied with the haze texture swapped in (MatLoader cannot load a mod path;
        // see RM_WeatherOverlay_GreentideRoil). Falls back to the plain fog look if the texture is missing.
        private static readonly Material HazeMat = MakeMat();

        private static Material MakeMat()
        {
            Material fog = MatLoader.LoadMat("Weather/FogOverlayWorld");
            Texture2D tex = ContentFinder<Texture2D>.Get("Weather/RM_FeverWood_OilBoilHaze", false);
            if (fog == null || tex == null)
            {
                return fog;
            }
            tex.wrapMode = TextureWrapMode.Repeat;
            return new Material(fog) { mainTexture = tex };
        }

        public RM_WeatherOverlay_OilBoilHaze()
        {
            worldOverlayMat = HazeMat;
            worldOverlayPanSpeed1 = 0.00008f;   // a haze that barely drifts. INVENTED
            worldOverlayPanSpeed2 = 0.00005f;
            worldPanDir1 = new Vector2(0.3f, 1f);
            worldPanDir2 = new Vector2(-0.4f, 0.7f);
        }
    }

    // ---- Harmony: yield doubling and the shot/lightning sparks -------------------------------------------------

    [HarmonyPatch(typeof(Plant), nameof(Plant.YieldNow))]
    public static class RM_Patch_OilBoilYield
    {
        public static void Postfix(Plant __instance, ref int __result)
        {
            if (__result > 0 && __instance.def.defName == "RM_Seepril" && __instance.Spawned
                && RM_OilBoil.ActiveOn(__instance.Map) != null)
            {
                __result = Mathf.RoundToInt(__result * Mathf.Max(1f, RM_FeverWoodSettings.oilBoilYieldMultiplier));
            }
        }
    }

    [HarmonyPatch(typeof(Projectile), nameof(Projectile.Launch),
        new[] { typeof(Thing), typeof(Vector3), typeof(LocalTargetInfo), typeof(LocalTargetInfo), typeof(ProjectileHitFlags),
                typeof(bool), typeof(Thing), typeof(ThingDef) })]
    public static class RM_Patch_OilBoilShotFired
    {
        public static void Postfix(Projectile __instance, Thing launcher, Vector3 origin)
        {
            Map map = __instance.Map ?? launcher?.Map;
            if (map != null)
            {
                RM_OilBoil.TrySpark(map, origin.ToIntVec3(), "a shot fired from the haze");
            }
        }
    }

    [HarmonyPatch(typeof(Projectile), "Impact")]
    public static class RM_Patch_OilBoilShotLanded
    {
        public static void Prefix(Projectile __instance)
        {
            if (__instance.Spawned)
            {
                RM_OilBoil.TrySpark(__instance.Map, __instance.Position, "a shot landing in the haze");
            }
        }
    }

    [HarmonyPatch(typeof(WeatherEvent_LightningStrike), nameof(WeatherEvent_LightningStrike.DoStrike))]
    public static class RM_Patch_OilBoilLightning
    {
        public static void Prefix()
        {
            RM_GameCondition_OilBoil.lastLightningTick = Find.TickManager.TicksGame;
        }

        // DoStrike is static (IntVec3 strikeLoc, Map map, ref Mesh boltMesh): spark the struck cell on its own map
        // directly, so a strike in the haze flashes even when its explosion lights no Fire thing.
        public static void Postfix(IntVec3 strikeLoc, Map map)
        {
            if (map != null && strikeLoc.IsValid)
            {
                RM_OilBoil.TrySpark(map, strikeLoc, "a dry-lightning strike");
            }
        }
    }

    /// <summary>Proof hooks for the oil_boil chain (static_call, args "current").</summary>
    public static class RM_OilBoilProof
    {
        public static string ProofGate(Map map)
        {
            map = map ?? Find.CurrentMap;
            WeatherDef w = RM_OilBoil.Weather;
            return "canOccur=" + RM_OilBoil.CanOccur(map) + " temp=" + map?.mapTemperature.OutdoorTemp.ToString("0.0")
                   + " min=" + (w?.temperatureRange.min.ToString("0.0") ?? "?") + " enabled=" + RM_FeverWoodSettings.oilBoilEnabled;
        }

        /// <summary>Starts the condition (as the weather would) and reads the seepril yield with it on and off.</summary>
        public static string ProofYield(Map map)
        {
            map = map ?? Find.CurrentMap;
            ThingDef seepril = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Seepril");
            if (map == null || seepril == null)
            {
                return "ERROR no map or RM_Seepril";
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 20, c => c.Standable(map) && c.GetFirstThing<Plant>(map) == null
                    && c.GetEdifice(map) == null, out IntVec3 cell))
            {
                return "ERROR no cell";
            }
            var plant = (Plant)GenSpawn.Spawn(ThingMaker.MakeThing(seepril), cell, map);
            plant.Growth = 1f;
            GameCondition existing = map.gameConditionManager.GetActiveCondition(RM_OilBoil.Condition);
            existing?.End();
            int off = plant.YieldNow();
            GameCondition c = GameConditionMaker.MakeConditionPermanent(RM_OilBoil.Condition);
            map.gameConditionManager.RegisterCondition(c);
            int on = plant.YieldNow();
            c.End();
            plant.Destroy();
            return "yieldOff=" + off + " yieldOn=" + on;
        }

        /// <summary>Starts the condition and sparks at a hazed ground cell, or at a raised cell when "raised".</summary>
        public static string ProofSpark(Map map)
        {
            map = map ?? Find.CurrentMap;
            if (map == null || RM_OilBoil.Condition == null)
            {
                return "ERROR";
            }
            map.gameConditionManager.GetActiveCondition(RM_OilBoil.Condition)?.End();
            var c = (RM_GameCondition_OilBoil)GameConditionMaker.MakeConditionPermanent(RM_OilBoil.Condition);
            map.gameConditionManager.RegisterCondition(c);
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 25, x => RM_OilBoil.IsHazed(x, map) && x.Standable(map), out IntVec3 cell))
            {
                c.End();
                return "ERROR no hazed cell";
            }
            int firesBefore = map.listerThings.ThingsOfDef(ThingDefOf.Fire).Count;
            bool flashed = RM_OilBoil.TrySpark(map, cell, "a proof spark");
            int firesAfter = map.listerThings.ThingsOfDef(ThingDefOf.Fire).Count;
            return "flashed=" + flashed + " firesBefore=" + firesBefore + " firesAfter=" + firesAfter
                   + " conditionEnded=" + (map.gameConditionManager.GetActiveCondition(RM_OilBoil.Condition) == null);
        }
    }
}
