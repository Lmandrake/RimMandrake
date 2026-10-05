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
				+ "Liquid fills the deepest cells first and overflows into shallower ones. "
				+ "A channel dug into the strip along the map edge is a SINK: liquid reaching "
				+ "it leaves the map, which is how you empty a canal on purpose.";
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
				// PHASE 4, ruling 9 — SINKS. A sink is a map-edge drain, and the
				// edge band is precisely where vanilla refuses construction, so
				// with the edge refusal in place a sink could never be dug and
				// the mechanic could not exist. With sinks ON, the band opens to
				// the dig designator ONLY; nothing else about the no-build rule
				// changes, and an excavation in the band drains off-map by
				// definition. With sinks OFF, the old refusal stands unaltered.
				if (!RimMandrakeFlowWorksSettings.edgeSinksEnabled)
				{
					return "TooCloseToMapEdge".Translate();
				}
				if (c.OnEdge(Map))
				{
					return "TooCloseToMapEdge".Translate();
				}
			}
			if (Map.designationManager.DesignationAt(c, RimMandrakeFlowWorks_DefOf.RM_DigCanal) != null)
			{
				return "Already being dug as a canal.";
			}
			Building edifice = c.GetEdifice(Map);
			if (edifice != null)
			{
				// PIT_LEGACY_CODE_RETIRE_1: there are no pit buildings any more —
				// a pit is a canal cell dug to D=4, so digging deeper IS digging a pit.
				return "Must designate open ground.";
			}
			// Top layer (foundation first), not GetTerrain: a wet channel carries its liquid on the TEMP
			// layer (SetTempTerrain), and GetTerrain returns that, so every wet channel
			// read as "Already water." and could never be deepened. JobDriver_DigCanal
			// reads the base layer. NOT BaseTerrainAt here: that returns the soil UNDER
			// a player floor, and would let a floored cell be dug (floor destroyed).
			TerrainDef terrain = Map.terrainGrid.FoundationAt(c) ?? Map.terrainGrid.TopTerrainAt(c);
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
