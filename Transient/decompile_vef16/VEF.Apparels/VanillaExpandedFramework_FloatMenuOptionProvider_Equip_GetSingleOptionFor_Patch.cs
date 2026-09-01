using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(FloatMenuOptionProvider_Equip), "GetSingleOptionFor")]
public static class VanillaExpandedFramework_FloatMenuOptionProvider_Equip_GetSingleOptionFor_Patch
{
	public static void Postfix(FloatMenuOption __result, Thing clickedThing, FloatMenuContext context)
	{
		//IL_002a: Unknown result type (might be due to invalid IL or missing references)
		//IL_002f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0038: Unknown result type (might be due to invalid IL or missing references)
		//IL_008b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0090: Unknown result type (might be due to invalid IL or missing references)
		Apparel val = (Apparel)(object)((clickedThing is Apparel) ? clickedThing : null);
		if (val != null && ThingCompUtility.TryGetComp<CompEquippable>((Thing)(object)val) != null)
		{
			Pawn firstSelectedPawn = context.FirstSelectedPawn;
			TaggedString val2 = TranslatorFormattedStringExtensions.Translate("Equip", NamedArgument.op_Implicit(((Entity)val).LabelShort));
			if (__result != null && TaggedString.op_Implicit(val2) == __result.Label && firstSelectedPawn.equipment != null && !((Thing)val).def.UsableWithShields() && firstSelectedPawn.OffHandShield() is Apparel_Shield apparel_Shield)
			{
				__result.Label += string.Format(" {0}", TranslatorFormattedStringExtensions.Translate("VanillaFactionsExpanded.EquipWarningShieldUnusableWithWeapon", NamedArgument.op_Implicit(((Def)((Thing)apparel_Shield).def).label)));
			}
		}
	}
}
