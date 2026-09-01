using HarmonyLib;
using RimWorld;

namespace VEF.Storyteller;

[HarmonyPatch(typeof(Storyteller), "TryFire")]
public static class VanillaExpandedFramework_Storyteller_TryFire_Patch
{
	public static bool Prefix(FiringIncident fi)
	{
		if (fi?.def == null)
		{
			return false;
		}
		return true;
	}
}
