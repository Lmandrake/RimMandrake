using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FluidCanals
{
	/// <summary>
	/// Marks a cell of diggable soil to be carved into an empty channel.
	/// Pattern mirrors <see cref="Designator_SmoothFloors"/> exactly --
	/// vanilla's own cell-designation + labor-job shape, just targeting a
	/// different terrain and a different completion effect.
	/// </summary>
	public class Designator_DigCanal : Designator_Cells
	{
		public Designator_DigCanal()
		{
			defaultLabel = "Dig canal";
			defaultDesc = "Carve an empty channel that a fed reservoir can flood.";
			icon = ContentFinder<Texture2D>.Get("UI/Designators/Mine", true);
			useMouseIcon = true;
			soundDragSustain = SoundDefOf.Designate_DragStandard;
			soundDragChanged = SoundDefOf.Designate_DragStandard_Changed;
			soundSucceeded = SoundDefOf.Designate_Mine;
			hotKey = KeyBindingDefOf.Misc6;
		}

		public override AcceptanceReport CanDesignateCell(IntVec3 c)
		{
			if (!c.InBounds(Map) || c.Fogged(Map))
			{
				return false;
			}
			if (c.InNoBuildEdgeArea(Map))
			{
				return "TooCloseToMapEdge".Translate();
			}
			if (Map.designationManager.DesignationAt(c, RimMandrakeFluidCanals_DefOf.RM_DigCanal) != null)
			{
				return "Already being dug as a canal.";
			}
			if (c.GetEdifice(Map) != null)
			{
				return "Must designate open ground.";
			}
			TerrainDef terrain = c.GetTerrain(Map);
			if (terrain == RimMandrakeFluidCanals_DefOf.RM_Channel_Empty || terrain.IsWater)
			{
				return "Already a channel or water.";
			}
			if (!terrain.IsSoil)
			{
				return "Must designate diggable soil.";
			}
			return AcceptanceReport.WasAccepted;
		}

		public override void DesignateSingleCell(IntVec3 c)
		{
			Map.designationManager.AddDesignation(new Designation(c, RimMandrakeFluidCanals_DefOf.RM_DigCanal));
		}

		public override void SelectedUpdate()
		{
			GenUI.RenderMouseoverBracket();
		}
	}
}
