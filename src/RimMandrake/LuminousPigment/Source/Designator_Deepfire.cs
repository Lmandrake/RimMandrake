using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §3.3: "sits beside vanilla Paint (same DesignationCategoryDef as
    // Designator_PaintBuilding)" -- registered in Patches/DeepfireOrdersPatch.xml.
    // Drag-select shape (CanDesignateCell iterating the cell's ThingList,
    // DesignateSingleCell designating every match) copied from vanilla
    // Designator_PaintBuilding (RimWorld/Designator_PaintBuilding.cs,
    // read via RimSage this pass); the per-thing cost/eligibility split
    // (CanDesignateThing/DesignateThing) matches vanilla Designator_Deconstruct.
    public class Designator_Deepfire : Designator
    {
        protected override DesignationDef Designation => DeepfireDefOf.RM_ApplyDeepfireDesignation;

        public override DrawStyleCategoryDef DrawStyleCategory => DrawStyleCategoryDefOf.Orders;

        public Designator_Deepfire()
        {
            defaultLabel = "Apply deepfire";
            defaultDesc = "Mark a wall, floor furniture, art piece, apparel or weapon for a colonist to coat in deepfire. Colour comes from however it is currently painted; deepfire adds the glow. Up to three coats, each brightening the light.";
            icon = ContentFinder<Texture2D>.Get("UI/Designators/Paint_Bottom", reportFailure: false);
            useMouseIcon = true;
            soundDragSustain = SoundDefOf.Designate_DragStandard;
            soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
            soundSucceeded = SoundDefOf.Designate_Claim;
        }

        public override AcceptanceReport CanDesignateCell(IntVec3 c)
        {
            if (!c.InBounds(Map) || c.Fogged(Map)) return false;

            System.Collections.Generic.List<Thing> thingList = c.GetThingList(Map);
            for (int i = 0; i < thingList.Count; i++)
            {
                if (CanDesignateThing(thingList[i]).Accepted) return true;
            }
            return "Nothing here can take deepfire.";
        }

        public override void DesignateSingleCell(IntVec3 c)
        {
            System.Collections.Generic.List<Thing> thingList = c.GetThingList(Map);
            for (int i = 0; i < thingList.Count; i++)
            {
                if (CanDesignateThing(thingList[i]).Accepted) DesignateThing(thingList[i]);
            }
        }

        public override AcceptanceReport CanDesignateThing(Thing t)
        {
            CompDeepfire comp = t.TryGetComp<CompDeepfire>();
            if (comp == null) return false;
            if (!comp.CanAddCoat) return "Already fully coated.";
            if (t.Faction != Faction.OfPlayer) return false;
            if (Map.designationManager.DesignationOn(t, Designation) != null) return false;
            return true;
        }

        public override void DesignateThing(Thing t)
        {
            Map.designationManager.AddDesignation(new Designation(t, Designation));
        }
    }

    // Spec §3.3: "clears coats (no refund)" -- an immediate action, no
    // designation/job of its own; also cancels any pending apply order so a
    // pawn mid-walk to a now-stripped target isn't left with a stale job.
    public class Designator_RemoveDeepfire : Designator
    {
        public override DrawStyleCategoryDef DrawStyleCategory => DrawStyleCategoryDefOf.Orders;

        public Designator_RemoveDeepfire()
        {
            defaultLabel = "Remove deepfire";
            defaultDesc = "Strip all deepfire coats from a wall, floor furniture, art piece, apparel or weapon at once. No refund.";
            icon = ContentFinder<Texture2D>.Get("UI/Designators/Cancel", reportFailure: false);
            useMouseIcon = true;
            soundDragSustain = SoundDefOf.Designate_DragStandard;
            soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
            soundSucceeded = SoundDefOf.Designate_Cancel;
        }

        public override AcceptanceReport CanDesignateCell(IntVec3 c)
        {
            if (!c.InBounds(Map) || c.Fogged(Map)) return false;

            System.Collections.Generic.List<Thing> thingList = c.GetThingList(Map);
            for (int i = 0; i < thingList.Count; i++)
            {
                if (CanDesignateThing(thingList[i]).Accepted) return true;
            }
            return "Nothing here carries deepfire.";
        }

        public override void DesignateSingleCell(IntVec3 c)
        {
            System.Collections.Generic.List<Thing> thingList = c.GetThingList(Map);
            for (int i = 0; i < thingList.Count; i++)
            {
                if (CanDesignateThing(thingList[i]).Accepted) DesignateThing(thingList[i]);
            }
        }

        public override AcceptanceReport CanDesignateThing(Thing t)
        {
            CompDeepfire comp = t.TryGetComp<CompDeepfire>();
            if (comp == null) return false;
            if (comp.coats <= 0) return false;
            if (t.Faction != Faction.OfPlayer) return false;
            return true;
        }

        public override void DesignateThing(Thing t)
        {
            CompDeepfire comp = t.TryGetComp<CompDeepfire>();
            comp?.RemoveAllCoats();
            Map.designationManager.TryRemoveDesignationOn(t, DeepfireDefOf.RM_ApplyDeepfireDesignation);
        }
    }
}
