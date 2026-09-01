using HarmonyLib;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(PawnGenerator), "GenerateRandomAge")]
public static class PawnGenAgePatchCore
{
	[HarmonyPrefix]
	public static bool Prefix(Pawn pawn, ref PawnGenerationRequest request)
	{
		//IL_000e: Unknown result type (might be due to invalid IL or missing references)
		//IL_013e: Unknown result type (might be due to invalid IL or missing references)
		if (!pawn.RaceProps.Humanlike || DevelopmentalStageExtensions.Newborn(((PawnGenerationRequest)(ref request)).AllowedDevelopmentalStages))
		{
			return true;
		}
		int? num = null;
		int? num2 = null;
		foreach (PawnKindEdit item in PawnKindEdit.GetEditsFor(pawn.kindDef, ((Thing)pawn).Faction?.def))
		{
			if (item.MinGenerationAge.HasValue && (!item.IsGlobal || !num.HasValue))
			{
				num = item.MinGenerationAge;
			}
			if (item.MaxGenerationAge.HasValue && (!item.IsGlobal || !num2.HasValue))
			{
				num2 = item.MaxGenerationAge;
			}
		}
		if (!num.HasValue && !num2.HasValue)
		{
			return true;
		}
		FloatRange val = default(FloatRange);
		((FloatRange)(ref val))._002Ector((float)(num ?? pawn.kindDef.minGenerationAge), (float)(num2 ?? pawn.kindDef.maxGenerationAge));
		((PawnGenerationRequest)(ref request)).FixedBiologicalAge = ((FloatRange)(ref val)).RandomInRange;
		((PawnGenerationRequest)(ref request)).AllowedDevelopmentalStages = LifeStageUtility.CalculateDevelopmentalStage(pawn, ((PawnGenerationRequest)(ref request)).FixedBiologicalAge.Value);
		if (((PawnGenerationRequest)(ref request)).FixedChronologicalAge.HasValue && (double)((PawnGenerationRequest)(ref request)).FixedBiologicalAge.GetValueOrDefault() > (double)((PawnGenerationRequest)(ref request)).FixedChronologicalAge.GetValueOrDefault())
		{
			((PawnGenerationRequest)(ref request)).FixedChronologicalAge = ((PawnGenerationRequest)(ref request)).FixedBiologicalAge;
		}
		return true;
	}
}
