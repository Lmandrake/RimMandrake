using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld.Planet;
using Verse;

namespace VEF.Planet;

[HarmonyPatch(typeof(Caravan_PathFollower), "ExposeData")]
public static class VanillaExpandedFramework_Caravan_PathFollower_ExposeData_Patch
{
	public static Dictionary<Caravan_PathFollower, MovingBaseDestinationAction> caravansToFollow = new Dictionary<Caravan_PathFollower, MovingBaseDestinationAction>();

	public static void Postfix(Caravan_PathFollower __instance)
	{
		caravansToFollow.TryGetValue(__instance, out var value);
		Scribe_Deep.Look<MovingBaseDestinationAction>(ref value, "caravanToFollow", Array.Empty<object>());
		if (value != null)
		{
			caravansToFollow[__instance] = value;
		}
	}
}
