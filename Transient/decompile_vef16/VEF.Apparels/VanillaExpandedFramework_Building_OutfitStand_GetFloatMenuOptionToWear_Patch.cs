using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HotSwappable]
[HarmonyPatch(typeof(Building_OutfitStand), "GetFloatMenuOptions")]
public static class VanillaExpandedFramework_Building_OutfitStand_GetFloatMenuOptionToWear_Patch
{
	public static IEnumerable<FloatMenuOption> Postfix(IEnumerable<FloatMenuOption> __result, Building_OutfitStand __instance, Pawn selPawn)
	{
		//IL_003f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0045: Unknown result type (might be due to invalid IL or missing references)
		//IL_004a: Unknown result type (might be due to invalid IL or missing references)
		//IL_004f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0083: Unknown result type (might be due to invalid IL or missing references)
		//IL_0089: Unknown result type (might be due to invalid IL or missing references)
		//IL_008e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0093: Unknown result type (might be due to invalid IL or missing references)
		//IL_00e5: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ea: Unknown result type (might be due to invalid IL or missing references)
		//IL_00ef: Unknown result type (might be due to invalid IL or missing references)
		//IL_0151: Unknown result type (might be due to invalid IL or missing references)
		//IL_0156: Unknown result type (might be due to invalid IL or missing references)
		List<FloatMenuOption> list = __result.ToList();
		foreach (Thing heldItem in __instance.HeldItems)
		{
			if (heldItem is Apparel_Shield apparel_Shield)
			{
				TaggedString toCheck = TranslatorFormattedStringExtensions.Translate("ForceWear", NamedArgument.op_Implicit(((Entity)apparel_Shield).LabelCap), NamedArgument.op_Implicit((Thing)(object)apparel_Shield));
				FloatMenuOption val = GenCollection.FirstOrDefault<FloatMenuOption>(list, (Predicate<FloatMenuOption>)((FloatMenuOption x) => x.Label.Contains(TaggedString.op_Implicit(toCheck))));
				if (val != null)
				{
					list.Remove(val);
				}
				TaggedString toCheck2 = TranslatorFormattedStringExtensions.Translate("ForceTargetToWear", NamedArgument.op_Implicit(((Entity)apparel_Shield).LabelShort), NamedArgument.op_Implicit((Thing)(object)apparel_Shield));
				FloatMenuOption val2 = GenCollection.FirstOrDefault<FloatMenuOption>(list, (Predicate<FloatMenuOption>)((FloatMenuOption x) => x.Label.Contains(TaggedString.op_Implicit(toCheck2))));
				if (val2 != null)
				{
					list.Remove(val2);
				}
			}
			Apparel val3 = (Apparel)(object)((heldItem is Apparel) ? heldItem : null);
			if (val3 != null && ThingCompUtility.TryGetComp<CompEquippable>((Thing)(object)val3) != null)
			{
				TaggedString toCheck3 = TranslatorFormattedStringExtensions.Translate("Equip", NamedArgument.op_Implicit(((Entity)val3).LabelShort));
				FloatMenuOption val4 = __result.FirstOrDefault((FloatMenuOption x) => x.Label.Contains(TaggedString.op_Implicit(toCheck3)));
				if (val4 != null && selPawn.equipment != null && !((Thing)val3).def.UsableWithShields() && selPawn.OffHandShield() is Apparel_Shield apparel_Shield2)
				{
					val4.Label += string.Format(" {0}", TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.EquipWarningShieldUnusableWithWeapon", NamedArgument.op_Implicit(((Def)((Thing)apparel_Shield2).def).label)));
				}
				FloatMenuOption val5 = FloatMenuOptionProvider_EquipShield.AddShieldFloatMenuOption(selPawn, (Thing)(object)val3, (Thing)(object)__instance);
				if (val5 != null)
				{
					list.Add(val5);
				}
			}
		}
		return list;
	}
}
