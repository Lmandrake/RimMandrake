using RimWorld;
using UnityEngine;
using Verse;

namespace BigAndSmall;

public class CompAbilityEffect_SlimeCost : CompAbilityEffect_PoolCost
{
	public new CompProperties_SlimeCost Props => (CompProperties_SlimeCost)(object)((AbilityComp)this).props;

	protected override bool HasEnoughResource
	{
		get
		{
			Pawn_GeneTracker genes = ((AbilityComp)this).parent.pawn.genes;
			BS_GeneSlimePower bS_GeneSlimePower = ((genes != null) ? genes.GetFirstGeneOfType<BS_GeneSlimePower>() : null);
			if (bS_GeneSlimePower != null)
			{
				return ((Gene_Resource)bS_GeneSlimePower).Value >= Props.resourceCost;
			}
			return false;
		}
	}

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).Apply(target, dest);
		Pawn_GeneTracker genes = ((AbilityComp)this).parent.pawn.genes;
		BS_GeneSlimePower bS_GeneSlimePower = ((genes != null) ? genes.GetFirstGeneOfType<BS_GeneSlimePower>() : null);
		ResourcePoolUtils.OffsetResource(((AbilityComp)this).parent.pawn, 0f - Props.resourceCost, (Gene_Resource)(object)bS_GeneSlimePower);
		bS_GeneSlimePower.GetSlimeHediff().Severity = Mathf.Clamp(((Gene_Resource)bS_GeneSlimePower).Value, 0.05f, 9999f);
	}

	public override bool GizmoDisabled(out string reason)
	{
		Pawn_GeneTracker genes = ((AbilityComp)this).parent.pawn.genes;
		BS_GeneSlimePower bS_GeneSlimePower = ((genes != null) ? genes.GetFirstGeneOfType<BS_GeneSlimePower>() : null);
		if (bS_GeneSlimePower == null)
		{
			reason = "Ability Disabled: Missing Required Power Gene";
			return true;
		}
		if (((Gene_Resource)bS_GeneSlimePower).Value < Props.resourceCost)
		{
			reason = "Ability Disabled: Not enough Power";
			return true;
		}
		float num = TotalostOfQueuedAbilities();
		float num2 = Props.resourceCost + num;
		if (Props.resourceCost > float.Epsilon && num2 > ((Gene_Resource)bS_GeneSlimePower).Value)
		{
			reason = "Ability Disabled: Not enough Power";
			return true;
		}
		reason = null;
		return false;
	}
}
