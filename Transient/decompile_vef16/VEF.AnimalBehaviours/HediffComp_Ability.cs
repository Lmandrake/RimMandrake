using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

public class HediffComp_Ability : HediffComp
{
	public int tickCounter;

	public HediffCompProperties_Ability Props => (HediffCompProperties_Ability)(object)base.props;

	public override void CompPostTick(ref float severityAdjustment)
	{
		//IL_004c: Unknown result type (might be due to invalid IL or missing references)
		//IL_0056: Expected O, but got Unknown
		tickCounter++;
		if (tickCounter > Props.checkingInterval)
		{
			if (((Hediff)base.parent).pawn.abilities == null)
			{
				((Hediff)base.parent).pawn.abilities = new Pawn_AbilityTracker(((Hediff)base.parent).pawn);
			}
			if (((Hediff)base.parent).pawn.abilities.GetAbility(Props.ability, false) == null)
			{
				((Hediff)base.parent).pawn.abilities.GainAbility(Props.ability);
			}
			StaticCollectionsClass.AddAbilityUsingAnimalToList((Thing)(object)((Hediff)base.parent).pawn);
			tickCounter = 0;
		}
	}

	public override void CompPostPostAdd(DamageInfo? dinfo)
	{
		//IL_0028: Unknown result type (might be due to invalid IL or missing references)
		//IL_0032: Expected O, but got Unknown
		if (((Hediff)base.parent).pawn.abilities == null)
		{
			((Hediff)base.parent).pawn.abilities = new Pawn_AbilityTracker(((Hediff)base.parent).pawn);
		}
		if (((Hediff)base.parent).pawn.abilities.GetAbility(Props.ability, false) == null)
		{
			((Hediff)base.parent).pawn.abilities.GainAbility(Props.ability);
		}
		StaticCollectionsClass.AddAbilityUsingAnimalToList((Thing)(object)((Hediff)base.parent).pawn);
	}

	public override void CompPostPostRemoved()
	{
		((Hediff)base.parent).pawn.abilities.RemoveAbility(Props.ability);
	}
}
