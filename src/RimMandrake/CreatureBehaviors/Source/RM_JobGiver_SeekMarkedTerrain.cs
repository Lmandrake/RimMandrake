using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// SHIP_VERMIN_MOD_1. Generic "walk toward data-tagged terrain" JobGiver.
	/// Inserted globally via RM_ThinkTree_VerminBehaviors (insertTag =
	/// Animal_PreMain, vanilla's own Verse.AI.ThinkNode_SubtreesByTag extension
	/// point) so it runs for every animal in the game — it no-ops instantly for
	/// any pawn whose race lacks RM_SeekTargetExtension, so that is cheap and safe.
	/// </summary>
	public class RM_JobGiver_SeekMarkedTerrain : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RM_CreatureBehaviorsSettings.seekMarkedTerrainBehaviorEnabled)
			{
				return null; // mod option: seeking marked terrain disabled
			}
			RM_SeekTargetExtension ext = pawn.def?.GetModExtension<RM_SeekTargetExtension>();
			if (ext == null || pawn.Map == null)
			{
				return null;
			}
			if (!Rand.Chance(ext.seekChancePerCheck))
			{
				return null;
			}
			// Already on a matching cell — nothing to seek, let the rest of the think tree run.
			if (Matches(pawn.Position, pawn.Map, ext))
			{
				return null;
			}
			Map map = pawn.Map;
			bool found = CellFinder.TryFindRandomCellNear(pawn.Position, map, (int)ext.searchRadius,
				(IntVec3 c) => Matches(c, map, ext) && c.Standable(map) && map.reachability.CanReach(pawn.Position, c, PathEndMode.OnCell, TraverseParms.For(pawn)),
				out IntVec3 target);
			if (!found)
			{
				return null;
			}
			return JobMaker.MakeJob(JobDefOf.Goto, target);
		}

		private static bool Matches(IntVec3 c, Map map, RM_SeekTargetExtension ext)
		{
			if (!c.InBounds(map))
			{
				return false;
			}
			if (ext.seekSubstructure)
			{
				TerrainDef foundation = map.terrainGrid.FoundationAt(c);
				if (foundation != null && foundation.IsSubstructure)
				{
					return true;
				}
			}
			if (!ext.seekTerrainDefNames.NullOrEmpty())
			{
				string terrainName = map.terrainGrid.TerrainAt(c)?.defName;
				if (terrainName != null && ext.seekTerrainDefNames.Contains(terrainName))
				{
					return true;
				}
			}
			return false;
		}
	}
}
