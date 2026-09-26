using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveGrowth
{
    /// <summary>
    /// Names the plant the bloom sows. Put it on the IncidentDef.
    /// </summary>
    public class RM_BloomBurstExtension : DefModExtension
    {
        public ThingDef bloomPlant;
        /// <summary>Fraction of eligible soaked cells that get a sprout.</summary>
        public float sowChance = 0.6f;
        /// <summary>How long the bloom keeps the floor soaked.</summary>
        public float soakHours = 24f;
    }

    /// <summary>
    /// The FLOOD_WITNESS_EVENT_1 contract (design doc §5): the map-scale
    /// invocation. The quest passes nothing but the map. The incident
    ///   1. soaks every floor cell the flood wetted — i.e. every cell this
    ///      engine currently holds as soaked (FloodedCanyon pushes its flood
    ///      footprint in); with nothing soaked it falls back to a flood-shaped
    ///      blob of open fertile ground, so the quest's stub degrades
    ///      gracefully on any map;
    ///   2. sows bloom-crop sprouts on that fresh soil, all at once;
    ///   3. and so runs the §2→§3 cycle in carpet synchrony over the following
    ///      day: sown together, they mature and charge together (±10% per
    ///      plant, so the valley goes up in waves).
    /// Intensity, terminal moment and harvest rules are this engine's, not the
    /// quest's — the bloom plant's own top decides what happens.
    /// </summary>
    public class RM_IncidentWorker_BloomBurst : IncidentWorker
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            return ExplosiveGrowthSettings.enabled && parms.target is Map map
                && !RM_ExplosiveGrowthRegistry.BiomeRefusesSoak(map.Biome);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            if (!(parms.target is Map map)) return false;
            RM_MapComponent_ExplosiveGrowth comp = RM_MapComponent_ExplosiveGrowth.For(map);
            if (comp == null) return false;

            RM_BloomBurstExtension ext = def.GetModExtension<RM_BloomBurstExtension>() ?? new RM_BloomBurstExtension();
            int soakTicks = Mathf.Max(2500, Mathf.RoundToInt(ext.soakHours * 2500f));

            List<IntVec3> floor = comp.SoakedCells.ToList();
            if (floor.Count == 0) floor = FallbackFloor(map);
            if (floor.Count == 0) return false;

            int soaked = 0, sown = 0;
            ThingDef bloom = ext.bloomPlant;
            int now = Find.TickManager.TicksGame;
            foreach (IntVec3 c in floor)
            {
                if (!comp.TrySoak(c, soakTicks)) continue;
                soaked++;
                if (bloom != null && Rand.Chance(ext.sowChance)
                    && RM_SproutRing.CanSprout(map, c, bloom, respectBuiltGround: true, comp, now))
                {
                    Plant p = (Plant)GenSpawn.Spawn(bloom, c, map);
                    p.Growth = Rand.Range(0.05f, 0.12f);
                    sown++;
                }
            }

            if (soaked == 0) return false;
            SendStandardLetter(def.letterLabel ?? "Bloom", def.letterText ?? "The soaked ground is blooming.",
                def.letterDef ?? LetterDefOf.NeutralEvent, parms, new TargetInfo(floor[floor.Count / 2], map));
            Log.Message("[RM ExplosiveGrowth] BloomBurst: soaked " + soaked + " cells, sowed " + sown + " " + (bloom?.defName ?? "(no bloom plant)"));
            return true;
        }

        private static List<IntVec3> FallbackFloor(Map map)
        {
            var result = new List<IntVec3>();
            bool Eligible(IntVec3 c) => c.InBounds(map) && !c.Roofed(map) && !c.Fogged(map)
                && c.GetTerrain(map) is TerrainDef t && !t.IsWater && !t.IsFloor
                && map.fertilityGrid.FertilityAt(c) > 0.4f && c.GetEdifice(map) == null;

            if (!CellFinderLoose.TryGetRandomCellWith(Eligible, map, 2000, out IntVec3 seed)) return result;
            int target = Mathf.Clamp(map.Area / 20, 40, 400);
            var visited = new HashSet<IntVec3> { seed };
            var frontier = new Queue<IntVec3>();
            frontier.Enqueue(seed);
            while (frontier.Count > 0 && result.Count < target)
            {
                IntVec3 c = frontier.Dequeue();
                if (!Eligible(c)) continue;
                result.Add(c);
                foreach (IntVec3 d in GenAdj.CardinalDirections)
                {
                    IntVec3 n = c + d;
                    if (visited.Add(n) && Rand.Value < 0.88f) frontier.Enqueue(n);
                }
            }
            return result;
        }
    }
}
