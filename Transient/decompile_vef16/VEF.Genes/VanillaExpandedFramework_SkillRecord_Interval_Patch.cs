using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(SkillRecord), "Interval")]
public static class VanillaExpandedFramework_SkillRecord_Interval_Patch
{
	[HarmonyPrefix]
	public static bool Prefix(Pawn ___pawn, SkillRecord __instance)
	{
		if (StaticCollectionsClass.noSkillLoss_gene_pawns.ContainsKey((Thing)(object)___pawn) && StaticCollectionsClass.noSkillLoss_gene_pawns[(Thing)(object)___pawn] == __instance.def)
		{
			return false;
		}
		return true;
	}

	[HarmonyPostfix]
	public static void Postfix(Pawn ___pawn, SkillRecord __instance)
	{
		if (StaticCollectionsClass.skillDegradation_gene_pawns.Contains(___pawn) && __instance.levelInt < 10)
		{
			__instance.Learn(-0.1f, false, false);
		}
	}
}
