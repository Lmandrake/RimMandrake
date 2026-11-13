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
	}
}
