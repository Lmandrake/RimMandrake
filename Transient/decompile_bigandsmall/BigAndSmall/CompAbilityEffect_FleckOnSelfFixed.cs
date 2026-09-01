using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_FleckOnSelfFixed : CompAbilityEffect_FleckOnTargetFixed
{
	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_000c: Unknown result type (might be due to invalid IL or missing references)
		//IL_001c: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect_FleckOnTarget)this).Apply(LocalTargetInfo.op_Implicit((Thing)(object)((AbilityComp)this).parent.pawn), LocalTargetInfo.op_Implicit((Thing)(object)((AbilityComp)this).parent.pawn));
	}
}
