using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class GiveAbilitiesComp : HediffComp
{
	public CompProperties_GiveAbilities Props => (CompProperties_GiveAbilities)(object)base.props;

	public override void CompPostMake()
	{
		((HediffComp)this).CompPostMake();
		ApplyAbilities();
	}

	public override void CompExposeData()
	{
		((HediffComp)this).CompExposeData();
		ApplyAbilities();
	}

	public void ApplyAbilities()
	{
		Pawn pawn = ((Hediff)base.parent).pawn;
		List<AbilityDef> abilities = Props.abilities;
		if (pawn == null || abilities == null || GenCollection.Any<Ability>(pawn.abilities.abilities, (Predicate<Ability>)((Ability x) => abilities.Contains(x.def))))
		{
			return;
		}
		foreach (AbilityDef item in abilities)
		{
			pawn.abilities.GainAbility(item);
		}
	}

	public override void CompPostPostRemoved()
	{
		((HediffComp)this).CompPostPostRemoved();
		RemoveAbilities();
	}

	public void RemoveAbilities()
	{
		Pawn pawn = ((Hediff)base.parent).pawn;
		List<AbilityDef> abilities = Props.abilities;
		if (pawn == null || abilities == null || !GenCollection.Any<Ability>(pawn.abilities.abilities, (Predicate<Ability>)((Ability x) => abilities.Contains(x.def))))
		{
			return;
		}
		foreach (AbilityDef item in abilities)
		{
			pawn.abilities.RemoveAbility(item);
		}
	}
}
