using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.DivingInteraction
{
    // Auto-registered by FloatMenuMakerMap.Init() (reflection over every
    // FloatMenuOptionProvider subclass — no Harmony, no def, see About.xml).
    // Right-click any RM_DiveEligible cell to offer the two dive jobs.
    public class RM_FloatMenuOptionProvider_Dive : FloatMenuOptionProvider
    {
        protected override bool Drafted => true;
        protected override bool Undrafted => true;
        protected override bool Multiselect => false;
        protected override bool RequiresManipulation => true;
        protected override bool MechanoidCanDo => false;

        protected override bool AppliesInt(FloatMenuContext context)
        {
            return RM_DivingSettings.masterEnabled
                && (RM_DivingSettings.huntEnabled || RM_DivingSettings.communeEnabled)
                && RM_DiveUtility.CellIsDiveSite(context.ClickedCell, context.map);
        }

        public override IEnumerable<FloatMenuOption> GetOptions(FloatMenuContext context)
        {
            IntVec3 cell = context.ClickedCell;
            Map map = context.map;
            Pawn pawn = context.FirstSelectedPawn;
            if (pawn == null)
            {
                yield break;
            }

            RM_MapComponent_DiveSites comp = map.GetComponent<RM_MapComponent_DiveSites>();
            int ticksRemaining = 0;
            bool onCooldown = comp != null && comp.OnCooldown(cell, out ticksRemaining);
            bool canReach = pawn.CanReach(cell, PathEndMode.OnCell, Danger.Deadly);

            if (RM_DivingSettings.huntEnabled)
            {
                yield return BuildOption(pawn, cell, RM_DivingDefOf.RM_Job_DiveHunt,
                    "RM_FloatMenu_DiveHunt".Translate(), canReach, onCooldown, ticksRemaining);
            }
            if (RM_DivingSettings.communeEnabled)
            {
                yield return BuildOption(pawn, cell, RM_DivingDefOf.RM_Job_DiveCommune,
                    "RM_FloatMenu_DiveCommune".Translate(), canReach, onCooldown, ticksRemaining);
            }
        }

        private FloatMenuOption BuildOption(Pawn pawn, IntVec3 cell, JobDef jobDef, string label,
            bool canReach, bool onCooldown, int ticksRemaining)
        {
            if (!canReach)
            {
                return new FloatMenuOption(label + ": " + "NoPath".Translate(), null);
            }
            if (onCooldown)
            {
                return new FloatMenuOption(
                    label + ": " + "RM_DiveOnCooldown".Translate(ticksRemaining.ToStringTicksToPeriod()),
                    null);
            }

            void Action()
            {
                Job job = JobMaker.MakeJob(jobDef, cell);
                pawn.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            }

            return FloatMenuUtility.DecoratePrioritizedTask(
                new FloatMenuOption(label, Action), pawn, cell);
        }
    }
}
