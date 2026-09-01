using System;
using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using Verse;

namespace FactionLoadout.Patches;

[HarmonyPatch(typeof(PawnGenerator), "GenerateNewPawnInternal")]
public static class PawnGenPatchCore
{
	[HarmonyPostfix]
	public static void Postfix(Pawn __result, PawnGenerationRequest request)
	{
		//IL_03ae: Unknown result type (might be due to invalid IL or missing references)
		//IL_03b9: Expected O, but got Unknown
		object obj;
		if (__result == null)
		{
			obj = null;
		}
		else
		{
			PawnKindDef kindDef = __result.kindDef;
			obj = ((kindDef != null) ? ((Def)kindDef).GetModExtension<ForcedExtrasModExtension>() : null);
		}
		if (obj == null)
		{
			if (__result == null)
			{
				obj = null;
			}
			else
			{
				PawnKindDef kindDef2 = __result.kindDef;
				obj = ((kindDef2 != null) ? ((Def)kindDef2).GetModExtension<ForcedHediffModExtension>() : null);
			}
		}
		ForcedExtrasModExtension forcedExtrasModExtension = (ForcedExtrasModExtension)obj;
		if (forcedExtrasModExtension == null)
		{
			return;
		}
		foreach (ForcedHediff forcedHediff in forcedExtrasModExtension.forcedHediffs)
		{
			if (forcedHediff.HediffDef == null || !Rand.Chance(forcedHediff.chance))
			{
				continue;
			}
			List<DefRef<BodyPartDef>> parts = forcedHediff.parts;
			Stack<BodyPartRecord> stack = ((parts == null || parts.Count <= 0) ? null : new Stack<BodyPartRecord>(GenCollection.InRandomOrder<BodyPartRecord>(from p in __result.health.hediffSet.GetNotMissingParts((BodyPartHeight)0, (BodyPartDepth)0, (BodyPartTagDef)null, (BodyPartRecord)null)
				where GenCollection.Any<DefRef<BodyPartDef>>(forcedHediff.parts, (Predicate<DefRef<BodyPartDef>>)((DefRef<BodyPartDef> r) => r.Def == p.def))
				select p, (IList<BodyPartRecord>)null)));
			int num = Math.Min(forcedHediff.PartsToHit(), stack?.Count ?? 1);
			for (int i = 0; i < num; i++)
			{
				if (__result.health.hediffSet.GetHediffCount(forcedHediff.HediffDef) >= num)
				{
					break;
				}
				BodyPartRecord val = stack?.Pop();
				if (val == null && typeof(Hediff_Implant).IsAssignableFrom(forcedHediff.HediffDef.hediffClass))
				{
					ModCore.Warn("Skipping hediff '" + ((Def)forcedHediff.HediffDef).defName + "' on pawn '" + ((Def)(__result.kindDef?)).defName + "': implant requires a body part but none was found.");
					continue;
				}
				try
				{
					Hediff val2 = HediffMaker.MakeHediff(forcedHediff.HediffDef, __result, val);
					__result.health.AddHediff(val2, (BodyPartRecord)null, (DamageInfo?)null, (DamageResult)null);
				}
				catch (Exception ex)
				{
					ModCore.Warn("Failed to apply hediff '" + ((Def)forcedHediff.HediffDef).defName + "' to pawn '" + ((Def)(__result.kindDef?)).defName + "': " + ex.Message);
				}
			}
		}
		Pawn_GeneTracker genes = __result.genes;
		if (genes != null)
		{
			foreach (ForcedGene forcedGene in forcedExtrasModExtension.forcedGenes)
			{
				if (forcedGene.GeneDef == null || !Rand.Chance(forcedGene.chance))
				{
					continue;
				}
				Gene val3 = genes.AddGene(forcedGene.GeneDef, false);
				if (!forcedGene.forceActive || val3 == null)
				{
					continue;
				}
				val3.OverrideBy((Gene)null);
				foreach (Gene item in genes.GenesListForReading)
				{
					if (item != val3 && item.def.ConflictsWith(val3.def))
					{
						genes.RemoveGene(item);
					}
				}
			}
		}
		TraitSet val4 = __result.story?.traits;
		if (val4 == null)
		{
			return;
		}
		foreach (ForcedTrait forcedTrait in forcedExtrasModExtension.forcedTraits)
		{
			if (forcedTrait.TraitDef != null && Rand.Chance(forcedTrait.chance) && !val4.HasTrait(forcedTrait.TraitDef, forcedTrait.degree))
			{
				val4.GainTrait(new Trait(forcedTrait.TraitDef, forcedTrait.degree, false), false);
			}
		}
	}
}
