using System.Collections.Generic;
using Verse;

namespace VEF.Abilities;

public class CompProperties_AbilitiesApparel : CompProperties
{
	public List<AbilityDef> abilities;

	public CompProperties_AbilitiesApparel()
	{
		base.compClass = typeof(CompAbilitiesApparel);
	}
}
