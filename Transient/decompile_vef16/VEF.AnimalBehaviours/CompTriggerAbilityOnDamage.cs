using RimWorld;
using Verse;

namespace VEF.AnimalBehaviours;

internal class CompTriggerAbilityOnDamage : ThingComp
{
	public CompProperties_TriggerAbilityOnDamage Props => (CompProperties_TriggerAbilityOnDamage)(object)base.props;

	public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
	{
		//IL_0058: Unknown result type (might be due to invalid IL or missing references)
		//IL_0064: Unknown result type (might be due to invalid IL or missing references)
		//IL_0069: Unknown result type (might be due to invalid IL or missing references)
		ThingWithComps parent = base.parent;
		Pawn val = (Pawn)(object)((parent is Pawn) ? parent : null);
		if (val != null && totalDamageDealt >= Props.minDamageToTrigger && ((DamageInfo)(ref dinfo)).Instigator != null)
		{
			Pawn_AbilityTracker abilities = val.abilities;
			Ability val2 = ((abilities != null) ? abilities.GetAbility(Props.ability, false) : null);
			if (val2 != null && !val2.OnCooldown)
			{
				val2.QueueCastingJob(LocalTargetInfo.op_Implicit(((DamageInfo)(ref dinfo)).Instigator), LocalTargetInfo.op_Implicit(((DamageInfo)(ref dinfo)).Instigator.Position));
			}
		}
	}
}
