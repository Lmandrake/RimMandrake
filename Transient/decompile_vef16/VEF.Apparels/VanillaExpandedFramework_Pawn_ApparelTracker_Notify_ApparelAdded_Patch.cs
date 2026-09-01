using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Pawn_ApparelTracker), "Notify_ApparelAdded")]
public static class VanillaExpandedFramework_Pawn_ApparelTracker_Notify_ApparelAdded_Patch
{
	public static void Postfix(Pawn_ApparelTracker __instance, Apparel apparel)
	{
		if (apparel is Apparel_Shield apparel_Shield)
		{
			apparel_Shield.CompShield.equippedOffHand = true;
			CompEquippable comp = ((ThingWithComps)apparel_Shield).GetComp<CompEquippable>();
			if (comp != null)
			{
				foreach (Verb allVerb in comp.AllVerbs)
				{
					allVerb.caster = (Thing)(object)((Apparel)apparel_Shield).Wearer;
					allVerb.Reset();
				}
			}
		}
		ApparelExtensionUtilities.EquipGear(__instance.pawn, (Thing)(object)apparel);
	}
}
