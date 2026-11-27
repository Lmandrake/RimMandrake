// Studying a machine (DESIGN.md "Research"): the base game's analysis, made into standing work.
// Read from the 1.6 decomp: no base-game work giver starts JobDefOf.AnalyzeItem (CompAnalyzable.OrderForceTarget, reached from the
// targeter gizmo or the float menu, is the only starter); JobDriver_AnalyzeItem goes to the thing (ClosestTouch), waits
// analysisDurationHours*2500/ResearchSpeed ticks and calls OnAnalyzed; progress is kept by analysis id in Find.AnalysisManager; and
// CompInteractable.CanInteract refuses while cooldownTicks > 0, but nothing on the analysis path starts that cooldown (only
// Interact, which analysis never calls). So this comp starts the cooldown itself after each session that leaves the analysis
// unfinished, which is what spaces the sessions out.
using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.WreckedMachines
{
    public class CompMachineStudy : CompAnalyzableUnlockResearch
    {
        /// <summary>The player's standing order: researchers study this machine whenever it can be studied.</summary>
        public bool studyOn;

        public AnalysisDetails Details
        {
            get
            {
                Find.AnalysisManager.TryGetAnalysisProgress(AnalysisID, out AnalysisDetails d);
                return d;
            }
        }

        public bool Complete => Find.AnalysisManager.IsAnalysisComplete(AnalysisID);

        /// <summary>The machine's line is switched on (a switched-off line's projects are hidden, so its study is too).</summary>
        public bool LineOn
        {
            get
            {
                RM_MachineLineDef l = RM_MachineLines.LineOf(parent.def, out _);
                return l == null || RM_MachineLines.IsOn(l);
            }
        }

        public bool Wanted => studyOn && !Complete && LineOn;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref studyOn, "rmStudyOn", false);
        }

        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            // Replaces the base targeter gizmo; the base float-menu order (CompFloatMenuOptions) stays as it is.
            if (parent.SpawnedOrAnyParentSpawned && !Complete && LineOn)
            {
                AnalysisDetails d = Details;
                string progress = d != null ? " (" + d.timesDone + " of " + d.required + " sessions done)" : "";
                yield return new Command_Toggle
                {
                    defaultLabel = "Study",
                    defaultDesc = "When on, researchers come to study this machine by themselves, one session after each cooldown, until "
                        + "the analysis is complete" + progress + ". Completing it unlocks its restoration research.",
                    icon = UIIcon,
                    isActive = () => studyOn,
                    toggleAction = () => studyOn = !studyOn,
                };
            }
            if (DebugSettings.ShowDevGizmos)
            {
                if (OnCooldown)
                    yield return new Command_Action { defaultLabel = "DEV: Reset cooldown", action = () => ResetCooldown() };
                Pawn any = Find.CurrentMap?.mapPawns.FreeColonistsSpawned.FirstOrFallback();
                if (any != null && !Complete)
                    yield return new Command_Action { defaultLabel = "DEV: Finish one study session", action = () => OnAnalyzed(any) };
            }
        }

        public override void OnAnalyzed(Pawn pawn)
        {
            base.OnAnalyzed(pawn);
            if (!parent.Destroyed && !Complete && Props.cooldownTicks > 0) StartCooldown();
        }

        public override string CompInspectStringExtra()
        {
            string s = base.CompInspectStringExtra();
            AnalysisDetails d = Details;
            if (d == null) return s;
            string line = "Study: " + d.timesDone + " of " + d.required + " sessions";
            return s.NullOrEmpty() ? line : s + "\n" + line;
        }
    }

    /// <summary>Research work: study a machine whose Study toggle is on, whose analysis is unfinished and which the pawn may
    /// interact with now (not on cooldown, reachable, not forbidden, the pawn able to research).</summary>
    public class WorkGiver_StudyMachine : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.ClosestTouch;

        public override Danger MaxPathDanger(Pawn pawn) => Danger.Deadly;

        private static CompMachineStudy StudyOf(Thing t)
        {
            CompMachineStudy c = t.TryGetComp<CompMachineStudy>();
            return c != null && c.Wanted && c.Props.canStudyInPlace ? c : null;
        }

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            foreach (Thing t in pawn.Map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial))
                if (StudyOf(t) != null) yield return t;
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            if (StatDefOf.ResearchSpeed.Worker.IsDisabledFor(pawn)) return true;
            foreach (Thing t in pawn.Map.listerThings.ThingsInGroup(ThingRequestGroup.BuildingArtificial))
                if (StudyOf(t) != null) return false;
            return true;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            CompMachineStudy c = StudyOf(t);
            if (c == null || !t.Spawned) return false;
            if (t.Faction != null && t.Faction != pawn.Faction) return false;
            if (t.IsBurning()) return false;
            AcceptanceReport r = c.CanInteract(pawn);
            if (!r.Accepted)
            {
                if (!r.Reason.NullOrEmpty()) JobFailReason.Is(r.Reason);
                return false;
            }
            return pawn.CanReserve(t, 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!HasJobOnThing(pawn, t, forced)) return null;
            return JobMaker.MakeJob(JobDefOf.AnalyzeItem, t, LocalTargetInfo.Invalid, IntVec3.Invalid);
        }
    }
}
