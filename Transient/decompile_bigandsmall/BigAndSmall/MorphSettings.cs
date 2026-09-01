using System.Collections.Generic;
using BigAndSmall.FilteredLists;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class MorphSettings
{
	public bool isRetromorph;

	public bool isStandalone;

	protected bool requiresFrequentChecks;

	/// <summary>
	/// Requires the conditional stat effector to evaluate to true for the morph to be allowed.
	/// </summary>
	public List<ConditionalStatAffecter> conditionals;

	public List<HediffDef> requiredHediffs;

	public List<HediffDef> disallowedHediffs;

	public List<GeneDef> requiredGenes;

	public List<GeneDef> disallowedGenes;

	public FilterListSet<ThingDef> raceFilter;

	public int? morphOverAge;

	public int? morphUnderAge;

	public bool morphIfPregnant;

	public bool morphIfNight;

	public bool morphIfDay;

	public bool RequiresFrequentChecks
	{
		get
		{
			if (!requiresFrequentChecks && !morphIfDay)
			{
				return morphIfNight;
			}
			return true;
		}
	}

	public bool CanMorph(Pawn pawn)
	{
		if (morphOverAge.HasValue && pawn.ageTracker.AgeBiologicalYears < morphOverAge)
		{
			return false;
		}
		if (morphUnderAge.HasValue && pawn.ageTracker.AgeBiologicalYears >= morphUnderAge)
		{
			return false;
		}
		if (morphIfPregnant && !pawn.health.hediffSet.HasHediff(HediffDefOf.PregnantHuman, false))
		{
			return false;
		}
		if (morphIfDay && ((Thing)pawn).Map.skyManager.CurSkyGlow < 0.3f)
		{
			return false;
		}
		if (morphIfNight && ((Thing)pawn).Map.skyManager.CurSkyGlow > 0.3f)
		{
			return false;
		}
		if (conditionals != null && !ConditionalManager.TestConditionals(pawn, conditionals))
		{
			return false;
		}
		if (requiredHediffs != null)
		{
			foreach (HediffDef requiredHediff in requiredHediffs)
			{
				if (!pawn.health.hediffSet.HasHediff(requiredHediff, false))
				{
					return false;
				}
			}
		}
		if (disallowedHediffs != null)
		{
			foreach (HediffDef disallowedHediff in disallowedHediffs)
			{
				if (pawn.health.hediffSet.HasHediff(disallowedHediff, false))
				{
					return false;
				}
			}
		}
		HashSet<GeneDef> allActiveGeneDefs = GeneHelpers.GetAllActiveGeneDefs(pawn);
		if (requiredGenes != null)
		{
			foreach (GeneDef requiredGene in requiredGenes)
			{
				if (!allActiveGeneDefs.Contains(requiredGene))
				{
					return false;
				}
			}
		}
		if (disallowedGenes != null)
		{
			foreach (GeneDef disallowedGene in disallowedGenes)
			{
				if (allActiveGeneDefs.Contains(disallowedGene))
				{
					return false;
				}
			}
		}
		if (raceFilter != null && raceFilter.GetFilterResult(((Thing)pawn).def).Denied())
		{
			return false;
		}
		return true;
	}
}
