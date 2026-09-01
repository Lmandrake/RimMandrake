using System.Collections.Generic;
using Verse;

namespace VEF.Abilities;

public class PawnKindAbilityExtension : DefModExtension
{
	public List<AbilityDef> giveAbilities = new List<AbilityDef>();

	public HediffDef implantDef;

	public int initialLevel = 1;

	public bool giveRandomAbilities;
}
