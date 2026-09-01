using Verse;

namespace BigAndSmall;

/// <summary>
/// Basically this Damageworker deals only half as much damage and attacks only the outer body parts.
/// </summary>
public class DamageWorker_OuterAndHalfDamage : DamageWorker_AddInjury
{
	public override DamageResult Apply(DamageInfo dinfo, Thing thing)
	{
		//IL_001d: Unknown result type (might be due to invalid IL or missing references)
		((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount * 0.5f);
		((DamageInfo)(ref dinfo)).SetAllowDamagePropagation(false);
		return ((DamageWorker_AddInjury)this).Apply(dinfo, thing);
	}

	protected override BodyPartRecord ChooseHitPart(DamageInfo dinfo, Pawn pawn)
	{
		//IL_0014: Unknown result type (might be due to invalid IL or missing references)
		return pawn.health.hediffSet.GetRandomNotMissingPart(((DamageInfo)(ref dinfo)).Def, ((DamageInfo)(ref dinfo)).Height, (BodyPartDepth)2, (BodyPartRecord)null);
	}
}
