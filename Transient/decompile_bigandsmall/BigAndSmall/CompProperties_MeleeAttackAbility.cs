using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_MeleeAttackAbility : CompProperties_AbilityEffect
{
	public DamageDef damageDef;

	public int damageAmount;

	public int armorPenetration;

	public float screenShakeFactor = 0.1f;

	public bool asExplosion;

	public CompProperties_MeleeAttackAbility()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_MeleeAttackAbility);
	}
}
