using HarmonyLib;
using RimMandrake.FlowWorks.LiquidTypes;
using Verse;
using Verse.AI;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS (owner by card 2026-10-16: "show meters of depth when hovering over liquid"):
	/// the bottom-left cell readout's terrain line gains the liquid standing in the square, "Deep water (Walk speed 30%) —
	/// 2 m deep, 4 kL".
	///
	/// Vanilla 1.6 MouseoverReadout.MouseoverReadoutOnGUI caches the terrain line per TerrainDef (cachedTerrain /
	/// cachedPolluted / cachedTerrainString) and rebuilds it only when the terrain under the mouse changes, so a per-square
	/// number cannot ride on the terrain label. This prefix owns that cache for liquid squares instead: it writes the vanilla
	/// line (same parts, same order) plus the depth suffix and sets the cache keys so vanilla prints it as-is; on a square
	/// with no liquid it clears cachedTerrain once, so vanilla rebuilds its own line. No transpiler, no layout change.
	/// </summary>
	[HarmonyPatch(typeof(MouseoverReadout), nameof(MouseoverReadout.MouseoverReadoutOnGUI))]
	[RimMandrake.Shared.PatchFeature("Liquid depth in the cell readout")]
	public static class RM_Patch_MouseoverDepth
	{
		private static readonly AccessTools.FieldRef<MouseoverReadout, TerrainDef> cachedTerrain =
			AccessTools.FieldRefAccess<MouseoverReadout, TerrainDef>("cachedTerrain");
		private static readonly AccessTools.FieldRef<MouseoverReadout, bool> cachedPolluted =
			AccessTools.FieldRefAccess<MouseoverReadout, bool>("cachedPolluted");
		private static readonly AccessTools.FieldRef<MouseoverReadout, string> cachedTerrainString =
			AccessTools.FieldRefAccess<MouseoverReadout, string>("cachedTerrainString");

		/// <summary>True while the cache holds a line this patch wrote (vanilla must rebuild it on a dry square).</summary>
		private static bool ours;

		[HarmonyPrefix]
		public static void Prefix(MouseoverReadout __instance)
		{
			if (UnityEngine.Event.current.type != UnityEngine.EventType.Repaint)
			{
				return;
			}
			Map map = Find.CurrentMap;
			if (map == null)
			{
				return;
			}
			IntVec3 c = UI.MouseCell();
			string suffix = RimMandrakeFlowWorksSettings.mouseoverDepthEnabled && c.InBounds(map) && !c.Fogged(map)
				? DepthSuffix(map, c) : null;
			if (suffix == null)
			{
				if (ours)
				{
					cachedTerrain(__instance) = null;   // vanilla rebuilds its own line
					ours = false;
				}
				return;
			}
			TerrainDef terrain = c.GetTerrain(map);
			bool polluted = c.IsPolluted(map);
			float fertility = c.GetFertility(map);
			string fert = fertility > 0.0001f ? " " + "FertShort".TranslateSimple() + " " + fertility.ToStringPercent() : "";
			string label = polluted ? "PollutedTerrain".Translate(terrain.label).CapitalizeFirst().ToString() : terrain.LabelCap.ToString();
			string walk = terrain.passability != Traversability.Impassable
				? string.Format(" ({0})", "WalkSpeed".Translate(GenPath.SpeedPercentString(terrain.pathCost)) + fert) : null;
			cachedTerrainString(__instance) = label + walk + " — " + suffix;
			cachedTerrain(__instance) = terrain;
			cachedPolluted(__instance) = polluted;
			ours = true;
		}

		/// <summary>"1.5 m deep, 3 kL" for a square holding liquid, else null. A dug square (canal, pit) reads its fill
		/// levels; a natural water square reads its bed depth, scaled by its pond's fill when the pond is limited.</summary>
		public static string DepthSuffix(Map map, IntVec3 c)
		{
			RM_MapComponent_Excavation ex = map.GetComponent<RM_MapComponent_Excavation>();
			if (ex == null)
			{
				return null;
			}
			if (ex.IsExcavated(c))
			{
				int f = ex.FillAt(c);
				return f > 0 ? RM_Volume.DepthReadout(f, f * (double)RM_Volume.LitresPerLevel) : null;
			}
			TerrainDef t = c.GetTerrain(map);
			if (t == null || !(t.IsWater || RM_LiquidBottleUtility.LiquidAt(t) != null))
			{
				return null;
			}
			int bed = ex.BedLevelsAt(c);
			if (bed <= 0)
			{
				bed = RM_Volume.BedLevels(t.passability == Traversability.Impassable, t.pathCost);
			}
			RM_LiquidBody body = ex.Stock?.IndexedBodyAt(map, c);
			double frac = body != null && !body.limitless && body.capacity > 0f
				? System.Math.Max(0.0, System.Math.Min(1.0, body.stock / (double)body.capacity)) : 1.0;
			return RM_Volume.DepthReadout(bed * frac, bed * frac * RM_Volume.LitresPerLevel);
		}
	}
}
