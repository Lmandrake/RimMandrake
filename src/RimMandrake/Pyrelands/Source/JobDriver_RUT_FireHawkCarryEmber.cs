using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1, mechanism 3 — the flying half of the fire-hawk's
    /// twig (RUT_ruled_commissions_wave2.md §7c: "fly a short sortie and ignite
    /// one flammable cell N cells beyond the fire's edge").
    ///
    /// TargetA is the fire the ember comes FROM; TargetB is the cell it goes TO.
    /// Four toils: go to the fire's edge, take an ember, carry it out, drop it.
    ///
    /// The ember is not a Thing. Making it one would mean a def, a graphic, a
    /// carry-tracker interaction and a stack of failure cases (what happens when
    /// the hawk is downed mid-flight, does the ember burn the hawk, does it
    /// deteriorate) for a visual that lasts ninety ticks. The flecks thrown in the
    /// take toil are the visual; the job itself is the mechanism.
    ///
    /// FAILURE IS SILENT AND SAFE. If no free fire still burns at the source cell
    /// when the hawk gets there, the job ends and nothing is lit: the spread-only
    /// law (§7c) holds at the take. If the destination has stopped being flammable
    /// by the time the hawk arrives, TryStartFireIn simply returns false. Either
    /// way the cooldown was already charged by the job-giver, so a hawk cannot
    /// thrash against a bad target.
    ///
    /// The take reads the source CELL (TargetC), not the Fire thing (map t,
    /// 2026-11-07): a grass fire burns out in seconds, and the job failed the
    /// moment its one Fire despawned, on the way in or with the ember already in
    /// the beak. Two hawks over a 700-fire burn started sorties for 2.75 days and
    /// dropped one ember. Now any fire still burning beside that cell gives the
    /// ember, and once taken it is carried whatever its source does.
    /// </summary>
    public class JobDriver_RUT_FireHawkCarryEmber : JobDriver
    {
        private const TargetIndex SourceFireInd = TargetIndex.A;
        private const TargetIndex IgniteCellInd = TargetIndex.B;
        private const TargetIndex SourceCellInd = TargetIndex.C;

        /// <summary>How near the source cell a fire must still burn when the hawk arrives to give it an ember.</summary>
        private const float EmberReach = 2.9f;

        /// <summary>Script probe (jawa/static_call, FIREHAWK_EMBER_FIX_WALKS_ITS_TWIG): the hawk's flight STATE, never a
        /// visual. jobFlying is what Pawn_FlightTracker.Notify_JobStarted decided for the current job; cooldown &gt; 0 means
        /// vanilla may have refused the take-off (a walked sortie is then lawful).</summary>
        public static string ProbeFlight(Pawn p)
        {
            if (p == null) return "pawn=null";
            int cooldown = p.flight == null ? -1 : HarmonyLib.Traverse.Create(p.flight).Field("flightCooldownTicks").GetValue<int>();
            return "job=" + (p.CurJobDef?.defName ?? "none") + " jobFlying=" + (p.CurJob?.flying ?? false)
                + " flying=" + p.Flying + " canEverFly=" + (p.flight?.CanEverFly ?? false) + " cooldown=" + cooldown;
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            // Nothing is reserved: a fire is not a claimable resource, the
            // destination cell is not owned, and reservations on a wild (or tamed,
            // undrafted) animal's self-directed job buy nothing.
            return true;
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            // A job saved before TargetC existed takes its source cell from the fire, if that is still there.
            if (!job.GetTarget(SourceCellInd).IsValid && job.GetTarget(SourceFireInd).HasThing && job.GetTarget(SourceFireInd).Thing.Spawned)
            {
                job.SetTarget(SourceCellInd, job.GetTarget(SourceFireInd).Thing.Position);
            }
            this.FailOn(() => !job.GetTarget(SourceCellInd).IsValid);

            yield return Toils_Goto.GotoCell(SourceCellInd, PathEndMode.Touch);

            // No fire left at the source, no ember: the spread-only law expressed as a fail condition rather than a decision.
            Toil takeEmber = Toils_General.Wait(PyrelandsTuning.FireHawkTakeEmberTicks, SourceCellInd);
            takeEmber.AddPreInitAction(delegate
            {
                if (!FireStillBurns(job.GetTarget(SourceCellInd).Cell, pawn.Map))
                {
                    EndJobWith(JobCondition.Incompletable);
                }
            });
            takeEmber.tickAction = delegate
            {
                if (pawn.IsHashIntervalTick(15))
                {
                    FleckMaker.ThrowMicroSparks(pawn.DrawPos, pawn.Map);
                }
            };
            yield return takeEmber;

            Toil carry = Toils_Goto.GotoCell(IgniteCellInd, PathEndMode.OnCell);
            carry.AddPreTickAction(delegate
            {
                GameComponent_RM_FireHawkSighting.NoteCarrying(pawn);   // the first-sighting letter: every carry, however short
                if (pawn.IsHashIntervalTick(20) && pawn.Map != null)
                {
                    FleckMaker.ThrowMicroSparks(pawn.DrawPos, pawn.Map);
                }
            });
            yield return carry;

            Toil dropEmber = ToilMaker.MakeToil("RUT_FireHawkDropEmber");
            dropEmber.defaultCompleteMode = ToilCompleteMode.Instant;
            dropEmber.initAction = delegate
            {
                IntVec3 cell = job.GetTarget(IgniteCellInd).Cell;
                if (!cell.IsValid || !cell.InBounds(pawn.Map))
                {
                    return;
                }

                // instigator: the hawk. That is what makes a TAMED hawk's
                // spreading show up as the colony's arson debt in
                // MapComponent_BurnLine — the ruled price of fire-falconry
                // (§7d: "the fire a tamed hawk spreads is still nobody's friend").
                CompFireHawkSpread comp = pawn.TryGetComp<CompFireHawkSpread>();
                float size = comp?.Props.startFireSize ?? PyrelandsTuning.SmoulderFireSize;

                bool lit = FireUtility.TryStartFireIn(cell, pawn.Map, size, pawn);
                if (lit)
                {
                    FleckMaker.ThrowFireGlow(cell.ToVector3Shifted(), pawn.Map, 1f);
                }
                comp?.Notify_EmberDropped(cell, lit);
            };
            yield return dropEmber;
        }

        /// <summary>A free ground fire (not a burning pawn or wall) within EmberReach of the source cell.</summary>
        private static bool FireStillBurns(IntVec3 cell, Map map)
        {
            if (map == null || !cell.IsValid) return false;
            int n = GenRadial.NumCellsInRadius(EmberReach);
            for (int i = 0; i < n; i++)
            {
                IntVec3 c = cell + GenRadial.RadialPattern[i];
                if (!c.InBounds(map)) continue;
                List<Thing> here = map.thingGrid.ThingsListAtFast(c);
                for (int k = 0; k < here.Count; k++)
                {
                    if (here[k] is Fire { parent: null } f && f.Spawned) return true;
                }
            }
            return false;
        }
    }
}
