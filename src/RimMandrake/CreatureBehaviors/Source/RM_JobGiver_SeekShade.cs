using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// GREENTIDE_STANDALONE_MOD_1. Inserted globally via RM_ThinkTree_VerminBehaviors
	/// (insertTag = Animal_PreMain), same shape as RM_JobGiver_SeekMarkedTerrain —
	/// no-ops instantly for any pawn whose race lacks RM_SeekShadeExtension.
	/// </summary>
	public class RM_JobGiver_SeekShade : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			RM_SeekShadeExtension ext = pawn.def?.GetModExtension<RM_SeekShadeExtension>();
			if (ext == null || pawn.Map == null)
			{
				return null;
			}
			if (!Rand.Chance(ext.seekChancePerCheck))
			{
				return null;
			}
			Map map = pawn.Map;
			if (map.roofGrid.Roofed(pawn.Position))
			{
				return null;
			}
			float ambientTemp = GenTemperature.GetTemperatureForCell(pawn.Position, map);
			if (ambientTemp < ext.tempThreshold)
			{
				return null;
			}
			bool found = CellFinder.TryFindRandomCellNear(pawn.Position, map, (int)ext.searchRadius,
				(IntVec3 c) => c.Standable(map) && map.roofGrid.Roofed(c)
					&& map.reachability.CanReach(pawn.Position, c, PathEndMode.OnCell, TraverseParms.For(pawn)),
				out IntVec3 target);
			if (!found)
			{
				return null;
			}
			return JobMaker.MakeJob(JobDefOf.Goto, target);
		}
	}
}
