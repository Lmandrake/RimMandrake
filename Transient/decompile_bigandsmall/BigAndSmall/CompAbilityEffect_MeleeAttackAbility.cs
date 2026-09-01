using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

internal class CompAbilityEffect_MeleeAttackAbility : CompAbilityEffect
{
	public CompProperties_MeleeAttackAbility Props => (CompProperties_MeleeAttackAbility)(object)((AbilityComp)this).props;

	public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
	{
		//IL_0001: Unknown result type (might be due to invalid IL or missing references)
		//IL_0002: Unknown result type (might be due to invalid IL or missing references)
		((CompAbilityEffect)this).Apply(target, dest);
		Pawn pawn = ((LocalTargetInfo)(ref target)).Pawn;
		if (pawn != null)
		{
			PerformAttack(((AbilityComp)this).parent.pawn, (Thing)(object)pawn);
		}
	}

	public void PerformAttack(Pawn attacker, Thing target)
	{
		//IL_0073: Unknown result type (might be due to invalid IL or missing references)
		//IL_007a: Unknown result type (might be due to invalid IL or missing references)
		//IL_0040: Unknown result type (might be due to invalid IL or missing references)
		if (!Props.asExplosion)
		{
			DamageInfo val = default(DamageInfo);
			((DamageInfo)(ref val))._002Ector(Props.damageDef, (float)Props.damageAmount, 0f, -1f, (Thing)(object)attacker, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false);
			target.TakeDamage(val);
			return;
		}
		new DamageInfo(Props.damageDef, (float)Props.damageAmount, 0f, -1f, (Thing)(object)attacker, (BodyPartRecord)null, (ThingDef)null, (SourceCategory)0, (Thing)null, true, true, (QualityCategory)2, true, false);
		IntVec3 position = target.Position;
		Map map = target.Map;
		DamageDef damageDef = Props.damageDef;
		int damageAmount = Props.damageAmount;
		float num = Props.armorPenetration;
		FloatRange? val2 = null;
		float screenShakeFactor = Props.screenShakeFactor;
		GenExplosion.DoExplosion(position, map, 0.9f, damageDef, (Thing)(object)attacker, damageAmount, num, (SoundDef)null, (ThingDef)null, (ThingDef)null, target, (ThingDef)null, 0f, 1, (GasType?)null, (float?)null, 255, false, (ThingDef)null, 0f, 1, 0f, false, (float?)null, (List<Thing>)null, val2, false, 1f, 0f, false, (ThingDef)null, screenShakeFactor, (SimpleCurve)null, (List<IntVec3>)null, (ThingDef)null, (ThingDef)null);
	}
}
