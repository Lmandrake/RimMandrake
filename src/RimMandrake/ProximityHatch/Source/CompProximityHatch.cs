using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.ProximityHatch
{
    // Requires a sibling CompProperties_Hatcher on the same ThingDef (the
    // vanilla egg comp, RimWorld/CompHatcher.cs). This comp never
    // re-implements pawn generation or spawning: it forces the exact same
    // CompHatcher.Hatch() every vanilla/modded egg already uses, just early
    // and on a different trigger. Everything CompHatcher already gets right
    // - stacked-egg splitting, TemperatureDamaged spoiling into an
    // unfertilized egg instead of hatching, parent-relation wiring, filth -
    // comes along for free because it is the same call.
    public class CompProximityHatch : ThingComp
    {
        private int ticksUntilScan;
        private bool hatchFired;

        public CompProperties_ProximityHatch Props => (CompProperties_ProximityHatch)props;

        public override void CompTick()
        {
            base.CompTick();
            if (hatchFired || !parent.Spawned) return;

            if (--ticksUntilScan > 0) return;
            ticksUntilScan = Props.scanIntervalTicks;
            RunScan();
        }

        // Split out so a bridge/quicktest can drive one deterministic scan
        // without stepping ticks and hoping the cadence lined up - same
        // shape as CompPitCoverTrigger.RunScan in this codebase.
        public void RunScan()
        {
            if (hatchFired || !parent.Spawned) return;

            CompHatcher hatcher = parent.GetComp<CompHatcher>();
            if (hatcher == null) return; // no vanilla hatch comp on this def - nothing to trigger, stay dormant

            Map map = parent.Map;
            if (map == null) return;

            Pawn nearest = null;
            int nearestDistSq = int.MaxValue;
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(parent.Position, map, Props.triggerRadius, useCenter: true))
            {
                if (t is Pawn p && p.Spawned && !p.Dead && p.RaceProps.IsFlesh)
                {
                    int distSq = (p.Position - parent.Position).LengthHorizontalSquared;
                    if (distSq < nearestDistSq)
                    {
                        nearestDistSq = distSq;
                        nearest = p;
                    }
                }
            }

            if (nearest != null)
            {
                Trigger(hatcher, nearest);
            }
        }

        private void Trigger(CompHatcher hatcher, Pawn triggeringPawn)
        {
            hatchFired = true; // set before Hatch() destroys parent, so a re-entrant tick can never double-fire

            Map map = parent.Map;
            IntVec3 pos = parent.PositionHeld;
            PawnKindDef expectedKind = hatcher.Props.hatcherPawn;

            hatcher.Hatch(); // vanilla spawn/relation/filth logic, completely unmodified; destroys parent internally

            if (map == null || expectedKind == null) return;

            // Hatch() runs synchronously and has already returned by the
            // time this line executes, so anything of the expected kind now
            // sitting at the egg's own former cell is what it just produced.
            // CompHatcher.Hatch() does not hand back a pawn reference to its
            // caller, so this reads the map state it already wrote rather
            // than reaching into its internals or re-deriving the pawn some
            // other way.
            foreach (Thing t in pos.GetThingList(map))
            {
                if (t is Pawn hatchling && hatchling.kindDef == expectedKind)
                {
                    Aggro(hatchling, triggeringPawn);
                }
            }
        }

        // The vanilla "spawn something and make it attack" pattern for an
        // ambush beat - see RimWorld/SignalAction_Ambush.cs,
        // GenStep_ManhunterPack.cs and IncidentWorker_Ambush_ManhunterPack.cs,
        // all of which wake a freshly spawned animal with
        // MentalStateDefOf.ManhunterPermanent rather than hand-building
        // hostility from scratch. Reused here rather than invented. A
        // permanent manhunter keeps attacking on its own after this tick, so
        // the forced AttackMelee job below only has to cover the very first
        // frame - it is what makes the beat read as "ambushed YOU" and not
        // "a manhunter is now loose somewhere nearby".
        private void Aggro(Pawn hatchling, Pawn triggeringPawn)
        {
            if (hatchling.RaceProps.Animal && hatchling.mindState != null)
            {
                hatchling.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.ManhunterPermanent);
            }

            if (hatchling.Spawned && triggeringPawn.Spawned && hatchling.jobs != null)
            {
                Job job = JobMaker.MakeJob(JobDefOf.AttackMelee, triggeringPawn);
                hatchling.jobs.StartJob(job, JobCondition.InterruptForced);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref ticksUntilScan, "ticksUntilScan", 0);
            Scribe_Values.Look(ref hatchFired, "hatchFired", false);
        }
    }
}
