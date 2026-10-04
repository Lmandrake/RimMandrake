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
    }
}
