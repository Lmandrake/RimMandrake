using Verse;

namespace BigAndSmall;

/// <summary>
/// Used to make Rimworld's attack picker think the attack deals 50% more damage than it actually does.
/// </summary>
public class DamageWorker_TwoThirdsDamage : DamageWorker_AddInjury
{
	public override DamageResult Apply(DamageInfo dinfo, Thing thing)
	{
		//IL_0015: Unknown result type (might be due to invalid IL or missing references)
		((DamageInfo)(ref dinfo)).SetAmount(((DamageInfo)(ref dinfo)).Amount * 0.66f);
		return ((DamageWorker_AddInjury)this).Apply(dinfo, thing);
	}
}
