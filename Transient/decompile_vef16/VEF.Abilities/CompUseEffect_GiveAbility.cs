using RimWorld;
using Verse;

namespace VEF.Abilities;

public class CompUseEffect_GiveAbility : CompUseEffect
{
	public CompProperties_UseEffectGiveAbility Props => (CompProperties_UseEffectGiveAbility)(object)((ThingComp)this).props;

	public override void DoEffect(Pawn usedBy)
	{
		((CompUseEffect)this).DoEffect(usedBy);
		if (Props.ability != null)
		{
			((ThingWithComps)usedBy).GetComp<CompAbilities>()?.GiveAbility(Props.ability);
		}
		else
		{
			(usedBy.health.hediffSet.GetFirstHediffOfDef(Props.requiredHediff, false) as Hediff_Abilities)?.GiveRandomAbilityAtLevel(Props.level);
		}
	}

	public override AcceptanceReport CanBeUsedBy(Pawn p)
	{
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		//IL_001e: Unknown result type (might be due to invalid IL or missing references)
		//IL_000f: Unknown result type (might be due to invalid IL or missing references)
		if (!AcceptanceReport.op_Implicit(((CompUseEffect)this).CanBeUsedBy(p)))
		{
			return AcceptanceReport.op_Implicit(false);
		}
		return AcceptanceReport.op_Implicit(((ThingWithComps)p).GetComp<CompAbilities>() != null);
	}
}
