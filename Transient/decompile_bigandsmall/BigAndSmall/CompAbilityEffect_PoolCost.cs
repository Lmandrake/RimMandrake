using RimWorld;
using Verse;

namespace BigAndSmall;

public abstract class CompAbilityEffect_PoolCost : CompAbilityEffect
{
	public CompProperties_PoolCost Props => (CompProperties_PoolCost)(object)((AbilityComp)this).props;

	protected abstract bool HasEnoughResource { get; }

	public override bool CanCast
	{
		get
		{
			if (HasEnoughResource)
			{
				return ((AbilityComp)this).CanCast;
			}
			return false;
		}
	}

	public override bool AICanTargetNow(LocalTargetInfo target)
	{
		return HasEnoughResource;
	}

	protected float TotalostOfQueuedAbilities()
	{
		Verb obj = ((AbilityComp)this).parent.pawn.jobs?.curJob?.verbToUse;
		Verb_CastAbility val = (Verb_CastAbility)(object)((obj is Verb_CastAbility) ? obj : null);
		float num;
		if (val == null)
		{
			num = 0f;
		}
		else
		{
			Ability ability = val.ability;
			num = ((ability != null) ? ResourcePoolUtils.PoolCost(ability) : 0f);
		}
		float num2 = num;
		if (((AbilityComp)this).parent.pawn.jobs != null)
		{
			for (int i = 0; i < ((AbilityComp)this).parent.pawn.jobs.jobQueue.Count; i++)
			{
				Verb verbToUse = ((AbilityComp)this).parent.pawn.jobs.jobQueue[i].job.verbToUse;
				Verb_CastAbility val2 = (Verb_CastAbility)(object)((verbToUse is Verb_CastAbility) ? verbToUse : null);
				if (val2 != null)
				{
					float num3 = num2;
					Ability ability2 = val2.ability;
					num2 = num3 + ((ability2 != null) ? ResourcePoolUtils.PoolCost(ability2) : 0f);
				}
			}
		}
		return num2;
	}
}
