using System.Runtime.CompilerServices;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// DUG_ICE_DIAGNOSE_COLD_FEET_WARM_WATER (live pass 2, 2026-10-19): dug water never froze. A vanilla 1.6 (Odyssey)
	/// bookkeeping gap, met only by water made after map generation. FreezeManager.DoWaterFreezing rolls
	///     num = 0.003 * (T / -5);  num += (1 - num) * Pow(body.numCellsFrozen / body.numCellsCanFreeze, 10)
	/// and WaterBody.numCellsCanFreeze is only ever counted in WaterBody.RecacheState. A body born at runtime
	/// (WaterBodyTracker.TryCreateBodyOrAddToExisting) runs Initialize -> RecacheState while its cell set is still EMPTY,
	/// and FloodFillBody adds every later cell without recounting, so the count stays 0: 0/0 = NaN, Pow(NaN) = NaN, and
	/// Rand.Chance(NaN) is false (Value &lt; NaN). The roll can never succeed and no exception is logged. Map-generated
	/// bodies are counted by ConstructBodies (map init and load), so a save/load heals it, which is why vanilla water
	/// freezes and freshly dug water (RM_WaterThin, canFreeze true, Freshwater) never does.
	/// Fix: a water-type change marks the bodies around the cell stale; the freeze roll recounts a stale (or zero-count)
	/// body before vanilla reads it. Cost: one dictionary lookup per freezable square the steady-effects cycle visits.
	/// </summary>
	[HarmonyPatch(typeof(WaterBodyTracker), nameof(WaterBodyTracker.Notify_TerrainChanged))]
	[RimMandrake.Shared.PatchFeature("Dug and refilled water freezes like the game's own water", typeof(RM_WaterMendSettings), "freezeCountMendEnabled")]
	public static class RM_Patch_WaterBodyFreezeCountMark
	{
		private static readonly AccessTools.FieldRef<WaterBodyTracker, Map> MapOf =
			AccessTools.FieldRefAccess<WaterBodyTracker, Map>("map");

		private static readonly ConditionalWeakTable<WaterBody, object> Stale = new ConditionalWeakTable<WaterBody, object>();
		private static readonly object Mark = new object();
		// bodies recounted to a true zero (no freezable base square): the zero-count fallback must not rescan them every roll
		private static readonly ConditionalWeakTable<WaterBody, object> CountedZero = new ConditionalWeakTable<WaterBody, object>();

		[HarmonyPostfix]
		[HarmonyPriority(Priority.Last)]
		public static void Postfix(WaterBodyTracker __instance, IntVec3 cell, TerrainDef oldTerr, TerrainDef newTerr)
		{
			if (!RM_WaterMendSettings.freezeCountMendEnabled || Current.ProgramState != ProgramState.Playing
				|| newTerr?.waterBodyType == oldTerr?.waterBodyType)
			{
				return;
			}
			MarkAt(__instance, cell);
			Map map = MapOf(__instance);
			if (map == null)
			{
				return;
			}
			for (int i = 0; i < 4; i++)
			{
				IntVec3 n = cell + GenAdj.CardinalDirections[i];
				if (n.InBounds(map))
				{
					MarkAt(__instance, n);       // the body a drying cell left, and any body a wetting cell merged
				}
			}
		}

		private static void MarkAt(WaterBodyTracker tracker, IntVec3 c)
		{
			if (tracker.TryGetWaterBodyAt(c, out WaterBody b) && b != null)
			{
				Stale.GetValue(b, _ => Mark);
			}
		}

		/// <summary>Recount the body if a terrain change made it stale, or if it reads zero freezable squares while
		/// holding the freezable square <paramref name="c"/> (the NaN state). True when it recounted.</summary>
		internal static bool RecountIfStale(WaterBody b)
		{
			if (b == null)
			{
				return false;
			}
			bool stale = Stale.TryGetValue(b, out _);
			if (!stale && (b.numCellsCanFreeze > 0 || CountedZero.TryGetValue(b, out _)))
			{
				return false;
			}
			if (stale)
			{
				Stale.Remove(b);
				CountedZero.Remove(b);
			}
			b.RecacheState();
			if (b.numCellsCanFreeze <= 0)
			{
				CountedZero.GetValue(b, _ => Mark);
			}
			return true;
		}
	}

	[HarmonyPatch(typeof(FreezeManager), "DoWaterFreezing")]
	[RimMandrake.Shared.PatchFeature("Dug and refilled water freezes like the game's own water", typeof(RM_WaterMendSettings), "freezeCountMendEnabled")]
	public static class RM_Patch_WaterBodyFreezeCountRecount
	{
		[HarmonyPrefix]
		public static void Prefix(Map ___map, IntVec3 c)
		{
			if (!RM_WaterMendSettings.freezeCountMendEnabled || ___map == null || !c.GetTerrain(___map).canFreeze)
			{
				return;
			}
			RM_Patch_WaterBodyFreezeCountMark.RecountIfStale(c.GetWaterBody(___map));
		}
	}
}
