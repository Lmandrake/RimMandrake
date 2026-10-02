using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.Pits
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
    // Only live while the host is COVERED (armed). An uncovered pit is an
    // obvious hole, not a trap.
    //
    // PIT_LEGACY_CODE_RETIRE_1 (2026-10-02): the host used to be the retired
    // Building_OpenPit (a pit as a building). The comp now talks to any
    // IPitCoverHost; no def carries it until PIT_COVER_FALL_REWIRE_1 builds
    // the multi-cell cover over D=4 cells whose Spring drops pawns in.
    public interface IPitCoverHost
    {
        bool Covered { get; }
        bool Sprung { get; }
        PitCoverTier CoverTier { get; }
        void Spring(List<Pawn> fallers);
    }

    public class CompPitCoverTrigger : ThingComp
    {
        private int ticksUntilScan;

        public CompProperties_PitCoverTrigger Props => (CompProperties_PitCoverTrigger)props;

        private IPitCoverHost Pit => parent as IPitCoverHost;

        public override void CompTick()
        {
            base.CompTick();
            if (Pit == null || !Pit.Covered || Pit.Sprung) return;

            if (--ticksUntilScan > 0) return;
            ticksUntilScan = Props.scanIntervalTicks;
            RunScan();
        }

        // The scan body, callable on demand. Split out so the quicktest matrix
        // can drive one deterministic scan from the bridge instead of stepping
        // ticks and hoping the cadence lined up; CompTick's behaviour is
        // unchanged.
        public void RunScan()
        {
            if (Pit == null || !Pit.Covered || Pit.Sprung) return;
            // Mod option: coarse gate, trapTriggerEnabled. Off means an armed
            // cover simply never sums mass or springs - no NRE, arming/
            // disarming still work, the pit just never fires on its own.
            if (!RimMandrakeFlowWorksSettings.trapTriggerEnabled) return;

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
                    // Unlike vanilla Building_Trap (KnowsOfTrap / a near-zero
                    // SpringChance for the trap's own faction), nothing here
                    // excluded the parent's own faction -- a colonist crossing
                    // their own armed pit sprang it exactly as readily as a
                    // raider, and the def is Standable/pathCost 30, so colonists
                    // route straight over it. A trap that captures its own
                    // colony is not the intended "raider trap" use case.
                    if (thingsHere[i] is Pawn p && !p.Dead && p.Faction != parent.Faction)
                    {
                        onCover.Add(p);
                        summedMass += p.GetStatValue(StatDefOf.Mass);
                    }
                }
            }

            float threshold = Pit.CoverTier.TriggerMassKg() * RimMandrakeFlowWorksSettings.trapSensitivityMultiplier;
            if (onCover.Count > 0 && summedMass >= threshold)
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
