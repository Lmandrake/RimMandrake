// RIMMANDRAKE_ALLOW_MEDIUM_FURNITURE_ON_PIT_FLOOR: a dry dug floor carries what the ground it was dug from carried
// (RM_PitFloorGroundMath), so a butcher table, battery or cooler stands on a pit floor dug in soil.

using System;
using System.Collections.Generic;
using RimMandrake.FlowWorks;

namespace RimMandrake.FlowWorks.SelfTest
{
	internal static class PitFloorGroundChecks
	{
		private static void Assert(bool ok, string what)
		{
			if (!ok)
			{
				throw new Exception(what);
			}
		}

		private static string Join(List<string> l) => string.Join(",", l);

		public static void Run(Action<string, Action> Case)
		{
			Case("PitFloorGround_dug_floor_carries_its_grounds_load", () =>
			{
				List<string> superdeep = new List<string> { "Light" };
				List<string> soil = new List<string> { "Light", "Medium", "Heavy", "Walkable", "GrowSoil", "Diggable" };
				List<string> softSand = new List<string> { "Light", "Walkable", "Diggable" };
				List<string> got = RM_PitFloorGroundMath.Carried(superdeep, soil, s => s);
				Assert(Join(got) == "Light,Medium,Heavy", "can-fail: a superdeep floor dug in soil carries Light, Medium, Heavy (" + Join(got) + ")");
				got = RM_PitFloorGroundMath.Carried(superdeep, softSand, s => s);
				Assert(Join(got) == "Light", "can-fail: soft sand lends nothing it never had (" + Join(got) + ")");
				List<string> shallow = new List<string> { "Walkable", "Light", "Diggable" };
				got = RM_PitFloorGroundMath.Carried(shallow, soil, s => s);
				Assert(Join(got) == "Walkable,Light,Diggable,Medium,Heavy",
					"can-fail: the floor keeps its own, then gains only load-bearing ones (" + Join(got) + ")");
				Assert(!got.Contains("GrowSoil"), "can-fail: a dug floor is no growing soil");
				Assert(RM_PitFloorGroundMath.Carried(superdeep, null, s => s) == superdeep, "can-fail: no ground recorded: the floor's own list");
				Assert(RM_PitFloorGroundMath.Carried(soil, soil, s => s) == soil, "can-fail: nothing to add: the same list, not a copy");
			});
		}
	}
}
