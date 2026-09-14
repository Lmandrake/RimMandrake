using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 S1 build pass (sump_kit_spec.md "the poured moat +
    // command ignition" > "the distant column": "cosmetic - a tall smoke
    // mote/overlay while >= N blaze cells live. INVENTED: N=20. No world-map
    // mechanic in v1."). Generic map-scoped threshold tracker, not Sump-
    // specific: any RM_CompTimedTerrainBurn instance with
    // marksColumnSource=true registers/deregisters itself here on spawn/
    // despawn (see that class), and this component throws a big smoke fleck
    // at the live sources' centroid on a slow pulse once the count clears
    // the threshold. Every non-abstract MapComponent subclass is
    // auto-instantiated per map by the engine (verified,
    // Verse/Map.cs:710-713, FillComponents/AllSubclassesNonAbstract) — no
    // XML wiring needed for this class to exist on every map.
    public class RM_MapComponent_ThresholdSmokeColumn : MapComponent
    {
        private readonly HashSet<Thing> sources = new HashSet<Thing>();
        private int ticksUntilNextPulse;

        // INVENTED (spec S1's own values, both explicitly marked INVENTED
        // there): threshold N=20 live blaze cells; pulse/size tuned for
        // "visible for a day's travel" read at map scale, not measured
        // against anything.
        private const int ColumnThreshold = 20;
        private const int TicksBetweenPulses = 250;
        private const float SmokeSize = 8f;

        public RM_MapComponent_ThresholdSmokeColumn(Map map)
            : base(map)
        {
        }

        public void Notify_SourceSpawned(Thing t)
        {
            sources.Add(t);
        }

        public void Notify_SourceDespawned(Thing t)
        {
            sources.Remove(t);
        }

        public override void MapComponentTick()
        {
            if (sources.Count < ColumnThreshold)
            {
                return;
            }
            if (--ticksUntilNextPulse > 0)
            {
                return;
            }
            ticksUntilNextPulse = TicksBetweenPulses;

            sources.RemoveWhere((Thing t) => t == null || !t.Spawned);
            if (sources.Count < ColumnThreshold)
            {
                return;
            }

            int sumX = 0;
            int sumZ = 0;
            foreach (Thing t in sources)
            {
                sumX += t.Position.x;
                sumZ += t.Position.z;
            }
            IntVec3 center = new IntVec3(sumX / sources.Count, 0, sumZ / sources.Count);
            if (center.InBounds(map))
            {
                FleckMaker.ThrowSmoke(center.ToVector3Shifted(), map, SmokeSize);
            }
        }
    }
}
