using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Graffiti
{
    // GRAFFITI_PUNK_IDEOLIGION_SCOPE_1 mechanism 4's Designator placer
    // (design §2.2's "Designator" placer column). Marks a wall cell for
    // graffiti the way vanilla marks a cell for mining or planting - a
    // DesignationDef the pawn later fulfils. Which specific mark gets
    // painted there is left to GraffitiPool.PickForDesignator (weighted,
    // designatorEligible-only) rather than a float-menu of every mark -
    // v2 territory (design's own note under §2.2), not required for the
    // designation mechanism itself to be real and useful.
    public class Designator_PaintGraffitiMark : Designator_Cells
    {
        public Designator_PaintGraffitiMark()
        {
            // Plain string literals, matching this mod's existing
            // convention (RM_GraffitiMod.cs's settings labels) - no
            // Languages/ keyed-string infra exists here yet to route
            // .Translate() through.
            defaultLabel = "Paint graffiti here";
            defaultDesc = "Mark a wall cell for a colonist to paint graffiti on, next time one is free.";
            icon = ContentFinder<Texture2D>.Get("Things/Filth/Art/RM_Graffiti_Vandal/vandal_0", reportFailure: false);
            useMouseIcon = true;
            soundDragSustain = SoundDefOf.Designate_DragStandard;
            soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
            soundSucceeded = SoundDefOf.Designate_Claim;
            hotKey = KeyBindingDefOf.Misc2;
        }

        protected override DesignationDef Designation => RMGraffitiDefOf.RM_PaintGraffitiHere;

        public override AcceptanceReport CanDesignateCell(IntVec3 loc)
        {
            if (!loc.InBounds(Map))
            {
                return false;
            }
            if (Map.designationManager.DesignationAt(loc, RMGraffitiDefOf.RM_PaintGraffitiHere) != null)
            {
                return false;
            }
            // Coarse but honest: reuse the same "is there a cardinal wall
            // nearby" search the job itself later uses, so this refuses a
            // designation nowhere near any wall at all rather than
            // accepting it and letting it sit unworked forever.
            if (!GraffitiJobUtility.TryFindWallMarkCellNear(loc, Map, out IntVec3 _))
            {
                return "No wall nearby to paint on.";
            }
            return true;
        }

        public override void DesignateSingleCell(IntVec3 c)
        {
            Map.designationManager.AddDesignation(new Designation(c, RMGraffitiDefOf.RM_PaintGraffitiHere));
        }
    }
}
