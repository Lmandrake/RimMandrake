using System.Collections.Generic;
using RimWorld;
using Verse;

namespace BigAndSmall;

public class CompProperties_AbilitySprayLiquid : CompProperties_AbilityEffect
{
	public ThingDef projectileDef;

	public int radiusToHit;

	public EffecterDef sprayEffecter;

	public int projectileCount = 1;

	public List<StatScaling> scaling = new List<StatScaling>();

	public ProjectileByStat projectileByStat;

	public ThingDef GetProjectile(Pawn pawn)
	{
		return projectileByStat?.GetProjectileByStat(projectileDef, pawn) ?? projectileDef;
	}

	public CompProperties_AbilitySprayLiquid()
	{
		((AbilityCompProperties)this).compClass = typeof(CompAbilityEffect_SprayLiquid);
	}
}
