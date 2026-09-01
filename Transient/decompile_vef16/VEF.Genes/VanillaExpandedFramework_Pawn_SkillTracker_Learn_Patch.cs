using HarmonyLib;
using RimWorld;
using Verse;

namespace VEF.Genes;

[HarmonyPatch(typeof(Pawn_SkillTracker))]
[HarmonyPatch("Learn")]
public static class VanillaExpandedFramework_Pawn_SkillTracker_Learn_Patch
{
	[HarmonyPostfix]
	public static void GiveRecreation(Pawn ___pawn, SkillDef sDef, float xp)
	{
		if (!(xp > 0f) || !StaticCollectionsClass.skillRecreation_gene_pawns.ContainsKey((Thing)(object)___pawn) || StaticCollectionsClass.skillRecreation_gene_pawns[(Thing)(object)___pawn] != sDef)
		{
			return;
		}
		Pawn_NeedsTracker needs = ___pawn.needs;
		if (needs != null)
		{
			Need_Joy joy = needs.joy;
			if (joy != null)
			{
				joy.GainJoy(xp * 0.001f, VEFDefOf.Gaming_Cerebral);
			}
		}
	}
}
