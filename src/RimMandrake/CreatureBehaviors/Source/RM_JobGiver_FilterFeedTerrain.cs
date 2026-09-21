using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
	/// <summary>
	/// DESERT_SHADE_WHALE_FILTERFEED_1. Requests RM_JobDefOf.RM_FilterFeedTerrain
	/// whenever a race carrying RM_FilterFeedExtension is hungry enough and can
	/// reach ground it is able to strain a meal out of.
	///
	/// Modelled on this assembly's own RM_JobGiver_SeekMarkedTerrain (same
	/// terrain-defName matching, same CellFinder search, same no-op-for-untagged
	/// contract) rather than on vanilla grazing: JobGiver_EatWild/JobDriver_Ingest
	/// need a Plant to reserve, ingest and destroy, and the whole point of this
	/// item is that the food here is the GROUND, which is not a Thing and cannot
	/// be eaten by anything that routes through FoodTypeFlags.
	///
	/// Inserted via RM_ThinkTree_VerminBehaviors (insertTag Animal_PreMain), so
	/// it is tried ahead of vanilla's own hunger handling — a filter-feeder
	/// standing on its own food should not walk off to find a plant. When this
	/// returns null (no extension, not hungry, no reachable feeding ground) the
	/// pawn falls through to ordinary vanilla eating unchanged, which is what
	/// keeps a filter-feeder survivable off its home terrain.
	/// </summary>
	public class RM_JobGiver_FilterFeedTerrain : ThinkNode_JobGiver
	{
		protected override Job TryGiveJob(Pawn pawn)
		{
			if (!RM_CreatureBehaviorsSettings.filterFeedingEnabled)
			{
				return null; // mod option: terrain filter-feeding disabled — the race eats like any other grazer
			}

			RM_FilterFeedExtension ext = pawn.def?.GetModExtension<RM_FilterFeedExtension>();
			if (ext == null || ext.feedTerrainDefNames.NullOrEmpty())
			{
				return null;
			}

			Map map = pawn.Map;
			if (map == null || pawn.needs?.food == null)
			{
				return null;
			}

			if (pawn.needs.food.CurLevelPercentage > ext.beginBelowFoodPercent)
			{
				return null; // not hungry enough to bother straining
			}

			// Standing on it already — feed here rather than walking to an
			// identical cell, which is both correct and what stops a megafauna
			// shuffling across a whole sand sheet one cell at a time.
			if (MatchesFeedTerrain(pawn.Position, map, ext))
			{
				return JobMaker.MakeJob(RM_JobDefOf.RM_FilterFeedTerrain, pawn.Position);
			}

			int radius = Mathf.Max(1, Mathf.RoundToInt(ext.searchRadius));
			if (!CellFinder.TryFindRandomCellNear(pawn.Position, map, radius,
				(IntVec3 c) => MatchesFeedTerrain(c, map, ext) && c.Standable(map)
					&& map.reachability.CanReach(pawn.Position, c, PathEndMode.OnCell, TraverseParms.For(pawn)),
				out IntVec3 target))
			{
				return null; // nothing edible underfoot within reach — vanilla hunger handling takes it from here
			}

			return JobMaker.MakeJob(RM_JobDefOf.RM_FilterFeedTerrain, target);
		}

		/// <summary>
		/// Whether the terrain at this cell is on the race's feed list. Reads
		/// TerrainAt, not FoundationAt: a filter-feeder strains what it is
		/// standing on, and a bridge or a floor laid over sand is exactly the
		/// case where it must stop being able to.
		/// </summary>
		public static bool MatchesFeedTerrain(IntVec3 c, Map map, RM_FilterFeedExtension ext)
		{
			if (!c.InBounds(map))
			{
				return false;
			}
			string terrainName = map.terrainGrid.TerrainAt(c)?.defName;
			return terrainName != null && ext.feedTerrainDefNames.Contains(terrainName);
		}
	}
}
