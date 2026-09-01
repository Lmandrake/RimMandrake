using HarmonyLib;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(HediffComp_PregnantHuman))]
[HarmonyPatch(/*Could not decode attribute arguments.*/)]
public static class VanillaExpandedFramework_HediffComp_PregnantHuman_CompTipStringExtra_Patch
{
	[HarmonyPostfix]
	public static void AddGeneMultiplierExplanation(HediffWithComps ___parent, ref string __result)
	{
		//IL_0034: Unknown result type (might be due to invalid IL or missing references)
		//IL_0039: Unknown result type (might be due to invalid IL or missing references)
		//IL_003e: Unknown result type (might be due to invalid IL or missing references)
		if (StaticCollectionsClass.pregnancySpeedFactor_gene_pawns.ContainsKey((Thing)(object)((Hediff)___parent).pawn))
		{
			__result = TaggedString.op_Implicit(__result + "\n" + TranslatorFormattedStringExtensions.Translate("VGE_PregnancyFactor", NamedArgument.op_Implicit(StaticCollectionsClass.pregnancySpeedFactor_gene_pawns[(Thing)(object)((Hediff)___parent).pawn])));
		}
	}
}
