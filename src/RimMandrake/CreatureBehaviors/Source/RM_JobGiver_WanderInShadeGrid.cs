using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_GRID_KEYSTONE_1. Same shape as vanilla's
	/// Verse.AI.JobGiver_WanderInRoofedCellsInPen (desert_ecology_feasibility.md
	/// §3): a JobGiver_Wander subclass whose wanderDestValidator scores candidate
	/// wander cells, inserted at insertTag Animal_PreWander via
	/// RM_ThinkTree_ShadeSeekingWander so it is tried, for EVERY animal on the
	/// map, before vanilla's own wander subnodes (RimSage-verified against
	/// Core's Animal.xml — Animal_PreWander sits immediately before the tame/wild
	/// wander branches). Vanilla's version validates cell.Roofed; this one
	/// validates RM_MapComponent_ShadeGrid.ShadeAt(cell) against the pawn's own
	/// RM_ShadeSeekingWanderExtension.minShadeToPrefer.
	///
	/// Returns no job at all — not even a Wait — for any pawn whose race lacks
	/// RM_ShadeSeekingWanderExtension, so this is safe to insert globally the
	/// same way RM_JobGiver_SeekShade already is: an un-tagged chicken or
	/// muffalo never sees a behaviour change, and base.TryGiveJob's
	/// pawn.mindState bookkeeping is never touched for it either.
	/// </summary>
	public class RM_JobGiver_WanderInShadeGrid : JobGiver_Wander
	{
		public RM_JobGiver_WanderInShadeGrid()
		{
			wanderRadius = 10f;
			ticksBetweenWandersRange = new IntRange(120, 240);
			expiryInterval = 500;
			wanderDestValidator = ValidateWanderDest;
		}

		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RM_CreatureBehaviorsSettings.shadeGridEnabled
				|| !RM_CreatureBehaviorsSettings.shadeSeekingWanderEnabled)
			{
				return null; // mod option: shade-seeking wander disabled
			}
			if (pawn.def?.GetModExtension<RM_ShadeSeekingWanderExtension>() == null || pawn.Map == null)
			{
				return null;
			}
			return base.TryGiveJob(pawn);
		}

		protected override IntVec3 GetWanderRoot(Pawn pawn)
		{
			return pawn.Position;
		}

		private static bool ValidateWanderDest(Pawn pawn, IntVec3 cell, IntVec3 root)
		{
			RM_MapComponent_ShadeGrid grid = pawn.Map?.GetComponent<RM_MapComponent_ShadeGrid>();
			if (grid == null)
			{
				return false;
			}
			RM_ShadeSeekingWanderExtension ext = pawn.def?.GetModExtension<RM_ShadeSeekingWanderExtension>();
			float minShade = ext?.minShadeToPrefer ?? 0.5f;
			return cell.Standable(pawn.Map) && grid.ShadeAt(cell) >= minShade;
		}
	}
}
