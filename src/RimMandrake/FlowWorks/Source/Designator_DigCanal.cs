using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks
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
			defaultDesc = "Carve a channel one level deeper. Designating a channel that is "
				+ "already dug deepens it again — shallow, mid, deep, then SUPERDEEP. "
				+ "Liquid fills the deepest cells first and overflows into shallower ones.";
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
			if (Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal) != null)
			{
				return "Already being dug as a canal.";
			}
			Building edifice = c.GetEdifice(Map);
			if (edifice != null)
			{
				// §19's hazard, settled by MEASUREMENT 2026-09-16 rather than
				// assumed: Pits' buildings all carry a <building> block and
				// BuildingProperties.isEdifice defaults to TRUE, so GetEdifice
				// DOES return them and the dig was never actually allowed on a
				// pit cell. The concern in §19 ("may not read as edifices
				// because they are passability Standable") is false —
				// passability and edifice-hood are unrelated fields. Kept as an
				// explicit refusal anyway, because "must designate open ground"
				// is the wrong thing to tell someone pointing at a hole, and
				// because once Pits merges in (ruling 18) the two become one
				// depth ladder and this is where the conversion will live.
				if (IsPitBuilding(edifice))
				{
					return "That is already an excavation. Digging a canal into a pit is not "
						+ "supported yet — pits and channels become one depth ladder when the "
						+ "two mods merge.";
				}
				return "Must designate open ground.";
			}
			TerrainDef terrain = c.GetTerrain(Map);
			if (terrain.IsWater)
			{
				return "Already water.";
			}
			// Digging an already-dug cell DEEPENS it (ruling 19): shallow, mid,
			// deep, SUPERDEEP. Depth is set by digging and by nothing else.
			byte depth = RM_ExcavationDepth.DepthOfDryTerrain(terrain);
			if (depth != RM_ExcavationDepth.Surface)
			{
				if (depth >= RM_ExcavationDepth.MaxDepth)
				{
					return "Already SUPERDEEP — this is as far down as digging goes.";
				}
				if (!RimMandrakeFlowWorksSettings.digToDepthEnabled)
				{
					return "Deepening is switched off in this mod's settings.";
				}
				return AcceptanceReport.WasAccepted;
			}
			if (!terrain.IsSoil)
			{
				return "Must designate diggable soil.";
			}
			return AcceptanceReport.WasAccepted;
		}

		/// <summary>Matched by namespace rather than by a hard assembly
		/// reference: Pits is a separate mod that may simply not be installed,
		/// and it exports no public "is this a pit" helper to reference even
		/// when it is.</summary>
		private static bool IsPitBuilding(Building edifice)
		{
			System.Type t = edifice.GetType();
			return t.FullName != null && t.FullName.StartsWith("RimMandrake.FlowWorks.Pits.");
		}

		public override void DesignateSingleCell(IntVec3 c)
		{
			Map.designationManager.AddDesignation(new Designation(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal));
		}

		public override void SelectedUpdate()
		{
			GenUI.RenderMouseoverBracket();
		}
	}
}
