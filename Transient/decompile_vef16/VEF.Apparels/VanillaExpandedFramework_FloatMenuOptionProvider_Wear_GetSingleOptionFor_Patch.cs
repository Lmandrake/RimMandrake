using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Apparels;

[HarmonyPatch(typeof(FloatMenuOptionProvider_Wear), "GetSingleOptionFor")]
public static class VanillaExpandedFramework_FloatMenuOptionProvider_Wear_GetSingleOptionFor_Patch
{
	public static void Postfix(ref FloatMenuOption __result, Thing clickedThing, FloatMenuContext context)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		//IL_001b: Unknown result type (might be due to invalid IL or missing references)
		//IL_0020: Unknown result type (might be due to invalid IL or missing references)
		//IL_0025: Unknown result type (might be due to invalid IL or missing references)
		//IL_0031: Unknown result type (might be due to invalid IL or missing references)
		if (clickedThing is Apparel_Shield apparel_Shield)
		{
			TaggedString val = TranslatorFormattedStringExtensions.Translate("ForceWear", NamedArgument.op_Implicit(((Entity)apparel_Shield).LabelCap), NamedArgument.op_Implicit((Thing)(object)apparel_Shield));
			if (__result != null && __result.Label == TaggedString.op_Implicit(val))
			{
				__result = null;
			}
		}
	}
}
