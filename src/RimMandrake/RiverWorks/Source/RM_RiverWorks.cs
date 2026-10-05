using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.RiverWorks
{
	/// <summary>
	/// The seams other mods plug into (design §6). River Works names no biome and no sea:
	/// TerminalBiomes (or anyone) registers a flood source or an arrest rule here.
	/// </summary>
	public static class RM_RiverWorks
	{
		private static readonly List<Func<Map, bool>> floodSources = new List<Func<Map, bool>>();

		private static readonly List<Func<Map, IntVec3, bool>> arrestRules = new List<Func<Map, IntVec3, bool>>();

		private static ThingDef seasonalFlood;

		private static ThingDef torrentialFlood;

		private static bool floodDefsLooked;

		/// <summary>Register an extra "a flood is on" source (e.g. the sea's undersurge).</summary>
		public static void RegisterFloodSource(Func<Map, bool> isLive)
		{
			if (isLive != null && !floodSources.Contains(isLive))
			{
				floodSources.Add(isLive);
			}
		}

		/// <summary>Register a rule that stops the carry on a cell (a weir's water cell).</summary>
		public static void RegisterArrestRule(Func<Map, IntVec3, bool> arrests)
		{
			if (arrests != null && !arrestRules.Contains(arrests))
			{
				arrestRules.Add(arrests);
			}
		}

		/// <summary>True while any counted flood is live on the map (design §3.6).</summary>
		public static bool FloodActive(Map map)
		{
			if (map == null)
			{
				return false;
			}
			if (!floodDefsLooked)
			{
				// Odyssey defs (Ethereal_Various.xml). All DLCs are assumed present, but a
				// silent lookup keeps a missing one inert rather than fatal.
				seasonalFlood = DefDatabase<ThingDef>.GetNamedSilentFail("SeasonalFlood");
				torrentialFlood = DefDatabase<ThingDef>.GetNamedSilentFail("TorrentialRainFlood");
				floodDefsLooked = true;
			}
			if (RM_RiverWorksSettings.countSeasonalFloods && seasonalFlood != null
				&& map.listerThings.ThingsOfDef(seasonalFlood).Count > 0)
			{
				return true;
			}
			if (RM_RiverWorksSettings.countTorrentialRainFloods && torrentialFlood != null
				&& map.listerThings.ThingsOfDef(torrentialFlood).Count > 0)
			{
				return true;
			}
			for (int i = 0; i < floodSources.Count; i++)
			{
				try
				{
					if (floodSources[i](map))
					{
						return true;
					}
				}
				catch (Exception ex)
				{
					Log.ErrorOnce("[River Works] a registered flood source threw: " + ex, 0x52570001 + i);
				}
			}
			return false;
		}

		public static bool IsArrested(Map map, IntVec3 c)
		{
			for (int i = 0; i < arrestRules.Count; i++)
			{
				if (arrestRules[i](map, c))
				{
					return true;
				}
			}
			return false;
		}
	}

	/// <summary>A race that rides the current instead of being carried by it (fish, river
	/// creatures we author). The sea's twin is TerminalBiomes' RM_ChannelNativeExtension.</summary>
	public class RM_RiverNativeExtension : DefModExtension
	{
	}

	/// <summary>
	/// Owner card 1 (2026-10-03): "colonists path around strong water to bridges/fords
	/// (drafted can still enter)". Vanilla already gives all water 180 undrafted perceived
	/// cost; this raises it on MOVING water only, once at startup, so ordinary jobs route to a
	/// bridge or ford. Drafted orders ignore extraNonDraftedPerceivedPathCost by definition.
	/// PROVISIONAL amounts. Done in C# (not an XML patch) so the setting can switch it off.
	/// </summary>
	[StaticConstructorOnStartup]
	public static class RM_RiverPathCost
	{
		public const int ExtraFastLane = 600;

		public const int ExtraEdgeLane = 120;

		static RM_RiverPathCost()
		{
			if (!RM_RiverWorksSettings.riverWorksEnabled || !RM_RiverWorksSettings.surfaceCurrentEnabled
				|| !RM_RiverWorksSettings.pathfinderAvoidsCurrents)
			{
				return;
			}
			foreach (TerrainDef t in DefDatabase<TerrainDef>.AllDefsListForReading)
			{
				if (!t.IsRiver)
				{
					continue;
				}
				t.extraNonDraftedPerceivedPathCost += RM_RiverCurrentLanes.IsFastLane(t) ? ExtraFastLane : ExtraEdgeLane;
			}
		}
	}

	public static class RM_RiverCurrentLanes
	{
		/// <summary>Chest-deep moving water (pathCost 42, WaterChestDeepBase) is the fast lane;
		/// shallow moving water (30, WaterShallowBase) the edge lane. Read off pathCost so a
		/// mod's toxic or tinted twin of either inherits the right lane.</summary>
		public static bool IsFastLane(TerrainDef t)
		{
			return t.pathCost >= 40;
		}

		public static int LaneOf(TerrainDef t)
		{
			if (t == null || !t.IsRiver)
			{
				return RM_RiverMath.LaneNone;
			}
			return IsFastLane(t) ? RM_RiverMath.LaneCentre : RM_RiverMath.LaneMargin;
		}
	}
}
