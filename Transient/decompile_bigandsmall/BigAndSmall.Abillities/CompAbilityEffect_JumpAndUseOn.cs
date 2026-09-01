using System;
using RimWorld;
using Verse;

namespace BigAndSmall.Abillities;

public abstract class CompAbilityEffect_JumpAndUseOn : CompAbilityEffect, ICompAbilityEffectOnJumpCompleted
{
	public void OnJumpCompleted(IntVec3 origin, LocalTargetInfo target)
	{
		//IL_000a: Unknown result type (might be due to invalid IL or missing references)
		//IL_000b: Unknown result type (might be due to invalid IL or missing references)
		try
		{
			if (((LocalTargetInfo)(ref target)).Pawn != null)
			{
				ApplyEffect(origin, target);
			}
		}
		catch (Exception ex)
		{
			Log.Error(string.Format("Error in {0} (target {1}, user: {2}).\n{3}\n{4}", "CompAbilityEffect_JumpAndUseOn", ((LocalTargetInfo)(ref target)).Pawn, ((AbilityComp)this).parent?.pawn, ex.Message, ex.StackTrace));
		}
	}

	public abstract void ApplyEffect(IntVec3 origin, LocalTargetInfo target);
}
