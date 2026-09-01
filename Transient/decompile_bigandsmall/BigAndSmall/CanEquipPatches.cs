using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class CanEquipPatches
{
	public static bool CanEquipThing(bool __result, ThingDef thing, Pawn pawn, ref string cantReason)
	{
		//IL_005f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0099: Unknown result type (might be due to invalid IL or missing references)
		//IL_00b9: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e6: Unknown result type (might be due to invalid IL or missing references)
		if (__result && thing != null && pawn != null)
		{
			RaceProperties raceProps = pawn.RaceProps;
			if (((raceProps != null) ? new bool?(raceProps.Humanlike) : ((bool?)null)) == true)
			{
				BSCache cache = FastAcccess.GetCache(pawn);
				if (cache != null)
				{
					if (thing.IsWeapon && !cache.canWield)
					{
						cantReason = TaggedString.op_Implicit(Translator.Translate("BS_GenePreventsEquipping"));
						return false;
					}
					ApparelRestrictions apparelRestrictions = cache.apparelRestrictions;
					if (apparelRestrictions != null)
					{
						string text = apparelRestrictions.CanWear(thing);
						if (text != null)
						{
							cantReason = text;
							return false;
						}
					}
					else
					{
						if (!thing.HasRequiredWeaponClassTags(new List<string>()))
						{
							cantReason = TaggedString.op_Implicit(Translator.Translate("BS_LacksRequiredClassTag"));
							return false;
						}
						if (!thing.HasRequiredWeaponTags(new List<string>()))
						{
							cantReason = TaggedString.op_Implicit(Translator.Translate("BS_LacksRequiredTag"));
							return false;
						}
						if (thing.apparel != null && !thing.apparel.HasRequiredApparelTags(new List<string>()))
						{
							cantReason = TaggedString.op_Implicit(Translator.Translate("BS_LacksRequiredTag"));
							return false;
						}
					}
				}
				return __result;
			}
		}
		return __result;
	}

	[HarmonyPatch(/*Could not decode attribute arguments.*/)]
	[HarmonyPostfix]
	public static void CanEquip_Postfix(ref bool __result, Thing thing, Pawn pawn, ref string cantReason, bool checkBonded = true)
	{
		__result = CanEquipThing(__result, thing.def, pawn, ref cantReason);
	}

	[HarmonyPatch(typeof(ApparelProperties), "PawnCanWear", new Type[]
	{
		typeof(Pawn),
		typeof(bool)
	})]
	[HarmonyPostfix]
	public static void PawnCanWear_Postfix(ApparelProperties __instance, ref bool __result, Pawn pawn)
	{
		if (pawn == null)
		{
			return;
		}
		RaceProperties raceProps = pawn.RaceProps;
		if (((raceProps != null) ? new bool?(raceProps.Humanlike) : ((bool?)null)) != true)
		{
			return;
		}
		BSCache cache = HumanoidPawnScaler.GetCache(pawn);
		if (cache != null && cache.apparelRestrictions != null)
		{
			if (cache.apparelRestrictions.CanWear(__instance, out var _) != null)
			{
				__result = false;
			}
		}
		else if (ItemRestrictionDef.AllRestrictedTags.Any(__instance.tags.Contains))
		{
			__result = false;
		}
	}

	[HarmonyPatch(typeof(ApparelRequirement), "AllowedForPawn")]
	[HarmonyPostfix]
	public static void AllowedForPawn_Postfix(ApparelRequirement __instance, ref bool __result, Pawn p, ThingDef apparel, bool ignoreGender)
	{
		if (__result)
		{
			string cantReason = "";
			__result = CanEquipThing(__result, apparel, p, ref cantReason);
		}
	}

	[HarmonyPatch(typeof(ApparelRequirement), "RequiredForPawn")]
	[HarmonyPostfix]
	public static void RequiredForPawn_Postfix(ApparelRequirement __instance, ref bool __result, Pawn p, ThingDef apparel, bool ignoreGender)
	{
		if (__result)
		{
			string cantReason = "";
			__result = CanEquipThing(__result, apparel, p, ref cantReason);
		}
	}

	[HarmonyPatch(typeof(Apparel), "PawnCanWear")]
	[HarmonyPostfix]
	public static void PawnCanWear_Postfix(Apparel __instance, ref bool __result, Pawn pawn, bool ignoreGender)
	{
		if (__result)
		{
			string cantReason = "";
			__result = CanEquipThing(__result, ((Thing)__instance).def, pawn, ref cantReason);
		}
	}
}
