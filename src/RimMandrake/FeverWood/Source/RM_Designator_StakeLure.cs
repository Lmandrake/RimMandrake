using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FeverWood
{
    /// <summary>FEVERWOOD_TWO_FRONT_LURE_1. "The lure is always a LIVING
    /// creature... one of your own tamed animals, a prisoner, or a
    /// nectar-beast from your herd" (design sheet §6l) — ⛔ never a crafted
    /// decoy, which was offered and declined. This designator flags which
    /// pawn the player is offering; RM_WorkGiver_StunForStaking and
    /// RM_WorkGiver_HaulToStake do the actual work. Shape cribbed from
    /// vanilla's own Designator_Slaughter (RimWorld/Designator_Slaughter.cs,
    /// read via RimSage this pass) — same CanDesignateThing/DesignateThing
    /// split, generalized to accept a tamed animal OR a colony prisoner
    /// instead of only "any animal."</summary>
    public class RM_Designator_StakeLure : Designator
    {
        protected override DesignationDef Designation => RM_TwoFrontLureDefOf.RM_Designation_StakeLure;

        public override DrawStyleCategoryDef DrawStyleCategory => DrawStyleCategoryDefOf.FilledRectangle;

        public RM_Designator_StakeLure()
        {
            defaultLabel = "Stake as lure";
            defaultDesc = "Flag a tamed animal or prisoner to be staked as living bait for the Fever Wood's raiders. It will be wounded down and chained in the open — there is no bloodless version of this.";
            icon = ContentFinder<Texture2D>.Get("UI/Designators/Slaughter");
            soundDragSustain = SoundDefOf.Designate_DragStandard;
            soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
            useMouseIcon = true;
            soundSucceeded = SoundDefOf.Designate_Slaughter;
        }

        public override AcceptanceReport CanDesignateCell(IntVec3 c)
        {
            return false; // pawn-only, like Designator_Slaughter's own cell path is really thing-driven; keep this one thing-select only for clarity
        }

        public override AcceptanceReport CanDesignateThing(Thing t)
        {
            if (!(t is Pawn pawn))
            {
                return false;
            }
            if (pawn.Dead)
            {
                return false; // a corpse is not "living bait"; an already-downed pawn is fine — it skips straight to the haul step
            }
            if (!(pawn.RaceProps.Animal && pawn.Faction == Faction.OfPlayer) && !pawn.IsPrisonerOfColony)
            {
                return "Only your own tamed animals or prisoners can be staked as a lure.";
            }
            if (Map.designationManager.DesignationOn(pawn, Designation) != null)
            {
                return false;
            }
            HediffDef staked = DefDatabase<HediffDef>.GetNamedSilentFail("RM_LureStaked");
            if (staked != null && pawn.health.hediffSet.HasHediff(staked))
            {
                return "Already staked.";
            }
            return true;
        }

        public override void DesignateThing(Thing t)
        {
            Map.designationManager.AddDesignation(new Designation(t, Designation));
        }
    }
}
