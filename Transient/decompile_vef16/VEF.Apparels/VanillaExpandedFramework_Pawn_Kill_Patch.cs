using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(Pawn), "Kill")]
public static class VanillaExpandedFramework_Pawn_Kill_Patch
{
	private static bool Prefix(Pawn __instance, out List<Thing> __state)
	{
		List<Thing> gearToRemove = null;
		bool allowedToDie = true;
		Pawn_ApparelTracker apparel = __instance.apparel;
		HandleEquipment<Apparel>((apparel != null) ? apparel.WornApparel : null);
		if (allowedToDie)
		{
			Pawn_EquipmentTracker equipment = __instance.equipment;
			HandleEquipment<ThingWithComps>((equipment != null) ? equipment.AllEquipmentListForReading : null);
		}
		if (!allowedToDie)
		{
			__state = null;
			return false;
		}
		__state = gearToRemove;
		return true;
		void HandleEquipment<T>(List<T> list) where T : Thing
		{
			if (list == null)
			{
				return;
			}
			foreach (T item in list)
			{
				ApparelExtension modExtension = ((Def)((Thing)item).def).GetModExtension<ApparelExtension>();
				if (modExtension != null)
				{
					if (modExtension.preventKilling)
					{
						float num = __instance.health.hediffSet.GetNotMissingParts((BodyPartHeight)0, (BodyPartDepth)0, (BodyPartTagDef)null, (BodyPartRecord)null).Sum((BodyPartRecord x) => x.def.GetMaxHealth(__instance)) / ((Thing)__instance).def.race.body.AllParts.Sum((BodyPartRecord x) => x.def.GetMaxHealth(__instance));
						if (modExtension.preventKillingUntilHealthHPPercentage < num && (!modExtension.preventKillingUntilBrainMissing || __instance.health.hediffSet.GetBrain() != null))
						{
							allowedToDie = false;
							break;
						}
					}
					if (modExtension.destroyedOnDeath)
					{
						if (gearToRemove == null)
						{
							gearToRemove = new List<Thing>();
						}
						gearToRemove.Add((Thing)(object)item);
					}
				}
			}
		}
	}

	private static void Postfix(Pawn __instance, List<Thing> __state)
	{
		if (!__instance.Dead || GenList.NullOrEmpty<Thing>((IList<Thing>)__state))
		{
			return;
		}
		foreach (Thing item in __state)
		{
			if (!item.Destroyed)
			{
				item.Destroy((DestroyMode)0);
			}
		}
	}
}
