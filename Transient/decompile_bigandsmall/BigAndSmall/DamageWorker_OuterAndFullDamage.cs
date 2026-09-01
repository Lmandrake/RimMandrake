using Verse;

namespace BigAndSmall;

public class DamageWorker_OuterAndFullDamage : DamageWorker_AddInjury
{
	public override DamageResult Apply(DamageInfo dinfo, Thing thing)
	{
		//IL_0017: Unknown result type (might be due to invalid IL or missing references)
		((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount);
		((DamageInfo)(ref dinfo)).SetAllowDamagePropagation(false);
		return ((DamageWorker_AddInjury)this).Apply(dinfo, thing);
	}

	protected override BodyPartRecord ChooseHitPart(DamageInfo dinfo, Pawn pawn)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		return pawn.health.hediffSet.GetRandomNotMissingPart(((DamageInfo)(ref dinfo)).Def, ((DamageInfo)(ref dinfo)).Height, (BodyPartDepth)2, (BodyPartRecord)null);
	}
}
