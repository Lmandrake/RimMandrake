using RimWorld;
using Verse;

namespace BigAndSmall;

public static class ResourcePoolUtils
{
	public static void OffsetResource(Pawn pawn, float gain, Gene_Resource gene)
	{
		gene.Value += gain;
	}

	public static float PoolCost(Ability ab)
	{
		if (ab.comps != null)
		{
			foreach (AbilityComp comp in ab.comps)
			{
				if (comp is CompAbilityEffect_PoolCost compAbilityEffect_PoolCost)
				{
					return compAbilityEffect_PoolCost.Props.resourceCost;
				}
			}
		}
		return 0f;
	}
}
