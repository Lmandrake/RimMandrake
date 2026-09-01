using System;
using System.Collections.Generic;
using RimWorld;
using VEF.Genes;
using Verse;

namespace VEF.Apparels;

public class ApparelExtension : DefModExtension, IMergeable
{
	public float priority;

	public float skillGainModifier = 1f;

	public WorkTags workDisables;

	public List<SkillDef> skillDisables;

	public List<StatModifier> equippedStatFactors;

	public List<TraitRequirement> traitsOnEquip;

	public List<TraitRequirement> traitsOnUnequip;

	public List<PawnCapacityMinLevel> pawnCapacityMinLevels;

	public bool preventDowning;

	public bool preventKilling;

	public float preventKillingUntilHealthHPPercentage = 1f;

	public bool preventKillingUntilBrainMissing;

	public bool preventBleeding;

	public bool destroyedOnDeath;

	public List<ThingDef> secondaryApparelGraphics;

	public bool isUnifiedApparel;

	public bool hideHead;

	public bool showBodyInBedAlways;

	public Dictionary<string, List<MoveSpeedFactor>> moveSpeedFactorByTerrainTag;

	public float Priority => priority;

	public bool CanMerge(object other)
	{
		if (other != null)
		{
			return other.GetType() == typeof(ApparelExtension);
		}
		return false;
	}

	public void Merge(object extension)
	{
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0022: Unknown result type (might be due to invalid IL or missing references)
		//IL_0027: Unknown result type (might be due to invalid IL or missing references)
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		ApparelExtension apparelExtension = (ApparelExtension)extension;
		skillGainModifier *= apparelExtension.skillGainModifier;
		workDisables |= apparelExtension.workDisables;
		CombineLists(ref skillDisables, apparelExtension.skillDisables);
		CombineStatModifiers(ref equippedStatFactors, apparelExtension.equippedStatFactors);
		CombineTraits(ref traitsOnEquip, apparelExtension.traitsOnEquip);
		CombineTraits(ref traitsOnUnequip, apparelExtension.traitsOnUnequip);
		CombineStatCapacityMinLevels(ref pawnCapacityMinLevels, apparelExtension.pawnCapacityMinLevels);
		preventDowning |= apparelExtension.preventDowning;
		preventKilling |= apparelExtension.preventKilling;
		preventKillingUntilHealthHPPercentage *= apparelExtension.preventKillingUntilHealthHPPercentage;
		preventKillingUntilBrainMissing |= apparelExtension.preventKillingUntilBrainMissing;
		preventBleeding |= apparelExtension.preventBleeding;
		destroyedOnDeath |= apparelExtension.destroyedOnDeath;
		CombineLists(ref secondaryApparelGraphics, apparelExtension.secondaryApparelGraphics);
		isUnifiedApparel |= apparelExtension.isUnifiedApparel;
		hideHead |= apparelExtension.hideHead;
		showBodyInBedAlways |= apparelExtension.showBodyInBedAlways;
	}

	private static void CombineLists<T>(ref List<T> original, List<T> other)
	{
		if (original == null)
		{
			original = other;
		}
		else if (other != null)
		{
			GenCollection.AddRangeUnique<T>(original, other);
		}
	}

	public static void CombineTraits(ref List<TraitRequirement> original, List<TraitRequirement> other)
	{
		if (original == null)
		{
			original = other;
		}
		else
		{
			if (other == null)
			{
				return;
			}
			foreach (TraitRequirement otherTrait in other)
			{
				if (!GenCollection.Any<TraitRequirement>(original, (Predicate<TraitRequirement>)((TraitRequirement trait) => trait.def == otherTrait.def)))
				{
					original.Add(otherTrait);
				}
			}
		}
	}

	private static void CombineStatModifiers(ref List<StatModifier> original, List<StatModifier> other)
	{
		if (original == null)
		{
			original = other;
		}
		else
		{
			if (other == null)
			{
				return;
			}
			foreach (StatModifier otherFactor in other)
			{
				StatModifier val = GenCollection.FirstOrDefault<StatModifier>(original, (Predicate<StatModifier>)((StatModifier f) => f.stat == otherFactor.stat));
				if (val == null)
				{
					original.Add(otherFactor);
				}
				else
				{
					val.value *= otherFactor.value;
				}
			}
		}
	}

	private static void CombineStatCapacityMinLevels(ref List<PawnCapacityMinLevel> original, List<PawnCapacityMinLevel> other)
	{
		if (original == null)
		{
			original = other;
		}
		else
		{
			if (other == null)
			{
				return;
			}
			foreach (PawnCapacityMinLevel otherMinLevel in other)
			{
				PawnCapacityMinLevel pawnCapacityMinLevel = GenCollection.FirstOrDefault<PawnCapacityMinLevel>(original, (Predicate<PawnCapacityMinLevel>)((PawnCapacityMinLevel f) => f.capacity == otherMinLevel.capacity));
				if (pawnCapacityMinLevel == null)
				{
					original.Add(otherMinLevel);
				}
				else
				{
					pawnCapacityMinLevel.minLevel = Math.Max(pawnCapacityMinLevel.minLevel, otherMinLevel.minLevel);
				}
			}
		}
	}
}
