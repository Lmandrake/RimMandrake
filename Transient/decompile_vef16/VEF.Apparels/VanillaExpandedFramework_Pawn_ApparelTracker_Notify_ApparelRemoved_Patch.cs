using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Pawn_ApparelTracker), "Notify_ApparelRemoved")]
public static class VanillaExpandedFramework_Pawn_ApparelTracker_Notify_ApparelRemoved_Patch
{
	public static void Postfix(Pawn_ApparelTracker __instance, Apparel apparel)
	{
		if (__instance.pawn != null && apparel is Apparel_Shield apparel_Shield)
		{
			apparel_Shield.CompShield.equippedOffHand = false;
			CompEquippable comp = ((ThingWithComps)apparel_Shield).GetComp<CompEquippable>();
			if (comp != null)
			{
				foreach (Verb allVerb in comp.AllVerbs)
				{
					allVerb.caster = null;
					allVerb.Reset();
				}
			}
		}
		ApparelExtensionUtilities.UnequipGear(__instance.pawn, (Thing)(object)apparel);
	}
}
