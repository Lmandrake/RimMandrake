using HarmonyLib;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Gene_PsychicBonding), "BondTo")]
public static class Gene_PsychicBonding_BondTo
{
	public static void Postfix(Gene_PsychicBonding __instance, ref Pawn ___bondedPawn)
	{
		if (GeneHelpers.GetActiveGenesByName(((Gene)__instance).pawn, "VU_LethalLover").Count > 0 && ___bondedPawn != null)
		{
			Hediff val = HediffMaker.MakeHediff(BSDefs.VU_SuccubusBond, ((Gene)__instance).pawn, (BodyPartRecord)null);
			((Gene)__instance).pawn.health.AddHediff(val, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			Hediff val2 = HediffMaker.MakeHediff(BSDefs.VU_SuccubusBond_Victim, ___bondedPawn, (BodyPartRecord)null);
			___bondedPawn.health.AddHediff(val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
		}
	}
}
