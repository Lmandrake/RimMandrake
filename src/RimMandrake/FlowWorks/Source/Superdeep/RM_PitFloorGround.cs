using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_ALLOW_MEDIUM_FURNITURE_ON_PIT_FLOOR (seen live 2026-11-12: a butcher table, tailoring bench, battery, cooler,
	/// resin jar shelf and brine crock refused on a 4 m dug floor, "requires terrain that supports Medium"): a DRY dug floor
	/// carries the load-bearing affordances of the ground recorded before its first cut
	/// (RM_MapComponent_Excavation.OriginalTerrainAt; RM_PitFloorGroundMath). GenConstruct.CanBuildOnTerrain reads every
	/// cell through GridsUtility.GetAffordances, so placement, frames and blueprints all see it. A foundation keeps vanilla's
	/// answer, a square under a suspension deck the deck's tier; a wet dug square is vanilla water and keeps its own rule
	/// (buildInDugWaterEnabled). A building already standing when a dig deepens under it stands, as before
	/// (RM_MapComponent_Excavation's one terrain-change rule).
	/// </summary>
	[HarmonyPatch(typeof(GridsUtility), nameof(GridsUtility.GetAffordances))]
	[RimMandrake.Shared.PatchFeature("A dug pit floor carries what its ground carried", typeof(RimMandrakeFlowWorksSettings), "pitFloorCarriesGroundEnabled")]
	internal static class RM_PitFloorGround
	{
		// (floor terrain, ground terrain) -> the merged list; defs live for the session, so this never grows past the pairs met
		private static readonly Dictionary<(TerrainDef, TerrainDef), List<TerrainAffordanceDef>> cache =
			new Dictionary<(TerrainDef, TerrainDef), List<TerrainAffordanceDef>>();

		[HarmonyPostfix]
		private static void Postfix(IntVec3 c, Map map, ref List<TerrainAffordanceDef> __result)
		{
			if (!RimMandrakeFlowWorksSettings.pitFloorCarriesGroundEnabled || map == null || map.terrainGrid.FoundationAt(c) != null)
			{
				return;
			}
			TerrainDef floor = map.terrainGrid.TerrainAt(c);
			if (RM_ExcavationDepth.DepthOfDryTerrain(floor) == RM_ExcavationDepth.Surface)
			{
				return;   // not a dry dug floor: vanilla's answer (every other square on the map pays this one compare chain)
			}
			if (Pits.RM_MapComponent_SuspensionBridges.DeckAt(map, c) != null)
			{
				return;   // what stands here stands on the deck, which lends by its own tier (RM_SuspensionMath.LentAffordances)
			}
			TerrainDef ground = map.GetComponent<RM_MapComponent_Excavation>()?.OriginalTerrainAt(c);
			if (ground == null || ground == floor)
			{
				return;
			}
			if (!cache.TryGetValue((floor, ground), out List<TerrainAffordanceDef> merged))
			{
				merged = RM_PitFloorGroundMath.Carried(floor.affordances, ground.affordances, a => a.defName);
				cache[(floor, ground)] = merged;
			}
			__result = merged;
		}
	}
}
