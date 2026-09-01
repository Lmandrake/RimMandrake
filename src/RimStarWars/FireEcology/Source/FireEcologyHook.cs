using System;
using System.Reflection;
using HarmonyLib;
using RimWorld;
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
            "RSW_FE_Ground_Sand", "Sand",
        };

        private const float FulguriteChancePerStrike = 0.35f;
        private const float ScorchFruitChancePerFireTick = 0.0025f;
        private const int MinFireSizeForAshDusting = 1; // any live Fire counts

        static FireEcologyHookMod()
        {
            var h = new Harmony("mandrake.rsw.fireecology");

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
            return n.StartsWith("RSW_FE_Ground_")
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
                if (!Rand.Chance(0.35f)) return; // FulguriteChancePerStrike, inlined: consts aren't accessible cross-class without exposing them

                ThingDef fulguriteDef = DefDatabase<ThingDef>.GetNamedSilentFail("RSW_FE_Fulgurite");
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
    // rolls only, never per-frame.
    public static class Patch_FireTick_AshAndScorchFruit
    {
        public static void Postfix(Fire __instance)
        {
            try
            {
                if (__instance == null || !__instance.Spawned) return;
                Map map = __instance.Map;
                IntVec3 pos = __instance.Position;
                if (map == null || !pos.InBounds(map)) return;

                TerrainDef terrain = pos.GetTerrain(map);
                if (!FireEcologyHookMod.IsScorchableGround(terrain)) return;

                // Loose ash dusting — rides alongside vanilla's own
                // unconditional Filth_Ash spawn (DamageWorker_Flame), does
                // not replace it.
                ThingDef ashFilth = DefDatabase<ThingDef>.GetNamedSilentFail("RSW_FE_Filth_LooseAsh");
                if (ashFilth != null && Rand.Chance(0.02f))
                {
                    FilthMaker.TryMakeFilth(pos, map, ashFilth);
                }

                // Scorch-fruit — rare, and only ever appears this way (never
                // in a biome's ordinary wildPlants list). Plain 3x3 scan
                // instead of a GenAdj/LINQ combinator: fewer ways to get the
                // overload wrong, and this runs at most a few times a fire.
                if (Rand.Chance(0.0025f))
                {
                    ThingDef fruitDef = DefDatabase<ThingDef>.GetNamedSilentFail("RSW_FE_Plant_ScorchFruit");
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
}
