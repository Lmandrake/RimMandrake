using System.Collections.Generic;
using RimWorld;
using VEF.Genes;
using Verse;

namespace VEF.Apparels;

public static class ApparelExtensionUtilities
{
	public static bool doNotRunTraitsPatch;

	public static bool GearAffectsStats(Thing gear, StatDef stat)
	{
		ApparelExtension apparelExtension = ((gear != null) ? ((Def)gear.def).GetModExtension<ApparelExtension>() : null);
		if (apparelExtension == null)
		{
			return false;
		}
		if (!GenList.NullOrEmpty<StatModifier>((IList<StatModifier>)apparelExtension.equippedStatFactors) && StatUtility.GetStatFactorFromList(apparelExtension.equippedStatFactors, stat) != 1f)
		{
			return true;
		}
		return false;
	}

	internal static bool GearAffectsStatsWrapper(bool original, Thing gear, StatDef stat)
	{
		if (!original)
		{
			return GearAffectsStats(gear, stat);
		}
		return true;
	}

	public static void EquipGear(Pawn pawn, Thing gear)
	{
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		if (pawn == null)
		{
			return;
		}
		ApparelExtension apparelExtension = ((gear != null) ? ((Def)gear.def).GetModExtension<ApparelExtension>() : null);
		if (apparelExtension == null)
		{
			return;
		}
		if ((!doNotRunTraitsPatch || !VanillaExpandedFramework_Pawn_ApparelTracker_Wear_Patch.doNotRunTraitsPatch) && pawn.story?.traits != null)
		{
			if (apparelExtension.traitsOnEquip != null)
			{
				AddTraits(apparelExtension.traitsOnEquip, pawn);
			}
			if (apparelExtension.traitsOnUnequip != null)
			{
				RemoveTraits(apparelExtension.traitsOnUnequip, pawn);
			}
		}
		if ((int)apparelExtension.workDisables != 0)
		{
			pawn.Notify_DisabledWorkTypesChanged();
		}
		if (!GenList.NullOrEmpty<StatModifier>((IList<StatModifier>)apparelExtension.equippedStatFactors))
		{
			pawn.health.capacities.Notify_CapacityLevelsDirty();
		}
		if (!GenDictionary.NullOrEmpty<string, List<MoveSpeedFactor>>(apparelExtension.moveSpeedFactorByTerrainTag))
		{
			global::VEF.Genes.StaticCollectionsClass.AddMoveSpeedFactorByTerrainTag((Thing)(object)pawn, gear, apparelExtension.moveSpeedFactorByTerrainTag);
		}
	}

	public static void UnequipGear(Pawn pawn, Thing gear)
	{
		//IL_0065: Unknown result type (might be due to invalid IL or missing references)
		if (pawn == null)
		{
			return;
		}
		ApparelExtension apparelExtension = ((gear != null) ? ((Def)gear.def).GetModExtension<ApparelExtension>() : null);
		if (apparelExtension == null)
		{
			return;
		}
		if ((!doNotRunTraitsPatch || !VanillaExpandedFramework_Pawn_ApparelTracker_Wear_Patch.doNotRunTraitsPatch) && pawn.story?.traits != null)
		{
			if (apparelExtension.traitsOnEquip != null)
			{
				RemoveTraits(apparelExtension.traitsOnEquip, pawn);
			}
			if (apparelExtension.traitsOnUnequip != null)
			{
				AddTraits(apparelExtension.traitsOnUnequip, pawn);
			}
		}
		if ((int)apparelExtension.workDisables != 0)
		{
			pawn.Notify_DisabledWorkTypesChanged();
		}
		if (!GenList.NullOrEmpty<StatModifier>((IList<StatModifier>)apparelExtension.equippedStatFactors))
		{
			pawn.health.capacities.Notify_CapacityLevelsDirty();
		}
		if (!GenDictionary.NullOrEmpty<string, List<MoveSpeedFactor>>(apparelExtension.moveSpeedFactorByTerrainTag))
		{
			global::VEF.Genes.StaticCollectionsClass.RemoveMoveSpeedFactorByTerrainTag((Thing)(object)pawn, gear);
		}
	}

	private static void AddTraits(List<TraitRequirement> traits, Pawn pawn)
	{
		//IL_008c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0097: Expected O, but got Unknown
		foreach (TraitRequirement trait in traits)
		{
			bool flag = false;
			foreach (Trait allTrait in pawn.story.traits.allTraits)
			{
				if (allTrait.sourceGene == null && allTrait.def == trait.def)
				{
					flag = true;
					break;
				}
			}
			if (!flag)
			{
				pawn.story.traits.GainTrait(new Trait(trait.def, trait.degree.GetValueOrDefault(), false), true);
			}
		}
	}

	private static void RemoveTraits(List<TraitRequirement> traits, Pawn pawn)
	{
		foreach (TraitRequirement trait in traits)
		{
			for (int num = pawn.story.traits.allTraits.Count - 1; num >= 0; num--)
			{
				Trait val = pawn.story.traits.allTraits[num];
				if (val.sourceGene == null && val.def == trait.def && (!trait.degree.HasValue || trait.degree == val.Degree))
				{
					pawn.story.traits.RemoveTrait(val, true);
				}
			}
		}
	}

	public static float GetStatFactor(Thing gear, StatDef stat)
	{
		return StatUtility.GetStatFactorFromList((gear == null) ? null : ((Def)gear.def).GetModExtension<ApparelExtension>()?.equippedStatFactors, stat);
	}
}
