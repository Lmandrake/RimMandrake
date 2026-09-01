using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_SoulEnergyCost : CompAbilityEffect_PoolCost
{
	protected readonly SoulEnergyTracker soulTracker = new SoulEnergyTracker();

	public new CompProperties_SoulEnergyCost Props => (CompProperties_SoulEnergyCost)(object)((AbilityComp)this).props;

	protected SoulResourceHediff Resource => soulTracker.Resource(((AbilityComp)this).parent.pawn);

	protected override bool HasEnoughResource
	{
		get
		{
			SoulResourceHediff resource = Resource;
			if (resource != null)
			{
				return resource.Value >= Props.resourceCost;
			}
			return false;
		}
	}

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).Apply(target, dest);
		Resource.Value -= Props.resourceCost;
	}

	public override bool GizmoDisabled(out string reason)
	{
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_0066: Unknown result type (might be due to invalid IL or missing references)
		if (Resource.Value < Props.resourceCost)
		{
			reason = TaggedString.op_Implicit(Translator.Translate("BS_NotEnoughSoulEnergy"));
			return true;
		}
		float num = TotalostOfQueuedAbilities();
		float num2 = Props.resourceCost + num;
		if (Props.resourceCost > float.Epsilon && num2 > Resource.Value)
		{
			reason = TaggedString.op_Implicit(Translator.Translate("BS_NotEnoughSoulEnergy"));
			return true;
		}
		reason = null;
		return false;
	}
}
