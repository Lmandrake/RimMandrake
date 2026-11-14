using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// RIMMANDRAKE_ALLOW_MEDIUM_FURNITURE_ON_PIT_FLOOR: a dry dug floor is solid ground a colony builds on, so it carries the
	/// load-bearing affordances (Light, Medium, Heavy) of the ground it was dug from, on top of its own. Digging lends no
	/// growing soil, no Walkable and no Diggable: only what a building stands on. Soft sand dug down is still soft sand.
	/// Verse-free: SelfTest PitFloorGroundChecks runs this; RM_PitFloorGround applies it to TerrainAffordanceDefs.
	/// </summary>
	public static class RM_PitFloorGroundMath
	{
		private static readonly string[] LoadBearing = { "Light", "Medium", "Heavy" };

		public static bool Lends(string affordance) => Array.IndexOf(LoadBearing, affordance) >= 0;

		/// <summary>The floor's own list, then each load-bearing entry of <paramref name="ground"/> it lacks. The SAME list
		/// when there is nothing to add (no ground recorded, or the floor already carries it all).</summary>
		public static List<T> Carried<T>(List<T> floor, List<T> ground, Func<T, string> name)
		{
			if (floor == null || ground == null)
			{
				return floor;
			}
			List<T> merged = null;
			foreach (T a in ground)
			{
				if (a == null || !Lends(name(a)) || floor.Contains(a) || (merged != null && merged.Contains(a)))
				{
					continue;
				}
				if (merged == null)
				{
					merged = new List<T>(floor);
				}
				merged.Add(a);
			}
			return merged ?? floor;
		}

		/// <summary>RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE (owner look 2026-11-14, his 12: "inside the pit the lanternstone floor is
		/// destroyed"): what a dug square's water picture write does with a floor a player laid on the pit floor. Vanilla's
		/// SetTerrain of a liquid clears the floor's under-layer, so the floor is recorded (sunk) before water is written over it
		/// and laid back on the dry floor when the water is gone.</summary>
		public enum FloorStep
		{
			Write,
			SinkFloorThenWrite,
			WriteThenRelay
		}

		public static FloorStep FloorUnderWater(bool floorOnTop, bool wantWet, bool floorSunk)
		{
			if (wantWet)
			{
				return floorOnTop && !floorSunk ? FloorStep.SinkFloorThenWrite : FloorStep.Write;
			}
			return floorSunk ? FloorStep.WriteThenRelay : FloorStep.Write;
		}

		/// <summary>The readout's floor phrase after the pit words: " · Lanternstone floor", or "... under the water" while it is
		/// sunk; "" with no floor.</summary>
		public static string FloorPhrase(string floorLabel, bool sunk, string liquidLabel)
		{
			if (string.IsNullOrEmpty(floorLabel))
			{
				return "";
			}
			return " \u00b7 " + floorLabel + (sunk ? " under the " + (string.IsNullOrEmpty(liquidLabel) ? "liquid" : liquidLabel) : "");
		}
	}
}
