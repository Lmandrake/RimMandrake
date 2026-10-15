using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.GimmeSomeSlack.Aerial
{
    /// <summary>
    /// GSS_RESTRING_DECIDE_FREE_INSTANT_SPLICE. Owner by card 2026-10-15: "Re-stringing a cut power line is instant and free...
    /// What ships? -> Make it a colonist job". Design 2.6: "Re-string: gizmo 'Re-string cut span' on either anchor -> a pawn
    /// job (300 ticks at the anchor)". The gizmo now only MARKS the anchor (designation RM_RestringSpan, a second click takes
    /// the mark off); a Construction worker walks to the cut (the cell the fallen half lies toward, or the anchor when that
    /// cell cannot be stood on or reached), works <see cref="AerialMath.RestringTicks"/> at his construction speed, and the
    /// span is restored (CompAerialAnchor.Restring) when the job ends. Gated by the overhead-lines master switch like every
    /// other aerial behaviour; no new setting.
    /// </summary>
    public static class Restringing
    {
        private static DesignationDef des;
        private static JobDef job;
        public static DesignationDef Des => des ??= DefDatabase<DesignationDef>.GetNamed("RM_RestringSpan");
        public static JobDef Job => job ??= DefDatabase<JobDef>.GetNamed("RM_RestringSpan");
        public static int jobsDone, spansRestrung;

        public static bool HasCut(CompAerialAnchor a) => a != null && a.links.Any(l => l.state == SpanState.Cut && l.other != null);

        public static bool Designated(Thing t) => t?.Map != null && t.Map.designationManager.DesignationOn(t, Des) != null;

        public static void SetDesignated(Thing t, bool on)
        {
            if (t?.Map == null) return;
            Designation d = t.Map.designationManager.DesignationOn(t, Des);
            if (on && d == null) t.Map.designationManager.AddDesignation(new Designation(t, Des));
            else if (!on && d != null) t.Map.designationManager.RemoveDesignation(d);
        }

        /// <summary>Where the cut is, seen from this anchor: the cell its fallen half of a cut span lies toward; the anchor's
        /// own cell when the halves were coiled (a roof cut) and nothing lies on the ground.</summary>
        public static IntVec3 CutCell(CompAerialAnchor a)
        {
            foreach (SpanLink l in a.links)
            {
                if (l.state != SpanState.Cut || l.other == null) continue;
                FallenCord f = a.fallen.FirstOrDefault(x => x.cutPartner == l.other.thingIDNumber);
                if (f != null) return f.toward;
            }
            return a.Position;
        }

        /// <summary>The job's work target: the cut cell when the pawn can stand on it and reach it, else the anchor.</summary>
        public static LocalTargetInfo WorkTarget(Pawn pawn, CompAerialAnchor a)
        {
            IntVec3 c = CutCell(a);
            if (c != a.Position && c.InBounds(a.Map) && c.Standable(a.Map) && pawn.CanReach(c, PathEndMode.OnCell, Danger.Some)) return c;
            return pawn.CanReach(a.parent, PathEndMode.Touch, Danger.Some) ? new LocalTargetInfo(a.parent) : LocalTargetInfo.Invalid;
        }

        /// <summary>Splice every cut span of the anchor. Returns how many came back up; refused counts the ones a roof over
        /// either anchor still blocks (CompAerialAnchor.Restring's own rule).</summary>
        public static int RestringAll(CompAerialAnchor a, out int refused)
        {
            refused = 0;
            int n = 0;
            foreach (CompAerialAnchor o in a.links.Where(l => l.state == SpanState.Cut).Select(l => l.other).Where(o => o != null).ToList())
            {
                if (CompAerialAnchor.Restring(a, o)) n++;
                else refused++;
            }
            spansRestrung += n;
            return n;
        }
    }

    public class WorkGiver_RestringSpan : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        public override bool ShouldSkip(Pawn pawn, bool forced = false) =>
            !AerialSettings.enabled || !pawn.Map.designationManager.AnySpawnedDesignationOfDef(Restringing.Des);

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn) =>
            pawn.Map.designationManager.SpawnedDesignationsOfDef(Restringing.Des).Select(d => d.target.Thing).Where(t => t != null);

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            CompAerialAnchor a = CompAerialAnchor.Of(t);
            if (a == null || !Restringing.Designated(t)) return false;
            if (!Restringing.HasCut(a)) { Restringing.SetDesignated(t, false); return false; }
            if (t.IsForbidden(pawn) || !pawn.CanReserve(t, 1, -1, null, forced)) return false;
            return Restringing.WorkTarget(pawn, a).IsValid;
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false) =>
            JobMaker.MakeJob(Restringing.Job, t, Restringing.WorkTarget(pawn, CompAerialAnchor.Of(t)));
    }

    public class JobDriver_RestringSpan : JobDriver
    {
        private int workLeft = -1, workTotal = 1;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref workLeft, "rmRestringWorkLeft", -1);
            Scribe_Values.Look(ref workTotal, "rmRestringWorkTotal", 1);
        }

        public override bool TryMakePreToilReservations(bool errorOnFailed) => pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !AerialSettings.enabled || !Restringing.Designated(TargetThingA) || !Restringing.HasCut(CompAerialAnchor.Of(TargetThingA)));
            yield return job.targetB.HasThing ? Toils_Goto.GotoThing(TargetIndex.B, PathEndMode.Touch) : Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.OnCell);
            Toil work = ToilMaker.MakeToil("RM_RestringSpan");
            work.initAction = () =>
            {
                if (workLeft > 0) return;                      // a loaded job keeps its progress
                workTotal = AerialMath.RestringTicks(pawn.GetStatValue(StatDefOf.ConstructionSpeed));
                workLeft = workTotal;
            };
            work.tickIntervalAction = delta =>
            {
                workLeft -= delta;
                pawn.skills?.Learn(SkillDefOf.Construction, 0.1f * delta);
                if (workLeft <= 0) ReadyForNextToil();
            };
            work.defaultCompleteMode = ToilCompleteMode.Never;
            work.WithProgressBar(TargetIndex.B, () => 1f - (float)workLeft / workTotal);
            work.activeSkill = () => SkillDefOf.Construction;
            yield return work;
            Toil done = ToilMaker.MakeToil("RM_RestringSpanDone");
            done.initAction = () =>
            {
                CompAerialAnchor a = CompAerialAnchor.Of(TargetThingA);
                int n = Restringing.RestringAll(a, out int refused);
                Restringing.jobsDone++;
                if (!Restringing.HasCut(a)) Restringing.SetDesignated(TargetThingA, false);
                if (refused > 0)
                    Messages.Message(pawn.LabelShortCap + " could not re-string " + refused + " wire" + (refused == 1 ? "" : "s") + " on " +
                                     TargetThingA.LabelShort + ": an anchor stands under a roof.", TargetThingA, MessageTypeDefOf.RejectInput, false);
                else if (n > 0) SoundDefOf.Tick_High.PlayOneShot(new TargetInfo(TargetThingA.Position, Map));
            };
            done.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return done;
        }
    }
}
