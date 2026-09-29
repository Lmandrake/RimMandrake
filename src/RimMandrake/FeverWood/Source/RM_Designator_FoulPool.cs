using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.EnvironmentalHazards;

namespace RimMandrake.FeverWood
{
    /// <summary>FEVERWOOD_TENTACLE_SETPIECE_TUNING_1, §6f's Uranium free
    /// tier. Marks a registered Fever Wood pool cell to be fouled with a
    /// radioactive suppressant charge; RM_WorkGiver_FoulPool does the
    /// actual hauling. Shape cribbed from vanilla Designator_Mine
    /// (RimWorld/Designator_Mine.cs, read via RimSage this pass) — a plain
    /// cell designator, no thing-select path needed since a pool cell
    /// rarely carries a Thing of its own.</summary>
    public class RM_Designator_FoulPool : Designator_Cells
    {
        protected override DesignationDef Designation => RM_SuppressionDefOf.RM_Designation_FoulPool;

        public override DrawStyleCategoryDef DrawStyleCategory => DrawStyleCategoryDefOf.Mine;

        public RM_Designator_FoulPool()
        {
            defaultLabel = "Foul pool with suppressant";
            defaultDesc = "Mark a Fever Wood pool cell to be fouled with a radioactive suppressant charge "
                + "(crafted from Uranium). A colonist will carry a charge there and dump it, driving "
                + "whatever lives beneath the pool down for several days — no hostile encounters and no "
                + "treasure trickle from that pool while it lasts.";
            icon = ContentFinder<Texture2D>.Get("UI/Designators/Mine");
            soundDragSustain = SoundDefOf.Designate_DragStandard;
            soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
            useMouseIcon = true;
            soundSucceeded = SoundDefOf.Designate_Mine;
        }

        public override AcceptanceReport CanDesignateCell(IntVec3 c)
        {
            if (!RM_FeverWoodSettings.tentacleUraniumSuppressionEnabled)
            {
                return false;
            }
            if (!c.InBounds(Map))
            {
                return false;
            }
            RUT_MapComponent_TheTenant tenant = Map.GetComponent<RUT_MapComponent_TheTenant>();
            if (tenant == null || !tenant.IsRegisteredWater(c))
            {
                return "Only a registered Fever Wood pool cell can be fouled.";
            }
            if (Map.designationManager.DesignationAt(c, Designation) != null)
            {
                return false;
            }
            return true;
        }

        public override void DesignateSingleCell(IntVec3 c)
        {
            Map.designationManager.AddDesignation(new Designation(c, Designation));
        }
    }
}
