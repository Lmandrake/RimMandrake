using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// The fire-hawk's coarse fuel map (owner, 2026-11-13: "Carry distance should actually be anywhere on the map, unlimited. To
    /// the largest fuel source easily found."): fuel cells per FireHawkFuelBucket square, counted by RM_FireHawkKernel.BucketFuel.
    /// Lazy: nothing ticks. The first sortie after the counts are FireHawkFuelRefreshTicks old rescans the map once (every cell a
    /// fog and roof read and one walk of its thing list, ~62,500 cells on a 250 map), so a map with no hawk pays nothing and one
    /// with hawks pays at most one scan an in-game hour. Unsaved: rebuilt on the first sortie after a load.
    /// </summary>
    public class MapComponent_RM_FireHawkFuel : MapComponent
    {
        /// <summary>Younger grass than this is a scar's sprouts, not fuel worth an ember.</summary>
        public const float MinFuelGrowth = 0.25f;

        private int[] counts;
        private int countedTick = -99999;
        private static readonly Dictionary<ThingDef, bool> FlammableDef = new Dictionary<ThingDef, bool>();

        public MapComponent_RM_FireHawkFuel(Map map) : base(map)
        {
        }

        public static MapComponent_RM_FireHawkFuel For(Map map) => map?.GetComponent<MapComponent_RM_FireHawkFuel>();

        /// <summary>The fuel counts, rescanned when older than FireHawkFuelRefreshTicks.</summary>
        public int[] Counts
        {
            get
            {
                int now = Find.TickManager.TicksGame;
                if (counts == null || now - countedTick >= PyrelandsTuning.FireHawkFuelRefreshTicks)
                {
                    counts = RM_FireHawkKernel.BucketFuel(map.Size.x, map.Size.z, PyrelandsTuning.FireHawkFuelBucket, FuelCell);
                    countedTick = now;
                }
                return counts;
            }
        }

        /// <summary>Drop the cached counts: the next read rescans (the live probe, after a test site is staged).</summary>
        public void Recount()
        {
            counts = null;
        }

        /// <summary>Fuel cells on the map in the cached counts (the live probe's sanity reading).</summary>
        public int CountedCells
        {
            get
            {
                int n = 0;
                foreach (int c in Counts) n += c;
                return n;
            }
        }

        /// <summary>RM_FireHawkKernel.MapFuelCell on the engine's facts: a grown plant that burns, no fire in the cell, not fogged,
        /// not roofed. The fog and roof reads come first, so hidden ground costs no thing-list walk.</summary>
        public bool FuelCell(int x, int z)
        {
            int idx = map.cellIndices.CellToIndex(x, z);
            bool fogged = map.fogGrid.IsFogged(idx), roofed = map.roofGrid.Roofed(idx);
            if (fogged || roofed)
            {
                return false;
            }
            Plant plant = null;
            bool burning = false;
            List<Thing> things = map.thingGrid.ThingsListAtFast(idx);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Fire)
                {
                    burning = true;
                }
                else if (plant == null && things[i] is Plant p)
                {
                    plant = p;
                }
            }
            float growth = plant == null ? -1f : plant.Growth;
            return RM_FireHawkKernel.MapFuelCell(plant != null && Flammable(plant.def), growth, MinFuelGrowth, burning, fogged, roofed);
        }

        private static bool Flammable(ThingDef def)
        {
            if (!FlammableDef.TryGetValue(def, out bool f))
            {
                f = def.GetStatValueAbstract(StatDefOf.Flammability) > 0f;
                FlammableDef[def] = f;
            }
            return f;
        }
    }
}
