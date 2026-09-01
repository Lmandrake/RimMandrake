using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_GiveAbilities : HediffCompProperties
{
	public List<AbilityDef> abilities;

	public CompProperties_GiveAbilities()
	{
		base.compClass = typeof(GiveAbilitiesComp);
	}
}
