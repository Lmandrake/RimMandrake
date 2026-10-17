using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    // EXPLOSIVE_GROWTH_PROBE_TOOL_1: state reads for the four behaviours the first north-star script marked UNCOVERED
    // (harvest jackpot, last-swing gamble, rupture mutation, the tell ladder). Built as jawa/static_call proofs in this
    // assembly, the pattern every later suite uses, instead of a JawaBench [Tool]: no companion rebuild/deploy, and the
    // proof reads the mod's own state directly. Args "current" = the current map. Each stages its own plant/pawn near
    // the map centre and removes what it placed. Output is key=value for the suite's regex.
    public static class RM_ExplosiveGrowthProof
    {
        private const int Reads = 200;

        private static Plant PlacePlant(Map map, string defName)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            if (def == null || map == null)
            {
                return null;
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 25, c => c.Standable(map) && c.GetPlant(map) == null
                    && c.GetEdifice(map) == null && def.CanEverPlantAt(c, map), out IntVec3 cell))
            {
                return null;
            }
            Plant p = (Plant)ThingMaker.MakeThing(def);
            p.Growth = 1f;
            GenSpawn.Spawn(p, cell, map);
            return p;
        }

        private static float MeanYield(Plant p)
        {
            long sum = 0;
            for (int i = 0; i < Reads; i++)
            {
                sum += p.YieldNow();
            }
            return sum / (float)Reads;
        }

        /// <summary>A mature corn plant: mean YieldNow uncharged, then at charge 1. Jackpot on = about 2x.</summary>
        public static string ProofJackpot(Map map)
        {
            map = map ?? Find.CurrentMap;
            var comp = RM_MapComponent_ExplosiveGrowth.For(map);
            Plant p = PlacePlant(map, "Plant_Corn");
            if (comp == null || p == null)
            {
                return "ERROR no map component or no cell for Plant_Corn";
            }
            float baseYield = MeanYield(p);
            comp.DebugSetCharge(p, 1f);
            float charged = MeanYield(p);
            comp.DebugSetCharge(p, 0f);
            p.Destroy();
            return string.Format("jackpotEnabled={0} base={1:0.00} charged={2:0.00} ratio={3:0.00}",
                ExplosiveGrowthSettings.harvestJackpotEnabled, baseYield, charged, baseYield > 0f ? charged / baseYield : 0f);
        }

        /// <summary>The gamble's chance curve, and one real cut below the tremble (always defuses, never fires).</summary>
        public static string ProofGamble(Map map)
        {
            map = map ?? Find.CurrentMap;
            var comp = RM_MapComponent_ExplosiveGrowth.For(map);
            Plant p = PlacePlant(map, "Plant_Corn");
            if (comp == null || p == null)
            {
                return "ERROR no map component or no cell for Plant_Corn";
            }
            comp.DebugSetCharge(p, 0.5f);
            IntVec3 cell = p.Position;
            p.PlantCollected(null, PlantDestructionMode.Cut);
            bool defused = comp.ChargeOf(p) == 0f;
            bool stillThere = p.Spawned;
            if (p.Spawned)
            {
                p.Destroy();
            }
            return string.Format("gambleEnabled={0} chanceAt0.5={1:0.00} chanceAt0.7={2:0.00} chanceAt1={3:0.00} cutBelowTrembleDefused={4} plantCollected={5}",
                ExplosiveGrowthSettings.lastSwingGambleEnabled, RM_Patch_Plant_PlantCollected_Gamble.GambleChance(0.5f),
                RM_Patch_Plant_PlantCollected_Gamble.GambleChance(0.7f), RM_Patch_Plant_PlantCollected_Gamble.GambleChance(1f),
                defused, !stillThere);
        }

        /// <summary>A muffalo standing in a rupture cloud, 200 exposure pulses: mutations counted against the setting.</summary>
        public static string ProofRupture(Map map)
        {
            map = map ?? Find.CurrentMap;
            List<HediffDef> pool = RM_ExplosiveGrowthRegistry.RuptureMutationHediffs;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("Muffalo");
            if (map == null || kind == null)
            {
                return "ERROR no map or Muffalo";
            }
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 25, c => c.Standable(map), out IntVec3 cell))
            {
                return "ERROR no standable cell";
            }
            Pawn pawn = (Pawn)GenSpawn.Spawn(PawnGenerator.GeneratePawn(kind), cell, map);
            var zone = new RM_RuptureZone { center = cell, radius = 2.9f, untilTick = Find.TickManager.TicksGame + 2500 };
            bool inZone = GenRadial.RadialCellsAround(zone.center, zone.radius, true).Contains(pawn.Position);
            int before = pawn.health.hediffSet.hediffs.Count(h => pool.Contains(h.def));
            for (int i = 0; i < 200 && pawn.Spawned && !pawn.Dead; i++)
            {
                RM_TopResolver.RuptureExposurePulse(map, zone);
            }
            int after = pawn.health.hediffSet.hediffs.Count(h => pool.Contains(h.def));
            if (pawn.Spawned)
            {
                pawn.Destroy();
            }
            return string.Format("pool={0} chance={1:0.000} inZone={2} pulses=200 mutations={3}",
                pool.Count, ExplosiveGrowthSettings.ruptureMutationChance, inZone, after - before);
        }

        /// <summary>The tell ladder: stage, draw scale and hue on one plant at each threshold's charge.</summary>
        public static string ProofTell(Map map)
        {
            map = map ?? Find.CurrentMap;
            var comp = RM_MapComponent_ExplosiveGrowth.For(map);
            Plant p = PlacePlant(map, "Plant_Corn");
            if (comp == null || p == null)
            {
                return "ERROR no map component or no cell for Plant_Corn";
            }
            var parts = new List<string>();
            foreach (float c in new[] { 0.1f, 0.2f, 0.5f, 0.75f, 0.9f, 0.97f })
            {
                comp.DebugSetCharge(p, c);
                comp.TryGetCharge(p, out RM_ChargeRecord rec);
                parts.Add(string.Format("c{0:0.00}={1}/{2:0.000}/{3:0.00}", c, rec?.stage, comp.VisualScaleFor(p), comp.HueFor(p)));
            }
            comp.DebugSetCharge(p, 0f);
            p.Destroy();
            return "maxScale=" + ExplosiveGrowthSettings.maxOvergrowthScale.ToString("0.00") + " " + string.Join(" ", parts);
        }

        /// <summary>EXPLOSIVE_GROWTH_MERGE_COMES_HOME. A field written through jawa/mod_settings_field does not run
        /// WriteSettings, so a registry-affecting setting (minGrowDaysToSoak, minGrowDaysToBoost, cavePlantsNeverSoak)
        /// only takes effect after this rebuild. Returns the same read as ProofScope.</summary>
        public static string ProofRebuild(Map map)
        {
            if (!RM_ExplosiveGrowthRegistry.TryRebuild("ProofRebuild")) return "ERROR rebuild failed (see the log)";
            return ProofScope(map);
        }

        /// <summary>TEST-ONLY: put every biome in scope (RM_ExplosiveGrowthRegistry.TestScopeAll, never Scribed) and
        /// rebuild, so the suite can stage on a quicktest map without writing the player's settings.</summary>
        public static string ProofTestScopeAllOn(Map map)
        {
            return SetTestScopeAll(map, true);
        }

        /// <summary>TEST-ONLY: clear the override and rebuild.</summary>
        public static string ProofTestScopeAllOff(Map map)
        {
            return SetTestScopeAll(map, false);
        }

        // The flag and the table move together: a failed rebuild puts the previous flag back.
        private static string SetTestScopeAll(Map map, bool on)
        {
            bool was = RM_ExplosiveGrowthRegistry.TestScopeAll;
            RM_ExplosiveGrowthRegistry.TestScopeAll = on;
            if (!RM_ExplosiveGrowthRegistry.TryRebuild("ProofTestScopeAll"))
            {
                RM_ExplosiveGrowthRegistry.TestScopeAll = was;
                return "ERROR rebuild failed (see the log); testScopeAll left at " + was;
            }
            return ProofScope(map);
        }

        /// <summary>The scope as the live engine holds it (owner, 2026-10-16: a BIOME scope): is this map's biome in
        /// scope, is it one of Baroque Biomes' own biomes (then the default-off arm cannot be seen here), how many home
        /// biomes loaded, and what forces every biome in.</summary>
        public static string ProofScope(Map map)
        {
            BiomeDef biome = map?.Biome;
            return "home=" + (ExplosiveGrowthMod.Home?.PackageId ?? "NONE")
                   + " option=" + ExplosiveGrowthSettings.nativesSameRuleInOtherBiomes
                   + " forcedBy=" + (RM_ExplosiveGrowthRegistry.ScopeForcedBy ?? "none")
                   + " testScopeAll=" + RM_ExplosiveGrowthRegistry.TestScopeAll
                   + " mapBiome=" + (biome?.defName ?? "NONE")
                   + " mapBiomeIsHome=" + (biome != null && RM_ExplosiveGrowthRegistry.HomeBiomes.Contains(biome))
                   + " biomeInScope=" + RM_ExplosiveGrowthRegistry.BiomeInScope(biome)
                   + " homeBiomes=" + RM_ExplosiveGrowthRegistry.HomeBiomes.Count
                   + " soaking=" + RM_ExplosiveGrowthRegistry.CountSoaking
                   + " dry=" + RM_ExplosiveGrowthRegistry.CountByArchetype[0]
                   + " wet=" + RM_ExplosiveGrowthRegistry.CountByArchetype[1]
                   + " fire=" + RM_ExplosiveGrowthRegistry.CountByArchetype[2]
                   + " exempt=" + RM_ExplosiveGrowthRegistry.CountByArchetype[3]
                   + " vanilla=" + RM_ExplosiveGrowthRegistry.CountByArchetype[4]
                   + " tidallyLocked=" + RM_ExplosiveGrowthRegistry.TidallyLocked;
        }

        // ── EXPLOSIVE_GROWTH_RULED_REWRITE (spec 2026-10-16): state reads of the ruled rules ──

        /// <summary>The first plantable def of an archetype. tree: a tree (tree_burst_design §2) with a limited life, else a
        /// non-tree, non-woody plant with a harvest that cycles on the default (Churn) top. mortal: for trees, limited life (true) or unlimited (false).</summary>
        private static ThingDef FirstOf(Map map, RM_Archetype a, bool tree, bool mortal = true, bool rupture = false)
        {
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d.plant == null || d.plant.growDays < 1f) continue;
                RM_PlantProfile p = RM_ExplosiveGrowthRegistry.For(d);
                if (p == null || p.archetype != a || p.isTree != tree) continue;
                if (tree && (d.plant.LimitedLifespan != mortal || (p.top == RM_GrowthTop.Rupture) != rupture)) continue;
                if (!tree && (p.woody || !p.Soaks || d.plant.harvestedThingDef == null || d.plant.harvestYield <= 0f)) continue;
                // the dry/wet cycle subjects must run the DEFAULT top: a Slime/Tinder/Rupture/Flush/Burst row ends in its own
                // top whatever churnEnabled says (live walk 2026-10-17: AB_Slimecasia, a Slime row, was picked and the churn
                // chains read its slime top as "churn off still destroys the plant")
                if (!tree && p.top != RM_GrowthTop.Churn) continue;
                if (d.plant.cavePlant || d.plant.interferesWithRoof) continue;
                if (CellFinder.TryFindRandomCellNear(map.Center, map, 25, c => d.CanEverPlantAt(c, map), out _)) return d;
            }
            return null;
        }

        private static Plant PlaceDef(Map map, ThingDef def, float growth)
        {
            if (def == null) return null;
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 25, c => c.Standable(map) && c.GetPlant(map) == null
                    && c.GetEdifice(map) == null && !c.Roofed(map) && def.CanEverPlantAt(c, map)
                    && !RM_ExplosiveGrowthRegistry.IsNaturalWater(c.GetTerrain(map)), out IntVec3 cell)) return null;
            Plant p = (Plant)ThingMaker.MakeThing(def);
            p.Growth = growth;
            GenSpawn.Spawn(p, cell, map);
            return p;
        }

        private static Thing Spill(Map map, IntVec3 c)
        {
            ThingDef f = RM_ExplosiveGrowthDefOf.RM_Filth_WaterSpill;
            if (f == null || !FilthMaker.TryMakeFilth(c, map, f)) return null;
            return c.GetThingList(map).FirstOrDefault(t => t.def == f);
        }

        /// <summary>The §2.5 rate table, live: r for a dry native dry and on a water spill, a dry-land tree (x0.1 dry, x1 wet: tree_burst_design T2), a wet native,
        /// a vanilla plant with and without water 2 cells away, then the spill consumed by a fire. rain=1 means it is raining
        /// on the map (every unroofed cell is wet): the dry arms then read UNMEASURED.</summary>
        public static string ProofRules(Map map)
        {
            map = map ?? Find.CurrentMap;
            var comp = RM_MapComponent_ExplosiveGrowth.For(map);
            if (comp == null) return "ERROR no map component";
            var parts = new List<string>();
            int now = Find.TickManager.TicksGame;
            parts.Add("rain=" + (map.weatherManager.RainRate > 0.05f ? 1 : 0));
            var placed = new List<Thing>();
            try
            {
                void Arm(string key, ThingDef def)
                {
                    Plant p = PlaceDef(map, def, 0.5f);
                    if (p == null) { parts.Add(key + "=NONE"); return; }
                    placed.Add(p);
                    RM_PlantProfile prof = RM_ExplosiveGrowthRegistry.For(p.def);
                    float dry = comp.MoistureFactorFor(p, prof);
                    Thing w = Spill(map, p.Position);
                    float wet = comp.MoistureFactorFor(p, prof);
                    parts.Add(string.Format("{0}={1} {0}Produce={5} {0}Dry={2:0.0000} {0}Wet={3:0.0000} {0}Spill={4}", key, p.def.defName, dry, wet, w != null,
                        p.def.plant.harvestedThingDef?.defName ?? "NONE"));
                    if (w != null)
                    {
                        int used = RM_WetSources.Consume(comp, p.Position, prof.liquids, now);
                        parts.Add(string.Format("{0}Consumed={1} {0}AfterUse={2:0.0000}", key, used, comp.MoistureFactorFor(p, prof)));
                        if (!w.Destroyed) w.Destroy();
                    }
                }
                Arm("dry", FirstOf(map, RM_Archetype.DryNative, false));
                Arm("tree", FirstOf(map, RM_Archetype.DryNative, true));
                Arm("wetn", FirstOf(map, RM_Archetype.WetNative, false));

                Plant v = PlaceDef(map, DefDatabase<ThingDef>.GetNamedSilentFail("Plant_Rice"), 0.5f);
                if (v == null) parts.Add("van=NONE");
                else
                {
                    placed.Add(v);
                    RM_PlantProfile vp = RM_ExplosiveGrowthRegistry.For(v.def);
                    float vDry = comp.MoistureFactorFor(v, vp);
                    IntVec3 near = v.Position + new IntVec3(2, 0, 0), far = v.Position + new IntVec3(3, 0, 0);
                    Thing wn = near.InBounds(map) ? Spill(map, near) : null;
                    float vNear = comp.MoistureFactorFor(v, vp);
                    if (wn != null && !wn.Destroyed) wn.Destroy();
                    Thing wf = far.InBounds(map) ? Spill(map, far) : null;
                    float vFar = comp.MoistureFactorFor(v, vp);
                    if (wf != null && !wf.Destroyed) wf.Destroy();
                    parts.Add(string.Format("van={0} vanArch={1} vanDry={2:0.0000} vanNear2={3:0.0000} vanFar3={4:0.0000} vanSpills={5}{6}",
                        v.def.defName, vp?.archetype, vDry, vNear, vFar, wn != null ? 1 : 0, wf != null ? 1 : 0));
                    // dormancy: one TickLong at r 0.1 adds ~200 to the age, not 2000
                    var ageRef = HarmonyLib.AccessTools.FieldRefAccess<Plant, int>("ageInt");
                    int a0 = ageRef(v);
                    v.TickLong();
                    parts.Add("vanAgeStep=" + (v.Destroyed ? -1 : ageRef(v) - a0));
                }
                // the outcome odds with the live settings
                ThingDef dd = FirstOf(map, RM_Archetype.DryNative, false);
                RM_PlantProfile dp = dd != null ? RM_ExplosiveGrowthRegistry.For(dd) : null;
                if (dp != null)
                {
                    int burst = 0, fruit = 0, n = 3000;
                    for (int i = 0; i < n; i++)
                    {
                        RM_Outcome o = RM_ExplosiveGrowthKernel.ResolveOutcome(dp.archetype, (byte)RM_TopResolver.Effective(RM_GrowthTop.Churn),
                            -1f, ExplosiveGrowthSettings.defaultRuptureChance, Rand.Value, false, true, ExplosiveGrowthSettings.burstEnabled);
                        if (o == RM_Outcome.Burst) burst++; else if (o == RM_Outcome.Fruit) fruit++;
                    }
                    parts.Add(string.Format("burstShare={0:0.000} fruitShare={1:0.000}", burst / (float)n, fruit / (float)n));
                }
                parts.Add("tidallyLocked=" + RM_ExplosiveGrowthRegistry.TidallyLocked);
            }
            finally
            {
                foreach (Thing t in placed) if (!t.Destroyed) t.Destroy();
            }
            return string.Join(" ", parts);
        }

        // ── TREE_BURST_BUILD_LITRES_BUY_YEARS (tree_burst_design_2026-10-17.md §3, §4, §6a): the tree rows, read live ──

        private static int CountNear(Map map, IntVec3 c, ThingDef def, float radius)
        {
            if (def == null) return 0;
            int n = 0;
            foreach (IntVec3 x in GenRadial.RadialCellsAround(c, radius, true))
            {
                if (!x.InBounds(map)) continue;
                List<Thing> things = x.GetThingList(map);
                for (int i = 0; i < things.Count; i++) if (things[i].def == def) n += things[i].stackCount;
            }
            return n;
        }

        private static void ClearNear(Map map, IntVec3 c, float radius, HashSet<int> keep)
        {
            var doomed = new List<Thing>();
            foreach (IntVec3 x in GenRadial.RadialCellsAround(c, radius, true))
            {
                if (!x.InBounds(map)) continue;
                foreach (Thing t in x.GetThingList(map))
                    if (!(t is Pawn) && !keep.Contains(t.thingIDNumber) && (t.def.category == ThingCategory.Item
                        || t.def.category == ThingCategory.Plant || t.def.category == ThingCategory.Filth
                        || t.def.category == ThingCategory.Building)) doomed.Add(t);   // only what the arm made: stumps, logs, seedlings
            }
            foreach (Thing t in doomed) if (!t.Destroyed) t.Destroy();
        }

        private static HashSet<int> IdsNear(Map map, IntVec3 c, float radius)
        {
            var ids = new HashSet<int>();
            foreach (IntVec3 x in GenRadial.RadialCellsAround(c, radius, true))
                if (x.InBounds(map)) foreach (Thing t in x.GetThingList(map)) ids.Add(t.thingIDNumber);
            return ids;
        }

        /// <summary>The tree rows: (1) a jungle tree does not cycle at maturity and runs x4 young / x1 grown; its end of life
        /// bursts. (2) a dry-land tree reads x0.1 dry / x1 wet; a spill buys 400/40 = 10 days (growth when young); a drink past
        /// its lifespan bursts it with logs and seedlings. (3) the same tree crossing its lifespan with no water falls (vanilla
        /// Dying, no burst). (4) an unlimited-life tree drinks a spill as growth and never bursts. Each arm stages its own plant
        /// and removes what it placed and what the burst threw. growthRate=0 on an arm means the site cannot grow it now
        /// (night, cold): the drink rows then read UNMEASURED.</summary>
        public static string ProofTreeLife(Map map)
        {
            map = map ?? Find.CurrentMap;
            var comp = RM_MapComponent_ExplosiveGrowth.For(map);
            if (comp == null) return "ERROR no map component";
            var parts = new List<string> { "trees=" + RM_ExplosiveGrowthRegistry.CountTrees, "rain=" + (map.weatherManager.RainRate > 0.05f ? 1 : 0),
                "litresPerSpill=" + RM_TreeLife.LitresPerSpill, "perDay=" + ExplosiveGrowthSettings.treeLitresPerDayOfLife };
            var placed = new List<Thing>();
            try
            {
                Plant Place(ThingDef def, float growth, out HashSet<int> before)
                {
                    before = null;
                    Plant p = PlaceDef(map, def, growth);
                    if (p == null) return null;
                    placed.Add(p);
                    before = IdsNear(map, p.Position, 4.9f);
                    return p;
                }

                // (1) jungle tree
                ThingDef jd = FirstOf(map, RM_Archetype.WetNative, true);
                Plant j = Place(jd, 1f, out HashSet<int> jKeep);
                if (j == null) parts.Add("jungle=NONE");
                else
                {
                    RM_PlantProfile jp = RM_ExplosiveGrowthRegistry.For(j.def);
                    parts.Add(string.Format("jungle={0} jungleCycles={1} jungleMatureR={2:0.0000}", j.def.defName, comp.CyclesHere(j, jp),
                        comp.MoistureFactorFor(j, jp)));
                    j.Growth = 0.5f;
                    parts.Add(string.Format("jungleYoungR={0:0.0000}", comp.MoistureFactorFor(j, jp)));
                    j.Growth = 1f;
                    IntVec3 jc = j.Position;
                    RM_TreeLife.SetAge(j, j.def.plant.LifespanTicks - 500);
                    RM_TopResolver.LastTreeBurst = "";
                    j.TickLong();
                    parts.Add(string.Format("jungleEndBurst={0} jungleBurst=[{1}]", j.Destroyed, RM_TopResolver.LastTreeBurst.Replace(' ', ',').Replace('=', ':')));
                    ClearNear(map, jc, 4.9f, jKeep);
                }

                // (2) dry-land tree: rates, a young drink, a water-driven death
                ThingDef td = FirstOf(map, RM_Archetype.DryNative, true);
                Plant t = Place(td, 0.2f, out HashSet<int> tKeep);
                if (t == null) parts.Add("tree=NONE");
                else
                {
                    RM_PlantProfile tp = RM_ExplosiveGrowthRegistry.For(t.def);
                    IntVec3 tc = t.Position;
                    parts.Add(string.Format("tree={0} treeGrowDays={1} treeLifeDays={2:0} treeCycles={3} treeDryR={4:0.0000} treeGrowthRate={5:0.000}",
                        t.def.defName, t.def.plant.growDays, t.def.plant.LifespanDays, comp.CyclesHere(t, tp), comp.MoistureFactorFor(t, tp), t.GrowthRate));
                    Thing w = Spill(map, tc);
                    parts.Add(string.Format("treeWetR={0:0.0000} treeSpill={1}", comp.MoistureFactorFor(t, tp), w != null));
                    if (w != null)
                    {
                        float g0 = t.Growth;
                        RM_TreeLife.LastDrink = default(RM_DrinkResult);
                        t.TickLong();
                        parts.Add(string.Format("treeDrinkDays={0:0.000} treeYoungGain={1:0.0000} treeSpillUsed={2}",
                            RM_TreeLife.LastDrink.days, t.Growth - g0, w.Destroyed));
                    }
                    // water-driven death: grown, one day short of its lifespan, a spill on the cell
                    t.Growth = 1f;
                    RM_TreeLife.SetAge(t, t.def.plant.LifespanTicks - RM_ExplosiveGrowthKernel.TicksPerDay);
                    Thing w2 = Spill(map, tc);
                    RM_TopResolver.LastTreeBurst = "";
                    t.TickLong();
                    parts.Add(string.Format("treeWaterBurst={0} treeBurst=[{1}] treeSeedlingsNear={2}", t.Destroyed && w2 != null,
                        RM_TopResolver.LastTreeBurst.Replace(' ', ',').Replace('=', ':'), CountNear(map, tc, td, 3.9f)));
                    ClearNear(map, tc, 4.9f, tKeep);

                    // (3) natural death: the same tree crossing its lifespan with no water on its cell falls (vanilla Dying)
                    Plant n = Place(td, 1f, out HashSet<int> nKeep);
                    if (n == null) parts.Add("natural=NONE");
                    else
                    {
                        IntVec3 nc = n.Position;
                        bool wetCell = RM_WetSources.IsWet(comp, nc, tp.liquids, Find.TickManager.TicksGame);
                        // 50 ticks short: even a dry tree's dormant step (x0.1 = 200 ticks) carries it over
                        RM_TreeLife.SetAge(n, n.def.plant.LifespanTicks - 50);
                        RM_TopResolver.LastTreeBurst = "";
                        n.TickLong();
                        parts.Add(string.Format("naturalWetCell={0} naturalBurst={1} naturalDying={2}", wetCell,
                            RM_TopResolver.LastTreeBurst.Length > 0, !n.Destroyed && n.Dying));
                        ClearNear(map, nc, 4.9f, nKeep);
                    }
                }

                // (4) unlimited life: a spill is growth, never an end
                ThingDef od = FirstOf(map, RM_Archetype.DryNative, true, mortal: false);
                Plant o = Place(od, 0.5f, out HashSet<int> oKeep);
                if (o == null) parts.Add("immortal=NONE");
                else
                {
                    IntVec3 oc = o.Position;
                    Thing w = Spill(map, oc);
                    float g0 = o.Growth;
                    RM_TopResolver.LastTreeBurst = "";
                    o.TickLong();
                    parts.Add(string.Format("immortal={0} immortalSpill={1} immortalGain={2:0.0000} immortalBurst={3} immortalAlive={4}",
                        o.def.defName, w != null, o.Growth - g0, RM_TopResolver.LastTreeBurst.Length > 0, !o.Destroyed));
                    ClearNear(map, oc, 4.9f, oKeep);
                }
            }
            finally
            {
                foreach (Thing t in placed) if (!t.Destroyed) t.Destroy();
            }
            return string.Join(" ", parts);
        }
    }
}
