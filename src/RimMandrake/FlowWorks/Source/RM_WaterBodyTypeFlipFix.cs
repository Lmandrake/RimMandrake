using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// FLOWWORKS_WATERBODY_DIAGNOSE_SOIL_THROW (live 2026-10-16): a vanilla 1.6 (Odyssey) bookkeeping bug, not a
	/// FlowWorks one. When a water cell changes between two water body TYPES (fresh to salt, or any of our liquids
	/// whose waterBodyType differs from the water next to it), WaterBodyTracker.Notify_TerrainChanged only calls
	/// TryCreateBodyOrAddToExisting: the cell joins (or founds) a body of the new type, and the OLD body keeps
	/// counting it (CellCount is never decremented, its bodiesByCell entry is overwritten). Later, when the last
	/// real cells of that old body are turned to land, RemoveCellFromExistingBody sees CellCount still above 0,
	/// tries to move rootCell with bodiesByCell.Keys.First(...) and throws "Sequence contains no matching element"
	/// out of TerrainGrid.SetTerrain. Reproduced on vanilla terrain alone: WaterShallow 3x3, one cell to
	/// WaterOceanShallow (and optionally back), then Soil over the 3x3 -> throw; without the flip -> clean.
	/// This prefix detaches the cell from its old-type body first, exactly as RemoveCellFromExistingBody would,
	/// then lets vanilla add it to the new-type body. A save/load already heals the counts (ConstructBodies refloods).
	/// </summary>
	[HarmonyPatch(typeof(WaterBodyTracker), nameof(WaterBodyTracker.Notify_TerrainChanged))]
	[RimMandrake.Shared.PatchFeature("Water changing type keeps the game's water-body counts right", typeof(RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings), "waterBodyTypeFlipFixEnabled")]
	public static class RM_Patch_WaterBodyTypeFlip
	{
		private static readonly AccessTools.FieldRef<WaterBodyTracker, List<WaterBody>> Bodies =
			AccessTools.FieldRefAccess<WaterBodyTracker, List<WaterBody>>("bodies");

		private static readonly AccessTools.FieldRef<WaterBodyTracker, Dictionary<IntVec3, WaterBody>> BodiesByCell =
			AccessTools.FieldRefAccess<WaterBodyTracker, Dictionary<IntVec3, WaterBody>>("bodiesByCell");

		private static readonly AccessTools.FieldRef<WaterBodyTracker, Map> MapOf =
			AccessTools.FieldRefAccess<WaterBodyTracker, Map>("map");

		[HarmonyPrefix]
		public static void Prefix(WaterBodyTracker __instance, IntVec3 cell, TerrainDef oldTerr, TerrainDef newTerr)
		{
			if (!RimMandrakeFlowWorksSettings.waterBodyTypeFlipFixEnabled || Current.ProgramState != ProgramState.Playing)
			{
				return;
			}
			WaterBodyType oldType = oldTerr?.waterBodyType ?? WaterBodyType.None;
			WaterBodyType newType = newTerr?.waterBodyType ?? WaterBodyType.None;
			if (oldType == WaterBodyType.None || newType == WaterBodyType.None || oldType == newType)
			{
				return;
			}
			Map map = MapOf(__instance);
			if (map == null || !__instance.TryGetWaterBodyAt(cell, out WaterBody body) || body == null)
			{
				return;
			}
			if (body.waterBodyType == cell.GetWaterBodyType(map))
			{
				return;
			}
			Detach(__instance, cell, body);
		}

		internal static void Detach(WaterBodyTracker tracker, IntVec3 cell, WaterBody body)
		{
			BodiesByCell(tracker).Remove(cell);
			body.cells.Remove(cell);
			body.CellCount--;
			if (body.CellCount <= 0 || body.cells.Count == 0)
			{
				Bodies(tracker).Remove(body);
				return;
			}
			if (body.rootCell == cell)
			{
				foreach (IntVec3 c in body.cells)
				{
					body.rootCell = c;
					break;
				}
			}
		}
	}
}
