using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>Raises a cell one level. Same vanilla JobDriver_AffectFloor
	/// engine the dig job rides, read in the other direction.</summary>
	public class JobDriver_FillInCanal : JobDriver_AffectFloor
	{
		/// <summary>Filling in is cheaper than cutting, and cheaper at every
		/// level: shovelling spoil back into a hole is not the same labour as
		/// cutting it and throwing it clear. Half the dig cost for the level
		/// being undone, so the ladder still costs more the deeper it goes and
		/// a fill-in is never free.</summary>
		protected override int BaseWorkAmount
		{
			get
			{
				Map map = base.Map;
				if (map == null || !job.targetA.IsValid)
				{
					return RM_ExcavationDepth.WorkPerLevel / 2;
				}
				IntVec3 c = job.targetA.Cell;
				if (!c.InBounds(map))
				{
					return RM_ExcavationDepth.WorkPerLevel / 2;
				}
				RM_MapComponent_Excavation excavation = map.GetComponent<RM_MapComponent_Excavation>();
				byte current = excavation != null
					? excavation.DepthAt(c)
					: RM_ExcavationDepth.DepthOfDryTerrain(map.terrainGrid.BaseTerrainAt(c));
				if (current < 1)
				{
					current = 1;
				}
				return RM_ExcavationDepth.WorkToDeepen((byte)(current - 1)) / 2;
			}
		}

		protected override DesignationDef DesDef => RimMandrakeFlowWorks_DefOf.RM_FillInCanal;

		protected override StatDef SpeedStat => StatDefOf.MiningSpeed;

		protected override void DoEffect(IntVec3 c)
		{
			RM_MapComponent_Excavation excavation = Map.GetComponent<RM_MapComponent_Excavation>();
			if (excavation == null)
			{
				// Defensive only: MapComponents are auto-discovered by
				// reflection, so this branch means something is badly wrong. Do
				// NOTHING rather than writing terrain behind the grid's back —
				// a depth grid that disagrees with the map is worse than a job
				// that quietly accomplished nothing.
				return;
			}
			excavation.FillIn(c);
		}
	}
}
