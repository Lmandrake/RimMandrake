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
    // "roll a chance, spawn a prop nearby" while a fire burns.
    //
    // Everything else in FIRE_ECOLOGY_LOOP_1 (the weather-table strip, Black
    // Rain's trigger, burnedDef to deep ash) is pure XML riding
    // vanilla mechanisms that already exist — see the .xml files' own
    // comments for the RimSage citations. Only "a specific prop appears at a
    // specific cell because a specific event just happened here" has no
    // XML-only route, because Fire.TickInterval exposes no event, signal or
    // XML hook a def can bind.
    [StaticConstructorOnStartup]
    public static class FireEcologyHookMod
    {
        // Shipped defaults for the numbers below now live as tunable fields on
        // RM_PyrelandsSettings (MOD_OPTIONS_RETROFIT_1) — read those at the
        // call sites, not these. Kept only as the historical/default record.
        internal const float AshDustingChancePerFireTick = 0.02f;
        internal const float ScorchFruitChancePerFireTick = 0.0025f;
        internal const int MinFireSizeForAshDusting = 1; // any live Fire counts — not yet gated on; reserved for a future fire-size check

        static FireEcologyHookMod()
        {
            var h = new Harmony("mandrake.rm.pyrelands");

            Apply(h, AccessTools.Method(typeof(Fire), "TickInterval"),
                  typeof(Patch_FireTick_AshAndScorchFruit), "fire-tick-ash-scorchfruit",
                  "armed; burning cells on scorchable ground may dust loose ash "
                  + "and rarely seed a scorch-fruit pod");
            Apply(h, AccessTools.Method(typeof(FilthMaker), nameof(FilthMaker.CanMakeFilth)),
                  typeof(Patch_FilthMaker_NoAshOnAsh), "no-vanilla-ash-on-natural-ground",
                  "armed; flame leaves no Filth_Ash on natural ground here, the biome's own loose ash marks a burn");
            Apply(h, AccessTools.Method(AccessTools.TypeByName("RimWorld.WorkGiver_StudyInteract"), "HasJobOnThing"),
                  typeof(Patch_StudyInteract_NotInTheFire), "no-study-in-the-fire",
                  "armed; nobody walks into a live front to study a scorch-fruit unless ordered");
        }

        private static void Apply(Harmony h, MethodBase target, Type patchClass,
                                  string rule, string detail)
        {
            if (target == null)
            {
                Log.Error("[RimMandrake.Pyrelands] " + rule + ": TARGET METHOD NOT FOUND — "
                          + "this rule is NOT in effect. A game update renamed it.");
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

        // Scorchable ground: ANY Pyrelands ground (RM_FE_*, deep ash included,
        // not a floor) OR vanilla Soil/Sand/Gravel/SoilRich. The ground
        // alone opts no map in: the fire-tick hook also needs FireEcologyBiomeGate.
        internal static bool IsScorchableGround(TerrainDef terrain)
        {
            return terrain != null && RM_FireEcoKernel.IsScorchableGround(terrain.defName);
        }
    }

    // FIRE_ECOLOGY_DIAGNOSE_FOREST_FIRES_FRUIT: does fire ecology run on this map? The Pyrelands biome always; another biome only
    // through the cross-biome opt-in (RM_PyrelandsSettings.AppliesToBiome, the setting the ash drift already reads). Asked once
    // per live Fire per interval, and AppliesToBiome parses the biome list, so the answer is cached PER MAP and recomputed only
    // when the map's biome or one of the three cross-biome settings changes (they apply live, SettingScope.Now).
    public static class FireEcologyBiomeGate
    {
        private const string NativeBiomeDefName = "RM_Pyrelands";

        private sealed class Entry
        {
            public bool valid;
            public BiomeDef biome;
            public bool enabled;
            public bool everywhere;
            public string list;
            public bool on;
        }

        private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<Map, Entry> byMap =
            new System.Runtime.CompilerServices.ConditionalWeakTable<Map, Entry>();

        public static bool On(Map map)
        {
            if (map == null) return false;
            Entry e = byMap.GetValue(map, _ => new Entry());
            BiomeDef biome = map.Biome;
            bool enabled = RM_PyrelandsSettings.crossBiomeEnabled, everywhere = RM_PyrelandsSettings.crossBiomeEverywhere;
            string list = RM_PyrelandsSettings.crossBiomeBiomeList;
            if (!e.valid || e.biome != biome || e.enabled != enabled || e.everywhere != everywhere || !string.Equals(e.list, list))
            {
                e.on = ForBiome(biome);
                e.biome = biome;
                e.enabled = enabled;
                e.everywhere = everywhere;
                e.list = list;
                e.valid = true;
            }
            return e.on;
        }

        /// <summary>The uncached answer for one biome under the current settings.</summary>
        public static bool ForBiome(BiomeDef biome)
        {
            return RM_FireEcoKernel.FireEcologyOnMap(biome != null && biome.defName == NativeBiomeDefName, RM_PyrelandsSettings.AppliesToBiome(biome));
        }

        /// <summary>static_call probe for FIRE_ECOLOGY_DIAGNOSE_FOREST_FIRES_FRUIT: the gate for TemperateForest with the cross-biome
        /// setting off, on for every biome, on naming it, and on naming another biome; the Pyrelands with it off; and the current
        /// map's cached answer before and after a settings flip (the cache must follow the setting). Settings are restored.
        /// "FORESTGATE forestOff B | forestEverywhere B | forestListed B | forestOtherListed B | pyrelandsOff B | mapCacheFollows B".
        /// PASS = False True True False True True.</summary>
        public static string ProofForestGate()
        {
            BiomeDef forest = DefDatabase<BiomeDef>.GetNamedSilentFail("TemperateForest");
            BiomeDef pyre = DefDatabase<BiomeDef>.GetNamedSilentFail(NativeBiomeDefName);
            if (forest == null || pyre == null) return "REFUSED: TemperateForest or RM_Pyrelands not loaded";
            bool wasEnabled = RM_PyrelandsSettings.crossBiomeEnabled, wasEvery = RM_PyrelandsSettings.crossBiomeEverywhere;
            string wasList = RM_PyrelandsSettings.crossBiomeBiomeList;
            try
            {
                RM_PyrelandsSettings.crossBiomeEnabled = false;
                RM_PyrelandsSettings.crossBiomeEverywhere = false;
                RM_PyrelandsSettings.crossBiomeBiomeList = "";
                bool forestOff = ForBiome(forest), pyrelandsOff = ForBiome(pyre);
                Map map = Find.CurrentMap;
                bool mapBefore = map != null && On(map);
                RM_PyrelandsSettings.crossBiomeEnabled = true;
                RM_PyrelandsSettings.crossBiomeEverywhere = true;
                bool forestEverywhere = ForBiome(forest);
                bool mapAfter = map != null && On(map);
                RM_PyrelandsSettings.crossBiomeEverywhere = false;
                RM_PyrelandsSettings.crossBiomeBiomeList = "AridShrubland, TemperateForest";
                bool forestListed = ForBiome(forest);
                RM_PyrelandsSettings.crossBiomeBiomeList = "AridShrubland";
                bool forestOtherListed = ForBiome(forest);
                // On the Pyrelands (native) the map answer is true either way; elsewhere it must flip from false to true.
                bool mapCacheFollows = map != null && mapBefore == ForBiomeWith(map.Biome, false) && mapAfter;
                return "FORESTGATE forestOff " + forestOff + " | forestEverywhere " + forestEverywhere + " | forestListed " + forestListed
                    + " | forestOtherListed " + forestOtherListed + " | pyrelandsOff " + pyrelandsOff + " | mapCacheFollows " + mapCacheFollows
                    + " | map " + (map?.Biome?.defName ?? "none");
            }
            finally
            {
                RM_PyrelandsSettings.crossBiomeEnabled = wasEnabled;
                RM_PyrelandsSettings.crossBiomeEverywhere = wasEvery;
                RM_PyrelandsSettings.crossBiomeBiomeList = wasList;
            }
        }

        private static bool ForBiomeWith(BiomeDef biome, bool crossApplies)
        {
            return RM_FireEcoKernel.FireEcologyOnMap(biome != null && biome.defName == NativeBiomeDefName, crossApplies);
        }
    }

    /// <summary>Vanilla's flame drops Filth_Ash (beauty -12) on all it destroys. Here that is every grass plant, so one burn laid
    /// 50,000 of them over 62,500 cells beside our 50,000 loose ash (live, 2026-11-07): ash on deep ash, a cell reading "Ash,
    /// Loose ash, Deep ash", colonists at "Ugly environment" and cleaning for days after every front. Natural ground takes
    /// only the biome's loose ash; a floor still gets vanilla's.</summary>
    public static class Patch_FilthMaker_NoAshOnAsh
    {
        public static void Postfix(ref bool __result, IntVec3 cell, Map map, ThingDef filthDef)
        {
            if (!__result || filthDef != ThingDefOf.Filth_Ash || map == null || !PyrelandsMechanicsGate.On) return;
            MapComponent_BurnLine line = MapComponent_BurnLine.For(map);
            if (line == null || !line.IsPyrelandsMap || !cell.InBounds(map)) return;
            if (!map.terrainGrid.TerrainAt(cell).IsFloor) __result = false;
        }
    }

    /// <summary>Scorch-fruit only stands in a fresh burn, right behind the front, and its shade-cloth study (EnvironmentalHazards'
    /// found-tech comp) is served automatically by vanilla's study work giver, which knows nothing of fire. On map n
    /// (2026-11-07) two colonists walked 70 cells into the opening front on day 0 and one came back with three burns. A pod
    /// with fire within FireClear cells is not studied unless the player orders it.
    /// Nor is one far from home: on map r (2026-11-07) a colonist walked 120 cells across open ground at 60 C to study a pod
    /// beside the burn, with thirst 0.23, food 0.19 and heatstroke 0.34. A pod outside the home area is studied unordered only
    /// within StudyReach cells of the studier.</summary>
    public static class Patch_StudyInteract_NotInTheFire
    {
        private const int FireClear = 6;
        private const int StudyReach = 25;
        private static ThingDef pod;

        public static void Postfix(ref bool __result, Pawn pawn, Thing t, bool forced)
        {
            if (!__result || forced || t == null || !t.Spawned) return;
            if (pod == null) pod = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_ScorchFruit");
            if (t.def != pod) return;
            Map map = t.Map;
            bool atHome = map.areaManager?.Home != null && map.areaManager.Home[t.Position];
            if (!atHome && (pawn == null || !t.Position.InHorDistOf(pawn.Position, StudyReach))) { __result = false; return; }
            foreach (IntVec3 c in GenRadial.RadialCellsAround(t.Position, FireClear, true))
            {
                if (c.InBounds(map) && c.ContainsStaticFire(map)) { __result = false; return; }
            }
        }
    }

    /// <summary>The pod rots through CompRottable, which runs in base.TickInterval; a rot landing on the pod's long-tick hash
    /// destroys it and Plant.TickInterval then calls TickLong on a thing with no map (NRE in CheckMakeLeafless).</summary>
    public class Plant_ScorchFruitPod : Plant
    {
        public override void TickLong()
        {
            if (Destroyed) return;
            base.TickLong();
        }
    }

    /// <summary>One static drift field per map: a low-frequency noise giving every cell a target loose-ash thickness 0..3
    /// (RM_FireEcoKernel.DriftTarget), shared by the fire's scar ash, ash fall and yesterday's fire. Conductor ruling 2026-11-07
    /// on map s: "make the drifts fewer, of varied size and clustered (pooled against walls and along the burn edge), rather than
    /// redrawing the grain again." Unsaved: rebuilt from the map's own uniqueID, so a reload puts every drift's ceiling back.</summary>
    public static class PyrelandsDriftField
    {
        private sealed class Field
        {
            public int mapId;
            public Verse.Noise.Perlin noise;
            public RM_DriftCuts cuts;
        }

        private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<Map, Field> fields =
            new System.Runtime.CompilerServices.ConditionalWeakTable<Map, Field>();

        // ~10-cell features: a clump is a few cells across with a core, and a wide bare stretch lies between clumps. The old
        // ash-fall field (0.045) banked over 20-cell sweeps, wider than a burn scar's own width.
        private const double Frequency = 0.1;
        // A 48x48 lattice of samples sets the cuts: enough for stable quantiles, never a scan of every cell.
        private const int SampleSide = 48;

        private static ThingDef ashDef;
        private static bool ashResolved;

        public static ThingDef AshDef
        {
            get
            {
                if (!ashResolved)
                {
                    ashResolved = true;
                    ashDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Filth_LooseAsh");
                }
                return ashDef;
            }
        }

        private static Field For(Map map)
        {
            if (fields.TryGetValue(map, out Field f) && f.mapId == map.uniqueID) return f;
            if (f != null) fields.Remove(map);
            f = new Field { mapId = map.uniqueID };
            f.noise = new Verse.Noise.Perlin(Frequency, 2.0, 0.5, 3, map.uniqueID * 7919 + 1543, Verse.Noise.QualityMode.Medium);
            var samples = new float[SampleSide * SampleSide];
            for (int i = 0; i < SampleSide; i++)
            {
                for (int j = 0; j < SampleSide; j++)
                {
                    double x = (i + 0.5) * map.Size.x / SampleSide;
                    double z = (j + 0.5) * map.Size.z / SampleSide;
                    samples[i * SampleSide + j] = (float)f.noise.GetValue(x, 0.0, z);
                }
            }
            f.cuts = RM_FireEcoKernel.DriftCuts(samples);
            fields.Add(map, f);
            return f;
        }

        /// <summary>True when a cardinal neighbour holds an edifice (rock, a wall, a ruin): the lee ash banks against.</summary>
        public static bool Lee(Map map, IntVec3 c)
        {
            for (int k = 0; k < 4; k++)
            {
                IntVec3 n = c + GenAdj.CardinalDirections[k];
                if (n.InBounds(map) && n.GetEdifice(map) != null) return true;
            }
            return false;
        }

        /// <summary>True when a cardinal neighbour still holds standing grass that is not burning: the scar's rim.</summary>
        public static bool BurnEdge(Map map, IntVec3 c)
        {
            for (int k = 0; k < 4; k++)
            {
                IntVec3 n = c + GenAdj.CardinalDirections[k];
                if (!n.InBounds(map)) continue;
                Plant p = n.GetPlant(map);
                if (p != null && !p.def.plant.IsTree && !n.ContainsStaticFire(map)) return true;
            }
            return false;
        }

        /// <summary>The cell's target thickness 0..3: the field's height, plus the lee, plus the burn edge when it may count.</summary>
        public static int Target(Map map, IntVec3 c, bool countEdge)
        {
            Field f = For(map);
            float n = (float)f.noise.GetValue(c.x, 0.0, c.z);
            return RM_FireEcoKernel.DriftTarget(n, f.cuts, Lee(map, c), countEdge && BurnEdge(map, c));
        }

        /// <summary>The current loose-ash thickness on a cell, 0 for none.</summary>
        public static int Thickness(Map map, IntVec3 c)
        {
            ThingDef def = AshDef;
            return def != null && c.GetFirstThing(map, def) is Filth f ? f.thickness : 0;
        }

        /// <summary>Lays a burned cell's whole scar ash at once (yesterday's fire, GenStep_PyrelandsYesterdayFire): its drift-field
        /// target with the lee and the burn edge, never spilling, never thinning a deeper drift already there.</summary>
        public static void LayScarAsh(Map map, IntVec3 c)
        {
            ThingDef def = AshDef;
            if (def == null || map == null || !c.InBounds(map)) return;
            int have = Thickness(map, c);
            int target = Target(map, c, true);
            if (RM_FireEcoKernel.ScarAshMayThicken(have, target))
            {
                FilthMaker.TryMakeFilth(c, map, def, target - have, FilthSourceFlags.None, false);
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
        // PER MAP, saved with it (MapComponent_PyrelandsAshField.RolledFruitFires);
        // this weak table is the fallback for a map without that component.
        // Never static: a reload re-issues the same thingIDNumbers,
        // and a static set then blocked every reloaded fire's roll
        // (PYRE_SCORCHFRUIT_DIAGNOSE_FIRE_BEARS_NOTHING, RM_FireEcoKernel.RollSetFor).
        // Never shrunk per-fire (despawn hooks cost more than they save);
        // cleared wholesale when it grows past a bound no live map reaches.
        private static readonly System.Runtime.CompilerServices.ConditionalWeakTable<object, HashSet<int>> rolledFiresByMap =
            new System.Runtime.CompilerServices.ConditionalWeakTable<object, HashSet<int>>();

        // Bound past which rolledFires is cleared wholesale (RM_FireEcoKernel.MarkOnce).
        private const int RolledBound = 100000;

        /// <summary>The 3x3 scan of RM_FireEcoKernel.FirstFruitSpot, written out so the hot fire tick allocates nothing.</summary>
        private static int FirstLegalFruitSpot(IntVec3 pos, Map map)
        {
            for (int i = 0; i < RM_FireEcoKernel.FruitSpotDx.Length; i++)
            {
                IntVec3 c = new IntVec3(pos.x + RM_FireEcoKernel.FruitSpotDx[i], 0, pos.z + RM_FireEcoKernel.FruitSpotDz[i]);
                bool inb = c.InBounds(map);
                if (RM_FireEcoKernel.FruitLandingLegal(inb, inb && c.Standable(map), inb && c.GetPlant(map) != null,
                        inb && FireEcologyHookMod.IsScorchableGround(c.GetTerrain(map))))
                {
                    return i;
                }
            }
            return -1;
        }

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
                // FIRE_ECOLOGY_DIAGNOSE_FOREST_FIRES_FRUIT: vanilla soils are scorchable ground, so the map's biome must also opt in
                // (the Pyrelands, or the cross-biome setting) or a temperate-forest fire dusts ash, stamps burns and grows fruit.
                bool scorchable = RM_FireEcoKernel.ScorchableHere(usable && FireEcologyBiomeGate.On(map), terrain?.defName);
                // The fresh-burn stamp (PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED §4): this cell burned now. Its own toggle, independent
                // of dusting and fruit. The gate is scorchable ground, deep ash included, on a map fire ecology runs on (ScorchableHere).
                if (RM_FireEcoKernel.BurnStampMay(PyrelandsMechanicsGate.On, RM_PyrelandsSettings.freshBurnBonusEnabled, usable,
                        __instance.parent != null, scorchable))
                {
                    MapComponent_PyrelandsAshField.For(map)?.StampBurn(pos, Find.TickManager.TicksGame);
                }
                if (!RM_FireEcoKernel.FireTickMayRoll(PyrelandsMechanicsGate.On, RM_PyrelandsSettings.ashDustingEnabled,
                        RM_PyrelandsSettings.scorchFruitEnabled, usable, __instance.parent != null, scorchable)) return;

                // Loose ash dusting: the scar's ash (vanilla's Filth_Ash is kept off natural ground here, Patch_FilthMaker_NoAshOnAsh).
                // A fire heaps its own cell up to that cell's drift-field target and never spills: rolled per tick, a long burn filled
                // its cell to the cap and FilthMaker then propagated the overflow to the neighbours, so 6,335 of 6,924 burned cells sat
                // at x4 and the scar read as one pale sheet (map n, 2026-11-07). Only ash fall heaps drifts deeper.
                if (RM_PyrelandsSettings.ashDustingEnabled)
                {
                    ThingDef ashFilth = PyrelandsDriftField.AshDef;
                    // The target is fixed per cell (PyrelandsDriftField), so a long burn cannot re-roll its way in or past it. A
                    // hashed third of the cells at x1 read as polka dots (map s, 2026-11-07): every drift alone and one size. Now most
                    // cells take none and the rest lie in clumps with x2-x3 cores, pooled in the lee and along the rim. The rim counts
                    // only once the fire has burned a while: early on, the grass ahead of the front has not caught yet.
                    if (ashFilth != null && Rand.Chance(RM_FireEcoKernel.DustChance(RM_PyrelandsSettings.ashDustingChance, delta)))
                    {
                        int target = PyrelandsDriftField.Target(map, pos, __instance.TicksSinceSpawn >= RM_FireEcoKernel.ScarEdgeSettleTicks);
                        if (RM_FireEcoKernel.ScarAshMayThicken(PyrelandsDriftField.Thickness(map, pos), target))
                        {
                            FilthMaker.TryMakeFilth(pos, map, ashFilth, 1, FilthSourceFlags.None, false);
                        }
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
                // The set is SAVED with the map (MapComponent_PyrelandsAshField, SCORCH_FRUIT_FIX_LANDS_ON_FIREBREAK), so a fire still
                // burning at a save does not roll again after the load; the weak table is only the fallback with no component.
                HashSet<int> rolledFires = RM_PyrelandsSettings.scorchFruitEnabled
                    ? (MapComponent_PyrelandsAshField.For(map)?.RolledFruitFires ?? RM_FireEcoKernel.RollSetFor(rolledFiresByMap, map)) : null;
                if (rolledFires != null && !rolledFires.Contains(__instance.thingIDNumber))
                {
                    // FIRE_SCAN_DIAGNOSE_BIG_BURN_COST: a static scan, never a lambda. A lambda capturing `pos`/`map` made C# hoist
                    // both into a closure object allocated on EVERY call of this postfix -- every fire, every interval, rolled or not.
                    int spotIndex = RM_FireEcoKernel.TakeFruitRollAt(rolledFires, __instance.thingIDNumber, RolledBound,
                        FirstLegalFruitSpot(pos, map));
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
                            // Ripe at birth: the crack IS the ripening. Left to grow it starts at 0.15 of a 0.65 harvest line,
                            // rests at night and stops dead above its 58C ceiling, so at this biome's heat it could rot unripe.
                            if (fruit is Plant pod) pod.Growth = 1f;
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

        // Cross-biome ambient drift (no weather behind it, so it never stops): one candidate per this many cells per batch, the
        // old sprinkle rate, ~15 on a 250x250 map.
        private const float CellsPerDepositAttempt = 4000f;

        // Under ash fall or cinderfall: one new-cell candidate AND one bank-growth pick per this many cells per batch, ~156 each
        // on a 250x250 map. The old sprinkle (one per 4,000 cells, mostly landing under grass) left a six-hour fall invisible on
        // map s (sky_s_1ashfall_b.png, 2026-11-07). Each candidate is a handful of cell lookups and one noise read; no batch
        // scans the map.
        //
        // 2026-11-08, owner on map x after ~7 h of fall: "accumulating very slowly. If this were snow ... much faster." 400 -> 50
        // cells per candidate (8x): ~1,250 of each per batch on a 250x250 map. Vanilla hard snow (snowRate 1.2) lays
        // 0.046 x 1.2 x ~0.58 = 0.032 depth on every outdoor cell each visit, a cell visited every 1,645 ticks (38 cells a tick, 62,500 cells),
        // so ~0.049 depth per game hour on 100% of the map; a drift here heaps ~0.5 of its 4 levels per hour (5,000 picks an hour over
        // ~10,000 drifts) = ~0.12 depth an hour, and the cover cap (AshFallCoverCap) rose with it.
        private const float CellsPerFallCandidate = 50f;

        private const float CinderfallRateFactor = 0.45f;

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
            ashFallWeather = DefDatabase<WeatherDef>.GetNamedSilentFail("RM_FE_Weather_AshFall");
            cinderfallWeather = DefDatabase<WeatherDef>.GetNamedSilentFail("RM_FE_Weather_Cinderfall");
        }

        /// <summary>One ash-fall deposit on a cell: lands under open sky on dry ground, kept by the drift field's chance for that
        /// cell (grass in a bank half the time and elsewhere rarely, a hollow or a lee on bare ground always), heaped no deeper than the cell's ash-fall ceiling.
        /// Never spills to a neighbour.</summary>
        private bool TryDeposit(IntVec3 c, ThingDef ashDef)
        {
            if (!c.InBounds(map) || map.roofGrid.Roofed(c) || c.GetTerrain(map).IsWater)
            {
                return false;
            }
            Plant plant = c.GetPlant(map);
            bool underGrass = plant != null && !plant.def.plant.IsTree;
            int target = PyrelandsDriftField.Target(map, c, false);
            if (PyrelandsDriftField.Thickness(map, c) >= RM_FireEcoKernel.AshFallCeiling(target, ashDef.filth.maxThickness))
            {
                return false;
            }
            if (!Rand.Chance(RM_FireEcoKernel.AshFallAccept(target, underGrass)))
            {
                return false;
            }
            return FilthMaker.TryMakeFilth(c, map, ashDef, 1, FilthSourceFlags.None, false);
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
            ThingDef ashDef = PyrelandsDriftField.AshDef;
            if (ashDef == null)
            {
                return;
            }

            WeatherManager wm = map.weatherManager;
            WeatherDef current = (wm != null) ? wm.curWeather : null;
            bool ashFall = current != null && current == ashFallWeather;
            bool cinderfall = current != null && current == cinderfallWeather;

            bool isNativeBiome = map.Biome != null && map.Biome.defName == "RM_Pyrelands";

            // Cross-biome opt-in (MOD_OPTIONS_RETROFIT_1 §6a): an opted-in non-Pyrelands biome gets ambient ash drift regardless
            // of its own current weather, scaled by crossBiomeCoverage. Off by default; never fires unless the owner names this
            // biome or ticks "every biome". A rate of zero (coverage slider at 0) deposits nothing.
            float rate = RM_FireEcoKernel.AshRate(ashFall, cinderfall,
                CinderfallRateFactor, isNativeBiome, !isNativeBiome && RM_PyrelandsSettings.AppliesToBiome(map.Biome),
                RM_PyrelandsSettings.crossBiomeCoverage, RM_PyrelandsSettings.ashfallRateMultiplier);
            if (rate < 0f)
            {
                return;
            }

            bool falling = ashFall || cinderfall;
            int attempts = RM_FireEcoKernel.AshAttempts(map.Area, falling ? CellsPerFallCandidate : CellsPerDepositAttempt, rate);

            try
            {
                // New drifts: random cells, kept where the ash shows and banks (bare ground, the field's hollows, the lee).
                List<Thing> drifts = map.listerThings.ThingsOfDef(ashDef);
                if (RM_FireEcoKernel.AshFallMaySpread(drifts.Count, map.Area, RM_FireEcoKernel.AshFallCoverCap))
                {
                    for (int i = 0; i < attempts; i++)
                    {
                        TryDeposit(CellFinder.RandomCell(map), ashDef);
                    }
                }
                if (!falling)
                {
                    return;
                }
                // Banks grow: a drift already lying (laid by this fall, an earlier one, or a fire's scar) heaps toward its
                // ceiling, and once there spills its growth onto a neighbour the field accepts, so a hollow fills out to its
                // edges hour by hour while the plain between banks stays thin.
                for (int i = 0; i < attempts; i++)
                {
                    int count = drifts.Count;
                    if (count == 0)
                    {
                        break;
                    }
                    IntVec3 at = drifts[Rand.Range(0, count)].Position;
                    if (TryDeposit(at, ashDef))
                    {
                        continue;
                    }
                    if (RM_FireEcoKernel.AshFallMaySpread(count, map.Area, RM_FireEcoKernel.AshFallCoverCap))
                    {
                        TryDeposit(at + GenAdj.AdjacentCells[Rand.Range(0, 8)], ashDef);
                    }
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
                        if (CharFloor(map, c, cur))
                        {
                            // a ruin's floor stays a floor, blackened (CharFloor)
                        }
                        else if (ashDeep != null && RM_FireEcoKernel.RuinScorchLays(cur != null && cur.IsWater, cur?.defName))
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

        // pyre_ruins_scorched: the ruin itself stands black and damaged, not just the ground under it. Vanilla's paint slot
        // (Building.ChangePaint) replaces the stuff colour on any building with no comp and no new graphic.
        private static void CharRuinBuilding(Building b)
        {
            ColorDef charred = DefDatabase<ColorDef>.GetNamedSilentFail("RM_FE_Charred");
            if (charred != null) b.ChangePaint(charred);
            if (b.def.useHitPoints && b.MaxHitPoints > 1)
            {
                b.HitPoints = Math.Max(1, (int)(b.MaxHitPoints * Rand.Range(0.35f, 0.8f)));
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
                    CharRuinBuilding(b);
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
                        if (CharFloor(map, c, cur)) { }
                        else if (RM_FireEcoKernel.RuinScorchLays(false, cur?.defName)) map.terrainGrid.SetTerrain(c, ashDeep);
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
            try
            {
                // Every floor left on the map at generation is a ruin's (a ruin whose walls fell, an ancient slab): the sweep
                // above only reaches one cell past a standing building, so the rest lay pale and clean in a burned land
                // (map r: a flagstone shrine floor in the middle of the opening scar; the judge: "the ruin floors look clean").
                foreach (IntVec3 c in map.AllCells)
                {
                    CharFloor(map, c, map.terrainGrid.TerrainAt(c));
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] scorch-ruin-floors: " + e.Message, 0x46E06);
            }
        }

        /// <summary>A built floor (not a road, not water) keeps its pattern and takes the charred paint, the same ColorDef the
        /// ruin walls get: blackened flagstone, not bare ash where a floor plan was. True when the cell is such a floor.</summary>
        private static bool CharFloor(Map map, IntVec3 c, TerrainDef cur)
        {
            if (cur == null || !cur.IsFloor || cur.IsRoad || cur.IsWater) return false;
            ColorDef charred = DefDatabase<ColorDef>.GetNamedSilentFail("RM_FE_Charred");
            if (charred == null) return false;
            if (map.terrainGrid.ColorAt(c) != charred) map.terrainGrid.SetTerrainColor(c, charred);
            return true;
        }
    }
}
