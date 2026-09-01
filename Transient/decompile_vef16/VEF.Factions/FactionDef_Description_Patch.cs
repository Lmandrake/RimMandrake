using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Factions;

[HarmonyPatch(typeof(FactionDef))]
[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class FactionDef_Description_Patch
{
	public static readonly Lazy<FieldRef<FactionDef, string>> cachedDescription = new Lazy<FieldRef<FactionDef, string>>(() => AccessTools.FieldRefAccess<FactionDef, string>("cachedDescription"));

	public static void Prefix(FactionDef __instance, out bool __state)
	{
		string text = cachedDescription.Value.Invoke(__instance);
		__state = text == null;
	}

	public static void Postfix(FactionDef __instance, bool __state, ref string __result)
	{
		//IL_00c7: Unknown result type (might be due to invalid IL or missing references)
		//IL_00d1: Unknown result type (might be due to invalid IL or missing references)
		//IL_011a: Unknown result type (might be due to invalid IL or missing references)
		//IL_011f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0168: Unknown result type (might be due to invalid IL or missing references)
		//IL_016d: Unknown result type (might be due to invalid IL or missing references)
		if (!__state)
		{
			return;
		}
		HashSet<Def> hashSet = new HashSet<Def>();
		HashSet<Def> hashSet2 = new HashSet<Def>();
		foreach (ContrabandDef item in DefDatabase<ContrabandDef>.AllDefs.Where((ContrabandDef cb) => cb.factions.Contains(__instance)))
		{
			if (item.impactMultiplier > 0f)
			{
				GenCollection.AddRange<Def>(hashSet, item.AllContraband());
			}
			else
			{
				GenCollection.AddRange<Def>(hashSet2, item.AllContraband());
			}
		}
		StringBuilder stringBuilder = new StringBuilder(__result);
		if (!GenCollection.NullOrEmpty<Def>(hashSet) || !GenCollection.NullOrEmpty<Def>(hashSet2))
		{
			stringBuilder.AppendLine();
			stringBuilder.AppendLine();
			stringBuilder.AppendLine(ColoredText.AsTipTitle(Translator.Translate("VEF.Factions.FactionDef_Description_Contraband") + ":"));
		}
		if (hashSet.Count > 0)
		{
			stringBuilder.AppendLine(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.Factions.FactionDef_Description_Positives", NamedArgument.op_Implicit(Gen.ToStringSafeEnumerable((IEnumerable)hashSet.Select((Def p) => p.LabelCap))))));
		}
		if (hashSet2.Count > 0)
		{
			stringBuilder.AppendLine(TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("VEF.Factions.FactionDef_Description_Negatives", NamedArgument.op_Implicit(Gen.ToStringSafeEnumerable((IEnumerable)hashSet2.Select((Def p) => p.LabelCap))))));
		}
		__result = stringBuilder.ToString();
		cachedDescription.Value.Invoke(__instance) = __result;
	}
}
