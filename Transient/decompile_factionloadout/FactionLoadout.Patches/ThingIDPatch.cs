using HarmonyLib;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(ThingIDMaker), "GiveIDTo")]
public static class ThingIDPatch
{
	public static bool Active;

	[HarmonyPriority(800)]
	public static bool Prefix(Thing t)
	{
		if (Active)
		{
			t.thingIDNumber = 69420;
			return false;
		}
		return true;
	}
}
