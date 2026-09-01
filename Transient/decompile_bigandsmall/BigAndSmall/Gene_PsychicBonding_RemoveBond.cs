using System;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace BigAndSmall;

[HarmonyPatch(typeof(Gene_PsychicBonding), "RemoveBond")]
public static class Gene_PsychicBonding_RemoveBond
{
	public static void Prefix(Gene_PsychicBonding __instance, ref Pawn ___bondedPawn)
	{
		//IL_01aa: Unknown result type (might be due to invalid IL or missing references)
		//IL_01b1: Expected O, but got Unknown
		//IL_021f: Unknown result type (might be due to invalid IL or missing references)
		//IL_0224: Unknown result type (might be due to invalid IL or missing references)
		if (GeneHelpers.GetActiveGenesByName(((Gene)__instance).pawn, "VU_LethalLover").Count <= 0)
		{
			return;
		}
		Pawn obj = ___bondedPawn;
		if (obj != null)
		{
			Pawn_NeedsTracker needs = obj.needs;
			if (needs != null)
			{
				Need_Mood mood = needs.mood;
				if (mood != null)
				{
					ThoughtHandler thoughts = mood.thoughts;
					if (thoughts != null)
					{
						MemoryThoughtHandler memories = thoughts.memories;
						if (memories != null)
						{
							memories.TryGainMemory(ThoughtDefOf.PsychicBondTorn, ((Gene)__instance).pawn, (Precept)null);
						}
					}
				}
			}
		}
		if (___bondedPawn == null)
		{
			return;
		}
		Hediff firstHediffOfDef = ((Gene)__instance).pawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.VU_SuccubusBond, false);
		if (firstHediffOfDef != null)
		{
			((Gene)__instance).pawn.health.RemoveHediff(firstHediffOfDef);
		}
		Hediff firstHediffOfDef2 = ___bondedPawn.health.hediffSet.GetFirstHediffOfDef(BSDefs.VU_SuccubusBond_Victim, false);
		if (firstHediffOfDef2 != null)
		{
			___bondedPawn.health.RemoveHediff(firstHediffOfDef2);
		}
		Pawn partnerPawn = ___bondedPawn;
		___bondedPawn = null;
		Hediff firstHediffOfDef3 = ((Gene)__instance).pawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.PsychicBond, false);
		Hediff_PsychicBond val = (Hediff_PsychicBond)(object)((firstHediffOfDef3 is Hediff_PsychicBond) ? firstHediffOfDef3 : null);
		if (val != null && ((HediffWithTarget)val).target == partnerPawn)
		{
			((Gene)__instance).pawn.health.RemoveHediff((Hediff)(object)val);
		}
		Hediff firstHediffOfDef4 = partnerPawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.PsychicBond, false);
		Hediff_PsychicBond val2 = (Hediff_PsychicBond)(object)((firstHediffOfDef4 is Hediff_PsychicBond) ? firstHediffOfDef4 : null);
		if (val2 != null)
		{
			partnerPawn.health.RemoveHediff((Hediff)(object)val2);
		}
		Pawn_GeneTracker genes = partnerPawn.genes;
		if (genes != null)
		{
			Gene_PsychicBonding firstGeneOfType = genes.GetFirstGeneOfType<Gene_PsychicBonding>();
			if (firstGeneOfType != null)
			{
				firstGeneOfType.RemoveBond();
			}
		}
		if (((Gene)__instance).pawn.Dead)
		{
			if (partnerPawn.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.PsychicBondTorn, false) == null)
			{
				Hediff_PsychicBondTorn val3 = (Hediff_PsychicBondTorn)HediffMaker.MakeHediff(HediffDefOf.PsychicBondTorn, partnerPawn, (BodyPartRecord)null);
				((HediffWithTarget)val3).target = (Thing)(object)((Gene)__instance).pawn;
				partnerPawn.health.AddHediff((Hediff)(object)val3, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
			}
			MentalBreakDef val4 = default(MentalBreakDef);
			if (GenCollection.TryRandomElementByWeight<MentalBreakDef>(DefDatabase<MentalBreakDef>.AllDefsListForReading.Where((MentalBreakDef d) => (int)d.intensity == 3 && d.Worker.BreakCanOccur(partnerPawn)), (Func<MentalBreakDef, float>)((MentalBreakDef d) => d.Worker.CommonalityFor(partnerPawn, true)), ref val4))
			{
				val4.Worker.TryStart(partnerPawn, TaggedString.op_Implicit(TranslatorFormattedStringExtensions.Translate("MentalStateReason_BondedHumanDeath", NamedArgument.op_Implicit((Thing)(object)((Gene)__instance).pawn))), false);
			}
		}
	}
}
