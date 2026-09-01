using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_FleckOnTargetFixed : CompAbilityEffect_FleckOnTarget
{
	public override bool AICanTargetNow(LocalTargetInfo target)
	{
		return true;
	}
}
