using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch]
public static class GenerateNewPawnInternal
{
	[HarmonyPatch(typeof(PawnGenerator), "GenerateNewPawnInternal")]
	[HarmonyPrefix]
	public static void MaySetForcedGender(ref Pawn __result, ref PawnGenerationRequest request)
	{
		try
		{
			ThingDef val = ((PawnGenerationRequest)(ref request)).KindDef?.race;
			if (val != null)
			{
				RaceExtension raceExtension = val.GetRaceExtensions()?.FirstOrDefault();
				if (raceExtension != null && raceExtension.femaleGenderChance.HasValue && !((PawnGenerationRequest)(ref request)).FixedGender.HasValue)
				{
					bool flag = Rand.Value < raceExtension.femaleGenderChance;
					((PawnGenerationRequest)(ref request)).FixedGender = (Gender)(flag ? 2 : 2);
				}
			}
		}
		catch (Exception ex)
		{
			Log.Error("Managed error when setting female gender chance in GenerateNewPawnInternalPrefix:\n" + ex.Message + "\n" + ex.StackTrace);
		}
	}

	[HarmonyPatch(typeof(PawnBioAndNameGenerator), "GiveAppropriateBioAndNameTo")]
	[HarmonyPrefix]
	public static void GiveAppropriateBioAndNameToPrefix(Pawn pawn, FactionDef factionType, PawnGenerationRequest request, XenotypeDef xenotype = null)
	{
		//IL_0088: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Unknown result type (might be due to invalid IL or missing references)
		if (xenotype == null)
		{
			return;
		}
		try
		{
			List<PawnExtension> list = xenotype.AllGenes.SelectMany((GeneDef x) => x.ExtensionsOnDef<PawnExtension, GeneDef>((List<Type>)null, (List<Type>)null, doSort: true)).ToList();
			bool flag = GenCollection.Any<PawnExtension>(list, (Predicate<PawnExtension>)((PawnExtension x) => x.forceGender == (Gender?)2));
			bool flag2 = GenCollection.Any<PawnExtension>(list, (Predicate<PawnExtension>)((PawnExtension x) => x.forceGender == (Gender?)1));
			if (flag && !flag2)
			{
				pawn.gender = (Gender)2;
			}
			else if (flag2 && !flag)
			{
				pawn.gender = (Gender)1;
			}
		}
		catch (Exception ex)
		{
			Log.Error("Managed error in GiveAppropriateBioAndNameToPrefix when setting gender based on genes:\n" + ex.Message + "\n" + ex.StackTrace);
		}
	}
}
