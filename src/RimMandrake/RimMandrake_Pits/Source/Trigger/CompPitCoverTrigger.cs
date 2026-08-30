using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Pits
{
    // The mass-sum trigger, section 3/4 of covered_pit_traps_spec.md: "Load
    // sums - a tight raider knot can overload a plank cover together; a
    // spread line crosses." Sums StatDefOf.Mass (body mass + gear/inventory,
    // confirmed in-source: RimWorld/MassUtility.cs and CollectionsMassCalculator.cs
    // both read pawn.GetStatValue(StatDefOf.Mass) for "this pawn's total
    // weight including everything it carries") across every pawn currently
    // standing in the pit's occupied cells, and springs the trap once the sum
    // crosses the armed cover tier's rating.
    //
    // Only live while the parent pit is COVERED (armed). An uncovered pit is
    // an obvious hole, not a trap - see Building_OpenPit.
    public class CompPitCoverTrigger : ThingComp
    {
        private int ticksUntilScan;

        public CompProperties_PitCoverTrigger Props => (CompProperties_PitCoverTrigger)props;

        private Building_OpenPit Pit => (Building_OpenPit)parent;

        public override void CompTick()
        {
            base.CompTick();
            if (!Pit.Covered || Pit.Sprung) return;

            if (--ticksUntilScan > 0) return;
            ticksUntilScan = Props.scanIntervalTicks;

            float summedMass = 0f;
            List<Pawn> onCover = new List<Pawn>();
            CellRect rect = parent.OccupiedRect();
            Map map = parent.Map;
            if (map == null) return;

            foreach (IntVec3 cell in rect)
            {
                List<Thing> thingsHere = cell.GetThingList(map);
                for (int i = 0; i < thingsHere.Count; i++)
                {
                    if (thingsHere[i] is Pawn p && !p.Dead)
                    {
                        onCover.Add(p);
                        summedMass += p.GetStatValue(StatDefOf.Mass);
                    }
                }
            }

            if (onCover.Count > 0 && summedMass >= Pit.CoverTier.TriggerMassKg())
            {
                Pit.Spring(onCover);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksUntilScan, "ticksUntilScan", 0);
        }
    }
}
